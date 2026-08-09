import React from 'react';
import { BarChart3, TrendingUp, AlertOctagon, CheckSquare, RefreshCw, IndianRupee, PieChart } from 'lucide-react';

export default function AnalyticsSection({ stats }) {
  if (!stats) return null;

  const cards = [
    {
      title: 'Total Processed',
      value: stats.processed || 0,
      icon: <CheckSquare size={18} color="#6366f1" />,
      color: '#6366f1',
      sub: 'Synchronously Ingested'
    },
    {
      title: 'Tasks Created',
      value: stats.tasks_created || 0,
      icon: <TrendingUp size={18} color="#10b981" />,
      color: '#10b981',
      sub: 'Actionable Inbounds'
    },
    {
      title: 'Threads Reconciled',
      value: stats.tasks_updated || 0,
      icon: <RefreshCw size={18} color="#06b6d4" />,
      color: '#06b6d4',
      sub: `${(stats.threads_updated_multiple_times || []).length} Multi-Update Threads`
    },
    {
      title: 'Noise Skipped',
      value: stats.skipped || 0,
      icon: <AlertOctagon size={18} color="#94a3b8" />,
      color: '#94a3b8',
      sub: `Spurious Rate: ${((stats.spurious_rate || 0) * 100).toFixed(1)}%`
    },
    {
      title: 'RFP Pipeline Value',
      value: stats.total_deal_value_inr ? `₹${(stats.total_deal_value_inr / 100000).toFixed(1)}L` : '₹0',
      icon: <IndianRupee size={18} color="#fbbf24" />,
      color: '#fbbf24',
      sub: `${stats.rfps_with_no_stated_value || 0} RFPs with budget TBD`
    }
  ];

  return (
    <section className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
        <BarChart3 size={22} color="#a855f7" />
        <div>
          <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700, color: '#ffffff' }}>
            4. Real-Time Routing Analytics (/api/stats)
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Directly aggregated metrics persisted in PostgreSQL database — no fabricated numbers.
          </p>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        {cards.map((c, idx) => (
          <div key={idx} style={{
            background: 'rgba(0, 0, 0, 0.3)',
            borderRadius: '12px',
            padding: '16px',
            border: '1px solid var(--border-subtle)',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600 }}>{c.title}</span>
              <div style={{ padding: '6px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)' }}>
                {c.icon}
              </div>
            </div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#ffffff', fontFamily: 'var(--font-heading)', letterSpacing: '-0.02em', marginBottom: '4px' }}>
              {c.value}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              {c.sub}
            </div>
          </div>
        ))}
      </div>

      {/* Category & Assignee Distributions */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
        {/* Category Breakdown */}
        <div style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-subtle)' }}>
          <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <PieChart size={16} color="#38bdf8" /> Category Breakdown
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {Object.entries(stats.categories || {}).length === 0 ? (
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No category data yet.</span>
            ) : (
              Object.entries(stats.categories || {}).map(([cat, cnt]) => (
                <div key={cat} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.82rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>{cat}</span>
                  <span style={{ fontWeight: 700, color: '#f8fafc', fontFamily: "'JetBrains Mono', monospace" }}>{cnt}</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Assignee Breakdown */}
        <div style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-subtle)' }}>
          <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <PieChart size={16} color="#a855f7" /> Assignee Queue Load
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {Object.entries(stats.assignees || {}).length === 0 ? (
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No assignee data yet.</span>
            ) : (
              Object.entries(stats.assignees || {}).map(([assignee, cnt]) => (
                <div key={assignee} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.82rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>{assignee}</span>
                  <span style={{ fontWeight: 700, color: '#f8fafc', fontFamily: "'JetBrains Mono', monospace" }}>{cnt}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
