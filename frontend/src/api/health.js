export async function checkHealth(signal) {
  const response = await fetch('/api/health', { signal });
  if (!response.ok) {
    throw new Error(`Health check failed (${response.status})`);
  }
  const data = await response.json();
  if (data.status !== 'ok') {
    throw new Error('Unexpected health response');
  }
  return data;
}
