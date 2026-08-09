import React, { useState } from 'react';
import { Layers, CheckCircle, RefreshCw, XCircle, AlertCircle, Search, ExternalLink, Calendar, DollarSign } from 'lucide-react';

const ASSIGNEE_NAMES = {
  'u_aarti': 'Aarti Menon (Enterprise)',
  'u_rohit': 'Rohit Sharma (SMB)',
  'u_meera': 'Meera Iyer (Marketing)',
  'u_karan': 'Karan Doshi (Alliances)',
  'u_divya': 'Divya Rao (Finance)',
  'u_triage': 'Triage Queue (Ops)'
};

export default function ResultsTable({ tasks, processedEmails }) {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedItem, setSelectedItem] = useState(null);

  // Combine tasks and processed emails for full audit trail
  const combinedList = (processedEmails || []).map(pe => {
    const linkedTask = (tasks || []).find(t => t.task_id === pe.task_id || t.source_email_id === pe.email_id);
    return {
      ...pe,
      task_id: pe.task_id || (linkedTask ? linkedTask.task_id : null),
      title: linkedTask ? linkedTask.title : pe.subject,
      description: linkedTask ? linkedTask.description : pe.routing_reason,
      deal_value_inr: linkedTask ? linkedTask.deal_value_inr : pe.deal_value_inr,
      due_date: linkedTask ? linkedTask.due_date : pe.due_date,
      company_name: linkedTask ? linkedTask.company_name : pe.company_name,
      priority: linkedTask ? linkedTask.priority : pe.priority,
      category: linkedTask ? linkedTask.category : pe.category,
      assignee_id: linkedTask ? linkedTask.assignee_id : pe.assignee_id,
      confidence: linkedTask ? linkedTask.confidence : pe.confidence
    };
  });

  const filteredItems = combinedList.filter(item => {
    // Tab filter
    if (activeTab === 'created' && item.decision !== 'created') return false;
    if (activeTab === 'updated' && item.decision !== 'updated') return false;
    if (activeTab === 'skipped' && item.decision !== 'skipped') return false;
    if (activeTab === 'triage' && item.category !== 'triage') return false;

    // Search filter
    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      const matchText = `${item.subject || ''} ${item.from_name || ''} ${item.from_email || ''} ${item.company_name || ''} ${item.task_id || ''}`.toLowerCase();
      if (!matchText.includes(q)) return false;
    }
    return true;
  });

  const getCategoryBadge = (cat) => {
    switch (cat) {
      case 'enterprise_rfp': return <span className="badge badge-enterprise">Enterprise RFP</span>;
      case 'smb_enquiry': return <span className="badge badge-smb">SMB Enquiry</span>;
      case 'marketing': return <span className="badge badge-marketing">Marketing</span>;
      case 'alliances': return <span className="badge badge-alliances">Alliances</span>;
      case 'finance': return <span className="badge badge-finance">Finance</span>;
      case 'triage': return <span className="badge badge-triage">Triage</span>;
      default: return <span className="badge badge-priority-low">{cat || '—'}</span>;
    }
  };

  const getPriorityBadge = (prio) => {
    switch (prio) {
      case 'high': return <span className="badge badge-priority-high">High</span>;
      case 'medium': return <span className="badge badge-priority-medium">Medium</span>;
      case 'low': return <span className="badge badge-priority-low">Low</span>;
      default: return <span style={{ color: 'var(--text-muted)' }}>—</span>;
    }
  };

  const getDecisionBadge = (decision, skipReason) => {
    if (decision === 'created') {
      return <span className="badge badge-decision-created"><CheckCircle size={11} /> Created</span>;
    }
    if (decision === 'updated') {
      return <span className="badge badge-decision-updated"><RefreshCw size={11} /> Updated</span>;
    }
    return (
      <span className="badge badge-decision-skipped" title={skipReason || 'Skipped'}>
        <XCircle size={11} /> Skipped ({skipReason || 'Noise'})
      </span>
    );
  };

  return (
    <section className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Layers size={22} color="#06b6d4" />
          <div>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700, color: '#ffffff' }}>
              3. Processing &amp; Routing Results
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Deterministic routing outcomes, task assignments, deal valuations, and skip audits.
            </p>
          </div>
        </div>

        {/* Search */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(0,0,0,0.3)', padding: '6px 14px', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
          <Search size={14} color="var(--text-muted)" />
          <input
            type="text"
            placeholder="Search company, subject, email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#f8fafc',
              fontSize: '0.82rem',
              outline: 'none',
              width: '220px'
            }}
          />
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '10px', flexWrap: 'wrap' }}>
        <button
          className={`btn ${activeTab === 'all' ? 'btn-primary' : 'btn-secondary'}`}
          style={{ padding: '6px 14px', fontSize: '0.8rem' }}
          onClick={() => setActiveTab('all')}
        >
          All Items ({combinedList.length})
        </button>
        <button
          className={`btn ${activeTab === 'created' ? 'btn-primary' : 'btn-secondary'}`}
          style={{ padding: '6px 14px', fontSize: '0.8rem' }}
          onClick={() => setActiveTab('created')}
        >
          Created Tasks ({combinedList.filter(i => i.decision === 'created').length})
        </button>
        <button
          className={`btn ${activeTab === 'updated' ? 'btn-primary' : 'btn-secondary'}`}
          style={{ padding: '6px 14px', fontSize: '0.8rem' }}
          onClick={() => setActiveTab('updated')}
        >
          Updated Threads ({combinedList.filter(i => i.decision === 'updated').length})
        </button>
        <button
          className={`btn ${activeTab === 'skipped' ? 'btn-primary' : 'btn-secondary'}`}
          style={{ padding: '6px 14px', fontSize: '0.8rem' }}
          onClick={() => setActiveTab('skipped')}
        >
          Skipped Noise ({combinedList.filter(i => i.decision === 'skipped').length})
        </button>
        <button
          className={`btn ${activeTab === 'triage' ? 'btn-primary' : 'btn-secondary'}`}
          style={{ padding: '6px 14px', fontSize: '0.8rem' }}
          onClick={() => setActiveTab('triage')}
        >
          Triage Queue ({combinedList.filter(i => i.category === 'triage').length})
        </button>
      </div>

      {/* Results Table */}
      <div style={{ overflowX: 'auto', maxHeight: '420px', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: '90px' }}>Task ID</th>
              <th style={{ width: '100px' }}>Decision</th>
              <th style={{ width: '150px' }}>Assignee</th>
              <th style={{ width: '130px' }}>Category</th>
              <th style={{ width: '80px' }}>Priority</th>
              <th style={{ width: '140px' }}>Company</th>
              <th style={{ width: '110px' }}>Deal Value</th>
              <th style={{ width: '100px' }}>Due Date</th>
              <th style={{ width: '90px' }}>Confidence</th>
              <th>Routing Reason</th>
            </tr>
          </thead>
          <tbody>
            {filteredItems.length === 0 ? (
              <tr>
                <td colSpan="10" style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                  No items match the selected filter.
                </td>
              </tr>
            ) : (
              filteredItems.map((item, idx) => {
                const confPercent = Math.round((item.confidence || 0) * 100);
                const confColor = confPercent >= 80 ? '#34d399' : confPercent >= 60 ? '#fbbf24' : '#f87171';
                const formattedVal = item.deal_value_inr ? `₹${item.deal_value_inr.toLocaleString('en-IN')}` : '—';

                return (
                  <tr key={item.email_id || idx} onClick={() => setSelectedItem(item)} style={{ cursor: 'pointer' }}>
                    <td>
                      <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.75rem', fontWeight: 600, color: '#38bdf8' }}>
                        {item.task_id || '—'}
                      </span>
                    </td>
                    <td>
                      {getDecisionBadge(item.decision, item.skip_reason)}
                    </td>
                    <td style={{ fontSize: '0.8rem', fontWeight: 500 }}>
                      {item.assignee_id ? (
                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                          <span style={{ color: '#f1f5f9', fontWeight: 600 }}>{ASSIGNEE_NAMES[item.assignee_id] || item.assignee_id}</span>
                          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: "'JetBrains Mono', monospace" }}>{item.assignee_id}</span>
                        </div>
                      ) : (
                        <span style={{ color: 'var(--text-muted)' }}>—</span>
                      )}
                    </td>
                    <td>
                      {getCategoryBadge(item.category)}
                    </td>
                    <td>
                      {getPriorityBadge(item.priority)}
                    </td>
                    <td style={{ fontWeight: 600, color: item.company_name ? '#e2e8f0' : 'var(--text-muted)' }}>
                      {item.company_name || 'null'}
                    </td>
                    <td style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 600, color: item.deal_value_inr ? '#34d399' : 'var(--text-muted)' }}>
                      {formattedVal}
                    </td>
                    <td style={{ fontSize: '0.8rem', color: item.due_date ? '#fde047' : 'var(--text-muted)' }}>
                      {item.due_date || 'null'}
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <div style={{ width: '38px', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ width: `${confPercent}%`, height: '100%', backgroundColor: confColor }}></div>
                        </div>
                        <span style={{ fontSize: '0.75rem', fontFamily: "'JetBrains Mono', monospace", color: confColor }}>
                          {item.confidence ? `${(item.confidence).toFixed(2)}` : '—'}
                        </span>
                      </div>
                    </td>
                    <td style={{ color: 'var(--text-secondary)', fontSize: '0.78rem', maxWidth: '240px' }}>
                      <span title={item.routing_reason}>{item.routing_reason || item.description || '—'}</span>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Selected Item Modal / Drawer */}
      {selectedItem && (
        <div style={{
          marginTop: '16px',
          padding: '16px 20px',
          borderRadius: '12px',
          background: 'rgba(0,0,0,0.5)',
          border: '1px solid var(--border-accent)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          gap: '16px',
          flexWrap: 'wrap'
        }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span style={{ fontWeight: 700, fontSize: '0.95rem', color: '#ffffff' }}>{selectedItem.subject}</span>
              {getCategoryBadge(selectedItem.category)}
              {getPriorityBadge(selectedItem.priority)}
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
              <strong>From:</strong> {selectedItem.from_name} ({selectedItem.from_email}) | <strong>Thread:</strong> {selectedItem.thread_id} | <strong>Received:</strong> {selectedItem.received_at}
            </p>
            <p style={{ fontSize: '0.85rem', color: '#93c5fd', marginBottom: '6px' }}>
              <strong>Routing Rationale:</strong> {selectedItem.routing_reason || '—'}
            </p>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', background: 'rgba(0,0,0,0.3)', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <strong>Email Body:</strong> {selectedItem.body}
            </div>
          </div>
          <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '0.75rem' }} onClick={() => setSelectedItem(null)}>
            Close Details
          </button>
        </div>
      )}
    </section>
  );
}
