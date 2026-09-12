import { useEffect, useRef, useState } from 'react';
import { fetchStats, searchChat } from './api/search.js';
import AboutSearch from './components/AboutSearch.jsx';
import CorpusStats from './components/CorpusStats.jsx';
import Icon from './components/Icon.jsx';
import Interpretation from './components/Interpretation.jsx';
import ResultCard from './components/ResultCard.jsx';

const EXAMPLES = [
  'When did we decide on Manali?',
  'What did Ishita say about the budget?',
  'What did we discuss last month?',
  'Which backend did we finally pick?',
];

export default function App() {
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [status, setStatus] = useState('idle');
  const [response, setResponse] = useState(null);
  const [error, setError] = useState('');
  const [stats, setStats] = useState(null);
  const [statsState, setStatsState] = useState('loading');
  const [statsAttempt, setStatsAttempt] = useState(0);
  const inputRef = useRef(null);
  const requestRef = useRef(null);
  const resultsRef = useRef(null);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    const timeout = setTimeout(() => controller.abort(), 8000);
    setStatsState('loading');
    fetchStats(controller.signal).then((data) => {
      if (active) { setStats(data); setStatsState('ready'); }
    }).catch(() => { if (active) setStatsState('error'); }).finally(() => clearTimeout(timeout));
    return () => { active = false; clearTimeout(timeout); controller.abort(); };
  }, [statsAttempt]);

  useEffect(() => {
    function focusSearch(event) {
      if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey &&
          !['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName) && !event.target.isContentEditable) {
        event.preventDefault(); inputRef.current?.focus();
      }
    }
    document.addEventListener('keydown', focusSearch);
    return () => { document.removeEventListener('keydown', focusSearch); requestRef.current?.abort(); requestRef.current = null; };
  }, []);

  async function submitSearch(value) {
    if (!value.trim()) { inputRef.current?.focus(); return; }
    requestRef.current?.abort();
    const controller = new AbortController();
    requestRef.current = controller;
    setSubmittedQuery(value); setStatus('loading'); setResponse(null); setError('');
    const timeout = setTimeout(() => controller.abort(), 45000);
    try {
      const data = await searchChat(value, controller.signal);
      if (requestRef.current !== controller) return;
      setResponse(data); setStatus('success');
      requestAnimationFrame(() => resultsRef.current?.focus({ preventScroll: true }));
    } catch (failure) {
      if (requestRef.current !== controller) return;
      setError(failure.name === 'AbortError' ? 'That search took longer than expected. Please try again.' : failure.message);
      setStatus('error');
    } finally {
      clearTimeout(timeout);
      if (requestRef.current === controller) requestRef.current = null;
    }
  }

  function chooseExample(example) { setQuery(example); submitSearch(example); }

  return <div className="app-shell">
    <a href="#search-input" className="skip-link">Skip to search</a>
    <header className="site-header">
      <a className="brand" href="#top" aria-label="RecallChat home"><span className="brand-mark"><Icon name="chat" size={23} /></span>RecallChat<span className="brand-period">.</span></a>
      <span className={`connection-indicator ${statsState}`}><span />{statsState === 'ready' ? 'Archive connected' : statsState === 'loading' ? 'Connecting to archive' : 'Archive unavailable'}</span>
    </header>
    <main id="top" className="main-content">
      <section className="hero" aria-labelledby="hero-title">
        <div className="hero-eyebrow"><span />LESS SCROLLING. MORE REMEMBERING.</div>
        <h1 id="hero-title">Search what your group<br className="desktop-break" /> <span>actually meant.</span></h1>
        <p className="hero-description">The trip plan. The final stack. That one message.<br />Find your way back to the conversation.</p>
        <div className="search-panel">
          <form className="search-form" onSubmit={(event) => { event.preventDefault(); submitSearch(query); }} role="search">
            <Icon name="search" size={23} />
            <label className="sr-only" htmlFor="search-input">Search your group chat</label>
            <input id="search-input" ref={inputRef} type="search" value={query} onChange={(event) => setQuery(event.target.value)} maxLength={2000} required autoComplete="off" placeholder="Ask a question. No exact words needed." aria-describedby="search-hint" />
            <kbd className="search-shortcut">/</kbd>
            <button className="search-button" type="submit" disabled={!query.trim() || status === 'loading'}>{status === 'loading' ? <><span className="spinner" />Searching</> : <>Search chat<Icon name="arrow" size={18} /></>}</button>
          </form>
          <p id="search-hint" className="search-hint"><Icon name="sparkle" size={13} />Ask in your own words. English or Hinglish, both welcome.</p>
        </div>
        <div className="examples"><span className="examples-label">TRY ASKING</span><div className="example-chips">{EXAMPLES.map((example) => <button type="button" key={example} onClick={() => chooseExample(example)}><span>{example}</span><Icon name="arrow" size={14} /></button>)}</div></div>
      </section>
      <CorpusStats stats={stats} state={statsState} onRetry={() => setStatsAttempt((value) => value + 1)} />
      <section className="search-results" aria-label="Search results" aria-busy={status === 'loading'}>
        {status === 'idle' && <div className="welcome-state"><span className="welcome-icon"><Icon name="chat" size={30} /></span><h2>Your next “oh right, that!” starts here.</h2><p>Ask a question above. We’ll bring back the original messages,<br className="desktop-break" /> with a little conversation around them.</p><span className="welcome-rule" /></div>}
        {status === 'loading' && <div className="loading-state"><p role="status"><span className="spinner" />Looking through the conversation…</p>{[1, 2].map((key) => <div className="skeleton-card" key={key} aria-hidden="true"><div /><div /><div /></div>)}</div>}
        {status === 'error' && <div className="error-state" role="alert"><Icon name="alert" size={27} /><h2>Couldn’t bring that conversation back.</h2><p>{error}</p><button type="button" className="secondary-button" onClick={() => submitSearch(submittedQuery)}>Try search again<Icon name="arrow" size={16} /></button></div>}
        {status === 'success' && response && <>
          <div className="results-heading" ref={resultsRef} tabIndex={-1}><div><p className="section-eyebrow">BACK FROM THE ARCHIVE</p><h2>{response.results.length ? `${response.results.length} message${response.results.length === 1 ? '' : 's'} to revisit` : 'No matching messages'}</h2></div><span className="latency"><Icon name="clock" size={15} />{Math.round(response.search_time_ms)} ms</span></div>
          <p className="searched-query">Results for “{response.query}”</p>
          <Interpretation metadata={response.interpreted_query} />
          <p className="sr-only" role="status">{response.results.length} results found in {Math.round(response.search_time_ms)} milliseconds.</p>
          {response.results.length ? <div className="result-list">{response.results.map((result) => <ResultCard key={`${response.query}-${result.matching_message.id}`} result={result} timeZone={response.interpreted_query.timezone} />)}</div> : <div className="empty-state"><Icon name="search" size={28} /><h3>No messages in that corner of the archive.</h3><p>Try a broader date range, another group member, or a few words about the topic.</p>{stats && <p className="empty-range">This archive covers {stats.date_range.start.slice(0, 10)} to {stats.date_range.end.slice(0, 10)}.</p>}<button type="button" className="text-button" onClick={() => inputRef.current?.focus()}>Edit your question<Icon name="arrow" size={15} /></button></div>}
          {response.results.length > 0 && <p className="results-note">A useful lead isn’t always the answer. Check the highlighted message and its context.</p>}
        </>}
      </section>
      <AboutSearch />
      <footer className="site-footer"><span>RecallChat <span aria-hidden="true">✳</span> Made for the “wait, what did we decide?”</span><span>Synthetic conversations. Real context.</span></footer>
    </main>
  </div>;
}
