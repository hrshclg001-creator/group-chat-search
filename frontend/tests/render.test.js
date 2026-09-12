import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { after, before, test } from 'node:test';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { createServer } from 'vite';

let server;
const sample = JSON.parse(await readFile(new URL('../../examples/search_filtered_response.json', import.meta.url), 'utf8'));
const stats = JSON.parse(await readFile(new URL('../../examples/stats_response.json', import.meta.url), 'utf8'));
before(async () => { server = await createServer({ server: { middlewareMode: true }, appType: 'custom' }); });
after(async () => { await server?.close(); });

async function render(component, props = {}) {
  const { default: Component } = await server.ssrLoadModule(`/src/${component}.jsx`);
  return renderToStaticMarkup(React.createElement(Component, props));
}

test('renders the actual target separately from quieter neighbors with scores and context control', async () => {
  const html = await render('components/ResultCard', { result: sample.results[0], timeZone: 'Asia/Kolkata' });
  assert.equal((html.match(/class="chat-row is-match"/g) || []).length, 1);
  assert.ok(html.includes(sample.results[0].matching_message.text));
  assert.ok(html.includes('Matching message'));
  assert.ok(html.includes(sample.results[0].search_score.toFixed(3)));
  assert.ok(html.includes('Show more context'));
  assert.ok(html.includes('aria-expanded="false"'));
  assert.ok(html.includes(sample.results[0].next_messages[0].text));
  assert.ok(!html.includes(sample.results[0].next_messages[2].text));
});

test('renders message text safely instead of executing markup', async () => {
  const result = structuredClone(sample.results[0]);
  result.matching_message.text = '<img src=x onerror=alert(1)>';
  const html = await render('components/ResultCard', { result, timeZone: 'Asia/Kolkata' });
  assert.ok(html.includes('&lt;img'));
  assert.ok(!html.includes('<img'));
});

test('renders person/time badges from backend interpretation', async () => {
  const html = await render('components/Interpretation', { metadata: sample.interpreted_query });
  assert.ok(html.includes('Person: Ananya Verma'));
  assert.ok(html.includes('Time: August 2026'));
  const unfiltered = { ...sample.interpreted_query, person: null, person_mode: 'none', start_date: null, end_date: null };
  const plain = await render('components/Interpretation', { metadata: unfiltered });
  assert.ok(!plain.includes('Person:'));
  assert.ok(!plain.includes('Time:'));
});

test('renders real corpus statistics and accessible search form without fake result cards', async () => {
  const corpus = await render('components/CorpusStats', { stats, state: 'ready' });
  assert.ok(corpus.includes('4,634'));
  assert.ok(corpus.includes('<strong>8</strong>'));
  assert.ok(corpus.includes('<strong>6</strong>'));
  const app = await render('App');
  assert.ok(app.includes('RecallChat'));
  assert.ok(app.includes('role="search"'));
  assert.ok(app.includes('for="search-input"'));
  assert.ok(!app.includes('class="result-card"'));
});
