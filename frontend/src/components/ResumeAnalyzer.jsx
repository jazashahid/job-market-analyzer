import { useState } from 'react'
import { analyzeResume } from '../services/api.js'

const SCORE_COLORS = {
  high:   { ring: '#7FA882', bg: '#D1E3D3' },
  mid:    { ring: '#C4A96E', bg: '#F0E4CC' },
  low:    { ring: '#C4A09D', bg: '#EDD8D6' },
}

function scoreColor(score) {
  if (score >= 65) return SCORE_COLORS.high
  if (score >= 35) return SCORE_COLORS.mid
  return SCORE_COLORS.low
}

export default function ResumeAnalyzer() {
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    setIsLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await analyzeResume(text.trim())
      setResult(res.data)
    } catch (err) {
      setError(
        err.response?.data?.detail ??
        'Analysis failed. Make sure you have fetched job listings first (the analyzer needs trending skills from the DB).'
      )
    } finally {
      setIsLoading(false)
    }
  }

  const canAnalyze = text.trim().length >= 50 && !isLoading

  return (
    <div className="resume-grid">
      {/* ── Left: input ── */}
      <div className="card resume-input-card">
        <div className="card-title">Your Résumé</div>
        <p className="resume-hint">
          Paste your full résumé text. Claude will compare it against the top trending skills
          in the job market database and identify gaps.
        </p>
        <textarea
          className="resume-textarea"
          placeholder="Paste your résumé here…"
          value={text}
          onChange={e => setText(e.target.value)}
        />
        <button
          className="btn btn-primary btn-full"
          onClick={handleAnalyze}
          disabled={!canAnalyze}
        >
          {isLoading ? 'Analyzing with Claude…' : 'Analyze Skills Gap'}
        </button>
        {error && (
          <div className="banner banner-error" style={{ marginTop: 12 }}>
            {error}
          </div>
        )}
      </div>

      {/* ── Right: results ── */}
      <div className="card">
        {!result && !isLoading && (
          <div className="result-empty">
            <span className="result-empty-icon">◎</span>
            <p>Your skills gap report will appear here.</p>
            <p className="text-muted" style={{ fontSize: 12, maxWidth: 280 }}>
              Fetch some job listings first, then paste your résumé and click Analyze.
            </p>
          </div>
        )}

        {isLoading && (
          <div className="result-empty">
            <span className="result-empty-icon" style={{ fontSize: 24, opacity: 0.5 }}>⟳</span>
            <p>Analyzing with Claude…</p>
            <p className="text-muted" style={{ fontSize: 12 }}>This usually takes 5–10 seconds.</p>
          </div>
        )}

        {result && <ResultPanel result={result} />}
      </div>
    </div>
  )
}

function ResultPanel({ result }) {
  const { ring, bg } = scoreColor(result.match_score)

  return (
    <div className="result">
      {/* Score + summary */}
      <div className="result-score-row">
        <div
          className="score-ring"
          style={{
            background: `conic-gradient(${ring} ${result.match_score}%, ${bg} 0)`,
          }}
        >
          {/* White inner circle for donut effect */}
          <div style={{
            position: 'absolute',
            inset: 7,
            borderRadius: '50%',
            background: '#fff',
          }} />
          <span className="score-number" style={{ position: 'relative', zIndex: 1 }}>
            {result.match_score}
          </span>
          <span className="score-sub" style={{ position: 'relative', zIndex: 1 }}>
            / 100
          </span>
        </div>
        <p className="result-summary">{result.summary}</p>
      </div>

      {/* Skills you have / need */}
      <div className="skills-gap-grid">
        <div>
          <div className="gap-label gap-label--have">✓ Skills You Have</div>
          <div className="skill-tags">
            {result.skills_you_have.length
              ? result.skills_you_have.map(s => (
                  <span key={s} className="skill-tag skill-tag--have">{s}</span>
                ))
              : <span className="skill-tag--none">None matched</span>
            }
          </div>
        </div>
        <div>
          <div className="gap-label gap-label--need">✗ Skills to Develop</div>
          <div className="skill-tags">
            {result.skills_you_need.slice(0, 12).map(s => (
              <span key={s} className="skill-tag skill-tag--need">{s}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div>
        <div className="recs-label">Recommendations</div>
        <ol className="recs-list">
          {result.recommendations.map((rec, i) => (
            <li key={i}>{rec}</li>
          ))}
        </ol>
      </div>
    </div>
  )
}
