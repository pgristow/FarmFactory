# Import System Database Quick Start Guide

**For Backend Developers - Sprint 2**

---

## Quick Setup (2 minutes)

### 1. Run the Migration
```bash
cd backend
alembic upgrade head
```

This creates:
- ✅ 3 tables (import_jobs, import_errors, import_templates)
- ✅ 3 enum types
- ✅ 4 monitoring views
- ✅ 18 indexes

### 2. Verify Installation
```python
from app.models.import_job import ImportJob, ImportError, ImportTemplate
from app.models.views import get_import_statistics

# Should run without errors
print("Import system ready!")
```

---

## Common Usage Patterns

### Pattern 1: Create Import Job

```python
from app.models.import_job import ImportJob, ImportStatus, DataType

# Create new import job
job = ImportJob(
    file_name="farms_data.csv",
    file_size=1048576,  # 1MB
    file_path="/uploads/farms_data.csv",
    file_type="csv",
    data_type=DataType.FARMS_PLOTS,
    status=ImportStatus.PENDING,
    total_rows=1000
)

session.add(job)
session.commit()

print(f"Job ID: {job.id}")
```

### Pattern 2: Update Job Progress

```python
# Update progress during processing
job.status = ImportStatus.PROCESSING
job.started_at = datetime.now()
job.processed_rows = 500
job.successful_rows = 480
job.failed_rows = 20

session.commit()

# Check progress
print(f"Progress: {job.progress_percentage}%")
print(f"Success rate: {job.success_rate}%")
```

### Pattern 3: Log Import Errors

```python
from app.models.import_job import ImportError, ErrorType

# Log a validation error
error = ImportError(
    job_id=job.id,
    row_number=42,
    column_name="total_area_hectares",
    error_type=ErrorType.RANGE_ERROR,
    error_message="Area cannot be negative",
    invalid_value="-5.2",
    suggested_value="5.2",
    row_data={"name": "Test Farm", "area": -5.2}
)

session.add(error)
session.commit()
```

### Pattern 4: Bulk Insert Data

```python
from app.utils.bulk_insert import bulk_insert_csv

# Fast CSV import
result = bulk_insert_csv(
    session=session,
    model=Farm,
    csv_file_path="/uploads/farms.csv",
    use_copy=True,  # Fastest method
    progress_callback=lambda p: print(f"{p:.1f}% complete")
)

print(f"Imported {result.successful_rows} rows in {result.duration_seconds}s")
print(f"Speed: {result.rows_per_second:.0f} rows/second")
```

### Pattern 5: Complete Job Successfully

```python
# Mark job as complete
job.status = ImportStatus.COMPLETED
job.completed_at = datetime.now()
job.processed_rows = job.total_rows
job.successful_rows = 980
job.failed_rows = 20

session.commit()
```

### Pattern 6: Handle Job Failure

```python
# Mark job as failed
job.status = ImportStatus.FAILED
job.completed_at = datetime.now()
job.error_message = "File format not recognized"
job.error_summary = {
    "parse_error": 1,
    "validation_error": 0
}

session.commit()
```

### Pattern 7: Monitor Import Statistics

```python
from app.models.views import (
    get_import_statistics,
    get_import_job_details,
    get_error_frequency
)

# Overall stats
stats = get_import_statistics(session)
print(f"Total imports: {stats['total_imports']}")
print(f"Success rate: {stats['success_rate_percent']}%")
print(f"Last 24h: {stats['imports_last_24h']}")

# Specific job details
job_details = get_import_job_details(session, job_id)
print(f"Progress: {job_details['progress_percent']}%")
print(f"Errors: {job_details['error_count']}")

# Error analytics
errors = get_error_frequency(session)
for error in errors:
    print(f"{error['error_type']}: {error['total_occurrences']} times")
```

### Pattern 8: Save Import Template

