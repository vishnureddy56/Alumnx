import React from 'react';
import { Inbox, Hash, Calendar, Mail, User } from 'lucide-react';

export default function RawInboxTable({ emails }) {
  if (!emails || emails.length === 0) {
    return (
      <section className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
          <Inbox size={20} color="#6366f1" />
          <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700, color: '#ffffff' }}>
            2. Raw Inbox (Pre-Routing Sanity View)
          </h2>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          No emails loaded yet. Paste a JSON batch or click "Load Sample Emails" above to preview raw incoming items before routing.
        </p>
      </section>
    );
  }

  return (
    <section className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Inbox size={20} color="#6366f1" />
          <div>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700, color: '#ffffff' }}>
              2. Raw Inbox (Pre-Routing Sanity View)
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Independent raw view of the batch ({emails.length} emails) prior to algorithmic classification and routing.
            </p>
          </div>
        </div>
        <span style={{ fontSize: '0.8rem', padding: '4px 10px', borderRadius: '6px', background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)', border: '1px solid var(--border-subtle)' }}>
          {emails.length} Raw Records Loaded
        </span>
      </div>

      <div style={{ overflowX: 'auto', maxHeight: '340px', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: '150px' }}>From Name</th>
              <th style={{ width: '190px' }}>From Email</th>
              <th style={{ width: '220px' }}>Subject</th>
              <th style={{ width: '130px' }}>Received At</th>
              <th style={{ width: '100px' }}>Thread ID</th>
              <th>Body Preview</th>
            </tr>
          </thead>
          <tbody>
            {emails.map((em, idx) => {
              const recDate = em.received_at ? em.received_at.substring(0, 16).replace('T', ' ') : '—';
              const bodySnippet = (em.body || '').substring(0, 120) + ((em.body || '').length > 120 ? '...' : '');

              return (
                <tr key={em.email_id || idx}>
                  <td style={{ fontWeight: 600, color: '#e2e8f0' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <User size={13} color="var(--text-muted)" />
                      <span>{em.from_name || '—'}</span>
                    </div>
                  </td>
                  <td style={{ color: '#38bdf8', fontFamily: "'JetBrains Mono', monospace", fontSize: '0.8rem' }}>
                    {em.from_email}
                  </td>
                  <td style={{ fontWeight: 500 }}>
                    {em.subject}
                  </td>
                  <td style={{ color: 'var(--text-secondary)', fontSize: '0.78rem', whiteSpace: 'nowrap' }}>
                    {recDate}
                  </td>
                  <td>
                    <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.75rem', padding: '2px 6px', background: 'rgba(0,0,0,0.3)', borderRadius: '4px', border: '1px solid var(--border-subtle)', color: '#a5b4fc' }}>
                      {em.thread_id}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem', lineHeight: '1.4' }}>
                    {bodySnippet}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
