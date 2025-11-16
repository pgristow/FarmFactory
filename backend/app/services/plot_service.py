"""
Business logic for Plot operations
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
import logging

from app.schemas.plot import PlotCreate, PlotUpdate, PlotListItem
from app.models.plot import Plot
from app.models.farm import Farm

logger = logging.getLogger(__name__)


class PlotService:
    """Service class for Plot business logic"""

    @staticmethod
    def create_plot(db: Session, plot_data: PlotCreate) -> Plot:
        """
        Create a new plot

        Args:
            db: Database session
            plot_data: Plot creation data

        Returns:
            Created Plot instance

        Raises:
            ValueError: If farm does not exist
        """
        # Verify farm exists
        farm = db.query(Farm).filter(Farm.id == plot_data.farm_id).first()
        if not farm:
            raise ValueError(f"Farm with id {plot_data.farm_id} not found")

        plot = Plot(**plot_data.model_dump())
        db.add(plot)
        db.commit()
        db.refresh(plot)
        logger.info(f"Created plot: {plot.id} - {plot.name}")
        return plot

    @staticmethod
    def get_plot(db: Session, plot_id: UUID) -> Optional[Plot]:
        """
        Get a plot by ID

        Args:
            db: Database session
            plot_id: Plot UUID

        Returns:
            Plot instance or None if not found
        """
        return db.query(Plot).filter(Plot.id == plot_id).first()

    @staticmethod
    def get_plots(
        db: Session,
        farm_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[PlotListItem], int]:
        """
        Get list of plots with pagination

        Args:
            db: Database session
            farm_id: Optional farm ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of plots, total count)
        """
        # Base query
        query = db.query(Plot)

        # Filter by farm if provided
        if farm_id:
            query = query.filter(Plot.farm_id == farm_id)

        # Get total count
        total = query.count()

        # Get plots
        plots = query.offset(skip).limit(limit).all()

        # Convert to PlotListItem
        plot_list = []
        for plot in plots:
            # TODO: Get planting count when planting model is implemented
            plot_dict = {
                "id": plot.id,
                "farm_id": plot.farm_id,
                "name": plot.name,
                "plot_number": plot.plot_number,
                "area_hectares": plot.area_hectares,
                "elevation_meters": plot.elevation_meters,
                "slope_degrees": plot.slope_degrees,
                "created_at": plot.created_at,
                "planting_count": 0  # Placeholder
            }
            plot_list.append(PlotListItem(**plot_dict))

        return plot_list, total

    @staticmethod
    def update_plot(
        db: Session,
        plot_id: UUID,
        plot_data: PlotUpdate
    ) -> Optional[Plot]:
        """
        Update a plot

        Args:
            db: Database session
            plot_id: Plot UUID
            plot_data: Plot update data

        Returns:
            Updated Plot instance or None if not found
        """
        plot = db.query(Plot).filter(Plot.id == plot_id).first()
        if not plot:
            return None

        # Update only provided fields
        update_data = plot_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(plot, field, value)

        db.commit()
        db.refresh(plot)
        logger.info(f"Updated plot: {plot.id} - {plot.name}")
        return plot

    @staticmethod
    def delete_plot(db: Session, plot_id: UUID) -> bool:
        """
        Delete a plot

        Args:
            db: Database session
            plot_id: Plot UUID

        Returns:
            True if deleted, False if not found
        """
        plot = db.query(Plot).filter(Plot.id == plot_id).first()
        if not plot:
            return False

        db.delete(plot)
        db.commit()
        logger.info(f"Deleted plot: {plot_id}")
        return True

    @staticmethod
    def plot_exists(db: Session, plot_id: UUID) -> bool:
        """
        Check if a plot exists

        Args:
            db: Database session
            plot_id: Plot UUID

        Returns:
            True if plot exists, False otherwise
        """
        return db.query(Plot).filter(Plot.id == plot_id).count() > 0

    @staticmethod
    def get_plots_by_farm(db: Session, farm_id: UUID) -> List[Plot]:
        """
        Get all plots for a specific farm

        Args:
            db: Database session
            farm_id: Farm UUID

        Returns:
            List of Plot instances
        """
        return db.query(Plot).filter(Plot.farm_id == farm_id).all()
