"""Main FastAPI application"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from config import settings
from database import get_db
import models
import schemas
from query_service import QueryService
from cache_service import cache_service

app = FastAPI(
    title="Nola Restaurant Analytics API",
    description="Analytics platform for restaurant data",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Health check"""
    return {"status": "ok", "service": "Nola Restaurant Analytics API"}


@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    """Health check with database connection"""
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}


# Metadata endpoints
@app.get("/api/stores", response_model=List[schemas.StoreBasic])
def get_stores(db: Session = Depends(get_db)):
    """Get all stores"""
    cache_key = "stores:all"
    cached = cache_service.get(cache_key)
    if cached:
        return cached
    
    stores = db.query(models.Store).filter(models.Store.is_active == True).all()
    result = [schemas.StoreBasic.from_orm(s) for s in stores]
    cache_service.set(cache_key, [r.dict() for r in result], ttl=3600)
    return result


@app.get("/api/channels", response_model=List[schemas.ChannelBasic])
def get_channels(db: Session = Depends(get_db)):
    """Get all channels"""
    cache_key = "channels:all"
    cached = cache_service.get(cache_key)
    if cached:
        return cached
    
    channels = db.query(models.Channel).all()
    result = [schemas.ChannelBasic.from_orm(c) for c in channels]
    cache_service.set(cache_key, [r.dict() for r in result], ttl=3600)
    return result


