import { useEffect, useState } from 'react';
import { checkHealth } from './api/health.js';

const statusText = {
  checking: 'Checking backend connection...',
  connected: 'Backend connected',
  disconnected: 'Backend disconnected. Start the backend and try again.',
};

export default function App() {
  const [status, setStatus] = useState('checking');
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    checkHealth(controller.signal)
      .then(() => { if (active) setStatus('connected'); })
      .catch(() => { if (active) setStatus('disconnected'); })
      .finally(() => clearTimeout(timeout));

    return () => {
      active = false;
      clearTimeout(timeout);
      controller.abort();
    };
  }, [attempt]);

  function retry() {
    setStatus('checking');
    setAttempt((value) => value + 1);
  }

  return (
    <main>
      <p className="eyebrow">Application setup</p>
      <h1>Group Chat Search</h1>
      <p>The starting point for search over a synthetic group chat.</p>
      <section aria-label="Backend connection" className="connection">
        <p role="status" className={`status ${status}`}>{statusText[status]}</p>
        <button onClick={retry} disabled={status === 'checking'}>
          Check again
        </button>
      </section>
      <p className="note">Search and chat data will be added in a later phase.</p>
    </main>
  );
}
