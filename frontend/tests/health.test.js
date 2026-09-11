import assert from 'node:assert/strict';
import { test } from 'node:test';
import { checkHealth } from '../src/api/health.js';

test('requests the relative health endpoint with cancellation support', async (t) => {
  const controller = new AbortController();
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    assert.equal(url, '/api/health');
    assert.equal(options.signal, controller.signal);
    return Response.json({ status: 'ok' });
  });
  assert.deepEqual(await checkHealth(controller.signal), { status: 'ok' });
});

test('rejects unsuccessful HTTP responses', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => new Response('', { status: 503 }));
  await assert.rejects(checkHealth(), /503/);
});

test('rejects an unexpected health payload', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => Response.json({ status: 'error' }));
  await assert.rejects(checkHealth(), /Unexpected health response/);
});

test('propagates connection failures', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => { throw new TypeError('Failed to fetch'); });
  await assert.rejects(checkHealth(), /Failed to fetch/);
});
