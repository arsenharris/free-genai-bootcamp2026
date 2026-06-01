import React, {useMemo, useState} from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const exampleRequests = [
  'Find lyrics for Luis Fonsi Despacito',
  'Find lyrics for Enrique Iglesias Bailando',
  'Lyrics: Canto con mi corazón en la noche. La vida sigue con luz y amor.',
]

const fallbackTranslations = {
  amor: 'love',
  corazón: 'heart',
  corazon: 'heart',
  vida: 'life',
  noche: 'night',
  luz: 'light',
  canto: 'I sing',
  canción: 'song',
  cancion: 'song',
  contigo: 'with you',
  mundo: 'world',
  sol: 'sun',
  luna: 'moon',
}

function getVocabularyKey(item, index){
  return `${item.original || item.word || item.spanish || 'vocab'}-${index}`
}

function formatParts(parts){
  if(!Array.isArray(parts) || parts.length === 0) return 'No parts listed'
  return parts.map(part => {
    if(typeof part === 'string') return part
    const pronunciation = Array.isArray(part.pronunciation) ? part.pronunciation.join(', ') : part.pronunciation
    return [part.original, pronunciation].filter(Boolean).join(' - ')
  }).join('; ')
}

function extractLyricsFromRequest(requestText){
  const marker = requestText.toLowerCase().indexOf('lyrics:')
  if(marker >= 0){
    return requestText.slice(marker + 'lyrics:'.length).trim()
  }

  return [
    'Estas son letras de ejemplo para probar Song Vocab.',
    'Canto con mi corazón en la noche.',
    'La vida sigue con luz y amor.',
  ].join('\n')
}

function buildLocalResult(requestText){
  const lyrics = extractLyricsFromRequest(requestText)
  const stopwords = new Set(['el', 'la', 'los', 'las', 'un', 'una', 'de', 'que', 'y', 'en', 'a', 'mi', 'tu', 'su', 'con', 'por', 'para', 'no', 'sí', 'si'])
  const words = lyrics.toLowerCase().match(/[a-záéíóúüñ]+/gi) || []
  const seen = new Set()
  const vocabulary = []

  for(const word of words){
    if(word.length < 3 || stopwords.has(word) || seen.has(word)) continue
    seen.add(word)
    vocabulary.push({
      original: word,
      pronunciation: word,
      english: fallbackTranslations[word] || '',
      parts: [],
    })
  }

  return {
    song_id: 'local-demo-song',
    lyrics,
    vocabulary,
  }
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
      const requestOptions = {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message_request: requestText}),
      }
      let response
      try{
        response = await fetch('/api/agent', requestOptions)
      }catch(proxyError){
        response = await fetch(`${API_BASE_URL}/api/agent`, requestOptions)
      }
      const contentType = response.headers.get('content-type') || ''
      const data = contentType.includes('application/json')
        ? await response.json()
        : {error: await response.text()}
      if(!response.ok){
        throw new Error(data.detail || data.error || 'Song vocab request failed.')
      }
      setResult(data)
    }catch(err){
      setResult(buildLocalResult(requestText))
      setError(`Backend unavailable (${err.message}). Showing local demo extraction instead.`)
    }finally{
      setLoading(false)
    }
  }

  return (
    <div>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',gap:12,flexWrap:'wrap'}}>
        <h2>Song Vocab</h2>
        <div className="badge level-badge">Spanish</div>
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
                      <strong>{item.original || item.word || item.spanish || 'Unknown word'}</strong>
                      {item.pronunciation && <span className="badge">{Array.isArray(item.pronunciation) ? item.pronunciation.join(', ') : item.pronunciation}</span>}
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
