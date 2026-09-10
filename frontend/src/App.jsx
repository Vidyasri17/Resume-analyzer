import { useState, useRef } from 'react'
import axios from 'axios'

const API = ''

function ScoreRing({ score }) {
  const r = 52, c = 2 * Math.PI * r, pct = score / 100
  const color = score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : '#ef4444'
  return (
    <div style={{ position: 'relative', width: 120, height: 120 }}>
      <svg width={120} height={120} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={60} cy={60} r={r} stroke="#e5e7eb" strokeWidth={10} fill="none" />
        <circle cx={60} cy={60} r={r} stroke={color} strokeWidth={10} fill="none" strokeLinecap="round" strokeDasharray={c} strokeDashoffset={c * (1 - pct)} style={{ transition: 'stroke-dashoffset 0.8s ease' }} />
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <span style={{ fontSize: 28, fontWeight: 800, color }}>{score}</span>
        <span style={{ fontSize: 11, color: '#6b7280', fontWeight: 600 }}>/ 100</span>
      </div>
    </div>
  )
}

function Bar({ label, value }) {
  const color = value >= 80 ? '#10b981' : value >= 60 ? '#f59e0b' : '#ef4444'
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
        <span style={{ color: '#374151', fontWeight: 600 }}>{label}</span><span style={{ color, fontWeight: 700 }}>{value}%</span>
      </div>
      <div style={{ height: 8, background: '#e5e7eb', borderRadius: 99 }}>
        <div style={{ width: `${value}%`, height: '100%', background: color, borderRadius: 99, transition: 'width 0.6s' }} />
      </div>
    </div>
  )
}

