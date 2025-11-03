"""Query service for building dynamic queries"""
from sqlalchemy import func, cast, Date, extract, case
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import models
import pandas as pd


class QueryService:
    """Service for building and executing dynamic queries"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_revenue_metrics(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Get revenue metrics with comparison"""
        query = self.db.query(
            func.sum(models.Sale.total_amount).label('total_revenue'),
            func.count(models.Sale.id).label('total_sales'),
            func.avg(models.Sale.total_amount).label('avg_ticket'),
            func.sum(models.Sale.total_discount).label('total_discount')
        ).filter(models.Sale.sale_status_desc == 'COMPLETED')
        
        if filters:
            query = self._apply_filters(query, filters)
        
        result = query.first()
        
        # Get previous period for comparison
        prev_result = None
        if filters and filters.get('date_range'):
            prev_query = self._get_previous_period_query(filters)
            prev_result = prev_query.first()
        
        return {
            'revenue': float(result.total_revenue or 0),
            'sales_count': int(result.total_sales or 0),
            'avg_ticket': float(result.avg_ticket or 0),
            'total_discount': float(result.total_discount or 0),
            'previous': {
                'revenue': float(prev_result.total_revenue or 0) if prev_result else None,
                'sales_count': int(prev_result.total_sales or 0) if prev_result else None,
                'avg_ticket': float(prev_result.avg_ticket or 0) if prev_result else None,
            } if prev_result else None
        }
    
    def get_time_series(
        self,
        metric: str,
        time_bucket: str = 'day',
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Get time series data"""
        
        # Determine time bucket
        if time_bucket == 'hour':
            time_expr = func.date_trunc('hour', models.Sale.created_at)
        elif time_bucket == 'day':
            time_expr = cast(models.Sale.created_at, Date)
        elif time_bucket == 'week':
            time_expr = func.date_trunc('week', models.Sale.created_at)
        elif time_bucket == 'month':
            time_expr = func.date_trunc('month', models.Sale.created_at)
        else:
            time_expr = cast(models.Sale.created_at, Date)
        
        # Select metric
        metric_expr = self._get_metric_expression(metric)
        
        query = self.db.query(
            time_expr.label('period'),
            metric_expr.label('value')
        ).filter(models.Sale.sale_status_desc == 'COMPLETED')
        
        if filters:
            query = self._apply_filters(query, filters)
        
        query = query.group_by('period').order_by('period')
        
        results = query.all()
        
        return [
            {
                'period': r.period.isoformat() if hasattr(r.period, 'isoformat') else str(r.period),
                'value': float(r.value) if r.value else 0
            }
            for r in results
        ]
    
    def get_aggregation(
        self,
        metric: str,
        group_by: List[str],
        filters: Optional[Dict] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get aggregated data by dimensions"""
        
        metric_expr = self._get_metric_expression(metric)
        group_expressions = []
        group_labels = []
        
        # Build group by expressions
        for dimension in group_by:
            if dimension == 'store':
                group_expressions.append(models.Store.name)
                group_labels.append('store_name')
                query = self.db.query(
                    models.Store.name.label('store_name'),
                    metric_expr.label('value')
                ).join(models.Sale.store)
            elif dimension == 'channel':
                group_expressions.append(models.Channel.name)
                group_labels.append('channel_name')
                query = self.db.query(
                    models.Channel.name.label('channel_name'),
                    metric_expr.label('value')
                ).join(models.Sale.channel)
            elif dimension == 'product':
                group_expressions.append(models.Product.name)
                group_labels.append('product_name')
                query = self.db.query(
                    models.Product.name.label('product_name'),
                    metric_expr.label('value')
                ).join(models.ProductSale).join(models.ProductSale.product)
            elif dimension == 'weekday':
                weekday_expr = extract('dow', models.Sale.created_at)
                group_expressions.append(weekday_expr)
                group_labels.append('weekday')
                query = self.db.query(
                    weekday_expr.label('weekday'),
                    metric_expr.label('value')
                )
            elif dimension == 'hour':
                hour_expr = extract('hour', models.Sale.created_at)
                group_expressions.append(hour_expr)
                group_labels.append('hour')
                query = self.db.query(
                    hour_expr.label('hour'),
                    metric_expr.label('value')
                )
            else:
                continue
        
        if not group_expressions:
            return []
        
        query = query.filter(models.Sale.sale_status_desc == 'COMPLETED')
        
        if filters:
            query = self._apply_filters(query, filters)
        
        for expr in group_expressions:
            query = query.group_by(expr)
        
        query = query.order_by(metric_expr.desc()).limit(limit)
        
        results = query.all()
        
        return [
            {
                **{label: getattr(r, label) for label in group_labels},
                'value': float(r.value) if r.value else 0
            }
            for r in results
        ]
    
    def get_top_products(
        self,
        filters: Optional[Dict] = None,
        limit: int = 10,
        order_by: str = 'revenue'
    ) -> List[Dict[str, Any]]:
        """Get top products"""
        
        if order_by == 'revenue':
            metric = func.sum(models.ProductSale.total_price).label('value')
        elif order_by == 'quantity':
            metric = func.sum(models.ProductSale.quantity).label('value')
        else:
            metric = func.count(models.ProductSale.id).label('value')
        
        query = self.db.query(
            models.Product.name.label('product_name'),
            models.Category.name.label('category_name'),
            metric
        ).join(
            models.ProductSale, models.ProductSale.product_id == models.Product.id
        ).join(
            models.Category, models.Category.id == models.Product.category_id
        ).join(
            models.Sale, models.Sale.id == models.ProductSale.sale_id
        ).filter(
            models.Sale.sale_status_desc == 'COMPLETED'
        )
        
        if filters:
            query = self._apply_filters(query, filters)
        
        query = query.group_by(
            models.Product.name,
            models.Category.name
        ).order_by(metric.desc()).limit(limit)
        
        results = query.all()
        
        return [
            {
                'product_name': r.product_name,
                'category_name': r.category_name,
                'value': float(r.value) if r.value else 0
            }
            for r in results
        ]
    
    def get_hourly_distribution(
        self,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Get sales distribution by hour"""
        
        hour_expr = extract('hour', models.Sale.created_at)
        
        query = self.db.query(
            hour_expr.label('hour'),
            func.count(models.Sale.id).label('sales_count'),
            func.sum(models.Sale.total_amount).label('revenue')
        ).filter(
            models.Sale.sale_status_desc == 'COMPLETED'
        )
        
        if filters:
            query = self._apply_filters(query, filters)
        
        query = query.group_by('hour').order_by('hour')
        
        results = query.all()
        
        return [
            {
                'hour': int(r.hour),
                'sales_count': int(r.sales_count),
                'revenue': float(r.revenue or 0)
            }
            for r in results
        ]
    
    def get_channel_performance(
        self,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Get performance by channel"""
        
        query = self.db.query(
            models.Channel.name.label('channel_name'),
            func.count(models.Sale.id).label('sales_count'),
            func.sum(models.Sale.total_amount).label('revenue'),
            func.avg(models.Sale.total_amount).label('avg_ticket'),
            func.sum(models.Sale.total_discount).label('total_discount')
        ).join(
            models.Sale.channel
        ).filter(
            models.Sale.sale_status_desc == 'COMPLETED'
        )
        
        if filters:
            query = self._apply_filters(query, filters)
        
        query = query.group_by(models.Channel.name)
        
        results = query.all()
        
        return [
            {
                'channel_name': r.channel_name,
                'sales_count': int(r.sales_count),
                'revenue': float(r.revenue or 0),
                'avg_ticket': float(r.avg_ticket or 0),
                'total_discount': float(r.total_discount or 0)
            }
            for r in results
        ]
    
    def get_store_comparison(
        self,
        filters: Optional[Dict] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Compare store performance"""
        
        query = self.db.query(
            models.Store.name.label('store_name'),
            models.Store.city.label('city'),
            func.count(models.Sale.id).label('sales_count'),
            func.sum(models.Sale.total_amount).label('revenue'),
            func.avg(models.Sale.total_amount).label('avg_ticket')
        ).join(
            models.Sale.store
        ).filter(
            models.Sale.sale_status_desc == 'COMPLETED'
        )
        
        if filters:
            query = self._apply_filters(query, filters)
        
        query = query.group_by(
            models.Store.name,
            models.Store.city
        ).order_by(
            func.sum(models.Sale.total_amount).desc()
        ).limit(limit)
        
        results = query.all()
        
        return [
            {
                'store_name': r.store_name,
                'city': r.city,
                'sales_count': int(r.sales_count),
                'revenue': float(r.revenue or 0),
                'avg_ticket': float(r.avg_ticket or 0)
            }
            for r in results
        ]
    
    def _get_metric_expression(self, metric: str):
        """Get SQLAlchemy expression for metric"""
        if metric == 'revenue':
            return func.sum(models.Sale.total_amount)
        elif metric == 'sales_count':
            return func.count(models.Sale.id)
        elif metric == 'avg_ticket':
            return func.avg(models.Sale.total_amount)
        elif metric == 'total_discount':
            return func.sum(models.Sale.total_discount)
        elif metric == 'avg_production_time':
            return func.avg(models.Sale.production_seconds) / 60  # in minutes
        elif metric == 'avg_delivery_time':
            return func.avg(models.Sale.delivery_seconds) / 60  # in minutes
        else:
            return func.count(models.Sale.id)
    
    def _apply_filters(self, query, filters: Dict):
        """Apply filters to query"""
        if filters.get('date_range'):
            date_range = filters['date_range']
            if date_range.get('start_date'):
                start_date = date_range['start_date']
                # Convert string to datetime if needed
                if isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(models.Sale.created_at >= start_date)
            if date_range.get('end_date'):
                end_date = date_range['end_date']
                # Convert string to datetime if needed
                if isinstance(end_date, str):
                    end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(models.Sale.created_at <= end_date)
        
        if filters.get('store_ids'):
            query = query.filter(models.Sale.store_id.in_(filters['store_ids']))
        
        if filters.get('channel_ids'):
            query = query.filter(models.Sale.channel_id.in_(filters['channel_ids']))
        
        if filters.get('status'):
            query = query.filter(models.Sale.sale_status_desc == filters['status'])
        
        return query
    
    def _get_previous_period_query(self, filters: Dict):
        """Get query for previous period comparison"""
        date_range = filters.get('date_range', {})
        start = date_range.get('start_date')
        end = date_range.get('end_date')
        
        if not start or not end:
            return None
        
        # Convert strings to datetime if needed
        if isinstance(start, str):
            start = datetime.fromisoformat(start.replace('Z', '+00:00'))
        if isinstance(end, str):
            end = datetime.fromisoformat(end.replace('Z', '+00:00'))
        
        # Calculate period length
        period_length = (end - start).days
        prev_start = start - timedelta(days=period_length)
        prev_end = start
        
        prev_filters = {**filters}
        prev_filters['date_range'] = {
            'start_date': prev_start,
            'end_date': prev_end
        }
        
        query = self.db.query(
            func.sum(models.Sale.total_amount).label('total_revenue'),
            func.count(models.Sale.id).label('total_sales'),
            func.avg(models.Sale.total_amount).label('avg_ticket')
        ).filter(models.Sale.sale_status_desc == 'COMPLETED')
        
        return self._apply_filters(query, prev_filters)
