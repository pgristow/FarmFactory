"""
Database views for import monitoring and statistics.

Views provide pre-computed aggregations and analytics for import operations.
These views can be used for dashboards, reporting, and monitoring.
"""
from sqlalchemy import text
from sqlalchemy.orm import Session


# SQL for import statistics view
IMPORT_STATISTICS_VIEW_SQL = """
CREATE OR REPLACE VIEW v_import_statistics AS
SELECT
    -- Overall statistics
    COUNT(*) as total_imports,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_imports,
    COUNT(*) FILTER (WHERE status = 'failed') as failed_imports,
    COUNT(*) FILTER (WHERE status = 'cancelled') as cancelled_imports,
    COUNT(*) FILTER (WHERE status IN ('pending', 'parsing', 'validating', 'processing')) as in_progress_imports,

    -- Success rate
    ROUND(
        COUNT(*) FILTER (WHERE status = 'completed')::numeric /
        NULLIF(COUNT(*) FILTER (WHERE status IN ('completed', 'failed'))::numeric, 0) * 100,
        2
    ) as success_rate_percent,

    -- Row statistics
    SUM(total_rows) as total_rows_attempted,
    SUM(successful_rows) as total_rows_successful,
    SUM(failed_rows) as total_rows_failed,

    -- Average processing metrics
    AVG(
        EXTRACT(EPOCH FROM (completed_at - started_at))
    ) FILTER (WHERE completed_at IS NOT NULL AND started_at IS NOT NULL) as avg_processing_time_seconds,

    AVG(
        successful_rows::numeric /
        NULLIF(EXTRACT(EPOCH FROM (completed_at - started_at)), 0)
    ) FILTER (WHERE completed_at IS NOT NULL AND started_at IS NOT NULL AND successful_rows > 0)
    as avg_rows_per_second,

    -- File size statistics
    AVG(file_size) as avg_file_size_bytes,
    MAX(file_size) as max_file_size_bytes,

    -- By data type
    json_object_agg(
        data_type,
        json_build_object(
            'total', COUNT(*) FILTER (WHERE data_type = data_type),
            'completed', COUNT(*) FILTER (WHERE data_type = data_type AND status = 'completed'),
            'failed', COUNT(*) FILTER (WHERE data_type = data_type AND status = 'failed')
        )
    ) FILTER (WHERE data_type IS NOT NULL) as stats_by_data_type,

    -- Recent activity (last 24 hours)
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '24 hours') as imports_last_24h,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as imports_last_7d,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as imports_last_30d,

    -- Last update
    MAX(created_at) as last_import_at

FROM import_jobs;
"""


# SQL for import job details view with error summary
IMPORT_JOB_DETAILS_VIEW_SQL = """
CREATE OR REPLACE VIEW v_import_job_details AS
SELECT
    ij.id,
    ij.user_id,
    ij.file_name,
    ij.file_size,
    ij.data_type,
    ij.status,
    ij.total_rows,
    ij.processed_rows,
    ij.successful_rows,
    ij.failed_rows,
    ij.started_at,
    ij.completed_at,
    ij.created_at,

    -- Calculated fields
    CASE
        WHEN ij.total_rows > 0 THEN
            ROUND((ij.processed_rows::numeric / ij.total_rows::numeric) * 100, 2)
        ELSE 0
    END as progress_percent,

    CASE
        WHEN ij.processed_rows > 0 THEN
            ROUND((ij.successful_rows::numeric / ij.processed_rows::numeric) * 100, 2)
        ELSE 0
    END as success_rate_percent,

    CASE
        WHEN ij.completed_at IS NOT NULL AND ij.started_at IS NOT NULL THEN
            EXTRACT(EPOCH FROM (ij.completed_at - ij.started_at))
        ELSE NULL
    END as processing_duration_seconds,

    CASE
        WHEN ij.completed_at IS NOT NULL AND ij.started_at IS NOT NULL AND ij.successful_rows > 0 THEN
            ROUND(
                ij.successful_rows::numeric /
                NULLIF(EXTRACT(EPOCH FROM (ij.completed_at - ij.started_at)), 0),
                2
            )
        ELSE NULL
    END as processing_speed_rows_per_second,

    -- Error summary from import_errors table
    (
        SELECT COUNT(*)
        FROM import_errors ie
        WHERE ie.job_id = ij.id
    ) as error_count,

    (
        SELECT json_object_agg(error_type, count)
        FROM (
            SELECT error_type, COUNT(*) as count
            FROM import_errors
            WHERE job_id = ij.id
            GROUP BY error_type
        ) error_counts
    ) as errors_by_type,

    (
        SELECT json_agg(
            json_build_object(
                'row_number', row_number,
                'column_name', column_name,
                'error_type', error_type,
                'error_message', error_message
            )
        )
        FROM (
            SELECT row_number, column_name, error_type, error_message
            FROM import_errors
            WHERE job_id = ij.id
            ORDER BY created_at DESC
            LIMIT 10
        ) recent_errors
    ) as recent_errors

FROM import_jobs ij;
"""


