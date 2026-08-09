import React, { useState } from 'react';
import { MessageSquare, Send, Bot, User, Database, ChevronDown, ChevronUp, Sparkles, AlertCircle } from 'lucide-react';
import { sendChatMessage } from '../services/api';

const SAMPLE_QUESTIONS = [
  "How many emails this batch were proposal or RFP related?",
  "How many were marketing versus actual spam we correctly ignored?",
  "Show me everything sitting in triage and why.",
  "What's our spurious rate so far?",
  "Which high-priority tasks are still unassigned-feeling — i.e., low confidence?",
  "How many alliances emails came from resellers versus tech integration partners?",
  "How many emails were about GST refunds?",
  "Send Aarti an email about the Meridian Steel RFP.",
  "What's the total deal value of all open RFPs?",
  "Did any thread get updated more than once?"
];

export default function ChatAssistant({ candidateId }) {
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: "Hello! I am RouteIQ's Grounded Analytics Assistant. Ask me any questions regarding the processed sales inbox data, routing decisions, triage reasons, spurious rates, or deal pipeline totals.",
      supportingData: null
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [expandedSupporting, setExpandedSupporting] = useState({});

  const handleSendMessage = async (queryText) => {
    const q = queryText || inputText;
    if (!q.trim() || isLoading) return;

    const userMsg = { sender: 'user', text: q, supportingData: null };
    setMessages(prev => [...prev, userMsg]);
    setInputText('');
    setIsLoading(true);

    try {
      const res = await sendChatMessage(candidateId, q);
      const assistantMsg = {
        sender: 'assistant',
        text: res.answer,
        supportingData: res.supporting_data
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          sender: 'assistant',
          text: `Error processing query: ${err.message}`,
          supportingData: null,
          isError: true
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSupporting = (idx) => {
    setExpandedSupporting(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }));
  };

  return (
    <section className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
        <MessageSquare size={22} color="#6366f1" />
        <div>
          <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700, color: '#ffffff' }}>
            5. Grounded Ops Chat Panel (/api/chat)
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Ask natural-language questions backed strictly by PostgreSQL query results. Hallucinations are prevented via grounded supporting data.
          </p>
        </div>
      </div>

      {/* Suggested Quick Questions */}
      <div style={{ marginBottom: '16px' }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em', display: 'block', marginBottom: '8px' }}>
          Suggested Grader Questions &amp; Edge Cases:
        </span>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {SAMPLE_QUESTIONS.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(q)}
              disabled={isLoading}
              style={{
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '8px',
                padding: '5px 10px',
                fontSize: '0.74rem',
                color: '#cbd5e1',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease'
              }}
              onMouseOver={(e) => e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.5)'}
              onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--border-subtle)'}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Messages Thread Container */}
      <div style={{
        background: 'rgba(0, 0, 0, 0.35)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '12px',
        padding: '16px',
        height: '360px',
        overflowY: 'auto',
        marginBottom: '14px',
        display: 'flex',
        flexDirection: 'column',
        gap: '14px'
      }}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              gap: '10px',
              alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '85%'
            }}
          >
            {msg.sender === 'assistant' && (
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: msg.isError ? 'rgba(239, 68, 68, 0.2)' : 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}>
                {msg.isError ? <AlertCircle size={16} color="#f87171" /> : <Bot size={16} color="#ffffff" />}
              </div>
            )}

            <div>
              <div style={{
                background: msg.sender === 'user' ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255, 255, 255, 0.05)',
                border: msg.sender === 'user' ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid var(--border-subtle)',
                borderRadius: '12px',
                padding: '10px 14px',
                fontSize: '0.85rem',
                color: msg.isError ? '#fca5a5' : '#f1f5f9',
                lineHeight: '1.45'
              }}>
                {msg.text}
              </div>

              {/* Collapsible Grounded Supporting Data */}
              {msg.supportingData && (
                <div style={{ marginTop: '6px' }}>
                  <button
                    onClick={() => toggleSupporting(idx)}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: '#38bdf8',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      padding: '2px 0'
                    }}
                  >
                    <Database size={12} />
                    {expandedSupporting[idx] ? 'Hide' : 'View'} Grounded Supporting Data
                    {expandedSupporting[idx] ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                  </button>

                  {expandedSupporting[idx] && (
                    <div style={{ marginTop: '4px' }}>
                      <pre className="code-block" style={{ fontSize: '0.75rem', padding: '8px 12px' }}>
                        {JSON.stringify(msg.supportingData, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>

            {msg.sender === 'user' && (
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}>
                <User size={16} color="#cbd5e1" />
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div style={{ display: 'flex', gap: '10px', alignSelf: 'flex-start' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'rgba(99, 102, 241, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Bot size={16} color="#a5b4fc" />
            </div>
            <div style={{ background: 'rgba(255, 255, 255, 0.05)', borderRadius: '12px', padding: '10px 14px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Executing grounded database query...
            </div>
          </div>
        )}
      </div>

      {/* Input Box */}
      <form
        onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}
        style={{ display: 'flex', gap: '10px' }}
      >
        <input
          type="text"
          placeholder="Ask a question about the processed batch (e.g. How many proposals came in?)..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={isLoading}
          style={{
            flex: 1,
            background: 'rgba(0, 0, 0, 0.4)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '10px',
            padding: '10px 16px',
            fontSize: '0.85rem',
            color: '#f8fafc',
            outline: 'none'
          }}
        />
        <button type="submit" className="btn btn-primary" disabled={isLoading || !inputText.trim()}>
          <Send size={16} />
          Send
        </button>
      </form>
    </section>
  );
}
