"""
Column mapping utility for FarmFactory data import system.

Provides intelligent column name mapping with fuzzy matching,
auto-detection, and confidence scoring.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher


class ColumnMapper:
    """Intelligent column name mapper with fuzzy matching."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the column mapper.

        Args:
            config_path: Path to column_mappings.json config file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "import_config" / "column_mappings.json"

        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.fuzzy_config = self.config.get("fuzzy_matching", {})
        self.auto_detect_rules = self.config.get("auto_detection_rules", {})

    def normalize_column_name(self, col_name: str) -> str:
        """
        Normalize a column name for comparison.

        Args:
            col_name: Raw column name from CSV

        Returns:
            Normalized column name
        """
        if not self.fuzzy_config.get("case_sensitive", False):
            col_name = col_name.lower()

        if self.fuzzy_config.get("strip_whitespace", True):
            col_name = col_name.strip()

        if self.fuzzy_config.get("ignore_special_chars", True):
            # Keep only alphanumeric and underscores
            col_name = re.sub(r'[^a-zA-Z0-9_]', '_', col_name)
            # Replace multiple underscores with single
            col_name = re.sub(r'_+', '_', col_name)
            col_name = col_name.strip('_')

        return col_name

    def calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity score between two strings.

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Normalize both strings
        str1 = self.normalize_column_name(str1)
        str2 = self.normalize_column_name(str2)

        # Exact match
        if str1 == str2:
            return 1.0

        # SequenceMatcher for Levenshtein-like similarity
        return SequenceMatcher(None, str1, str2).ratio()

    def map_column(
        self,
        source_column: str,
        data_type: str,
        threshold: Optional[float] = None
    ) -> Tuple[Optional[str], float, List[Tuple[str, float]]]:
        """
        Map a source column to a target field.

        Args:
            source_column: Column name from CSV file
            data_type: Data type (e.g., 'farms_and_plots', 'irrigation_events')
            threshold: Minimum similarity threshold (default from config)

        Returns:
            Tuple of (best_match, confidence_score, all_candidates)
            - best_match: Target field name or None
            - confidence_score: Confidence (0.0 to 1.0)
            - all_candidates: List of (field_name, score) for all matches
        """
        if threshold is None:
            threshold = self.fuzzy_config.get("similarity_threshold", 0.8)

        if data_type not in self.config:
            return None, 0.0, []

        field_mappings = self.config[data_type]
        candidates = []

        for target_field, field_config in field_mappings.items():
            variations = field_config.get("variations", [])
            priority = field_config.get("priority", 50)

            # Check exact matches first
            for variation in variations:
                similarity = self.calculate_similarity(source_column, variation)

                # Apply priority boost for exact or near-exact matches
                if similarity >= 0.95:
                    similarity = min(1.0, similarity * (1 + priority / 1000))

                candidates.append((target_field, similarity))

        # Check for unit conversions
        for target_field, field_config in field_mappings.items():
            unit_conversions = field_config.get("unit_conversions", {})
            for conversion_col, _ in unit_conversions.items():
                similarity = self.calculate_similarity(source_column, conversion_col)
                if similarity >= 0.95:
                    # Mark as unit conversion candidate
                    similarity = min(1.0, similarity * 0.95)  # Slightly lower than direct match
                    candidates.append((f"{target_field}__convert_from_{conversion_col}", similarity))

        # Sort by similarity score
        candidates.sort(key=lambda x: x[1], reverse=True)

        # Get best match above threshold
        if candidates and candidates[0][1] >= threshold:
            best_match, best_score = candidates[0]
            return best_match, best_score, candidates[:5]  # Return top 5

        return None, 0.0, candidates[:5]

    def map_columns(
        self,
        source_columns: List[str],
        data_type: str,
        threshold: Optional[float] = None
    ) -> Dict[str, Dict]:
        """
        Map all source columns to target fields.

        Args:
            source_columns: List of column names from CSV
            data_type: Data type (e.g., 'farms_and_plots')
            threshold: Minimum similarity threshold

        Returns:
            Dictionary mapping source columns to:
            {
                'source_column_1': {
                    'target_field': 'mapped_field_name',
                    'confidence': 0.95,
                    'requires_conversion': False,
                    'conversion_type': None,
                    'alternatives': [(field, score), ...]
                },
                ...
            }
        """
        results = {}

        for source_col in source_columns:
            best_match, confidence, alternatives = self.map_column(
                source_col, data_type, threshold
            )

            requires_conversion = False
            conversion_type = None
            target_field = best_match

            # Check if this is a unit conversion mapping
            if best_match and "__convert_from_" in best_match:
                parts = best_match.split("__convert_from_")
                target_field = parts[0]
                conversion_source = parts[1]
                requires_conversion = True

                # Get conversion type from config
                field_config = self.config[data_type].get(target_field, {})
                unit_conversions = field_config.get("unit_conversions", {})
                conversion_type = unit_conversions.get(conversion_source)

            results[source_col] = {
                'target_field': target_field,
                'confidence': confidence,
                'requires_conversion': requires_conversion,
                'conversion_type': conversion_type,
                'alternatives': alternatives,
                'is_mapped': confidence >= (threshold or 0.8)
            }

        return results

    def get_unmapped_required_fields(
        self,
        mapping_results: Dict[str, Dict],
        data_type: str
    ) -> List[str]:
        """
        Get list of required fields that were not mapped.

        Args:
            mapping_results: Results from map_columns()
            data_type: Data type

        Returns:
            List of unmapped required field names
        """
        if data_type not in self.config:
            return []

        field_mappings = self.config[data_type]
        mapped_fields = set()

        for result in mapping_results.values():
            if result['is_mapped'] and result['target_field']:
                mapped_fields.add(result['target_field'])

        unmapped_required = []
        for field_name, field_config in field_mappings.items():
            if field_config.get('required', False) and field_name not in mapped_fields:
                unmapped_required.append(field_name)

        return unmapped_required

    def get_field_info(self, data_type: str, field_name: str) -> Optional[Dict]:
        """
        Get information about a target field.

        Args:
            data_type: Data type
            field_name: Target field name

        Returns:
            Field configuration dictionary or None
        """
        if data_type not in self.config:
            return None

        return self.config[data_type].get(field_name)

    def validate_data_type(self, data_type: str) -> bool:
        """
        Check if a data type is supported.

        Args:
            data_type: Data type to validate

        Returns:
            True if supported, False otherwise
        """
        return data_type in self.config and data_type not in [
            "fuzzy_matching", "auto_detection_rules"
        ]

    def get_supported_data_types(self) -> List[str]:
        """
        Get list of supported data types.

        Returns:
            List of data type names
        """
        return [
            key for key in self.config.keys()
            if key not in ["fuzzy_matching", "auto_detection_rules"]
        ]

    def auto_detect_data_type(self, columns: List[str]) -> Optional[str]:
        """
        Attempt to auto-detect the data type based on column names.

        Args:
            columns: List of column names from CSV

        Returns:
            Detected data type or None
        """
        scores = {}

        for data_type in self.get_supported_data_types():
            mapping_results = self.map_columns(columns, data_type, threshold=0.7)

            # Calculate score based on number of mapped fields and confidence
            mapped_count = sum(1 for r in mapping_results.values() if r['is_mapped'])
            avg_confidence = sum(r['confidence'] for r in mapping_results.values()) / len(mapping_results) if mapping_results else 0

            # Get required fields match rate
            required_fields = [
                f for f, cfg in self.config[data_type].items()
                if cfg.get('required', False)
            ]
            mapped_required = sum(
                1 for r in mapping_results.values()
                if r['is_mapped'] and r['target_field'] in required_fields
            )
            required_match_rate = mapped_required / len(required_fields) if required_fields else 0

            # Combined score
            scores[data_type] = (
                (mapped_count / len(columns)) * 0.3 +
                avg_confidence * 0.3 +
                required_match_rate * 0.4
            )

        # Get data type with highest score
        if scores:
            best_type = max(scores.items(), key=lambda x: x[1])
            if best_type[1] >= 0.6:  # Minimum confidence threshold
                return best_type[0]

        return None


# Convenience function
def map_csv_columns(
    columns: List[str],
    data_type: str,
    threshold: float = 0.8
) -> Dict[str, Dict]:
    """
    Convenience function to map CSV columns.

    Args:
        columns: List of column names from CSV
        data_type: Data type (e.g., 'farms_and_plots')
        threshold: Minimum similarity threshold

    Returns:
        Mapping results dictionary
    """
    mapper = ColumnMapper()
    return mapper.map_columns(columns, data_type, threshold)
