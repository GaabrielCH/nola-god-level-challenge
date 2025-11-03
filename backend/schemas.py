"""Pydantic schemas for API"""
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List, Any, Dict


# Filters and Query Schemas
class DateRangeFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class QueryFilter(BaseModel):
    date_range: Optional[DateRangeFilter] = None
    store_ids: Optional[List[int]] = None
    channel_ids: Optional[List[int]] = None
    product_ids: Optional[List[int]] = None
    status: Optional[str] = None


class AggregationRequest(BaseModel):
    metric: str  # revenue, sales_count, avg_ticket, etc
    group_by: List[str]  # store, channel, product, date, hour, weekday
    filters: Optional[QueryFilter] = None
    time_bucket: Optional[str] = None  # day, week, month
    limit: Optional[int] = 100


class TimeSeriesRequest(BaseModel):
    metric: str
    filters: Optional[QueryFilter] = None
    time_bucket: str = "day"  # hour, day, week, month
    compare_previous: bool = False


class TopProductsRequest(BaseModel):
    filters: Optional[QueryFilter] = None
    limit: int = 10
    order_by: str = "revenue"  # revenue, quantity, frequency


class CustomQueryRequest(BaseModel):
    """Flexible query builder"""
    select: List[str]  # Fields to select
    from_table: str  # Main table
    joins: Optional[List[Dict[str, Any]]] = None
    filters: Optional[Dict[str, Any]] = None
    group_by: Optional[List[str]] = None
    order_by: Optional[List[Dict[str, str]]] = None
    limit: Optional[int] = None


# Response Schemas
class MetricCard(BaseModel):
    title: str
    value: Any
    change: Optional[float] = None
    change_label: Optional[str] = None
    format: str = "number"  # number, currency, percent, duration


class ChartData(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]


class TableData(BaseModel):
    columns: List[Dict[str, str]]
    rows: List[Dict[str, Any]]
    total_rows: int


class DashboardResponse(BaseModel):
    metrics: List[MetricCard]
    charts: Dict[str, ChartData]
    tables: Dict[str, TableData]


class AnalyticsResponse(BaseModel):
    data: List[Dict[str, Any]]
    total: int
    metadata: Optional[Dict[str, Any]] = None


# Entity Schemas
class StoreBasic(BaseModel):
    id: int
    name: str
    city: Optional[str]
    state: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True


class ChannelBasic(BaseModel):
    id: int
    name: str
    type: str
    
    class Config:
        from_attributes = True


class ProductBasic(BaseModel):
    id: int
    name: str
    category_id: Optional[int]
    
    class Config:
        from_attributes = True


class CategoryBasic(BaseModel):
    id: int
    name: str
    type: str
    
    class Config:
        from_attributes = True


# Insight Schemas
class Insight(BaseModel):
    type: str  # trend, anomaly, recommendation
    title: str
    description: str
    severity: str  # info, warning, critical
    data: Optional[Dict[str, Any]] = None
    action: Optional[str] = None


class InsightsResponse(BaseModel):
    insights: List[Insight]
    generated_at: datetime
