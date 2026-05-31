import React, {useState} from 'react'

export default function AudioOnly(){
  const [text, setText] = useState('Hola, ¿cómo estás?')
  const [gender, setGender] = useState('female')
  const [loading, setLoading] = useState(false)
  const [audioUrl, setAudioUrl] = useState(null)

  async function generate(){
    if(!text || !text.trim()) return alert('Enter text')
    setLoading(true)
    try{
      const payload = { Conversation: text, gender }
      const res = await fetch('/generate_audio', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
      const j = await res.json()
      if(j.success) setAudioUrl(j.url)
      else alert(JSON.stringify(j))
    }catch(err){ alert(err.message) }
    setLoading(false)
  }

  return (
    <div style={{maxWidth:800, margin:'0 auto'}}>
      <h1>Audio Test</h1>
      <p>Enter text and pick a voice gender, then click Generate.</p>
      <div style={{marginBottom:12}}>
        <textarea value={text} onChange={e=>setText(e.target.value)} rows={6} style={{width:'100%'}} />
      </div>
      <div style={{display:'flex', gap:12, alignItems:'center'}}>
        <label>Voice:
          <select value={gender} onChange={e=>setGender(e.target.value)} style={{marginLeft:8}}>
            <option value="female">Female</option>
            <option value="male">Male</option>
            <option value="announcer">Announcer</option>
          </select>
        </label>
        <button onClick={generate} disabled={loading}>{loading? 'Generating...':'Generate Audio'}</button>
      </div>

      {audioUrl && (
        <div style={{marginTop:16}}>
          <audio controls src={audioUrl} />
          <div style={{marginTop:8}}>File: <a href={audioUrl} target="_blank" rel="noreferrer">{audioUrl}</a></div>
        </div>
      )}
    </div>
  )
}
