import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { format, subDays } from 'date-fns';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getAggregation, getTimeSeries } from '../api';

export default function Analytics() {
  const [metric, setMetric] = useState('revenue');
  const [groupBy, setGroupBy] = useState(['channel']);
  const [timeBucket, setTimeBucket] = useState('day');
  const [dateRange, setDateRange] = useState({
    start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });

  const filters = {
    date_range: {
      start_date: dateRange.start,
      end_date: dateRange.end,
    },
  };

  const { data: aggregationData, isLoading: aggLoading } = useQuery({
    queryKey: ['aggregation', metric, groupBy, filters],
    queryFn: () => getAggregation(metric, groupBy, filters),
  });

  const { data: timeSeriesData, isLoading: tsLoading } = useQuery({
    queryKey: ['timeseries', metric, timeBucket, filters],
    queryFn: () => getTimeSeries(metric, timeBucket, filters),
  });

  const metricOptions = [
    { value: 'revenue', label: 'Faturamento' },
    { value: 'sales_count', label: 'Número de Vendas' },
    { value: 'avg_ticket', label: 'Ticket Médio' },
    { value: 'avg_production_time', label: 'Tempo Médio de Produção' },
    { value: 'avg_delivery_time', label: 'Tempo Médio de Entrega' },
  ];

  const groupByOptions = [
    { value: 'store', label: 'Loja' },
    { value: 'channel', label: 'Canal' },
    { value: 'product', label: 'Produto' },
    { value: 'weekday', label: 'Dia da Semana' },
    { value: 'hour', label: 'Horário' },
  ];

  const timeBucketOptions = [
    { value: 'hour', label: 'Por Hora' },
    { value: 'day', label: 'Por Dia' },
    { value: 'week', label: 'Por Semana' },
    { value: 'month', label: 'Por Mês' },
  ];

  return (
    <div style={{ padding: '2rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          Análises Customizadas
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Explore seus dados de forma flexível
        </p>
      </div>

      {/* Query Builder */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem' }}>
          Construtor de Análise
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>
              Métrica
            </label>
            <select className="select" value={metric} onChange={(e) => setMetric(e.target.value)}>
              {metricOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>
              Agrupar Por
            </label>
            <select className="select" value={groupBy[0]} onChange={(e) => setGroupBy([e.target.value])}>
              {groupByOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>
              Período
            </label>
            <select className="select" value={timeBucket} onChange={(e) => setTimeBucket(e.target.value)}>
              {timeBucketOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem' }}>
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
        </div>
      </div>

      {/* Results */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '1.5rem' }}>
        {/* Time Series Chart */}
        <div className="card">
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem' }}>
            Série Temporal
          </h3>
          {tsLoading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
              <div className="spinner" />
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={timeSeriesData || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="period" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={2} name={metricOptions.find(m => m.value === metric)?.label} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Aggregation Chart */}
        <div className="card">
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem' }}>
            Agregação por {groupByOptions.find(g => g.value === groupBy[0])?.label}
          </h3>
          {aggLoading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
              <div className="spinner" />
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={aggregationData?.slice(0, 15) || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={`${groupBy[0]}_name`} angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#10b981" name={metricOptions.find(m => m.value === metric)?.label} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Data Table */}
      {aggregationData && (
        <div className="card" style={{ marginTop: '1.5rem' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem' }}>
            Dados Detalhados
          </h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--border)' }}>
                  <th style={{ padding: '0.75rem', textAlign: 'left', fontWeight: '600' }}>
                    {groupByOptions.find(g => g.value === groupBy[0])?.label}
                  </th>
                  <th style={{ padding: '0.75rem', textAlign: 'right', fontWeight: '600' }}>
                    {metricOptions.find(m => m.value === metric)?.label}
                  </th>
                </tr>
              </thead>
              <tbody>
                {aggregationData.slice(0, 20).map((row: any, idx: number) => (
                  <tr key={idx} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '0.75rem' }}>
                      {row[`${groupBy[0]}_name`] || row[groupBy[0]]}
                    </td>
                    <td style={{ padding: '0.75rem', textAlign: 'right', fontWeight: '500' }}>
                      {metric.includes('revenue') || metric.includes('ticket')
                        ? `R$ ${Number(row.value).toFixed(2)}`
                        : Number(row.value).toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
