import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { test } from 'node:test';
import { fetchStats, searchChat } from '../src/api/search.js';

const response = JSON.parse(await readFile(new URL('../../examples/search_filtered_response.json', import.meta.url), 'utf8'));
const stats = JSON.parse(await readFile(new URL('../../examples/stats_response.json', import.meta.url), 'utf8'));

test('posts the exact question and K to the real relative endpoint, preserving original results', async (t) => {
  const controller = new AbortController();
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    assert.equal(url, '/api/search');
    assert.equal(options.method, 'POST');
    assert.equal(options.signal, controller.signal);
    assert.deepEqual(JSON.parse(options.body), { query: 'Ananya ne kya bola?', top_k: 5 });
    assert.equal(options.headers['Content-Type'], 'application/json');
    return Response.json(response);
  });
  assert.deepEqual(await searchChat('Ananya ne kya bola?', controller.signal), response);
});

test('loads actual corpus statistics without fabricated fallback counts', async (t) => {
  t.mock.method(globalThis, 'fetch', async (url) => {
    assert.equal(url, '/api/stats');
    return Response.json(stats);
  });
  assert.deepEqual(await fetchStats(), stats);
});

test('accepts empty search results with interpreted constraints', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => Response.json({ ...response, results: [] }));
  assert.deepEqual((await searchChat('today')).results, []);
});

test('shows a useful unavailable-service error', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => new Response('', { status: 503 }));
  await assert.rejects(searchChat('query'), /unavailable/);
});

test('handles validation errors', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => new Response('', { status: 422 }));
  await assert.rejects(searchChat('query'), /2,000/);
});

test('handles network errors without leaking browser internals', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => { throw new TypeError('Failed to fetch'); });
  await assert.rejects(searchChat('query'), /couldn’t reach/);
});

test('preserves cancellation for timeout and stale-request handling', async (t) => {
  const error = new DOMException('aborted', 'AbortError');
  t.mock.method(globalThis, 'fetch', async () => { throw error; });
  await assert.rejects(searchChat('query'), (failure) => failure === error);
});

test('rejects malformed responses before they reach chat components', async (t) => {
  for (const payload of [null, {}, { ...response, interpreted_query: {} },
    { ...response, results: [{ ...response.results[0], matching_message: { text: 'wrong' } }] },
    { ...response, interpreted_query: { ...response.interpreted_query, timezone: 'Invalid/Zone' } }]) {
    t.mock.method(globalThis, 'fetch', async () => Response.json(payload));
    await assert.rejects(searchChat('query'), /incomplete|invalid timezone/);
    t.mock.restoreAll();
  }
});

test('rejects missing or invalid statistics', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => Response.json({ message_count: 4634 }));
  await assert.rejects(fetchStats(), /unavailable/);
});

test('handles non-JSON success responses', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => new Response('<html>wrong server</html>'));
  await assert.rejects(searchChat('query'), /unexpected response/);
});
