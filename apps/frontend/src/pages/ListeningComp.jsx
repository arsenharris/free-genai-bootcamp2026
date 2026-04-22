import React, {useState} from 'react'

export default function ListeningComp(){
  const [jsonText, setJsonText] = useState('{"Conversation":"Hola, ¿cómo estás?", "gender":"female"}')
  const [audioUrl, setAudioUrl] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e){
    e && e.preventDefault()
    let payload
    try{ payload = JSON.parse(jsonText) } catch(err){ alert('Invalid JSON'); return }
    setLoading(true)
    try{
      const res = await fetch('/generate_audio', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
      const j = await res.json()
      if(j.success){ setAudioUrl(j.url) } else { alert(JSON.stringify(j)) }
    }catch(err){ alert(err.message) }
    setLoading(false)
  }

  return (
    <div>
      <h2>Listening Comprehension — Test</h2>
      <form onSubmit={handleSubmit}>
        <textarea value={jsonText} onChange={e=>setJsonText(e.target.value)} rows={8} cols={80} />
        <br />
        <button type="submit" disabled={loading}>{loading? 'Generating...':'Generate Audio'}</button>
      </form>
      {audioUrl && (
        <div style={{marginTop:12}}>
          <audio controls src={audioUrl} />
          <div>URL: <a href={audioUrl} target="_blank" rel="noreferrer">{audioUrl}</a></div>
        </div>
      )}
    </div>
  )
}
