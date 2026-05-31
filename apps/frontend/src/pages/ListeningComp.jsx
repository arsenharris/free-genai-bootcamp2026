import React, {useState, useRef} from 'react'

const TOPICS = [
  { value: 'restaurant', label: 'Restaurant' },
  { value: 'cafe', label: 'Cafe' },
  { value: 'airport', label: 'Airport' },
  { value: 'hotel', label: 'Hotel' },
  { value: 'shopping', label: 'Shopping' },
  { value: 'travel', label: 'Travel' },
  { value: 'school', label: 'School' },
  { value: 'directions', label: 'Directions' },
]

function questionKey(question){
  if(!question) return ''
  return [
    question.Introduction || '',
    question.Situation || '',
    question.Conversation || '',
    question.Question || '',
    ...(question.Options || []),
  ].join('|').toLowerCase()
}

export default function ListeningComp(){
  const [topic, setTopic] = useState('restaurant')
  const [section, setSection] = useState(2)
  const [question, setQuestion] = useState(null)
  const [audioUrl, setAudioUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const [audioLoading, setAudioLoading] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [feedback, setFeedback] = useState(null)
  const [tab, setTab] = useState('listening')
  const [writingText, setWritingText] = useState('')
  const audioRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const seenQuestionsRef = useRef(new Set())
  const [recording, setRecording] = useState(false)
  const [recordedUrl, setRecordedUrl] = useState(null)

  async function generateQuestion(){
    setLoading(true)
    try{
      let lastResponse = null
      for(let attempt = 0; attempt < 4; attempt += 1){
        const res = await fetch('/generate_question', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({section_num: section, topic})})
        const j = await res.json()
        lastResponse = j
        if(!j.success) break

        const key = questionKey(j.question)
        if(!seenQuestionsRef.current.has(key) || seenQuestionsRef.current.size > 20){
          seenQuestionsRef.current.add(key)
          setQuestion(j.question)
          setFeedback(null)
          setAudioUrl(null)
          setIsPlaying(false)
          if(audioRef.current){
            audioRef.current.pause()
            audioRef.current.removeAttribute('src')
            audioRef.current.load()
          }
          setLoading(false)
          return
        }
      }
      alert(lastResponse?.error || 'No new question available yet. Try another topic.')
    }catch(err){ alert(err.message) }
    setLoading(false)
  }

  async function toggleConversation(){
    if(!question) return alert('Generate a question first')
    if(audioRef.current && audioUrl && isPlaying){
      audioRef.current.pause()
      setIsPlaying(false)
      return
    }

    setAudioLoading(true)
    try{
      let nextAudioUrl = audioUrl
      if(!nextAudioUrl){
        const res = await fetch('/generate_audio', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(question)})
        const j = await res.json()
        if(j.success){
          nextAudioUrl = j.url
          setAudioUrl(j.url)
        } else {
          alert(JSON.stringify(j))
          setAudioLoading(false)
          return
        }
      }

      if(audioRef.current){
        if(audioRef.current.src !== new URL(nextAudioUrl, window.location.href).href){
          audioRef.current.src = nextAudioUrl
        }
        await audioRef.current.play()
        setIsPlaying(true)
      }
    }catch(err){ alert(err.message) }
    setAudioLoading(false)
  }

  async function submitAnswer(i){
    if(!question) return
    setLoading(true)
    try{
      const res = await fetch('/get_feedback', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({question, selected_answer: i})})
      const j = await res.json()
      if(j.success){ setFeedback(j.feedback) } else { alert(JSON.stringify(j)) }
    }catch(err){ alert(err.message) }
    setLoading(false)
  }

  function startRecording(){
    setRecordedUrl(null)
    navigator.mediaDevices.getUserMedia({audio:true}).then(stream =>{
      const mr = new MediaRecorder(stream)
      const chunks = []
      mr.ondataavailable = e => chunks.push(e.data)
      mr.onstop = () => {
        const blob = new Blob(chunks, {type: 'audio/webm'})
        const url = URL.createObjectURL(blob)
        setRecordedUrl(url)
      }
      mediaRecorderRef.current = mr
      mr.start()
      setRecording(true)
    }).catch(err=> alert('Microphone access denied'))
  }

  function stopRecording(){
    const mr = mediaRecorderRef.current
    if(mr){
      mr.stop()
      setRecording(false)
    }
  }

  return (
    <div className="listening-page">
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
        <h2>Listening Comprehension</h2>
        <div className="badge level-badge">A1</div>
      </div>

      <div className="controls">
        <label>Topic: <select value={topic} onChange={e=>setTopic(e.target.value)}>
          {TOPICS.map(item => <option key={item.value} value={item.value}>{item.label}</option>)}
        </select></label>
        <label>Question style: <select value={section} onChange={e=>setSection(Number(e.target.value))}>
          <option value={2}>Dialogue comprehension</option>
          <option value={3}>Situation question</option>
        </select></label>
        <button className="btn primary big-btn" onClick={generateQuestion} disabled={loading}>{loading? <span className="loading">GENERATING…</span> : 'GENERATE LESSON'}</button>
      </div>

      {tab === 'listening' && question && (
        <div className="panel">
          {question.Introduction && <div className="card"><strong>Intro:</strong> {question.Introduction}</div>}
          {question.Situation && <div className="card" style={{marginTop:8}}><strong>Situation:</strong> {question.Situation}</div>}
          {question.Conversation && <div className="card" style={{marginTop:8}}><strong>Conversation:</strong> {question.Conversation}</div>}

          <div style={{display:'flex',alignItems:'center',gap:12,marginTop:12}}>
            <button className="play-btn btn primary alt" onClick={toggleConversation} disabled={audioLoading}>
              {audioLoading ? 'LOADING' : isPlaying ? 'PAUSE' : 'PLAY'}
            </button>
            <audio
              ref={audioRef}
              src={audioUrl || undefined}
              onPlay={()=>setIsPlaying(true)}
              onPause={()=>setIsPlaying(false)}
              onEnded={()=>setIsPlaying(false)}
            />
            <div style={{marginLeft:'auto'}}>
              <button className="btn" onClick={()=>{ /* placeholder for transcript toggle */ }} >SHOW TRANSCRIPT</button>
            </div>
          </div>

          <div className="question" style={{marginTop:12,fontWeight:800}}><strong>Question:</strong> {question.Question}</div>

          <div className="options">
            {question.Options && question.Options.map((opt, idx)=> (
              <div key={idx} className={`option-card`} onClick={()=>submitAnswer(idx+1)}>
                <div style={{fontWeight:900}}>Option {idx+1}</div>
                <div>{opt}</div>
              </div>
            ))}
          </div>

          <div style={{display:'flex',gap:8,marginTop:12}}>
            <button className="btn success" onClick={()=>{/* check answers placeholder */}}>CHECK ANSWERS</button>
            <button className="btn" onClick={()=>{/* next lesson placeholder */}}>NEXT LESSON</button>
          </div>

          {feedback && (
            <div className="card" style={{marginTop:12}}>
              <div><strong>Correct:</strong> {String(feedback.correct)}</div>
              <div><strong>Explanation:</strong> {feedback.explanation}</div>
              <div><strong>Correct answer:</strong> {feedback.correct_answer}</div>
            </div>
          )}
        </div>
      )}

      {tab === 'writing' && (
        <div className="panel">
          <h3>Writing Practice</h3>
          <div className="card" style={{marginTop:8}}>
            {question ? (
              <div>
                {question.Conversation && <div><strong>Conversation:</strong> {question.Conversation}</div>}
                {question.Situation && <div><strong>Situation:</strong> {question.Situation}</div>}
              </div>
            ) : (
              <div className="muted">Generate a question to see a prompt here.</div>
            )}
          </div>
          <textarea className="writing-area" value={writingText} onChange={e=>setWritingText(e.target.value)} rows={8} />
          <div style={{marginTop:8}}>
            <button className="btn" onClick={()=>{ const blob = new Blob([writingText], {type:'text/plain'}); const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='writing.txt'; a.click(); }}>Save Writing</button>
          </div>
        </div>
      )}

      {tab === 'speaking' && (
        <div className="panel">
          <h3>Listening & Speaking</h3>
          <p>Play the conversation, then record yourself answering or repeating.</p>
          <div style={{display:'flex',gap:8,alignItems:'center'}}>
            <button className="btn" onClick={toggleConversation} disabled={audioLoading}>{isPlaying ? 'Pause Conversation' : 'Play Conversation'}</button>
          </div>
          <div style={{marginTop:12}}>
            {!recording && <button className="btn" onClick={startRecording}>Start Recording</button>}
            {recording && <button className="btn" onClick={stopRecording}>Stop Recording</button>}
            {recordedUrl && (<div style={{marginTop:8}}><audio controls src={recordedUrl} /></div>)}
          </div>
        </div>
      )}
    </div>
  )
}
