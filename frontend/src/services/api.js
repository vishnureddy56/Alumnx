const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return await res.json();
  } catch (err) {
    return { status: 'offline', error: err.message };
  }
}

export async function ingestEmails(candidateId, emails) {
  const res = await fetch(`${API_BASE}/ingest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      candidate_id: candidateId,
      emails: emails
    })
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Ingest failed with status ${res.status}`);
  }
  return await res.json();
}

export async function fetchApiTasks(candidateId) {
  const res = await fetch(`${API_BASE}/api/tasks?candidate_id=${encodeURIComponent(candidateId)}`);
  if (!res.ok) throw new Error('Failed to fetch tasks');
  return await res.json();
}

export async function fetchStats(candidateId) {
  const res = await fetch(`${API_BASE}/api/stats?candidate_id=${encodeURIComponent(candidateId)}`);
  if (!res.ok) throw new Error('Failed to fetch statistics');
  return await res.json();
}

export async function sendChatMessage(candidateId, query) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      candidate_id: candidateId,
      query: query
    })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Chat query failed');
  }
  return await res.json();
}

export async function fetchTeamRoster() {
  const res = await fetch(`${API_BASE}/users`);
  if (!res.ok) throw new Error('Failed to fetch team roster');
  return await res.json();
}
