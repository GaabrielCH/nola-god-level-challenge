import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { format, subDays } from 'date-fns';
import { TrendingUp, TrendingDown, DollarSign, ShoppingCart, Receipt, Calendar } from 'lucide-react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { getDashboardOverview, getStores, DashboardData } from '../api';

export default function Dashboard() {
  const [dateRange, setDateRange] = useState({
    start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });
  const [selectedStores, setSelectedStores] = useState<number[]>([]);

  const { data: stores } = useQuery({
    queryKey: ['stores'],
    queryFn: getStores,
  });

  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['dashboard', dateRange, selectedStores],
    queryFn: () => getDashboardOverview(
      dateRange.start,
      dateRange.end,
      selectedStores.length > 0 ? selectedStores : undefined
    ),
  });

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div className="spinner" />
      </div>
    );
  }

  const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

  return (
    <div style={{ padding: '2rem' }}>
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          Dashboard Principal
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Visão geral do desempenho dos restaurantes
        </p>
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>
              Data Inicial
            </label>
            <input
              type="date"
              className="input"
              value={dateRange.start}
              onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>
              Data Final
            </label>
            <input
              type="date"
              className="input"
              value={dateRange.end}
              onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>
              Lojas
            </label>
            <select
              className="select"
              multiple
              value={selectedStores.map(String)}
              onChange={(e) => {
                const values = Array.from(e.target.selectedOptions, option => Number(option.value));
                setSelectedStores(values);
              }}
              style={{ height: '38px' }}
            >
              {stores?.map((store) => (
                <option key={store.id} value={store.id}>
                  {store.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        {dashboardData?.metrics.map((metric, idx) => (
          <MetricCard key={idx} metric={metric} />
        ))}
      </div>

      {/* Charts Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '1.5rem' }}>
        {/* Revenue Time Series */}
        <div className="card">
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem' }}>
            Faturamento ao Longo do Tempo
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={dashboardData?.time_series || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <Tooltip formatter={(value: any) => `R$ ${Number(value).toFixed(2)}`} />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#2563eb" name="Receita" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Channel Performance */}
        <div className="card">
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem' }}>
            Performance por Canal
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dashboardData?.channel_performance || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="channel_name" />
              <YAxis />
              <Tooltip formatter={(value: any) => `R$ ${Number(value).toFixed(2)}`} />
              <Legend />
              <Bar dataKey="revenue" fill="#2563eb" name="Receita" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top Products */}
        <div className="card">
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem' }}>
            Top 10 Produtos
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dashboardData?.top_products || []} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="product_name" type="category" width={150} />
              <Tooltip formatter={(value: any) => `R$ ${Number(value).toFixed(2)}`} />
              <Bar dataKey="value" fill="#10b981" name="Receita" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Hourly Distribution */}
        <div className="card">
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem' }}>
            Distribuição por Horário
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dashboardData?.hourly_distribution || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="sales_count" fill="#8b5cf6" name="Vendas" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

interface MetricCardProps {
  metric: {
    title: string;
    value: number;
    change?: number;
    format: string;
  };
}

function MetricCard({ metric }: MetricCardProps) {
  const formatValue = (value: number, format: string) => {
    if (format === 'currency') {
      return `R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
    if (format === 'percent') {
      return `${value.toFixed(1)}%`;
    }
    return value.toLocaleString('pt-BR');
  };

  const getIcon = () => {
    if (metric.title.includes('Faturamento')) return <DollarSign size={24} />;
    if (metric.title.includes('Vendas')) return <ShoppingCart size={24} />;
    if (metric.title.includes('Ticket')) return <Receipt size={24} />;
    return <TrendingUp size={24} />;
  };

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', fontWeight: '500' }}>
          {metric.title}
        </p>
        <div style={{ color: 'var(--primary)' }}>
          {getIcon()}
        </div>
      </div>
      <p style={{ fontSize: '1.875rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
        {formatValue(metric.value, metric.format)}
      </p>
      {metric.change !== undefined && metric.change !== null && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {metric.change > 0 ? (
            <TrendingUp size={16} color="#10b981" />
          ) : (
            <TrendingDown size={16} color="#ef4444" />
          )}
          <span style={{
            fontSize: '0.875rem',
            color: metric.change > 0 ? '#10b981' : '#ef4444',
            fontWeight: '500'
          }}>
            {metric.change > 0 ? '+' : ''}{metric.change.toFixed(1)}%
          </span>
          <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            vs período anterior
          </span>
        </div>
      )}
    </div>
  );
}
