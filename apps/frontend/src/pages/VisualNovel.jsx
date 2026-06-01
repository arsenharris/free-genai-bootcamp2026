import React, {useEffect, useState} from 'react'

const BACKGROUNDS = {
  apartamento: 'apartment.jpg',
  apartment: 'apartment.jpg',
  cafe: 'cafe.jpg',
  classroom: 'classroom.jpg',
  'post-office': 'post-office.jpg',
  tienda: 'corner-store.jpg',
}

function spanishText(node){
  return node?.spanish || node?.japanese || node?.text || ''
}

function getSpeakerName(speakerId, mappings){
  if(!speakerId || speakerId === 'player') return 'You'
  return mappings.characterNames?.[speakerId] || speakerId
}

export default function VisualNovel(){
  const [scene, setScene] = useState(null)
  const [mappings, setMappings] = useState({characterNames: {}})
  const [nodeId, setNodeId] = useState(null)
  const [selectedResponse, setSelectedResponse] = useState(null)
  const [pendingNextId, setPendingNextId] = useState(null)
  const [showEnglish, setShowEnglish] = useState(true)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadScene(){
      setLoading(true)
      setError('')
      try{
        const [sceneRes, mappingsRes] = await Promise.all([
          fetch('/api/visual-novel/scenes/scene001'),
          fetch('/api/visual-novel/mappings'),
        ])
        const sceneData = await sceneRes.json()
        const mappingsData = await mappingsRes.json()

        if(!sceneData.success){
          throw new Error(sceneData.detail || 'Scene could not be loaded.')
        }

        if(!cancelled){
          setScene(sceneData.scene)
          setMappings(mappingsData.mappings || {characterNames: {}})
          setNodeId(sceneData.scene.startsAt || Object.keys(sceneData.scene.dialog || {})[0])
          setSelectedResponse(null)
          setPendingNextId(null)
          setHistory([])
        }
      }catch(err){
        if(!cancelled) setError(err.message)
      }finally{
        if(!cancelled) setLoading(false)
      }
    }

    loadScene()
    return () => {
      cancelled = true
    }
  }, [])

  const node = scene?.dialog?.[nodeId]
  const visibleNode = selectedResponse ? {
    speakerId: 'player',
    japanese: selectedResponse.japanese,
    english: selectedResponse.english,
    default_next_id: pendingNextId,
  } : node

  const backgroundFile = BACKGROUNDS[scene?.location_id] || 'apartment.jpg'
  const backgroundUrl = `/visual-novel-assets/assets/scenes/${backgroundFile}`
  const characterId = visibleNode?.appear || scene?.character_id
  const characterUrl = characterId ? `/visual-novel-assets/assets/characters/${characterId}.png` : null
  const speakerName = getSpeakerName(visibleNode?.speakerId || visibleNode?.speaker, mappings)

  function goTo(nextId){
    if(!nextId) return
    setSelectedResponse(null)
    setPendingNextId(null)
    setNodeId(nextId)
  }

  function choose(choice){
    setHistory(current => [
      ...current,
      {
        speaker: getSpeakerName(visibleNode?.speakerId || visibleNode?.speaker, mappings),
        spanish: spanishText(visibleNode),
        english: visibleNode?.english || '',
      },
      {
        speaker: 'You',
        spanish: choice.japanese,
        english: choice.english,
      },
    ].filter(item => item.spanish))
    setSelectedResponse(choice)
    setPendingNextId(choice.next_id || visibleNode?.default_next_id || null)
  }

  function continueDialog(){
    if(selectedResponse){
      goTo(pendingNextId)
      return
    }

    setHistory(current => [
      ...current,
      {
        speaker: getSpeakerName(visibleNode?.speakerId || visibleNode?.speaker, mappings),
        spanish: spanishText(visibleNode),
        english: visibleNode?.english || '',
      },
    ].filter(item => item.spanish))
    goTo(visibleNode?.default_next_id)
  }

  function restartScene(){
    setHistory([])
    goTo(scene.startsAt)
  }

  if(loading){
    return (
      <div>
        <h2>Visual Novel</h2>
        <div className="panel" style={{marginTop:12}}>Loading scene...</div>
      </div>
    )
  }

  if(error){
    return (
      <div>
        <h2>Visual Novel</h2>
        <div className="panel" style={{marginTop:12}}>{error}</div>
      </div>
    )
  }

  return (
    <div>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
        <h2>Visual Novel</h2>
        <div style={{display:'flex',gap:8,alignItems:'center',flexWrap:'wrap'}}>
          <button className="btn" onClick={()=>setShowEnglish(value => !value)}>{showEnglish ? 'Hide English' : 'Show English'}</button>
          <div className="badge">{scene?.title || 'Scene'}</div>
        </div>
      </div>

      <div className="vn-stage" style={{backgroundImage: `url(${backgroundUrl})`}}>
        {characterUrl && <img className="vn-character" src={characterUrl} alt={getSpeakerName(characterId, mappings)} />}
        <div className="vn-dialog">
          <div className="vn-speaker">{speakerName}</div>
          <p className="vn-spanish">{spanishText(visibleNode)}</p>
          {showEnglish && visibleNode?.english && <p className="vn-english">{visibleNode.english}</p>}
        </div>
      </div>

      <div className="panel" style={{marginTop:12}}>
        {selectedResponse ? (
          <button className="btn primary" onClick={continueDialog}>Continue</button>
        ) : visibleNode?.choices?.length ? (
          <div className="vn-choices">
            {visibleNode.choices.map((choice, index) => (
              <button className="tile-btn" key={`${choice.next_id}-${index}`} onClick={()=>choose(choice)}>
                <span>{choice.japanese}</span>
                {showEnglish && <span className="muted">{choice.english}</span>}
              </button>
            ))}
          </div>
        ) : visibleNode?.ends ? (
          <button className="btn primary" onClick={restartScene}>Restart Scene</button>
        ) : (
          <button className="btn primary" onClick={continueDialog}>Continue</button>
        )}
      </div>

      {scene?.languageLearning && (
        <div className="vn-learning">
          <div className="panel">
            <h3>Vocabulary</h3>
            <div className="vn-learning-grid">
              {(scene.languageLearning.vocabulary || []).map(item => (
                <div className="card" key={item.word}>
                  <strong>{item.word}</strong>
                  <p>{item.translation}</p>
                  {item.example && <p className="muted">{item.example}</p>}
                </div>
              ))}
            </div>
          </div>
          <div className="panel">
            <h3>Grammar & Culture</h3>
            {(scene.languageLearning.grammar || []).map(item => (
              <div className="card" style={{marginTop:8}} key={item.pattern}>
                <strong>{item.pattern}</strong>
                <p>{item.explanation}</p>
              </div>
            ))}
            {(scene.languageLearning.culturalNotes || []).map(item => (
              <div className="card" style={{marginTop:8}} key={item.title}>
                <strong>{item.title}</strong>
                <p>{item.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {history.length > 0 && (
        <details className="panel" style={{marginTop:12}}>
          <summary style={{fontWeight:900,cursor:'pointer'}}>Scene history</summary>
          <div className="vn-history">
            {history.map((item, index) => (
              <div className="card" key={`${item.speaker}-${index}`}>
                <strong>{item.speaker}</strong>
                <p>{item.spanish}</p>
                {showEnglish && item.english && <p className="muted">{item.english}</p>}
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}