@app.get("/api/products", response_model=List[schemas.ProductBasic])
def get_products(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get products"""
    cache_key = f"products:limit:{limit}"
    cached = cache_service.get(cache_key)
    if cached:
        return cached
    
    products = db.query(models.Product).limit(limit).all()
    result = [schemas.ProductBasic.from_orm(p) for p in products]
    cache_service.set(cache_key, [r.dict() for r in result], ttl=3600)
    return result


@app.get("/api/categories", response_model=List[schemas.CategoryBasic])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    cache_key = "categories:all"
    cached = cache_service.get(cache_key)
    if cached:
        return cached
    
    categories = db.query(models.Category).filter(models.Category.type == 'P').all()
    result = [schemas.CategoryBasic.from_orm(c) for c in categories]
    cache_service.set(cache_key, [r.dict() for r in result], ttl=3600)
    return result


# Dashboard endpoints
@app.post("/api/dashboard/overview")
def get_dashboard_overview(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    store_ids: Optional[List[int]] = Query(None),
    db: Session = Depends(get_db)
):
    """Get dashboard overview with key metrics"""
    
    # Default to last 30 days
    if not end_date:
        end_date_dt = datetime.now()
    else:
        end_date_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    
    if not start_date:
        start_date_dt = end_date_dt - timedelta(days=30)
    else:
        start_date_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    
    filters = {
        'date_range': {
            'start_date': start_date_dt,
            'end_date': end_date_dt
        }
    }
    if store_ids:
        filters['store_ids'] = store_ids
    
    # Cache key
    cache_key = cache_service.generate_cache_key("dashboard:overview", filters)
    cached = cache_service.get(cache_key)
    if cached:
        return cached
    
    query_service = QueryService(db)
    
    # Get metrics
    metrics = query_service.get_revenue_metrics(filters)
    
    # Calculate changes
    metric_cards = []
    if metrics.get('previous'):
        revenue_change = ((metrics['revenue'] - metrics['previous']['revenue']) / 
                         metrics['previous']['revenue'] * 100) if metrics['previous']['revenue'] > 0 else 0
        sales_change = ((metrics['sales_count'] - metrics['previous']['sales_count']) / 
                       metrics['previous']['sales_count'] * 100) if metrics['previous']['sales_count'] > 0 else 0
        ticket_change = ((metrics['avg_ticket'] - metrics['previous']['avg_ticket']) / 
                        metrics['previous']['avg_ticket'] * 100) if metrics['previous']['avg_ticket'] > 0 else 0
    else:
        revenue_change = sales_change = ticket_change = None
    
    metric_cards = [
        {
            'title': 'Faturamento Total',
            'value': metrics['revenue'],
            'change': revenue_change,
            'format': 'currency'
        },
        {
            'title': 'Total de Vendas',
            'value': metrics['sales_count'],
            'change': sales_change,
            'format': 'number'
        },
        {
            'title': 'Ticket Médio',
            'value': metrics['avg_ticket'],
            'change': ticket_change,
            'format': 'currency'
        },
        {
            'title': 'Total de Descontos',
            'value': metrics['total_discount'],
            'format': 'currency'
        }
    ]
    
    # Get time series
    time_series = query_service.get_time_series('revenue', 'day', filters)
    
    # Get channel performance
    channel_perf = query_service.get_channel_performance(filters)
    
    # Get top products
    top_products = query_service.get_top_products(filters, limit=10)
    
    # Get hourly distribution
    hourly = query_service.get_hourly_distribution(filters)
    
    result = {
        'metrics': metric_cards,
        'time_series': time_series,
        'channel_performance': channel_perf,
        'top_products': top_products,
        'hourly_distribution': hourly
    }
    
    cache_service.set(cache_key, result, ttl=300)
    return result


@app.post("/api/analytics/time-series")
def get_time_series(
    request: schemas.TimeSeriesRequest,
    db: Session = Depends(get_db)
):
    """Get time series data"""
    filters = request.filters.dict() if request.filters else {}
    
    cache_key = cache_service.generate_cache_key(
        f"timeseries:{request.metric}:{request.time_bucket}",
        filters
    )
    cached = cache_service.get(cache_key)
    if cached:
        return cached
    
    query_service = QueryService(db)
    data = query_service.get_time_series(request.metric, request.time_bucket, filters)
    
    cache_service.set(cache_key, data, ttl=300)
    return data


@app.post("/api/analytics/aggregation")
def get_aggregation(
    request: schemas.AggregationRequest,
    db: Session = Depends(get_db)
):
    """Get aggregated data"""
    filters = request.filters.dict() if request.filters else {}
    
    cache_key = cache_service.generate_cache_key(
        f"aggregation:{request.metric}:{'_'.join(request.group_by)}",
        filters
    )
    cached = cache_service.get(cache_key)
    if cached:
        return cached
    
    query_service = QueryService(db)
    data = query_service.get_aggregation(
        request.metric,
        request.group_by,
        filters,
        request.limit
    )
    
    cache_service.set(cache_key, data, ttl=300)
    return data


@app.post("/api/analytics/top-products")
def get_top_products(
    request: schemas.TopProductsRequest,
    db: Session = Depends(get_db)
):
    """Get top products"""
    filters = request.filters.dict() if request.filters else {}
    
    cache_key = cache_service.generate_cache_key(
        f"top_products:{request.order_by}:{request.limit}",
        filters
    )
    cached = cache_service.get(cache_key)
    if cached:
        return cached
    
    query_service = QueryService(db)
    data = query_service.get_top_products(filters, request.limit, request.order_by)
    
    cache_service.set(cache_key, data, ttl=300)
    return data


@app.post("/api/analytics/store-comparison")
def get_store_comparison(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Compare store performance"""
    
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    filters = {
        'date_range': {
            'start_date': start_date,
            'end_date': end_date
        }
    }
    
    cache_key = cache_service.generate_cache_key(f"store_comparison:{limit}", filters)
    cached = cache_service.get(cache_key)
    if cached:
        return cached
    
    query_service = QueryService(db)
    data = query_service.get_store_comparison(filters, limit)
    
    cache_service.set(cache_key, data, ttl=300)
    return data


@app.get("/api/analytics/insights")
def get_insights(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get automated insights"""
    
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    filters = {
        'date_range': {
            'start_date': start_date,
            'end_date': end_date
        }
    }
    
    cache_key = cache_service.generate_cache_key("insights", filters)
    cached = cache_service.get(cache_key)
    if cached:
        return cached
    
    query_service = QueryService(db)
    insights = []
    
    # Get channel performance
    channels = query_service.get_channel_performance(filters)
    if channels:
        best_channel = max(channels, key=lambda x: x['revenue'])
        insights.append({
            'type': 'trend',
            'title': f'Canal de melhor performance: {best_channel["channel_name"]}',
            'description': f'Gerou R$ {best_channel["revenue"]:.2f} em receita com {best_channel["sales_count"]} vendas.',
            'severity': 'info',
            'data': best_channel
        })
    
    # Get hourly patterns
    hourly = query_service.get_hourly_distribution(filters)
    if hourly:
        peak_hour = max(hourly, key=lambda x: x['sales_count'])
        insights.append({
            'type': 'trend',
            'title': f'Horário de pico: {peak_hour["hour"]}h',
            'description': f'{peak_hour["sales_count"]} vendas realizadas neste horário, gerando R$ {peak_hour["revenue"]:.2f}.',
            'severity': 'info',
            'data': peak_hour
        })
    
    # Get metrics for anomaly detection
    metrics = query_service.get_revenue_metrics(filters)
    if metrics.get('previous'):
        revenue_change = ((metrics['revenue'] - metrics['previous']['revenue']) / 
                         metrics['previous']['revenue'] * 100) if metrics['previous']['revenue'] > 0 else 0
        
        if revenue_change < -15:
            insights.append({
                'type': 'anomaly',
                'title': 'Queda significativa na receita',
                'description': f'Receita caiu {abs(revenue_change):.1f}% em relação ao período anterior.',
                'severity': 'critical',
                'action': 'Revisar operações e identificar causas da queda.'
            })
        elif revenue_change > 20:
            insights.append({
                'type': 'trend',
                'title': 'Crescimento expressivo na receita',
                'description': f'Receita cresceu {revenue_change:.1f}% em relação ao período anterior.',
                'severity': 'info',
                'action': 'Identificar fatores de sucesso para replicar.'
            })
    
    result = {
        'insights': insights,
        'generated_at': datetime.now()
    }
    
    cache_service.set(cache_key, result, ttl=600)
    return result


@app.delete("/api/cache/clear")
def clear_cache(pattern: str = "*"):
    """Clear cache (for development)"""
    try:
        count = cache_service.clear_pattern(pattern)
        return {"status": "ok", "cleared": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
