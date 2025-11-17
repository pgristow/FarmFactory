"""
Financial Data API endpoints (Input Costs and Harvests)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
import logging

from app.core.deps import get_db, get_pagination_params
from app.schemas.financial import (
    InputCostCreate, InputCostUpdate, InputCostInDB,
    HarvestCreate, HarvestUpdate, HarvestInDB,
    ProfitLossSummary, ROISummary
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.models.financial import InputCost, Harvest
from app.models.crop import Planting
from app.models.plot import Plot
from app.utils.query_helpers import (
    apply_pagination, apply_date_range_filter, get_paginated_response, get_total_count
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== INPUT COST ENDPOINTS ====================

@router.post(
    "/costs",
    response_model=InputCostInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create input cost",
    tags=["Financial"]
)
async def create_input_cost(
    cost_data: InputCostCreate,
    db: Session = Depends(get_db)
):
    """
    Record a new input cost.

    - **plot_id**: ID of the plot (optional)
    - **planting_id**: ID of the planting (optional)
    - **cost_date**: Date when cost was incurred (required)
    - **category**: Cost category (seeds, fertilizer, water, labor, etc.)
    - **description**: Detailed description
    - **quantity**: Quantity purchased/used
    - **unit**: Unit of measurement
    - **unit_cost**: Cost per unit
    - **total_cost**: Total cost amount (required)
    - **currency**: Currency code (default: USD)
    """
    try:
        # Verify plot exists if provided
        if cost_data.plot_id:
            plot = db.query(Plot).filter(Plot.id == cost_data.plot_id).first()
            if not plot:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Plot with id '{cost_data.plot_id}' not found"
                )

        # Verify planting exists if provided
        if cost_data.planting_id:
            planting = db.query(Planting).filter(Planting.id == cost_data.planting_id).first()
            if not planting:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Planting with id '{cost_data.planting_id}' not found"
                )

        cost = InputCost(**cost_data.model_dump())
        db.add(cost)
        db.commit()
        db.refresh(cost)
        return InputCostInDB.model_validate(cost)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating input cost: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating input cost: {str(e)}"
        )


@router.get(
    "/costs",
    response_model=PaginatedResponse[InputCostInDB],
    summary="List input costs",
    tags=["Financial"]
)
async def list_input_costs(
    pagination: dict = Depends(get_pagination_params),
    plot_id: Optional[UUID] = Query(None, description="Filter by plot ID"),
    planting_id: Optional[UUID] = Query(None, description="Filter by planting ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[date] = Query(None, description="Start date (inclusive)"),
    end_date: Optional[date] = Query(None, description="End date (inclusive)"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of input costs with filtering.

    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **plot_id**: Filter by plot ID
    - **planting_id**: Filter by planting ID
    - **category**: Filter by cost category
    - **start_date**: Start date
    - **end_date**: End date
    """
    try:
        query = db.query(InputCost)

        # Apply filters
        if plot_id:
            query = query.filter(InputCost.plot_id == plot_id)
        if planting_id:
            query = query.filter(InputCost.planting_id == planting_id)
        if category:
            query = query.filter(InputCost.category.ilike(f"%{category}%"))

        # Apply date range filter
        query = apply_date_range_filter(query, InputCost.cost_date, start_date, end_date)

        # Order by cost date descending
        query = query.order_by(desc(InputCost.cost_date))

        # Get total count before pagination
        total = get_total_count(query)

        # Apply pagination
        query, skip, limit = apply_pagination(query, pagination["page"], pagination["page_size"])

        costs = query.all()

        return get_paginated_response(
            items=[InputCostInDB.model_validate(cost) for cost in costs],
            total=total,
            page=pagination["page"],
            page_size=pagination["page_size"]
        )
    except Exception as e:
        logger.error(f"Error listing input costs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing input costs: {str(e)}"
        )


@router.put(
    "/costs/{cost_id}",
    response_model=InputCostInDB,
    summary="Update input cost",
    tags=["Financial"]
)
async def update_input_cost(
    cost_id: UUID,
    cost_data: InputCostUpdate,
    db: Session = Depends(get_db)
):
    """Update an input cost."""
    try:
        cost = db.query(InputCost).filter(InputCost.id == cost_id).first()
        if not cost:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Input cost not found"
            )

        # Update only provided fields
        update_data = cost_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(cost, field, value)

        db.commit()
        db.refresh(cost)
        return InputCostInDB.model_validate(cost)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating input cost: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating input cost: {str(e)}"
        )


