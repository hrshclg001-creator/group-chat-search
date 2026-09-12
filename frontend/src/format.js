const calendarDate = (value) => new Date(`${value.slice(0, 10)}T00:00:00Z`);
const dateLabel = (value, options) => new Intl.DateTimeFormat('en-GB', { timeZone: 'UTC', ...options }).format(calendarDate(value));

export function formatTimeRange(start, end) {
  if (!start || !end) return null;
  const first = calendarDate(start), last = calendarDate(end);
  if (Number.isNaN(first.getTime()) || Number.isNaN(last.getTime())) return null;
  const sameMonth = first.getUTCFullYear() === last.getUTCFullYear() && first.getUTCMonth() === last.getUTCMonth();
  const lastDay = new Date(Date.UTC(last.getUTCFullYear(), last.getUTCMonth() + 1, 0)).getUTCDate();
  if (sameMonth && first.getUTCDate() === 1 && last.getUTCDate() === lastDay) return dateLabel(start, { month: 'long', year: 'numeric' });
  const options = { day: 'numeric', month: 'short', year: 'numeric' };
  if (start === end) return dateLabel(start, options);
  return `${dateLabel(start, options)} – ${dateLabel(end, options)}`;
}

export function monthSpan(start, end) {
  // Use the supplied corpus calendar dates, not the viewer's local timezone.
  const first = calendarDate(start), last = calendarDate(end);
  return (last.getUTCFullYear() - first.getUTCFullYear()) * 12 + last.getUTCMonth() - first.getUTCMonth() + 1;
}

export function messageTime(timestamp, timeZone = 'Asia/Kolkata') {
  return new Intl.DateTimeFormat('en-GB', {
    day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZone,
  }).format(new Date(timestamp));
}

export function initials(name) {
  return name.split(/\s+/).filter(Boolean).map((word) => word[0]).filter((_, index, all) => index === 0 || index === all.length - 1).join('');
}
