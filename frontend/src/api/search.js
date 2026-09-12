const messageIsValid = (message) => message && ['id', 'sender', 'timestamp', 'text']
  .every((field) => typeof message[field] === 'string') && Number.isFinite(Date.parse(message.timestamp));

const metadataIsValid = (metadata) => metadata &&
  ['none', 'bonus', 'filter'].includes(metadata.person_mode) &&
  (metadata.person === null || typeof metadata.person === 'string') &&
  [metadata.start_date, metadata.end_date].every((value) => value === null ||
    (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value))) &&
  Array.isArray(metadata.warnings) && metadata.warnings.every((item) => typeof item === 'string') &&
  Array.isArray(metadata.explanations) && metadata.explanations.every((item) => typeof item === 'string') &&
  typeof metadata.reference_date === 'string' && typeof metadata.timezone === 'string';

async function request(path, options) {
  let response;
  try { response = await fetch(path, options); }
  catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new Error('We couldn’t reach the archive. Check your connection and try again.');
  }
  if (!response.ok) {
    if (response.status === 503) throw new Error('Search is unavailable right now. Please try again once the service is ready.');
    if (response.status === 422) throw new Error('Please enter a question with between 1 and 2,000 characters.');
    throw new Error('The archive couldn’t complete that request. Please try again.');
  }
  try { return await response.json(); }
  catch { throw new Error('The archive sent an unexpected response. Please try again.'); }
}

export async function fetchStats(signal) {
  const data = await request('/api/stats', { signal });
  if (!data || !Number.isInteger(data.message_count) || data.message_count < 1 ||
      !Number.isInteger(data.participant_count) || data.participant_count < 1 ||
      !Number.isFinite(Date.parse(data.date_range?.start)) || !Number.isFinite(Date.parse(data.date_range?.end))) {
    throw new Error('Corpus statistics are unavailable right now.');
  }
  return data;
}

export async function searchChat(query, signal) {
  const data = await request('/api/search', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k: 5 }), signal,
  });
  if (!data || typeof data.query !== 'string' || !metadataIsValid(data.interpreted_query) ||
      !Number.isFinite(data.search_time_ms) || !Array.isArray(data.results) ||
      !data.results.every((result) => messageIsValid(result.matching_message) &&
        Number.isFinite(result.search_score) && Number.isInteger(result.rank) &&
        Array.isArray(result.previous_messages) && result.previous_messages.every(messageIsValid) &&
        Array.isArray(result.next_messages) && result.next_messages.every(messageIsValid))) {
    throw new Error('The archive sent incomplete search results. Please try again.');
  }
  try { new Intl.DateTimeFormat('en-GB', { timeZone: data.interpreted_query.timezone }); }
  catch { throw new Error('The archive sent an invalid timezone. Please try again.'); }
  return data;
}