@router.delete(
    "/costs/{cost_id}",
    response_model=SuccessResponse,
    summary="Delete input cost",
    tags=["Financial"]
)
async def delete_input_cost(
    cost_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an input cost."""
    try:
        cost = db.query(InputCost).filter(InputCost.id == cost_id).first()
        if not cost:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Input cost not found"
            )

        db.delete(cost)
        db.commit()

        return SuccessResponse(
            success=True,
            message=f"Input cost deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting input cost: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting input cost: {str(e)}"
        )


# ==================== HARVEST ENDPOINTS ====================

@router.post(
    "/harvests",
    response_model=HarvestInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create harvest",
    tags=["Financial"]
)
async def create_harvest(
    harvest_data: HarvestCreate,
    db: Session = Depends(get_db)
):
    """
    Record a new harvest.

    - **planting_id**: ID of the planting (required)
    - **harvest_date**: Date of harvest (required)
    - **quantity_kg**: Harvested quantity in kg
    - **quality_grade**: Quality grade
    - **revenue_usd**: Revenue from harvest in USD
    - **market**: Market where sold
    - **notes**: Additional notes
    """
    try:
        # Verify planting exists
        planting = db.query(Planting).filter(Planting.id == harvest_data.planting_id).first()
        if not planting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planting with id '{harvest_data.planting_id}' not found"
            )

        harvest = Harvest(**harvest_data.model_dump())
        db.add(harvest)
        db.commit()
        db.refresh(harvest)
        return HarvestInDB.model_validate(harvest)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating harvest: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating harvest: {str(e)}"
        )


@router.get(
    "/harvests",
    response_model=PaginatedResponse[HarvestInDB],
    summary="List harvests",
    tags=["Financial"]
)
async def list_harvests(
    pagination: dict = Depends(get_pagination_params),
    planting_id: Optional[UUID] = Query(None, description="Filter by planting ID"),
    start_date: Optional[date] = Query(None, description="Start date (inclusive)"),
    end_date: Optional[date] = Query(None, description="End date (inclusive)"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of harvests with filtering.

    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **planting_id**: Filter by planting ID
    - **start_date**: Start date
    - **end_date**: End date
    """
    try:
        query = db.query(Harvest)

        # Apply filters
        if planting_id:
            query = query.filter(Harvest.planting_id == planting_id)

        # Apply date range filter
        query = apply_date_range_filter(query, Harvest.harvest_date, start_date, end_date)

        # Order by harvest date descending
        query = query.order_by(desc(Harvest.harvest_date))

        # Get total count before pagination
        total = get_total_count(query)

        # Apply pagination
        query, skip, limit = apply_pagination(query, pagination["page"], pagination["page_size"])

        harvests = query.all()

        return get_paginated_response(
            items=[HarvestInDB.model_validate(harvest) for harvest in harvests],
            total=total,
            page=pagination["page"],
            page_size=pagination["page_size"]
        )
    except Exception as e:
        logger.error(f"Error listing harvests: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing harvests: {str(e)}"
        )


@router.put(
    "/harvests/{harvest_id}",
    response_model=HarvestInDB,
    summary="Update harvest",
    tags=["Financial"]
)
async def update_harvest(
    harvest_id: UUID,
    harvest_data: HarvestUpdate,
    db: Session = Depends(get_db)
):
    """Update a harvest."""
    try:
        harvest = db.query(Harvest).filter(Harvest.id == harvest_id).first()
        if not harvest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Harvest not found"
            )

        # Update only provided fields
        update_data = harvest_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(harvest, field, value)

        db.commit()
        db.refresh(harvest)
        return HarvestInDB.model_validate(harvest)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating harvest: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating harvest: {str(e)}"
        )


