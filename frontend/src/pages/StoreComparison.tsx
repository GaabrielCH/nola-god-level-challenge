import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { format, subDays } from 'date-fns';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, MapPin } from 'lucide-react';
import { getStoreComparison } from '../api';

export default function StoreComparison() {
  const [dateRange, setDateRange] = useState({
    start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });

  const { data: storeData, isLoading } = useQuery({
    queryKey: ['store-comparison', dateRange],
    queryFn: () => getStoreComparison(dateRange.start, dateRange.end, 20),
  });

  return (
    <div style={{ padding: '2rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          Comparação de Lojas
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Compare o desempenho de diferentes lojas
        </p>
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom: '2rem' }}>
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

      {isLoading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
          <div className="spinner" />
        </div>
      ) : (
        <>
          {/* Revenue Chart */}
          <div className="card" style={{ marginBottom: '2rem' }}>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem' }}>
              Faturamento por Loja
            </h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={storeData || []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="store_name" type="category" width={200} />
                <Tooltip formatter={(value: any) => `R$ ${Number(value).toFixed(2)}`} />
                <Legend />
                <Bar dataKey="revenue" fill="#2563eb" name="Faturamento" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Sales Count Chart */}
          <div className="card" style={{ marginBottom: '2rem' }}>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem' }}>
              Número de Vendas por Loja
            </h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={storeData || []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="store_name" type="category" width={200} />
                <Tooltip />
                <Legend />
                <Bar dataKey="sales_count" fill="#10b981" name="Vendas" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Store Cards Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
            {storeData?.map((store: any, idx: number) => (
              <div key={idx} className="card" style={{ position: 'relative' }}>
                <div style={{
                  position: 'absolute',
                  top: '1rem',
                  right: '1rem',
                  backgroundColor: 'var(--primary)',
                  color: 'white',
                  padding: '0.25rem 0.75rem',
                  borderRadius: '1rem',
                  fontSize: '0.75rem',
                  fontWeight: '600'
                }}>
                  #{idx + 1}
                </div>

                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                  {store.store_name}
                </h3>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                  <MapPin size={16} />
                  <span style={{ fontSize: '0.875rem' }}>{store.city}</span>
                </div>

                <div style={{ display: 'grid', gap: '0.75rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Faturamento</span>
                    <span style={{ fontWeight: '600' }}>
                      R$ {store.revenue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                    </span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Vendas</span>
                    <span style={{ fontWeight: '600' }}>{store.sales_count}</span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Ticket Médio</span>
                    <span style={{ fontWeight: '600' }}>
                      R$ {store.avg_ticket.toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
