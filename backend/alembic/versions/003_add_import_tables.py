"""Add import tables for data import tracking

Revision ID: 003
Revises: 002
Create Date: 2025-11-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create import tracking tables for bulk data imports.

    Tables:
    - import_jobs: Track import job lifecycle and progress
    - import_errors: Track row-level errors during import
    - import_templates: Store reusable column mapping templates
    """

    # Create ENUM types
    op.execute("""
        CREATE TYPE import_status_enum AS ENUM (
            'pending', 'uploaded', 'parsing', 'mapping',
            'validating', 'processing', 'completed',
            'failed', 'failed_validation', 'cancelled'
        )
    """)

    op.execute("""
        CREATE TYPE data_type_enum AS ENUM (
            'farms_plots', 'irrigation', 'nutrients',
            'phenology', 'financial'
        )
    """)

    op.execute("""
        CREATE TYPE error_type_enum AS ENUM (
            'validation_error', 'data_type_error', 'range_error',
            'required_field_error', 'duplicate_error', 'reference_error',
            'parse_error', 'constraint_error'
        )
    """)

    # Create import_jobs table
    op.create_table(
        'import_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique identifier (UUID v4)'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True, comment='User who initiated the import'),
        sa.Column('file_name', sa.String(length=500), nullable=False, comment='Original filename of uploaded file'),
        sa.Column('file_size', sa.Integer(), nullable=True, comment='File size in bytes'),
        sa.Column('file_path', sa.String(length=1000), nullable=True, comment='Path to stored file'),
        sa.Column('file_type', sa.String(length=10), nullable=True, comment='File type (csv, xlsx, xls)'),
        sa.Column('data_type', postgresql.ENUM('farms_plots', 'irrigation', 'nutrients', 'phenology', 'financial', name='data_type_enum', create_type=False), nullable=False, comment='Type of data being imported'),
        sa.Column('status', postgresql.ENUM('pending', 'uploaded', 'parsing', 'mapping', 'validating', 'processing', 'completed', 'failed', 'failed_validation', 'cancelled', name='import_status_enum', create_type=False), nullable=False, server_default='pending', comment='Current status of the import'),
        sa.Column('total_rows', sa.Integer(), nullable=True, comment='Total number of rows in the file'),
        sa.Column('processed_rows', sa.Integer(), nullable=False, server_default='0', comment='Number of rows processed so far'),
        sa.Column('successful_rows', sa.Integer(), nullable=False, server_default='0', comment='Number of rows successfully imported'),
        sa.Column('failed_rows', sa.Integer(), nullable=False, server_default='0', comment='Number of rows that failed validation/import'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True, comment='When processing started'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='When processing completed'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Additional metadata (file encoding, delimiter, etc.)'),
        sa.Column('column_mapping', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Column name mapping from source to target'),
        sa.Column('error_summary', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Summary of errors by type'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='General error message if import failed'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.CheckConstraint('processed_rows >= 0', name='check_processed_rows_positive'),
        sa.CheckConstraint('successful_rows >= 0', name='check_successful_rows_positive'),
        sa.CheckConstraint('failed_rows >= 0', name='check_failed_rows_positive'),
        sa.CheckConstraint('processed_rows = successful_rows + failed_rows', name='check_row_counts_consistent'),
        sa.CheckConstraint('file_size >= 0 OR file_size IS NULL', name='check_file_size_positive'),
        sa.CheckConstraint('total_rows >= 0 OR total_rows IS NULL', name='check_total_rows_positive'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for import_jobs
    op.create_index('ix_import_jobs_user_id', 'import_jobs', ['user_id'])
    op.create_index('ix_import_jobs_status', 'import_jobs', ['status'])
    op.create_index('ix_import_jobs_data_type', 'import_jobs', ['data_type'])
    op.create_index('ix_import_jobs_created_at', 'import_jobs', ['created_at'])
    op.create_index('ix_import_jobs_status_created_at', 'import_jobs', ['status', 'created_at'])
    op.create_index('ix_import_jobs_data_type_status', 'import_jobs', ['data_type', 'status'])
    op.create_index('ix_import_jobs_user_id_created_at', 'import_jobs', ['user_id', 'created_at'])

    # Create import_errors table
    op.create_table(
        'import_errors',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique identifier (UUID v4)'),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Import job this error belongs to'),
        sa.Column('row_number', sa.Integer(), nullable=False, comment='Row number in the source file (1-indexed)'),
        sa.Column('column_name', sa.String(length=255), nullable=True, comment='Column where error occurred'),
        sa.Column('error_type', postgresql.ENUM('validation_error', 'data_type_error', 'range_error', 'required_field_error', 'duplicate_error', 'reference_error', 'parse_error', 'constraint_error', name='error_type_enum', create_type=False), nullable=False, comment='Type of error'),
        sa.Column('error_message', sa.Text(), nullable=False, comment='Human-readable error message'),
        sa.Column('invalid_value', sa.Text(), nullable=True, comment='The invalid value that caused the error'),
        sa.Column('suggested_value', sa.Text(), nullable=True, comment='Suggested correction for the error'),
        sa.Column('row_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Full row data for context'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when error was recorded'),
        sa.CheckConstraint('row_number > 0', name='check_row_number_positive'),
        sa.ForeignKeyConstraint(['job_id'], ['import_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for import_errors
    op.create_index('ix_import_errors_job_id', 'import_errors', ['job_id'])
    op.create_index('ix_import_errors_error_type', 'import_errors', ['error_type'])
    op.create_index('ix_import_errors_job_id_row_number', 'import_errors', ['job_id', 'row_number'])
    op.create_index('ix_import_errors_job_id_error_type', 'import_errors', ['job_id', 'error_type'])
    op.create_index('ix_import_errors_error_type_created_at', 'import_errors', ['error_type', 'created_at'])

    # Create import_templates table
    op.create_table(
        'import_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique identifier (UUID v4)'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Template name'),
        sa.Column('description', sa.Text(), nullable=True, comment='Template description'),
        sa.Column('data_type', postgresql.ENUM('farms_plots', 'irrigation', 'nutrients', 'phenology', 'financial', name='data_type_enum', create_type=False), nullable=False, comment='Type of data this template is for'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True, comment='User who created this template (null for system templates)'),
        sa.Column('column_mappings', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='Column name mapping from source to target columns'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false', comment='Whether this is a default template'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Whether this template is active/available'),
        sa.Column('use_count', sa.Integer(), nullable=False, server_default='0', comment='Number of times this template has been used'),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True, comment='Timestamp when template was last used'),
        sa.Column('validation_rules', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Custom validation rules for this template'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.CheckConstraint('use_count >= 0', name='check_use_count_positive'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for import_templates
    op.create_index('ix_import_templates_data_type', 'import_templates', ['data_type'])
    op.create_index('ix_import_templates_user_id', 'import_templates', ['user_id'])
    op.create_index('ix_import_templates_is_default', 'import_templates', ['is_default'])
    op.create_index('ix_import_templates_data_type_active', 'import_templates', ['data_type', 'is_active'])
    op.create_index('ix_import_templates_user_id_data_type', 'import_templates', ['user_id', 'data_type'])
    op.create_index('ix_import_templates_name_data_type', 'import_templates', ['name', 'data_type'])

    # Create monitoring views for import statistics
    # View 1: Overall import statistics
    op.execute("""
        CREATE OR REPLACE VIEW v_import_statistics AS
        SELECT
            COUNT(*) as total_imports,
            COUNT(*) FILTER (WHERE status = 'completed') as completed_imports,
            COUNT(*) FILTER (WHERE status = 'failed') as failed_imports,
            COUNT(*) FILTER (WHERE status = 'cancelled') as cancelled_imports,
            COUNT(*) FILTER (WHERE status IN ('pending', 'parsing', 'validating', 'processing')) as in_progress_imports,
            ROUND(
                COUNT(*) FILTER (WHERE status = 'completed')::numeric /
                NULLIF(COUNT(*) FILTER (WHERE status IN ('completed', 'failed'))::numeric, 0) * 100,
                2
            ) as success_rate_percent,
            SUM(total_rows) as total_rows_attempted,
            SUM(successful_rows) as total_rows_successful,
            SUM(failed_rows) as total_rows_failed,
            AVG(
                EXTRACT(EPOCH FROM (completed_at - started_at))
            ) FILTER (WHERE completed_at IS NOT NULL AND started_at IS NOT NULL) as avg_processing_time_seconds,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '24 hours') as imports_last_24h,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as imports_last_7d,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as imports_last_30d,
            MAX(created_at) as last_import_at
        FROM import_jobs
    """)

    # View 2: Import job details with error summary
    op.execute("""
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
            (
                SELECT COUNT(*)
                FROM import_errors ie
                WHERE ie.job_id = ij.id
            ) as error_count
        FROM import_jobs ij
    """)

    # View 3: Error frequency statistics
    op.execute("""
        CREATE OR REPLACE VIEW v_import_error_frequency AS
        SELECT
            error_type,
            COUNT(*) as total_occurrences,
            COUNT(DISTINCT job_id) as affected_jobs,
            COUNT(DISTINCT column_name) as affected_columns,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '24 hours') as occurrences_last_24h,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as occurrences_last_7d,
            MIN(created_at) as first_occurrence,
            MAX(created_at) as last_occurrence
        FROM import_errors
        GROUP BY error_type
        ORDER BY total_occurrences DESC
    """)

    # View 4: Data type statistics
    op.execute("""
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
        ORDER BY total_imports DESC
    """)


def downgrade() -> None:
    """
    Remove import tracking tables, views, and enum types.
    """
    # Drop views first (they depend on tables)
    op.execute('DROP VIEW IF EXISTS v_data_type_statistics')
    op.execute('DROP VIEW IF EXISTS v_import_error_frequency')
    op.execute('DROP VIEW IF EXISTS v_import_job_details')
    op.execute('DROP VIEW IF EXISTS v_import_statistics')

    # Drop tables (will also drop their indexes automatically)
    op.drop_table('import_templates')
    op.drop_table('import_errors')
    op.drop_table('import_jobs')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS error_type_enum')
    op.execute('DROP TYPE IF EXISTS data_type_enum')
    op.execute('DROP TYPE IF EXISTS import_status_enum')
