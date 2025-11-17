"""
File Storage Service for FarmFactory

Handles file uploads, validation, and storage management for import data.
Includes file size validation, MIME type checking, and automatic cleanup.
"""

import os
import shutil
import magic
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
import aiofiles

# Allowed file types
ALLOWED_MIME_TYPES = {
    "text/csv": [".csv"],
    "application/vnd.ms-excel": [".xls"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
}

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

# Magic number signatures for file type verification
MAGIC_SIGNATURES = {
    "csv": [b"\xef\xbb\xbf"],  # UTF-8 BOM (optional)
    "xlsx": [b"PK\x03\x04"],   # ZIP signature (XLSX is ZIP-based)
    "xls": [b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"],  # OLE2 signature
}

# Storage paths
UPLOAD_BASE_DIR = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))
STAGING_DIR = UPLOAD_BASE_DIR / "staging"
PROCESSED_DIR = UPLOAD_BASE_DIR / "processed"
FAILED_DIR = UPLOAD_BASE_DIR / "failed"

# File constraints
MAX_FILE_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
FILE_RETENTION_DAYS = int(os.getenv("FILE_RETENTION_DAYS", "30"))


class FileStorageService:
    """Service for managing file uploads and storage"""

    def __init__(self):
        """Initialize storage service and ensure directories exist"""
        self._ensure_directories()

    @staticmethod
    def _ensure_directories():
        """Create storage directories if they don't exist"""
        for directory in [STAGING_DIR, PROCESSED_DIR, FAILED_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _generate_unique_filename(original_filename: str) -> str:
        """
        Generate a unique filename to prevent collisions

        Args:
            original_filename: Original filename from upload

        Returns:
            Unique filename with timestamp
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        name, ext = os.path.splitext(original_filename)
        # Sanitize filename
        safe_name = "".join(c for c in name if c.isalnum() or c in ("-", "_"))[:50]
        return f"{safe_name}_{timestamp}{ext}"

    @staticmethod
    def _validate_file_extension(filename: str) -> bool:
        """
        Validate file extension

        Args:
            filename: Name of the file

        Returns:
            True if extension is allowed, False otherwise
        """
        ext = os.path.splitext(filename)[1].lower()
        return ext in ALLOWED_EXTENSIONS

    @staticmethod
    def _validate_mime_type(file_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate MIME type using python-magic

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (is_valid, mime_type)
        """
        try:
            mime = magic.Magic(mime=True)
            mime_type = mime.from_file(str(file_path))

            # Check if MIME type is allowed
            if mime_type in ALLOWED_MIME_TYPES:
                return True, mime_type

            # Special case: CSV files might be detected as text/plain
            if mime_type == "text/plain" and file_path.suffix.lower() == ".csv":
                return True, "text/csv"

            return False, mime_type
        except Exception as e:
            return False, None

    @staticmethod
    def _validate_magic_number(file_path: Path) -> bool:
        """
        Validate file by checking magic numbers (file signature)
        Prevents fake file extensions

        Args:
            file_path: Path to the file

        Returns:
            True if magic number matches extension, False otherwise
        """
        try:
            with open(file_path, "rb") as f:
                header = f.read(8)  # Read first 8 bytes

            ext = file_path.suffix.lower().lstrip(".")

            # CSV is plain text, so we allow it if it starts with printable characters
            if ext == "csv":
                # Check if file starts with printable ASCII or UTF-8 BOM
                return header[:3] == b"\xef\xbb\xbf" or all(
                    32 <= b < 127 or b in (9, 10, 13) for b in header[:20]
                )

            # Check XLSX (ZIP signature)
            if ext == "xlsx":
                return header[:4] == b"PK\x03\x04"

            # Check XLS (OLE2 signature)
            if ext == "xls":
                return header == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"

            return False
        except Exception:
            return False

    async def validate_and_save_file(
        self, file: UploadFile, max_size_bytes: Optional[int] = None
    ) -> Tuple[Path, dict]:
        """
        Validate and save uploaded file to staging directory

        Args:
            file: FastAPI UploadFile object
            max_size_bytes: Maximum file size in bytes (defaults to MAX_FILE_SIZE_BYTES)

        Returns:
            Tuple of (file_path, metadata_dict)

        Raises:
            HTTPException: If validation fails
        """
        max_size = max_size_bytes or MAX_FILE_SIZE_BYTES

        # Validate extension
        if not self._validate_file_extension(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        # Generate unique filename
        unique_filename = self._generate_unique_filename(file.filename)
        file_path = STAGING_DIR / unique_filename

        # Save file and validate size
        file_size = 0
        try:
            async with aiofiles.open(file_path, "wb") as f:
                while chunk := await file.read(8192):  # Read in 8KB chunks
                    file_size += len(chunk)
                    if file_size > max_size:
                        # Clean up partial file
                        await f.close()
                        file_path.unlink(missing_ok=True)
                        raise HTTPException(
                            status_code=413,
                            detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB",
                        )
                    await f.write(chunk)
        except HTTPException:
            raise
        except Exception as e:
            # Clean up on error
            file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=500, detail=f"Error saving file: {str(e)}"
            )

        # Validate MIME type
        is_valid_mime, mime_type = self._validate_mime_type(file_path)
        if not is_valid_mime:
            file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Detected: {mime_type}. Allowed: CSV, XLSX, XLS",
            )

        # Validate magic number (prevent fake extensions)
        if not self._validate_magic_number(file_path):
            file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail="File content does not match extension. File may be corrupted or have fake extension.",
            )

        # Create metadata
        metadata = {
            "original_filename": file.filename,
            "stored_filename": unique_filename,
            "file_path": str(file_path),
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "mime_type": mime_type,
            "uploaded_at": datetime.utcnow().isoformat(),
        }

        return file_path, metadata

    @staticmethod
    def move_to_processed(file_path: Path) -> Path:
        """
        Move file from staging to processed directory

        Args:
            file_path: Path to file in staging directory

        Returns:
            New path in processed directory
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        destination = PROCESSED_DIR / file_path.name
        shutil.move(str(file_path), str(destination))
        return destination

    @staticmethod
    def move_to_failed(file_path: Path, error_info: Optional[str] = None) -> Path:
        """
        Move file from staging to failed directory

        Args:
            file_path: Path to file in staging directory
            error_info: Optional error information to save

        Returns:
            New path in failed directory
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        destination = FAILED_DIR / file_path.name
        shutil.move(str(file_path), str(destination))

        # Save error info if provided
        if error_info:
            error_file = destination.with_suffix(destination.suffix + ".error.txt")
            error_file.write_text(error_info)

        return destination

    @staticmethod
    def cleanup_old_files(retention_days: Optional[int] = None) -> dict:
        """
        Clean up files older than retention period

        Args:
            retention_days: Number of days to retain files (defaults to FILE_RETENTION_DAYS)

        Returns:
            Dictionary with cleanup statistics
        """
        retention = retention_days or FILE_RETENTION_DAYS
        cutoff_date = datetime.utcnow() - timedelta(days=retention)

        stats = {"deleted_count": 0, "freed_bytes": 0, "errors": []}

        # Clean up all directories
        for directory in [STAGING_DIR, PROCESSED_DIR, FAILED_DIR]:
            if not directory.exists():
                continue

            for file_path in directory.iterdir():
                if not file_path.is_file():
                    continue

                try:
                    # Check file modification time
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

                    if file_mtime < cutoff_date:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        stats["deleted_count"] += 1
                        stats["freed_bytes"] += file_size
                except Exception as e:
                    stats["errors"].append(f"Error deleting {file_path}: {str(e)}")

        stats["freed_mb"] = round(stats["freed_bytes"] / (1024 * 1024), 2)
        return stats

    @staticmethod
    def get_storage_stats() -> dict:
        """
        Get storage statistics

        Returns:
            Dictionary with storage statistics
        """
        stats = {
            "staging": {"count": 0, "size_bytes": 0},
            "processed": {"count": 0, "size_bytes": 0},
            "failed": {"count": 0, "size_bytes": 0},
        }

        for dir_name, directory in [
            ("staging", STAGING_DIR),
            ("processed", PROCESSED_DIR),
            ("failed", FAILED_DIR),
        ]:
            if not directory.exists():
                continue

            for file_path in directory.iterdir():
                if file_path.is_file():
                    stats[dir_name]["count"] += 1
                    stats[dir_name]["size_bytes"] += file_path.stat().st_size

            stats[dir_name]["size_mb"] = round(
                stats[dir_name]["size_bytes"] / (1024 * 1024), 2
            )

        # Total stats
        stats["total"] = {
            "count": sum(s["count"] for s in stats.values() if isinstance(s, dict)),
            "size_bytes": sum(
                s["size_bytes"] for s in stats.values() if isinstance(s, dict)
            ),
        }
        stats["total"]["size_mb"] = round(
            stats["total"]["size_bytes"] / (1024 * 1024), 2
        )

        return stats


# Singleton instance
storage_service = FileStorageService()