```python
from app.models.import_job import ImportTemplate, DataType

# Save successful column mapping as template
template = ImportTemplate(
    name="Standard Farm Import",
    description="Standard column mapping for farm CSV files",
    data_type=DataType.FARMS_PLOTS,
    column_mappings={
        "Farm Name": "name",
        "Area (hectares)": "total_area_hectares",
        "Address": "address",
        "Latitude": "latitude",
        "Longitude": "longitude"
    },
    is_default=True,
    is_active=True
)

session.add(template)
session.commit()
```

### Pattern 9: Load and Use Template

```python
# Find default template for data type
template = session.query(ImportTemplate)\
    .filter_by(
        data_type=DataType.FARMS_PLOTS,
        is_default=True,
        is_active=True
    )\
    .first()

if template:
    # Use template mappings
    column_mapping = template.column_mappings

    # Update usage stats
    template.use_count += 1
    template.last_used_at = datetime.now()
    session.commit()
```

---

## Performance Tips

### For Small Imports (<1,000 rows)
```python
# Use standard ORM methods
farms = [Farm(**data) for data in farm_data]
session.bulk_insert_mappings(Farm, farm_data)
session.commit()
```

### For Medium Imports (1,000-10,000 rows)
```python
# Use bulk_insert_dataframe with batching
result = bulk_insert_dataframe(
    session=session,
    model=Farm,
    dataframe=df,
    batch_size=500  # Process 500 rows at a time
)
```

### For Large Imports (>10,000 rows)
```python
# Use COPY FROM for maximum speed
result = bulk_insert_csv(
    session=session,
    model=Farm,
    csv_file_path="large_file.csv",
    use_copy=True  # ~50,000-100,000 rows/second
)
```

### For Very Large Imports (>100,000 rows)
```python
from app.utils.bulk_insert import disable_indexes

# Disable indexes during import
with disable_indexes(session, 'farms'):
    result = bulk_insert_csv(
        session=session,
        model=Farm,
        csv_file_path="huge_file.csv",
        use_copy=True
    )
# Indexes automatically rebuilt after 'with' block
```

---

## API Endpoint Examples

### POST /api/v1/import/upload

```python
@router.post("/upload")
async def upload_import_file(
    file: UploadFile,
    data_type: DataType,
    db: Session = Depends(get_db)
):
    # Save file
    file_path = save_uploaded_file(file)

    # Create import job
    job = ImportJob(
        file_name=file.filename,
        file_size=file.size,
        file_path=file_path,
        file_type=file.filename.split('.')[-1],
        data_type=data_type,
        status=ImportStatus.UPLOADED
    )

    db.add(job)
    db.commit()

    return {"job_id": str(job.id), "status": job.status}
```

### GET /api/v1/import/status/{job_id}

```python
from app.models.views import get_import_job_details

@router.get("/status/{job_id}")
async def get_import_status(
    job_id: UUID,
    db: Session = Depends(get_db)
):
    # Get detailed job info from view
    details = get_import_job_details(db, str(job_id))

    if not details:
        raise HTTPException(404, "Job not found")

    return {
        "job_id": job_id,
        "status": details['status'],
        "progress": details['progress_percent'],
        "success_rate": details['success_rate_percent'],
        "error_count": details['error_count']
    }
```

### GET /api/v1/import/history

```python
from app.models.views import get_import_statistics

@router.get("/history")
async def get_import_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    # Query jobs with pagination
    jobs = db.execute(
        text("""
            SELECT * FROM v_import_job_details
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :skip
        """),
        {"limit": limit, "skip": skip}
    ).fetchall()

    # Get overall stats
    stats = get_import_statistics(db)

    return {
        "jobs": [dict(job._mapping) for job in jobs],
        "stats": stats
    }
```

### GET /api/v1/import/{job_id}/errors

