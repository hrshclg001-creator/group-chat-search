import { useId, useState } from 'react';
import { initials, messageTime } from '../format.js';
import Icon from './Icon.jsx';

function ChatMessage({ message, matching = false, timeZone }) {
  const color = [...message.sender].reduce((sum, character) => sum + character.charCodeAt(0), 0) % 4;
  return <li className={`chat-row ${matching ? 'is-match' : 'is-context'}`}>
    <span className={`avatar avatar-${color}`} aria-hidden="true">{initials(message.sender)}</span>
    <div className="bubble">
      <div className="message-meta"><strong>{message.sender}</strong><time dateTime={message.timestamp}>{messageTime(message.timestamp, timeZone)}</time></div>
      {matching && <span className="match-label"><Icon name="sparkle" size={12} />Matching message</span>}
      <p className="message-text">{message.text}</p>
    </div>
  </li>;
}

export default function ResultCard({ result, timeZone }) {
  const [expanded, setExpanded] = useState(false);
  const contextId = useId();
  const previous = expanded ? result.previous_messages : result.previous_messages.slice(-1);
  const next = expanded ? result.next_messages : result.next_messages.slice(0, 1);
  const hiddenCount = Math.max(0, result.previous_messages.length - 1) + Math.max(0, result.next_messages.length - 1);
  return <article className="result-card" aria-label={`Result ${result.rank}, matching message from ${result.matching_message.sender}`}>
    <header className="result-card-header"><span className="result-number">CONVERSATION <b>{String(result.rank).padStart(2, '0')}</b></span><span className="relevance" title="Hybrid ranking score, not a confidence percentage"><span className="score-dot" />{result.search_score.toFixed(3)} <span>relevance</span></span></header>
    <ol className="conversation" id={contextId}>
      {previous.map((message) => <ChatMessage key={message.id} message={message} timeZone={timeZone} />)}
      <ChatMessage message={result.matching_message} matching timeZone={timeZone} />
      {next.map((message) => <ChatMessage key={message.id} message={message} timeZone={timeZone} />)}
    </ol>
    <footer className="result-card-footer">
      {hiddenCount > 0 ? <button type="button" className="context-toggle" onClick={() => setExpanded(!expanded)} aria-expanded={expanded} aria-controls={contextId}><Icon name={expanded ? 'chevron' : 'plus'} size={15} />{expanded ? 'Show less context' : 'Show more context'}{!expanded && <span>+{hiddenCount}</span>}</button> : <span className="context-complete">All available nearby context</span>}
      <span className="context-window">Within 30 minutes</span>
    </footer>
  </article>;
}
