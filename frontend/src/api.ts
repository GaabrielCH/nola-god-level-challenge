import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Store {
  id: number;
  name: string;
  city: string;
  state: string;
  is_active: boolean;
}

export interface Channel {
  id: number;
  name: string;
  type: string;
}

export interface Product {
  id: number;
  name: string;
  category_id: number;
}

export interface MetricCard {
  title: string;
  value: number;
  change?: number;
  format: string;
}

export interface TimeSeriesData {
  period: string;
  value: number;
}

export interface ChannelPerformance {
  channel_name: string;
  sales_count: number;
  revenue: number;
  avg_ticket: number;
  total_discount: number;
}

export interface TopProduct {
  product_name: string;
  category_name: string;
  value: number;
}

export interface HourlyDistribution {
  hour: number;
  sales_count: number;
  revenue: number;
}

export interface DashboardData {
  metrics: MetricCard[];
  time_series: TimeSeriesData[];
  channel_performance: ChannelPerformance[];
  top_products: TopProduct[];
  hourly_distribution: HourlyDistribution[];
}

export interface Insight {
  type: string;
  title: string;
  description: string;
  severity: string;
  data?: any;
  action?: string;
}

export interface DateRange {
  start_date?: string;
  end_date?: string;
}

// API Functions
export const getStores = async (): Promise<Store[]> => {
  const response = await api.get('/api/stores');
  return response.data;
};

export const getChannels = async (): Promise<Channel[]> => {
  const response = await api.get('/api/channels');
  return response.data;
};

export const getProducts = async (limit = 100): Promise<Product[]> => {
  const response = await api.get(`/api/products?limit=${limit}`);
  return response.data;
};

export const getDashboardOverview = async (
  startDate?: string,
  endDate?: string,
  storeIds?: number[]
): Promise<DashboardData> => {
  const params: any = {};
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;
  if (storeIds && storeIds.length > 0) params.store_ids = storeIds;

  const response = await api.post('/api/dashboard/overview', null, { params });
  return response.data;
};

export const getTimeSeries = async (
  metric: string,
  timeBucket: string,
  filters?: any
): Promise<TimeSeriesData[]> => {
  const response = await api.post('/api/analytics/time-series', {
    metric,
    time_bucket: timeBucket,
    filters,
  });
  return response.data;
};

export const getAggregation = async (
  metric: string,
  groupBy: string[],
  filters?: any,
  limit = 100
): Promise<any[]> => {
  const response = await api.post('/api/analytics/aggregation', {
    metric,
    group_by: groupBy,
    filters,
    limit,
  });
  return response.data;
};

export const getTopProducts = async (
  filters?: any,
  limit = 10,
  orderBy = 'revenue'
): Promise<TopProduct[]> => {
  const response = await api.post('/api/analytics/top-products', {
    filters,
    limit,
    order_by: orderBy,
  });
  return response.data;
};

export const getStoreComparison = async (
  startDate?: string,
  endDate?: string,
  limit = 20
): Promise<any[]> => {
  const params: any = { limit };
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;

  const response = await api.post('/api/analytics/store-comparison', null, { params });
  return response.data;
};

export const getInsights = async (
  startDate?: string,
  endDate?: string
): Promise<{ insights: Insight[]; generated_at: string }> => {
  const params: any = {};
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;

  const response = await api.get('/api/analytics/insights', { params });
  return response.data;
};