```python
@router.get("/{job_id}/errors")
async def get_import_errors(
    job_id: UUID,
    error_type: Optional[ErrorType] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(ImportError).filter_by(job_id=job_id)

    if error_type:
        query = query.filter_by(error_type=error_type)

    errors = query.order_by(ImportError.row_number)\
                  .limit(limit)\
                  .all()

    return {
        "job_id": job_id,
        "error_count": len(errors),
        "errors": [
            {
                "row": e.row_number,
                "column": e.column_name,
                "type": e.error_type.value,
                "message": e.error_message,
                "invalid_value": e.invalid_value,
                "suggested_value": e.suggested_value
            }
            for e in errors
        ]
    }
```

---

## Celery Task Example

```python
from celery import Task
from app.utils.bulk_insert import bulk_insert_csv
from app.models.import_job import ImportJob, ImportStatus

@celery.task(bind=True)
def process_import_task(self: Task, job_id: str):
    """
    Celery task to process import job asynchronously.
    """
    db = SessionLocal()

    try:
        # Get job
        job = db.query(ImportJob).filter_by(id=job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Update status
        job.status = ImportStatus.PROCESSING
        job.started_at = datetime.now()
        db.commit()

        # Progress callback for Celery
        def update_progress(percent):
            self.update_state(
                state='PROGRESS',
                meta={'percent': percent}
            )

        # Perform bulk insert
        result = bulk_insert_csv(
            session=db,
            model=get_model_for_data_type(job.data_type),
            csv_file_path=job.file_path,
            use_copy=True,
            progress_callback=update_progress
        )

        # Update job with results
        job.status = ImportStatus.COMPLETED
        job.completed_at = datetime.now()
        job.processed_rows = result.total_rows
        job.successful_rows = result.successful_rows
        job.failed_rows = result.failed_rows

        db.commit()

        return {
            "status": "completed",
            "successful_rows": result.successful_rows,
            "failed_rows": result.failed_rows
        }

    except Exception as e:
        # Mark job as failed
        job.status = ImportStatus.FAILED
        job.completed_at = datetime.now()
        job.error_message = str(e)
        db.commit()

        raise

    finally:
        db.close()
```

---

## Monitoring Queries

### Dashboard Query
```sql
-- Get summary for dashboard
SELECT
    total_imports,
    completed_imports,
    failed_imports,
    success_rate_percent,
    imports_last_24h,
    avg_processing_time_seconds
FROM v_import_statistics;
```

### Job Performance Query
```sql
-- Find slow imports
SELECT
    id,
    file_name,
    data_type,
    total_rows,
    processing_duration_seconds,
    processing_speed_rows_per_second
FROM v_import_job_details
WHERE processing_duration_seconds > 60
ORDER BY processing_duration_seconds DESC;
```

### Error Analysis Query
```sql
-- Find most common errors
SELECT
    error_type,
    total_occurrences,
    affected_jobs,
    occurrences_last_7d
FROM v_import_error_frequency
ORDER BY total_occurrences DESC;
```

---

## Troubleshooting

### Issue: Import is slow
**Solutions**:
1. Use `use_copy=True` for CSV imports
2. Increase `batch_size` (try 1000-5000)
3. Use `disable_indexes()` for very large imports
4. Check database connection pool settings

### Issue: Running out of memory
**Solutions**:
1. Reduce `batch_size` (try 100-500)
2. Use CSV streaming instead of loading entire file
3. Process file in multiple smaller jobs
4. Increase server memory allocation

### Issue: Constraint violations
**Solutions**:
1. Check data before import with validation
2. Use `bulk_insert_with_validation()` to catch errors
3. Review error logs in `import_errors` table
4. Update templates with corrected mappings

### Issue: Foreign key errors
**Solutions**:
1. Ensure referenced records exist first
2. Import in correct order (farms → plots → events)
3. Use validation to check references
4. Provide clear error messages to users

---

## Need Help?

- **Models**: See `/backend/app/models/import_job.py`
- **Utils**: See `/backend/app/utils/bulk_insert.py`
- **Views**: See `/backend/app/models/views.py`
- **Migration**: See `/backend/alembic/versions/003_add_import_tables.py`
- **Full Docs**: See `/DATABASE_ARCHITECT_SPRINT2_SUMMARY.md`

---

**Quick Reference Complete** ✅