export default function App() {
  const [jdFile, setJdFile] = useState(null)
  const [resumes, setResumes] = useState([])
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState(null)
  const [chatInput, setChatInput] = useState('')
  const [chatMsgs, setChatMsgs] = useState([{ role: 'assistant', text: 'Upload & analyze, then ask me anything! e.g. "Which candidate is best?" or "Why did Candidate 2 score lower?"' }])
  const [chatLoading, setChatLoading] = useState(false)
  const jdRef = useRef(null), resRef = useRef(null), detailRef = useRef(null)

  const onJd = e => { const f = e.target.files[0]; if (f) setJdFile(f) }
  const onRes = e => {
    const files = Array.from(e.target.files || [])
    setResumes(prev => [...prev, ...files])
    e.target.value = ''
  }
  const removeRes = i => setResumes(prev => prev.filter((_, x) => x !== i))

  const analyze = async () => {
    setError('')
    if (!jdFile) { setError('Please upload a Job Description'); return }
    if (resumes.length < 1) { setError('Please upload at least 1 resume'); return }
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('jd', jdFile)
      resumes.forEach(f => fd.append('resumes', f))
      const res = await axios.post(`${API}/api/analyze`, fd, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 120000 })
      setData(res.data)
      setSelected(res.data.results[0])
      setChatMsgs(m => [...m, { role: 'assistant', text: `Analyzed ${res.data.summary.candidates_analyzed} candidates. Top: ${res.data.summary.top_candidate} (${res.data.summary.highest_score}/100). Ask me to compare!` }])
      setTimeout(() => document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' }), 300)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Analysis failed')
    } finally { setLoading(false) }
  }

  const sendChat = async () => {
    if (!chatInput.trim() || !data) return
    const q = chatInput.trim()
    setChatInput('')
    setChatMsgs(m => [...m, { role: 'user', text: q }])
    setChatLoading(true)
    try {
      const res = await axios.post(`${API}/api/chat`, { message: q, analysis: data })
      setChatMsgs(m => [...m, { role: 'assistant', text: res.data.answer }])
    } catch (e) {
      setChatMsgs(m => [...m, { role: 'assistant', text: e.response?.data?.detail || 'Chat failed' }])
    } finally { setChatLoading(false) }
  }

  const fitLabel = s => s >= 80 ? 'Strong Match' : s >= 65 ? 'Good Fit' : s >= 50 ? 'Moderate' : 'Weak Match'
  const fitColor = s => s >= 80 ? '#065f46' : s >= 65 ? '#92400e' : s >= 50 ? '#9a3412' : '#991b1b'
  const fitBg = s => s >= 80 ? '#d1fae5' : s >= 65 ? '#fef3c7' : s >= 50 ? '#ffedd5' : '#fee2e2'

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc', fontFamily: 'Inter, system-ui, sans-serif', color: '#111827' }}>
      <header style={{ background: 'white', borderBottom: '1px solid #e5e7eb', position: 'sticky', top: 0, zIndex: 10 }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '14px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: 'linear-gradient(135deg,#4f46e5,#06b6d4)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 800 }}>AI</div>
            <div>
              <div style={{ fontWeight: 800, fontSize: 16 }}>AI Resume ATS Analyzer</div>
              <div style={{ fontSize: 12, color: '#6b7280' }}>Compare multiple candidates against a job description using AI</div>
            </div>
          </div>

        </div>
      </header>

      <main style={{ maxWidth: 1200, margin: '0 auto', padding: '24px 20px' }}>
        <div style={{ background: 'white', borderRadius: 16, border: '1px solid #e5e7eb', padding: 20, marginBottom: 20 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div onClick={() => jdRef.current?.click()} style={{ border: `2px dashed ${jdFile ? '#4f46e5' : '#d1d5db'}`, borderRadius: 12, padding: 20, background: jdFile ? '#eef2ff' : '#f9fafb', cursor: 'pointer', textAlign: 'center' }}>
              <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 6 }}>📄 Job Description</div>
              <div style={{ fontSize: 12, color: '#6b7280', marginBottom: 10 }}>PDF, DOCX, TXT • Drag & drop or browse</div>
              <input ref={jdRef} type="file" accept=".pdf,.docx,.txt" onChange={onJd} style={{ display: 'none' }} />
              {jdFile ? <span style={{ background: 'white', border: '1px solid #e5e7eb', padding: '6px 12px', borderRadius: 99, fontSize: 12, fontWeight: 600 }}>{jdFile.name} ✓</span> : <span style={{ background: '#4f46e5', color: 'white', padding: '8px 16px', borderRadius: 8, fontSize: 12, fontWeight: 700 }}>Browse files</span>}
            </div>

            <div style={{ border: `2px dashed ${resumes.length ? '#10b981' : '#d1d5db'}`, borderRadius: 12, padding: 20, background: resumes.length ? '#ecfdf5' : '#f9fafb', textAlign: 'center' }}>
              <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 6 }}>👥 Candidate Resumes ({resumes.length})</div>
              <div style={{ fontSize: 12, color: '#6b7280', marginBottom: 10 }}>Upload resumes • PDF, DOCX, TXT</div>
              <input ref={resRef} type="file" multiple accept=".pdf,.docx,.txt" onChange={onRes} style={{ display: 'none' }} />
              <button onClick={() => resRef.current?.click()} style={{ background: '#111827', color: 'white', padding: '8px 16px', borderRadius: 8, fontSize: 12, fontWeight: 700, border: 'none', cursor: 'pointer' }}>+ Add resumes</button>
              {resumes.length > 0 && <div style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap', gap: 6, justifyContent: 'center' }}>
                {resumes.map((f, i) => <span key={i} style={{ background: 'white', border: '1px solid #e5e7eb', padding: '4px 8px', borderRadius: 99, fontSize: 11, display: 'flex', alignItems: 'center', gap: 6 }}>{f.name} <button onClick={() => removeRes(i)} style={{ border: 'none', background: '#fee2e2', borderRadius: 99, width: 16, height: 16, cursor: 'pointer', fontSize: 10 }}>×</button></span>)}
              </div>}
              {resumes.length < 1 && <div style={{ fontSize: 11, color: '#ef4444', marginTop: 8 }}>Need at least 1 resume</div>}
            </div>
          </div>

          {error && <div style={{ marginTop: 12, background: '#fee2e2', border: '1px solid #fecaca', color: '#991b1b', padding: 10, borderRadius: 8, fontSize: 13 }}>{error}</div>}

          <button onClick={analyze} disabled={loading} style={{ marginTop: 16, width: '100%', padding: 14, borderRadius: 10, background: loading ? '#9ca3af' : 'linear-gradient(90deg,#4f46e5,#06b6d4)', color: 'white', fontWeight: 800, fontSize: 15, border: 'none', cursor: loading ? 'not-allowed' : 'pointer' }}>
            {loading ? '⏳ Analyzing candidates...' : '🚀 Analyze Candidates'}
          </button>
        </div>

        {data && (
          <div id="results">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(150px,1fr))', gap: 12, marginBottom: 16 }}>
              {[
                { k: 'Candidates', v: data.summary.candidates_analyzed },
                { k: 'Top Candidate', v: data.summary.top_candidate },
                { k: 'Highest Score', v: `${data.summary.highest_score}%` },
                { k: 'Average Match', v: `${data.summary.average_score}%` },
              ].map(s => (
                <div key={s.k} style={{ background: 'white', border: '1px solid #e5e7eb', borderRadius: 12, padding: 14, textAlign: 'center' }}>
                  <div style={{ fontSize: 11, color: '#6b7280', fontWeight: 700, textTransform: 'uppercase' }}>{s.k}</div>
                  <div style={{ fontSize: 18, fontWeight: 800, marginTop: 4 }}>{s.v}</div>
                </div>
              ))}
            </div>

            <div style={{ background: 'white', borderRadius: 12, border: '1px solid #e5e7eb', padding: 14, marginBottom: 16 }}>
              <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 8 }}>🏆 Ranking</div>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {data.summary.ranking.map(r => (
                  <span key={r.rank} style={{ padding: '6px 12px', borderRadius: 99, background: r.rank === 1 ? '#4f46e5' : '#f3f4f6', color: r.rank === 1 ? 'white' : '#111827', fontWeight: 700, fontSize: 12 }}>{r.rank}. {r.candidate_name} — {r.score}/100</span>
                ))}
              </div>
              <div style={{ fontSize: 11, color: '#6b7280', marginTop: 8 }}>JD skills: {data.summary.jd_skills.join(', ') || '—'}</div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: 16, alignItems: 'start' }}>
              <div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(260px,1fr))', gap: 12 }}>
                  {data.results.map(c => (
                    <div key={c.candidate_name} onClick={() => { setSelected(c); setTimeout(() => detailRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 80) }} style={{ background: 'white', border: `2px solid ${selected?.candidate_name === c.candidate_name ? '#4f46e5' : '#e5e7eb'}`, borderRadius: 14, padding: 14, cursor: 'pointer', boxShadow: selected?.candidate_name === c.candidate_name ? '0 4px 16px rgba(79,70,229,.15)' : 'none' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{ fontWeight: 800, fontSize: 13 }}>{c.candidate_name}</div>
                        <span style={{ background: fitBg(c.ats_score), color: fitColor(c.ats_score), padding: '2px 8px', borderRadius: 99, fontSize: 10, fontWeight: 800 }}>{fitLabel(c.ats_score)}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 10 }}>
                        <div style={{ width: 56, height: 56, borderRadius: 99, border: `4px solid ${c.ats_score >= 80 ? '#10b981' : c.ats_score >= 60 ? '#f59e0b' : '#ef4444'}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: 16 }}>{c.ats_score}</div>
                        <div style={{ fontSize: 11, color: '#6b7280' }}>
                          <div>{'★'.repeat(Math.round(c.ats_score / 20))}{'☆'.repeat(5 - Math.round(c.ats_score / 20))}</div>
                          <div style={{ marginTop: 2 }}>Skills {c.score_breakdown.skills}% • Exp {c.score_breakdown.experience}%</div>
                        </div>
                      </div>
                      <div style={{ marginTop: 10 }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: '#065f46', marginBottom: 4 }}>MATCHING ({c.matching_skills.length})</div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>{c.matching_skills.slice(0, 8).map(s => <span key={s} style={{ background: '#d1fae5', color: '#065f46', padding: '2px 7px', borderRadius: 99, fontSize: 11, fontWeight: 600 }}>{s}</span>)}{c.matching_skills.length === 0 && <span style={{ fontSize: 11, color: '#9ca3af' }}>No direct matches</span>}</div>
                      </div>
                      <div style={{ marginTop: 8 }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: '#991b1b', marginBottom: 4 }}>MISSING ({c.missing_required_skills.length + c.missing_preferred_skills.length})</div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>{[...c.missing_required_skills.slice(0, 4), ...c.missing_preferred_skills.slice(0, 2)].map(s => <span key={s} style={{ background: '#fee2e2', color: '#991b1b', padding: '2px 7px', borderRadius: 99, fontSize: 11, fontWeight: 600 }}>{s}</span>)}{c.missing_required_skills.length === 0 && c.missing_preferred_skills.length === 0 && <span style={{ fontSize: 11, color: '#9ca3af' }}>None</span>}</div>
                      </div>
                    </div>
                  ))}
                </div>

                {selected && (
                  <div ref={detailRef} id="candidate-detail" style={{ background: 'white', border: '1px solid #e5e7eb', borderRadius: 14, padding: 16, marginTop: 16, scrollMarginTop: 72 }}>
                    <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'center' }}>
                      <ScoreRing score={selected.ats_score} />
                      <div style={{ flex: 1, minWidth: 220 }}>
                        <div style={{ fontWeight: 800, fontSize: 16 }}>{selected.candidate_name}</div>
                        <div style={{ fontSize: 12, color: '#6b7280' }}>{selected.filename} • Rank #{selected.rank} • {fitLabel(selected.ats_score)}</div>
                        <div style={{ marginTop: 10, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                          <Bar label="Skills (50%)" value={selected.score_breakdown.skills} />
                          <Bar label="Experience (20%)" value={selected.score_breakdown.experience} />
                          <Bar label="Education (10%)" value={selected.score_breakdown.education} />
                          <Bar label="Keywords (10%)" value={selected.score_breakdown.keywords} />
                        </div>
                        <Bar label="Certifications (10%)" value={selected.score_breakdown.certifications} />
                      </div>
                    </div>

                    <div style={{ marginTop: 14, background: '#f8fafc', border: '1px solid #e5e7eb', borderRadius: 10, padding: 12 }}>
                      <div style={{ fontWeight: 700, fontSize: 12 }}>💡 Why this score?</div>
                      <div style={{ fontSize: 12, color: '#374151', marginTop: 4 }}>{selected.why_score}</div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 12 }}>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: 12, color: '#065f46' }}>✅ Matching Skills</div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 6 }}>{selected.matching_skills.map(s => <span key={s} style={{ background: '#10b981', color: 'white', padding: '4px 9px', borderRadius: 99, fontSize: 12, fontWeight: 600 }}>{s}</span>)}{selected.matching_skills.length===0 && <span style={{fontSize:12,color:'#9ca3af'}}>None</span>}</div>
                        <div style={{ marginTop: 10, fontWeight: 700, fontSize: 12 }}>Strengths</div>
                        <ul style={{ fontSize: 12, color: '#374151', paddingLeft: 16, marginTop: 4 }}>{selected.strengths.map((s,i)=><li key={i}>{s}</li>)}</ul>
                      </div>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: 12, color: '#991b1b' }}>⚠️ Missing — Required</div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 6 }}>{selected.missing_required_skills.map(s => <span key={s} style={{ background: '#ef4444', color: 'white', padding: '4px 9px', borderRadius: 99, fontSize: 12, fontWeight: 600 }}>{s}</span>)}{selected.missing_required_skills.length===0 && <span style={{fontSize:12,color:'#065f46'}}>None 🎉</span>}</div>
                        <div style={{ marginTop: 8, fontWeight: 700, fontSize: 12, color: '#92400e' }}>Preferred missing</div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 6 }}>{selected.missing_preferred_skills.map(s => <span key={s} style={{ background: '#f59e0b', color: 'white', padding: '4px 9px', borderRadius: 99, fontSize: 12, fontWeight: 600 }}>{s}</span>)}{selected.missing_preferred_skills.length===0 && <span style={{fontSize:12,color:'#9ca3af'}}>None</span>}</div>
                        <div style={{ marginTop: 10, fontWeight: 700, fontSize: 12 }}>Gaps</div>
                        <ul style={{ fontSize: 12, color: '#374151', paddingLeft: 16, marginTop: 4 }}>{selected.gaps.map((s,i)=><li key={i}>{s}</li>)}</ul>
                      </div>
                    </div>

                    <div style={{ marginTop: 14 }}>
                      <div style={{ fontWeight: 800, fontSize: 13 }}>📚 Recommended Learning</div>
                      {selected.course_recommendations.length===0 ? <div style={{fontSize:12,color:'#9ca3af',marginTop:6}}>No recommendations — great fit!</div> :
                        <div style={{ display: 'grid', gap: 8, marginTop: 8 }}>
                          {selected.course_recommendations.map(r=>(
                            <div key={r.skill} style={{ border: '1px solid #e5e7eb', borderRadius: 10, padding: 10, display:'flex', justifyContent:'space-between', gap:10 }}>
                              <div>
                                <div style={{ fontWeight: 700, fontSize: 12 }}><span style={{ background: r.priority==='High'?'#fee2e2':'#fef3c7', color: r.priority==='High'?'#991b1b':'#92400e', padding:'1px 6px', borderRadius:99, fontSize:10 }}>{r.priority}</span> {r.skill}</div>
                                <div style={{ fontSize:11, color:'#6b7280', marginTop:2 }}>{r.reason}</div>
                              </div>
                              <div style={{ textAlign:'right', minWidth:160 }}>
                                {r.recommendations.map(c=>(
                                  <div key={c.title} style={{ fontSize:11 }}>
                                    {c.url ? <a href={c.url} target="_blank" rel="noreferrer" style={{ color:'#4f46e5', fontWeight:600 }}>{c.title}</a> : <span style={{fontWeight:600}}>{c.title}</span>}
                                    <span style={{ color:'#6b7280' }}> • {c.platform} • {c.level}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      }
                    </div>

                    <div style={{ marginTop: 12, borderTop: '1px solid #e5e7eb', paddingTop:10 }}>
                      <div style={{ fontWeight:700, fontSize:12 }}>🗂️ All detected skills</div>
                      <div style={{ display:'flex', flexWrap:'wrap', gap:6, marginTop:6 }}>
                        {Object.entries(selected.categorized_skills).map(([cat, skills])=>(
                          <span key={cat} style={{ background:'#f3f4f6', padding:'4px 8px', borderRadius:8, fontSize:11 }}><b>{cat}:</b> {skills.join(', ')}</span>
                        ))}
                      </div>
                      <div style={{ fontSize:11, color:'#6b7280', marginTop:8 }}>Experience: {selected.experience_years || 'Not specified'} yrs • Education: {selected.education_summary || 'Not identified'}</div>
                    </div>
                  </div>
                )}
              </div>

              <div style={{ background: 'white', border: '1px solid #e5e7eb', borderRadius: 14, display: 'flex', flexDirection: 'column', height: 640, position: 'sticky', top: 64 }}>
                <div style={{ padding: 12, borderBottom: '1px solid #e5e7eb', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ width: 28, height: 28, borderRadius: 99, background: '#4f46e5', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: 14 }}>💬</span>
                  <div>
                    <div style={{ fontWeight: 800, fontSize: 13 }}>Chat with ATS</div>
                    <div style={{ fontSize: 11, color: '#6b7280' }}>Ask about candidates</div>
                  </div>
                </div>
                <div style={{ flex: 1, overflowY: 'auto', padding: 12, display: 'flex', flexDirection: 'column', gap: 8, background: '#f8fafc' }}>
                  {chatMsgs.map((m, i) => (
                    <div key={i} style={{ alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '85%', background: m.role === 'user' ? '#4f46e5' : 'white', color: m.role === 'user' ? 'white' : '#111827', border: '1px solid #e5e7eb', padding: '8px 10px', borderRadius: 12, fontSize: 12, whiteSpace: 'pre-wrap' }}>{m.text}</div>
                  ))}
                  {chatLoading && <div style={{ fontSize: 12, color: '#6b7280' }}>Thinking…</div>}
                </div>
                <div style={{ padding: 10, borderTop: '1px solid #e5e7eb', display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {['Which candidate is best?', 'Why did last candidate score lower?', 'Compare candidates', 'What is missing from '+(selected?.candidate_name||'top candidate')+'?'].map(q=>(
                    <button key={q} onClick={()=>{setChatInput(q); setTimeout(()=>document.getElementById('chat-send')?.click(),50)}} style={{ fontSize:10, padding:'4px 8px', borderRadius:99, background:'#f3f4f6', border:'1px solid #e5e7eb', cursor:'pointer' }}>{q}</button>
                  ))}
                </div>
                <div style={{ padding: 10, borderTop: '1px solid #e5e7eb', display: 'flex', gap: 8 }}>
                  <input value={chatInput} onChange={e => setChatInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendChat()} placeholder={data ? 'Ask about candidates...' : 'Analyze first…'} disabled={!data} style={{ flex: 1, padding: '8px 10px', borderRadius: 8, border: '1px solid #d1d5db', fontSize: 12 }} />
                  <button id="chat-send" onClick={sendChat} disabled={!data || chatLoading} style={{ padding: '8px 14px', borderRadius: 8, background: '#111827', color: 'white', fontWeight: 700, fontSize: 12, border: 'none', cursor: 'pointer' }}>Send</button>
                </div>
              </div>
            </div>
          </div>
        )}

        <div style={{ textAlign: 'center', fontSize: 11, color: '#9ca3af', marginTop: 24 }}>Built for hackathon demo • ATS scoring is explainable & deterministic • Never hallucinates skills</div>
      </main>
    </div>
  )
}
