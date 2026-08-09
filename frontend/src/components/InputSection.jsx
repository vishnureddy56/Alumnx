import React, { useState } from 'react';
import { UploadCloud, Play, FileJson, RefreshCw, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function InputSection({
  jsonInput,
  setJsonInput,
  onParsePreview,
  onIngest,
  isLoading,
  ingestSummary,
  sample250Data,
  worked12Data
}) {
  const [errorMsg, setErrorMsg] = useState(null);

  const handleLoad250 = () => {
    if (sample250Data && sample250Data.length > 0) {
      setJsonInput(JSON.stringify(sample250Data, null, 2));
      onParsePreview(sample250Data);
      setErrorMsg(null);
    }
  };

  const handleLoadWorked12 = () => {
    if (worked12Data && worked12Data.length > 0) {
      setJsonInput(JSON.stringify(worked12Data, null, 2));
      onParsePreview(worked12Data);
      setErrorMsg(null);
    }
  };

  const handleTextChange = (e) => {
    const text = e.target.value;
    setJsonInput(text);
    if (!text.trim()) {
      onParsePreview([]);
      setErrorMsg(null);
      return;
    }
    try {
      const parsed = JSON.parse(text);
      const list = Array.isArray(parsed) ? parsed : (parsed.emails || [parsed]);
      onParsePreview(list);
      setErrorMsg(null);
    } catch (err) {
      // JSON is still being typed, just ignore
    }
  };

  const handleRunIngest = () => {
    try {
      if (!jsonInput.trim()) {
        setErrorMsg('Please paste email JSON or load a sample batch first.');
        return;
      }
      const parsed = JSON.parse(jsonInput);
      const list = Array.isArray(parsed) ? parsed : (parsed.emails || [parsed]);
      if (list.length === 0) {
        setErrorMsg('No email records found in JSON.');
        return;
      }
      setErrorMsg(null);
      onIngest(list);
    } catch (err) {
      setErrorMsg('Invalid JSON format: ' + err.message);
    }
  };

  return (
    <section className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700, color: '#ffffff' }}>
            1. Email Input &amp; Batch Ingestion
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Paste raw JSON emails (up to 100 per batch limit) or load sample batches.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button className="btn btn-secondary" onClick={handleLoadWorked12} disabled={isLoading}>
            <FileJson size={16} color="#38bdf8" />
            Load 12 Worked Cases
          </button>
          <button className="btn btn-secondary" onClick={handleLoad250} disabled={isLoading}>
            <UploadCloud size={16} color="#a855f7" />
            Load 250 Sample Emails
          </button>
          <button className="btn btn-primary" onClick={handleRunIngest} disabled={isLoading}>
            {isLoading ? <RefreshCw size={16} className="spin" /> : <Play size={16} />}
            {isLoading ? 'Ingesting Batch...' : 'Ingest Batch'}
          </button>
        </div>
      </div>

      <div style={{ position: 'relative' }}>
        <textarea
          value={jsonInput}
          onChange={handleTextChange}
          placeholder='[&#10;  {&#10;    "email_id": "em_00142",&#10;    "thread_id": "th_0091",&#10;    "from_name": "Suresh Kulkarni",&#10;    "from_email": "s.kulkarni@meridiansteel.co.in",&#10;    "subject": "RFP - Enterprise Document Management System",&#10;    "body": "Meridian Steel invites proposals for an enterprise DMS...",&#10;    "received_at": "2026-08-01T09:14:22+05:30"&#10;  }&#10;]'
          style={{
            width: '100%',
            height: '180px',
            backgroundColor: 'rgba(0, 0, 0, 0.45)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '12px',
            padding: '14px',
            color: '#f8fafc',
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: '0.82rem',
            lineHeight: '1.4',
            resize: 'vertical',
            outline: 'none',
            boxShadow: 'inset 0 2px 8px rgba(0,0,0,0.5)'
          }}
        />
      </div>

      {errorMsg && (
        <div style={{ marginTop: '12px', padding: '10px 14px', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#fca5a5', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}>
          <AlertTriangle size={16} />
          <span>{errorMsg}</span>
        </div>
      )}

      {ingestSummary && (
        <div style={{ marginTop: '16px', padding: '14px 18px', borderRadius: '12px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#34d399', fontWeight: 600, fontSize: '0.9rem' }}>
            <CheckCircle2 size={18} />
            <span>Ingest Complete</span>
          </div>
          <div style={{ display: 'flex', gap: '16px', fontSize: '0.85rem', color: '#e2e8f0', flexWrap: 'wrap' }}>
            <div><strong>Processed:</strong> {ingestSummary.processed}</div>
            <div style={{ color: '#34d399' }}><strong>Tasks Created:</strong> {ingestSummary.tasks_created}</div>
            <div style={{ color: '#38bdf8' }}><strong>Tasks Updated:</strong> {ingestSummary.tasks_updated}</div>
            <div style={{ color: '#94a3b8' }}><strong>Skipped:</strong> {ingestSummary.skipped}</div>
          </div>
        </div>
      )}
    </section>
  );
}
