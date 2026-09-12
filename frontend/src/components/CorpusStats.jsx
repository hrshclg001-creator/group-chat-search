import { formatTimeRange, monthSpan } from '../format.js';
import Icon from './Icon.jsx';

export default function CorpusStats({ stats, state, onRetry }) {
  return <section className="corpus-panel" aria-label="Corpus statistics">
    <div className="corpus-heading"><span className="archive-icon"><Icon name="people" /></span><div><h2>One group. A lot of memories.</h2><p>A fictional student chat, with very real group-chat energy.</p></div><span className="synthetic-label">SYNTHETIC ARCHIVE</span></div>
    {state === 'error' ? <div className="stats-error"><span>Couldn’t load archive details.</span><button type="button" className="text-button" onClick={onRetry}>Try again</button></div> : <div className="stats-grid" aria-busy={state === 'loading'}>
      <div><strong>{stats ? stats.message_count.toLocaleString('en-IN') : <span className="stat-skeleton" />}</strong><span>messages</span></div>
      <div><strong>{stats ? stats.participant_count : <span className="stat-skeleton" />}</strong><span>participants</span></div>
      <div><strong>{stats ? monthSpan(stats.date_range.start, stats.date_range.end) : <span className="stat-skeleton" />}</strong><span>months of conversation</span></div>
    </div>}
    {stats && <p className="archive-dates"><Icon name="calendar" size={13} />{formatTimeRange(stats.date_range.start.slice(0, 10), stats.date_range.end.slice(0, 10))}</p>}
  </section>;
}
