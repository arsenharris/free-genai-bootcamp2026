import React, {useMemo, useState} from 'react'

const exampleRequests = [
  'Find lyrics for Luis Fonsi Despacito',
  'Find lyrics for Enrique Iglesias Bailando',
]

function getVocabularyKey(item, index){
  return `${item.kanji || item.word || item.romaji || 'vocab'}-${index}`
}

function formatParts(parts){
  if(!Array.isArray(parts) || parts.length === 0) return 'No parts listed'
  return parts.map(part => {
    if(typeof part === 'string') return part
    const romaji = Array.isArray(part.romaji) ? part.romaji.join(', ') : part.romaji
    return [part.kanji, romaji].filter(Boolean).join(' - ')
  }).join('; ')
}

export default function SongVocab(){
  const [messageRequest, setMessageRequest] = useState(exampleRequests[0])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const vocabulary = useMemo(() => {
    if(!result?.vocabulary) return []
    return Array.isArray(result.vocabulary) ? result.vocabulary : []
  }, [result])

  async function submitRequest(event){
    event.preventDefault()
    const requestText = messageRequest.trim()
    if(!requestText){
      setError('Enter a song and artist first.')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try{
      const response = await fetch('/api/agent', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message_request: requestText}),
      })
      const data = await response.json()
      if(!response.ok){
        throw new Error(data.detail || data.error || 'Song vocab request failed.')
      }
      setResult(data)
    }catch(err){
      setError(err.message)
    }finally{
      setLoading(false)
    }
  }

  return (
    <div>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',gap:12,flexWrap:'wrap'}}>
        <h2>Song Vocab</h2>
        <div className="badge level-badge">Japanese</div>
      </div>

      <div className="panel" style={{marginTop:12}}>
        <form className="song-search" onSubmit={submitRequest}>
          <label>
            Song request
            <input
              value={messageRequest}
              onChange={event=>setMessageRequest(event.target.value)}
              placeholder="Find lyrics for artist and song title"
            />
          </label>
          <button className="btn primary big-btn" type="submit" disabled={loading}>
            {loading ? <span className="loading">SEARCHING...</span> : 'GET LYRICS'}
          </button>
        </form>

        <div className="example-row" aria-label="Example song requests">
          {exampleRequests.map(example => (
            <button className="starter-chip" type="button" key={example} onClick={()=>setMessageRequest(example)}>
              {example}
            </button>
          ))}
        </div>

        {error && (
          <div className="card song-error" style={{marginTop:12}}>
            <strong>Request failed</strong>
            <p>{error}</p>
          </div>
        )}

        {result && (
          <div className="song-results">
            <div className="song-summary">
              <div className="card">
                <strong>Song ID</strong>
                <p>{result.song_id}</p>
              </div>
              <div className="card">
                <strong>Vocabulary</strong>
                <p>{vocabulary.length} words found</p>
              </div>
            </div>

            <div className="song-layout">
              <div className="card">
                <h3>Lyrics</h3>
                <pre className="lyrics-text">{result.lyrics}</pre>
              </div>

              <div className="vocab-list">
                <h3>Vocabulary</h3>
                {vocabulary.length === 0 && <div className="card muted">No vocabulary returned yet.</div>}
                {vocabulary.map((item, index) => (
                  <div className="card vocab-card" key={getVocabularyKey(item, index)}>
                    <div className="vocab-card-head">
                      <strong>{item.kanji || item.word || 'Unknown word'}</strong>
                      {item.romaji && <span className="badge">{item.romaji}</span>}
                    </div>
                    {item.english && <p>{item.english}</p>}
                    <div className="muted">{formatParts(item.parts)}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
