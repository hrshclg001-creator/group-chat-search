import { formatTimeRange } from '../format.js';
import Icon from './Icon.jsx';

export default function Interpretation({ metadata }) {
  const time = formatTimeRange(metadata.start_date, metadata.end_date);
  const person = metadata.person_mode !== 'none' && metadata.person;
  return <section className="interpretation" aria-label="Query interpretation">
    <span className="interpretation-label">Understood as</span>
    <div className="interpretation-tags">
      <span className="tag"><Icon name="sparkle" size={14} />Semantic</span>
      {person && <span className="tag"><Icon name="people" size={14} />Person: {person}{metadata.person_mode === 'bonus' ? ' · preferred' : ''}</span>}
      {time && <span className="tag"><Icon name="calendar" size={14} />Time: {time}{metadata.hour_range ? ` · ${metadata.hour_range[0]}:00–${metadata.hour_range[1]}:00` : ''}</span>}
    </div>
    {(metadata.warnings || []).length > 0 && <p className="interpretation-warning">{metadata.warnings.join(' ')}</p>}
    {(metadata.explanations || []).some((reason) => reason.includes('event')) && <p className="interpretation-note">The event date is part of your question, not a filter on when messages were sent.</p>}
    {time && <p className="interpretation-note">Dates use the archive’s reference date: {metadata.reference_date}.</p>}
  </section>;
}