# SQL for error frequency view
ERROR_FREQUENCY_VIEW_SQL = """
CREATE OR REPLACE VIEW v_import_error_frequency AS
SELECT
    error_type,
    COUNT(*) as total_occurrences,
    COUNT(DISTINCT job_id) as affected_jobs,
    COUNT(DISTINCT column_name) as affected_columns,

    -- Most common error messages
    json_agg(
        DISTINCT json_build_object(
            'message', error_message,
            'count', (
                SELECT COUNT(*)
                FROM import_errors ie2
                WHERE ie2.error_type = ie.error_type
                AND ie2.error_message = ie.error_message
            )
        )
        ORDER BY (
            SELECT COUNT(*)
            FROM import_errors ie2
            WHERE ie2.error_type = ie.error_type
            AND ie2.error_message = ie.error_message
        ) DESC
    ) FILTER (WHERE error_message IS NOT NULL) as common_messages,

    -- Most affected columns
    json_agg(
        DISTINCT json_build_object(
            'column', column_name,
            'count', (
                SELECT COUNT(*)
                FROM import_errors ie2
                WHERE ie2.error_type = ie.error_type
                AND ie2.column_name = ie.column_name
            )
        )
        ORDER BY (
            SELECT COUNT(*)
            FROM import_errors ie2
            WHERE ie2.error_type = ie.error_type
            AND ie2.column_name = ie.column_name
        ) DESC
    ) FILTER (WHERE column_name IS NOT NULL) as affected_columns_detail,

    -- Recent occurrences
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '24 hours') as occurrences_last_24h,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as occurrences_last_7d,

    MIN(created_at) as first_occurrence,
    MAX(created_at) as last_occurrence

FROM import_errors ie
GROUP BY error_type
ORDER BY total_occurrences DESC;
"""


# SQL for data type import statistics
DATA_TYPE_STATISTICS_VIEW_SQL = """
CREATE OR REPLACE VIEW v_data_type_statistics AS
SELECT
    data_type,
    COUNT(*) as total_imports,
    COUNT(*) FILTER (WHERE status = 'completed') as successful_imports,
    COUNT(*) FILTER (WHERE status = 'failed') as failed_imports,

    ROUND(
        COUNT(*) FILTER (WHERE status = 'completed')::numeric /
        NULLIF(COUNT(*)::numeric, 0) * 100,
        2
    ) as success_rate_percent,

    SUM(total_rows) as total_rows_imported,
    AVG(total_rows) as avg_rows_per_import,

    AVG(
        EXTRACT(EPOCH FROM (completed_at - started_at))
    ) FILTER (WHERE completed_at IS NOT NULL AND started_at IS NOT NULL)
    as avg_processing_time_seconds,

    MAX(file_size) as max_file_size_bytes,
    AVG(file_size) as avg_file_size_bytes,

    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as imports_last_7d,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as imports_last_30d,

    MAX(created_at) as last_import_at

FROM import_jobs
GROUP BY data_type
ORDER BY total_imports DESC;
"""


def create_import_views(session: Session):
    """
    Create all import-related database views.

    This function should be called during database initialization or
    can be included in Alembic migrations.

    Args:
        session: SQLAlchemy session

    Example:
        from app.models.views import create_import_views
        from app.core.database import SessionLocal

        db = SessionLocal()
        create_import_views(db)
        db.close()
    """
    try:
        session.execute(text(IMPORT_STATISTICS_VIEW_SQL))
        session.execute(text(IMPORT_JOB_DETAILS_VIEW_SQL))
        session.execute(text(ERROR_FREQUENCY_VIEW_SQL))
        session.execute(text(DATA_TYPE_STATISTICS_VIEW_SQL))
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e


def drop_import_views(session: Session):
    """
    Drop all import-related database views.

    This function is useful for cleanup or when included in
    Alembic migration downgrade operations.

    Args:
        session: SQLAlchemy session
    """
    try:
        session.execute(text("DROP VIEW IF EXISTS v_data_type_statistics"))
        session.execute(text("DROP VIEW IF EXISTS v_import_error_frequency"))
        session.execute(text("DROP VIEW IF EXISTS v_import_job_details"))
        session.execute(text("DROP VIEW IF EXISTS v_import_statistics"))
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e


# View query helpers
def get_import_statistics(session: Session) -> dict:
    """
    Get overall import statistics.

    Returns:
        Dictionary with import statistics
    """
    result = session.execute(text("SELECT * FROM v_import_statistics")).fetchone()
    if result:
        return dict(result._mapping)
    return {}


def get_import_job_details(session: Session, job_id: str) -> dict:
    """
    Get detailed information about a specific import job.

    Args:
        session: SQLAlchemy session
        job_id: Import job UUID

    Returns:
        Dictionary with job details including error summary
    """
    result = session.execute(
        text("SELECT * FROM v_import_job_details WHERE id = :job_id"),
        {"job_id": job_id}
    ).fetchone()

    if result:
        return dict(result._mapping)
    return {}


def get_error_frequency(session: Session) -> list:
    """
    Get error frequency statistics.

    Returns:
        List of dictionaries with error type frequencies
    """
    results = session.execute(text("SELECT * FROM v_import_error_frequency")).fetchall()
    return [dict(row._mapping) for row in results]


def get_data_type_statistics(session: Session, data_type: str = None) -> list:
    """
    Get statistics by data type.

    Args:
        session: SQLAlchemy session
        data_type: Optional filter by specific data type

    Returns:
        List of dictionaries with statistics per data type
    """
    if data_type:
        results = session.execute(
            text("SELECT * FROM v_data_type_statistics WHERE data_type = :data_type"),
            {"data_type": data_type}
        ).fetchall()
    else:
        results = session.execute(text("SELECT * FROM v_data_type_statistics")).fetchall()

    return [dict(row._mapping) for row in results]
