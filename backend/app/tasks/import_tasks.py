"""
Import Tasks for asynchronous data processing.

Handles batch import of farm data with progress tracking and error handling.
"""
import pandas as pd
from celery import shared_task
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from pathlib import Path
import logging

from app.core.database import SessionLocal
from app.models.import_job import ImportJob, ImportStatus, DataType
from app.models.farm import Farm
from app.models.plot import Plot
from app.models.irrigation import IrrigationEvent
from app.models.nutrient import NutrientApplication
from app.services.csv_parser import CSVParser
from app.services.excel_parser import ExcelParser

logger = logging.getLogger(__name__)


BATCH_SIZE = 500  # Process 500 rows per batch


@shared_task(
    name="app.tasks.import_tasks.process_import",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def process_import(self, import_job_id: str):
    """
    Process a data import job asynchronously.

    Args:
        import_job_id: UUID of the import job to process

    Returns:
        Dictionary with processing results
    """
    db = SessionLocal()
    job_uuid = UUID(import_job_id)

    try:
        logger.info(f"Starting import processing for job {import_job_id}")

        # Load import job
        job = db.query(ImportJob).filter(ImportJob.id == job_uuid).first()
        if not job:
            raise ValueError(f"Import job {import_job_id} not found")

        # Update status
        job.status = ImportStatus.PROCESSING
        job.started_at = datetime.now()
        db.commit()

        # Parse file
        logger.info(f"Parsing file: {job.file_path}")
        if job.file_type == 'csv':
            df, metadata = CSVParser.parse_csv(job.file_path)
        elif job.file_type in ['xlsx', 'xls']:
            df, metadata = ExcelParser.parse_excel(job.file_path)
        else:
            raise ValueError(f"Unsupported file type: {job.file_type}")

        # Get column mapping
        column_mapping = job.column_mapping
        if not column_mapping:
            raise ValueError("Column mapping not found")

        # Reverse mapping (target -> source)
        target_to_source = {v: k for k, v in column_mapping.items()}

        # Process data based on data type
        total_rows = len(df)
        successful_rows = 0
        failed_rows = 0

        if job.data_type == DataType.FARMS_PLOTS:
            successful_rows, failed_rows = _process_farms_plots(
                db, df, target_to_source, job, self
            )
        elif job.data_type == DataType.IRRIGATION:
            successful_rows, failed_rows = _process_irrigation(
                db, df, target_to_source, job, self
            )
        elif job.data_type == DataType.NUTRIENTS:
            successful_rows, failed_rows = _process_nutrients(
                db, df, target_to_source, job, self
            )
        else:
            raise ValueError(f"Unsupported data type: {job.data_type}")

        # Update job status
        job.status = ImportStatus.COMPLETED
        job.completed_at = datetime.now()
        job.processed_rows = total_rows
        job.successful_rows = successful_rows
        job.failed_rows = failed_rows
        db.commit()

        # Move file to processed directory
        _move_file_to_processed(job.file_path)

        result = {
            'job_id': import_job_id,
            'status': 'completed',
            'total_rows': total_rows,
            'successful_rows': successful_rows,
            'failed_rows': failed_rows,
        }

        logger.info(f"Import job {import_job_id} completed successfully")
        return result

    except Exception as e:
        logger.error(f"Error processing import job {import_job_id}: {str(e)}", exc_info=True)

        # Update job status
        job = db.query(ImportJob).filter(ImportJob.id == job_uuid).first()
        if job:
            job.status = ImportStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()
            db.commit()

        # Move file to failed directory
        if job and job.file_path:
            _move_file_to_failed(job.file_path)

        # Retry on failure
        raise self.retry(exc=e)

    finally:
        db.close()


def _process_farms_plots(
    db: Session,
    df: pd.DataFrame,
    target_to_source: dict,
    job: ImportJob,
    task
) -> tuple:
    """Process farms and plots import"""
    successful_rows = 0
    failed_rows = 0
    processed_rows = 0

    # Group by farm to process efficiently
    farm_col = target_to_source.get('farm_name')
    if not farm_col:
        raise ValueError("farm_name column not mapped")

    for idx, row in df.iterrows():
        try:
            processed_rows += 1

            # Get or create farm
            farm_name = str(row[farm_col]).strip()
            farm = db.query(Farm).filter(Farm.name == farm_name).first()

            if not farm:
                # Create farm
                farm_data = {
                    'name': farm_name
                }

                # Optional fields
                if 'farm_address' in target_to_source:
                    addr_col = target_to_source['farm_address']
                    if addr_col in row and pd.notna(row[addr_col]):
                        farm_data['address'] = str(row[addr_col])

                if 'total_area_hectares' in target_to_source:
                    area_col = target_to_source['total_area_hectares']
                    if area_col in row and pd.notna(row[area_col]):
                        farm_data['total_area_hectares'] = float(row[area_col])

                farm = Farm(**farm_data)
                db.add(farm)
                db.flush()

            # Create plot if plot_name is provided
            plot_col = target_to_source.get('plot_name')
            if plot_col and plot_col in row and pd.notna(row[plot_col]):
                plot_name = str(row[plot_col]).strip()

                # Check if plot already exists
                existing_plot = db.query(Plot).filter(
                    Plot.farm_id == farm.id,
                    Plot.name == plot_name
                ).first()

                if not existing_plot:
                    plot_data = {
                        'farm_id': farm.id,
                        'name': plot_name
                    }

                    if 'plot_area_hectares' in target_to_source:
                        area_col = target_to_source['plot_area_hectares']
                        if area_col in row and pd.notna(row[area_col]):
                            plot_data['area_hectares'] = float(row[area_col])

                    plot = Plot(**plot_data)
                    db.add(plot)

            successful_rows += 1

            # Commit in batches
            if processed_rows % BATCH_SIZE == 0:
                db.commit()
                # Update progress
                job.processed_rows = processed_rows
                job.successful_rows = successful_rows
                db.commit()
                task.update_state(
                    state='PROGRESS',
                    meta={'processed': processed_rows, 'total': len(df)}
                )

        except Exception as e:
            logger.error(f"Error processing row {idx}: {str(e)}")
            failed_rows += 1
            db.rollback()

    # Final commit
    db.commit()

    return successful_rows, failed_rows


def _process_irrigation(
    db: Session,
    df: pd.DataFrame,
    target_to_source: dict,
    job: ImportJob,
    task
) -> tuple:
    """Process irrigation events import"""
    successful_rows = 0
    failed_rows = 0
    processed_rows = 0

    # Load farm/plot mapping
    farms = {f.name.lower(): f for f in db.query(Farm).all()}
    plots = {(p.farm.name.lower(), p.name.lower()): p for p in db.query(Plot).all()}

    for idx, row in df.iterrows():
        try:
            processed_rows += 1

            # Get farm and plot
            farm_col = target_to_source.get('farm_name')
            plot_col = target_to_source.get('plot_name')

            if not farm_col or not plot_col:
                raise ValueError("farm_name and plot_name required")

            farm_name = str(row[farm_col]).strip().lower()
            plot_name = str(row[plot_col]).strip().lower()

            plot = plots.get((farm_name, plot_name))
            if not plot:
                raise ValueError(f"Plot '{plot_name}' not found for farm '{farm_name}'")

            # Build irrigation event
            irrigation_data = {
                'plot_id': plot.id,
            }

            # Required fields
            if 'irrigation_date' in target_to_source:
                date_col = target_to_source['irrigation_date']
                irrigation_data['event_time'] = pd.to_datetime(row[date_col])

            if 'amount_liters' in target_to_source:
                amount_col = target_to_source['amount_liters']
                irrigation_data['amount_liters'] = float(row[amount_col])

            # Optional fields
            if 'duration_minutes' in target_to_source:
                dur_col = target_to_source['duration_minutes']
                if dur_col in row and pd.notna(row[dur_col]):
                    irrigation_data['duration_minutes'] = int(row[dur_col])

            if 'method' in target_to_source:
                method_col = target_to_source['method']
                if method_col in row and pd.notna(row[method_col]):
                    irrigation_data['method'] = str(row[method_col])

            event = IrrigationEvent(**irrigation_data)
            db.add(event)

            successful_rows += 1

            # Commit in batches
            if processed_rows % BATCH_SIZE == 0:
                db.commit()
                job.processed_rows = processed_rows
                job.successful_rows = successful_rows
                db.commit()
                task.update_state(
                    state='PROGRESS',
                    meta={'processed': processed_rows, 'total': len(df)}
                )

        except Exception as e:
            logger.error(f"Error processing row {idx}: {str(e)}")
            failed_rows += 1
            db.rollback()

    # Final commit
    db.commit()

    return successful_rows, failed_rows


def _process_nutrients(
    db: Session,
    df: pd.DataFrame,
    target_to_source: dict,
    job: ImportJob,
    task
) -> tuple:
    """Process nutrient applications import"""
    successful_rows = 0
    failed_rows = 0
    processed_rows = 0

    # Load farm/plot mapping
    plots = {(p.farm.name.lower(), p.name.lower()): p for p in db.query(Plot).all()}

    for idx, row in df.iterrows():
        try:
            processed_rows += 1

            # Get farm and plot
            farm_col = target_to_source.get('farm_name')
            plot_col = target_to_source.get('plot_name')

            if not farm_col or not plot_col:
                raise ValueError("farm_name and plot_name required")

            farm_name = str(row[farm_col]).strip().lower()
            plot_name = str(row[plot_col]).strip().lower()

            plot = plots.get((farm_name, plot_name))
            if not plot:
                raise ValueError(f"Plot '{plot_name}' not found for farm '{farm_name}'")

            # Build nutrient application
            nutrient_data = {
                'plot_id': plot.id,
            }

            # Required fields
            if 'application_date' in target_to_source:
                date_col = target_to_source['application_date']
                nutrient_data['event_time'] = pd.to_datetime(row[date_col])

            if 'nutrient_type' in target_to_source:
                type_col = target_to_source['nutrient_type']
                nutrient_data['nutrient_type'] = str(row[type_col])

            # Optional fields
            if 'amount_kg' in target_to_source:
                amount_col = target_to_source['amount_kg']
                if amount_col in row and pd.notna(row[amount_col]):
                    nutrient_data['amount_kg'] = float(row[amount_col])

            if 'method' in target_to_source:
                method_col = target_to_source['method']
                if method_col in row and pd.notna(row[method_col]):
                    nutrient_data['method'] = str(row[method_col])

            application = NutrientApplication(**nutrient_data)
            db.add(application)

            successful_rows += 1

            # Commit in batches
            if processed_rows % BATCH_SIZE == 0:
                db.commit()
                job.processed_rows = processed_rows
                job.successful_rows = successful_rows
                db.commit()
                task.update_state(
                    state='PROGRESS',
                    meta={'processed': processed_rows, 'total': len(df)}
                )

        except Exception as e:
            logger.error(f"Error processing row {idx}: {str(e)}")
            failed_rows += 1
            db.rollback()

    # Final commit
    db.commit()

    return successful_rows, failed_rows


def _move_file_to_processed(file_path: str):
    """Move successfully processed file to processed directory"""
    try:
        source = Path(file_path)
        if source.exists():
            processed_dir = source.parent / 'processed'
            processed_dir.mkdir(exist_ok=True)
            dest = processed_dir / source.name
            source.rename(dest)
            logger.info(f"Moved file to processed: {dest}")
    except Exception as e:
        logger.error(f"Error moving file to processed: {e}")


def _move_file_to_failed(file_path: str):
    """Move failed file to failed directory"""
    try:
        source = Path(file_path)
        if source.exists():
            failed_dir = source.parent / 'failed'
            failed_dir.mkdir(exist_ok=True)
            dest = failed_dir / source.name
            source.rename(dest)
            logger.info(f"Moved file to failed: {dest}")
    except Exception as e:
        logger.error(f"Error moving file to failed: {e}")
