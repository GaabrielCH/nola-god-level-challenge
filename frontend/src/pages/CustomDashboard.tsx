import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { format, subDays } from 'date-fns';
import { PlusCircle, Lightbulb, AlertCircle } from 'lucide-react';
import { getInsights } from '../api';

export default function CustomDashboard() {
  const [dateRange, setDateRange] = useState({
    start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });

  const { data: insightsData } = useQuery({
    queryKey: ['insights', dateRange],
    queryFn: () => getInsights(dateRange.start, dateRange.end),
  });

  return (
    <div style={{ padding: '2rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          Insights Automáticos
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Descubra padrões e oportunidades nos seus dados
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

      {/* Insights Grid */}
      <div style={{ display: 'grid', gap: '1.5rem' }}>
        {insightsData?.insights.map((insight: any, idx: number) => (
          <InsightCard key={idx} insight={insight} />
        ))}
      </div>

      {/* Empty State */}
      {(!insightsData?.insights || insightsData.insights.length === 0) && (
        <div className="card" style={{ padding: '4rem', textAlign: 'center' }}>
          <Lightbulb size={64} color="var(--text-secondary)" style={{ margin: '0 auto 1rem' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>
            Nenhum insight disponível
          </h3>
          <p style={{ color: 'var(--text-secondary)' }}>
            Ajuste o período para gerar insights automáticos
          </p>
        </div>
      )}

      {/* Info Card */}
      <div className="card" style={{ marginTop: '2rem', backgroundColor: 'var(--background)', border: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <div style={{ color: 'var(--primary)' }}>
            <PlusCircle size={24} />
          </div>
          <div>
            <h4 style={{ fontWeight: '600', marginBottom: '0.5rem' }}>
              Dashboard Customizado
            </h4>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
              Em breve você poderá criar dashboards personalizados arrastando e soltando widgets.
              Os insights automáticos te ajudam a identificar tendências e oportunidades de melhoria.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

interface InsightCardProps {
  insight: {
    type: string;
    title: string;
    description: string;
    severity: string;
    action?: string;
  };
}

function InsightCard({ insight }: InsightCardProps) {
  const getIcon = () => {
    if (insight.severity === 'critical') {
      return <AlertCircle size={24} color="#ef4444" />;
    }
    return <Lightbulb size={24} color={insight.type === 'anomaly' ? '#f59e0b' : '#10b981'} />;
  };

  const getBorderColor = () => {
    if (insight.severity === 'critical') return '#ef4444';
    if (insight.type === 'anomaly') return '#f59e0b';
    return '#10b981';
  };

  return (
    <div
      className="card"
      style={{
        borderLeft: `4px solid ${getBorderColor()}`,
        transition: 'transform 0.2s, box-shadow 0.2s',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = 'var(--shadow-lg)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = 'var(--shadow)';
      }}
    >
      <div style={{ display: 'flex', gap: '1rem' }}>
        <div style={{ paddingTop: '0.25rem' }}>
          {getIcon()}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600' }}>
              {insight.title}
            </h3>
            <span
              style={{
                fontSize: '0.75rem',
                fontWeight: '600',
                textTransform: 'uppercase',
                color: getBorderColor(),
                padding: '0.25rem 0.75rem',
                borderRadius: '1rem',
                backgroundColor: `${getBorderColor()}15`,
              }}
            >
              {insight.type}
            </span>
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: '1.5', marginBottom: '0.75rem' }}>
            {insight.description}
          </p>
          {insight.action && (
            <div style={{
              padding: '0.75rem',
              backgroundColor: 'var(--background)',
              borderRadius: '0.375rem',
              fontSize: '0.875rem',
              fontWeight: '500',
            }}>
              💡 {insight.action}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
