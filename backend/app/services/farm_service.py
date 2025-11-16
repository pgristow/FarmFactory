"""
Business logic for Farm operations
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
import logging

from app.schemas.farm import FarmCreate, FarmUpdate, FarmListItem
from app.models.farm import Farm
from app.models.plot import Plot

logger = logging.getLogger(__name__)


class FarmService:
    """Service class for Farm business logic"""

    @staticmethod
    def create_farm(db: Session, farm_data: FarmCreate) -> Farm:
        """
        Create a new farm

        Args:
            db: Database session
            farm_data: Farm creation data

        Returns:
            Created Farm instance
        """
        farm = Farm(**farm_data.model_dump())
        db.add(farm)
        db.commit()
        db.refresh(farm)
        logger.info(f"Created farm: {farm.id} - {farm.name}")
        return farm

    @staticmethod
    def get_farm(db: Session, farm_id: UUID) -> Optional[Farm]:
        """
        Get a farm by ID

        Args:
            db: Database session
            farm_id: Farm UUID

        Returns:
            Farm instance or None if not found
        """
        return db.query(Farm).filter(Farm.id == farm_id).first()

    @staticmethod
    def get_farms(
        db: Session,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[FarmListItem], int]:
        """
        Get list of farms with pagination

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of farms, total count)
        """
        # Get total count
        total = db.query(func.count(Farm.id)).scalar()

        # Get farms with plot count
        farms = (
            db.query(
                Farm,
                func.count(Plot.id).label("plot_count")
            )
            .outerjoin(Plot, Farm.id == Plot.farm_id)
            .group_by(Farm.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        # Convert to FarmListItem
        farm_list = []
        for farm, plot_count in farms:
            farm_dict = {
                "id": farm.id,
                "name": farm.name,
                "address": farm.address,
                "latitude": farm.latitude,
                "longitude": farm.longitude,
                "total_area_hectares": farm.total_area_hectares,
                "timezone": farm.timezone,
                "created_at": farm.created_at,
                "plot_count": plot_count or 0
            }
            farm_list.append(FarmListItem(**farm_dict))

        return farm_list, total

    @staticmethod
    def update_farm(
        db: Session,
        farm_id: UUID,
        farm_data: FarmUpdate
    ) -> Optional[Farm]:
        """
        Update a farm

        Args:
            db: Database session
            farm_id: Farm UUID
            farm_data: Farm update data

        Returns:
            Updated Farm instance or None if not found
        """
        farm = db.query(Farm).filter(Farm.id == farm_id).first()
        if not farm:
            return None

        # Update only provided fields
        update_data = farm_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(farm, field, value)

        db.commit()
        db.refresh(farm)
        logger.info(f"Updated farm: {farm.id} - {farm.name}")
        return farm

    @staticmethod
    def delete_farm(db: Session, farm_id: UUID) -> bool:
        """
        Delete a farm

        Args:
            db: Database session
            farm_id: Farm UUID

        Returns:
            True if deleted, False if not found
        """
        farm = db.query(Farm).filter(Farm.id == farm_id).first()
        if not farm:
            return False

        db.delete(farm)
        db.commit()
        logger.info(f"Deleted farm: {farm_id}")
        return True

    @staticmethod
    def farm_exists(db: Session, farm_id: UUID) -> bool:
        """
        Check if a farm exists

        Args:
            db: Database session
            farm_id: Farm UUID

        Returns:
            True if farm exists, False otherwise
        """
        return db.query(Farm).filter(Farm.id == farm_id).count() > 0