@router.delete(
    "/harvests/{harvest_id}",
    response_model=SuccessResponse,
    summary="Delete harvest",
    tags=["Financial"]
)
async def delete_harvest(
    harvest_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a harvest."""
    try:
        harvest = db.query(Harvest).filter(Harvest.id == harvest_id).first()
        if not harvest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Harvest not found"
            )

        db.delete(harvest)
        db.commit()

        return SuccessResponse(
            success=True,
            message=f"Harvest deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting harvest: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting harvest: {str(e)}"
        )


# ==================== FINANCIAL SUMMARY ENDPOINTS ====================

@router.get(
    "/profit-loss",
    response_model=ProfitLossSummary,
    summary="Get profit & loss report",
    tags=["Financial"]
)
async def get_profit_loss(
    plot_id: Optional[UUID] = Query(None, description="Filter by plot ID"),
    start_date: Optional[date] = Query(None, description="Start date (inclusive)"),
    end_date: Optional[date] = Query(None, description="End date (inclusive)"),
    db: Session = Depends(get_db)
):
    """
    Get Profit & Loss report for a specified period and optionally a specific plot.

    Returns total revenue, total costs, profit, profit margin, and cost breakdown by category.
    """
    try:
        # Get total costs
        cost_query = db.query(func.sum(InputCost.total_cost))
        if plot_id:
            cost_query = cost_query.filter(InputCost.plot_id == plot_id)
        if start_date:
            cost_query = cost_query.filter(InputCost.cost_date >= start_date)
        if end_date:
            cost_query = cost_query.filter(InputCost.cost_date <= end_date)

        total_costs = cost_query.scalar() or Decimal("0.00")

        # Get cost breakdown by category
        cost_breakdown_query = db.query(
            InputCost.category,
            func.sum(InputCost.total_cost).label('total')
        )
        if plot_id:
            cost_breakdown_query = cost_breakdown_query.filter(InputCost.plot_id == plot_id)
        if start_date:
            cost_breakdown_query = cost_breakdown_query.filter(InputCost.cost_date >= start_date)
        if end_date:
            cost_breakdown_query = cost_breakdown_query.filter(InputCost.cost_date <= end_date)

        cost_breakdown_data = cost_breakdown_query.group_by(InputCost.category).all()
        cost_breakdown = {
            category: float(total) for category, total in cost_breakdown_data
        }

        # Get total revenue
        revenue_query = db.query(func.sum(Harvest.revenue_usd))
        if plot_id:
            revenue_query = revenue_query.join(Planting, Harvest.planting_id == Planting.id).filter(
                Planting.plot_id == plot_id
            )
        if start_date:
            revenue_query = revenue_query.filter(Harvest.harvest_date >= start_date)
        if end_date:
            revenue_query = revenue_query.filter(Harvest.harvest_date <= end_date)

        total_revenue = revenue_query.scalar() or Decimal("0.00")

        # Calculate profit and margin
        profit = total_revenue - total_costs
        profit_margin = None
        if total_revenue > 0:
            profit_margin = (profit / total_revenue) * 100

        # Get plot name if plot_id provided
        plot_name = None
        if plot_id:
            plot = db.query(Plot).filter(Plot.id == plot_id).first()
            plot_name = plot.name if plot else None

        return ProfitLossSummary(
            plot_id=plot_id,
            plot_name=plot_name,
            period_start=start_date or date.min,
            period_end=end_date or date.today(),
            total_revenue=total_revenue,
            total_costs=total_costs,
            profit=profit,
            profit_margin=profit_margin,
            cost_breakdown=cost_breakdown
        )
    except Exception as e:
        logger.error(f"Error getting profit/loss: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting profit/loss: {str(e)}"
        )


@router.get(
    "/roi",
    response_model=List[ROISummary],
    summary="Get ROI by plot or crop",
    tags=["Financial"]
)
async def get_roi(
    plot_id: Optional[UUID] = Query(None, description="Filter by plot ID"),
    crop_id: Optional[UUID] = Query(None, description="Filter by crop ID"),
    db: Session = Depends(get_db)
):
    """
    Get Return on Investment (ROI) analysis by plot or crop.

    Returns investment, return, ROI percentage for each plot/crop combination.
    """
    try:
        # This is a simplified ROI calculation
        # In production, this would be more sophisticated with time-weighted returns

        results = []

        if plot_id:
            # ROI for specific plot
            plot = db.query(Plot).filter(Plot.id == plot_id).first()
            if not plot:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Plot with id '{plot_id}' not found"
                )

            # Get total investment (costs) for this plot
            total_investment = db.query(func.sum(InputCost.total_cost)).filter(
                InputCost.plot_id == plot_id
            ).scalar() or Decimal("0.00")

            # Get total return (revenue) for this plot
            total_return = db.query(func.sum(Harvest.revenue_usd)).join(
                Planting, Harvest.planting_id == Planting.id
            ).filter(Planting.plot_id == plot_id).scalar() or Decimal("0.00")

            # Calculate ROI
            roi_percentage = None
            if total_investment > 0:
                roi_percentage = ((total_return - total_investment) / total_investment) * 100

            results.append(ROISummary(
                plot_id=plot_id,
                plot_name=plot.name,
                total_investment=total_investment,
                total_return=total_return,
                roi_percentage=roi_percentage
            ))
        else:
            # ROI for all plots
            plots = db.query(Plot).all()
            for plot in plots:
                total_investment = db.query(func.sum(InputCost.total_cost)).filter(
                    InputCost.plot_id == plot.id
                ).scalar() or Decimal("0.00")

                total_return = db.query(func.sum(Harvest.revenue_usd)).join(
                    Planting, Harvest.planting_id == Planting.id
                ).filter(Planting.plot_id == plot.id).scalar() or Decimal("0.00")

                roi_percentage = None
                if total_investment > 0:
                    roi_percentage = ((total_return - total_investment) / total_investment) * 100

                results.append(ROISummary(
                    plot_id=plot.id,
                    plot_name=plot.name,
                    total_investment=total_investment,
                    total_return=total_return,
                    roi_percentage=roi_percentage
                ))

        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ROI: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting ROI: {str(e)}"
        )
