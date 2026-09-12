import Icon from './Icon.jsx';

export default function AboutSearch() {
  return <details className="about-search">
    <summary><span><Icon name="sparkle" size={18} />About this search</span><Icon name="chevron" size={18} /></summary>
    <div className="about-content">
      <p className="about-intro">A few different clues help bring the conversation back.</p>
      <div className="about-grid">
        <div><span>01</span><h3>Meaning, beyond keywords</h3><p>Local semantic embeddings compare the meaning of your question with messages, even when the wording differs.</p></div>
        <div><span>02</span><h3>The words still matter</h3><p>Lexical TF-IDF search picks up names, phrases and partial word patterns, with some tolerance for typos.</p></div>
        <div><span>03</span><h3>Who said it, and when</h3><p>Metadata helps narrow clear person and date requests. Relative dates use September 1, 2026, the archive’s fixed reference date.</p></div>
        <div><span>04</span><h3>Check the message itself</h3><p>Nearby conversation helps find candidates. A local multilingual reranker then compares your question with each candidate message. The highlighted bubble is always the actual retrieved message.</p></div>
      </div>
      <p className="honesty-note"><Icon name="chat" size={18} />Recall isn’t perfect. A related conversation can still be the wrong answer—check the matching message and its context.</p>
    </div>
  </details>;
}
