import assert from 'node:assert/strict';
import { test } from 'node:test';
import { formatTimeRange, initials, messageTime, monthSpan } from '../src/format.js';

test('formats whole months, exact days and partial ranges without consulting today', () => {
  assert.equal(formatTimeRange('2026-08-01', '2026-08-31'), 'August 2026');
  assert.equal(formatTimeRange('2024-02-01', '2024-02-29'), 'February 2024');
  assert.equal(formatTimeRange('2026-08-31', '2026-08-31'), '31 Aug 2026');
  assert.equal(formatTimeRange('2026-04-21', '2026-04-30'), '21 Apr 2026 – 30 Apr 2026');
  assert.equal(formatTimeRange(null, null), null);
});

test('derives inclusive corpus month count across calendar years', () => {
  assert.equal(monthSpan('2026-03-01T07:05:00+05:30', '2026-08-31T23:50:00+05:30'), 6);
  assert.equal(monthSpan('2025-12-01', '2026-01-31'), 2);
});

test('formats message timestamps in archive timezone, including midnight boundaries', () => {
  assert.match(messageTime('2026-08-30T20:00:00Z', 'Asia/Kolkata'), /31 Aug 2026.*01:30/);
});

test('uses participant initials without substituting displayed names', () => {
  assert.equal(initials('Ananya Verma'), 'AV');
  assert.equal(initials('Aarav'), 'A');
});
