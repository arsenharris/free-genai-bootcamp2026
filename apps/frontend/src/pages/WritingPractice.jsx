import React, {useMemo, useState} from 'react'

const beginnerPrompts = [
  {
    title: 'Introduce Yourself',
    level: 'A1',
    task: 'Write 4 short sentences about your name, nationality, city, and one thing you like.',
    goal: 4,
    starters: ['Me llamo...', 'Soy de...', 'Vivo en...', 'Me gusta...'],
    vocabulary: ['nombre', 'ciudad', 'país', 'gustar'],
    example: 'Me llamo Lycia. Soy de Australia. Vivo en Perth. Me gusta aprender español.',
    sentenceBank: ['Me llamo Ana.', 'Soy de Australia.', 'Vivo en Perth.', 'Me gusta aprender español.'],
  },
  {
    title: 'My Daily Routine',
    level: 'A1',
    task: 'Write 5 sentences about what you do in the morning.',
    goal: 5,
    starters: ['Me despierto a las...', 'Desayuno...', 'Voy a...', 'Estudio...'],
    vocabulary: ['mañana', 'desayuno', 'escuela', 'trabajo'],
    example: 'Me despierto a las siete. Desayuno pan y café. Voy a la escuela por la mañana. Estudio español. Después voy al trabajo.',
    sentenceBank: ['Me despierto a las siete.', 'Desayuno pan y fruta.', 'Voy a la escuela por la mañana.', 'Estudio español.', 'Después voy al trabajo.'],
  },
  {
    title: 'At the Cafe',
    level: 'A1',
    task: 'Write a short cafe order using polite Spanish.',
    goal: 4,
    starters: ['Quiero...', 'Para mí...', 'Por favor...', 'Gracias.'],
    vocabulary: ['café', 'té', 'agua', 'bocadillo'],
    example: 'Buenos días. Para mí, un café y un bocadillo, por favor. También quiero agua. Gracias.',
    sentenceBank: ['Buenos días.', 'Para mí, un café, por favor.', 'También quiero agua.', 'Gracias.'],
  },
  {
    title: 'My Weekend',
    level: 'A2',
    task: 'Write a short paragraph about what you did last weekend.',
    goal: 4,
    starters: ['El sábado...', 'Fui a...', 'Comí...', 'Fue...'],
    vocabulary: ['fin de semana', 'fui', 'comí', 'divertido'],
    example: 'El sábado fui al centro con mi amiga. Comí tapas en un restaurante pequeño. El domingo estudié español y vi una película. Fue un fin de semana divertido.',
    sentenceBank: ['El sábado fui al centro.', 'Fui a un restaurante con mi amiga.', 'Comí tapas.', 'Fue un fin de semana divertido.'],
  },
]

const accentFixes = {
  cafe: 'café',
  pais: 'país',
  manana: 'mañana',
  sabado: 'sábado',
  comi: 'comí',
}

function countSentences(text){
  const matches = text.trim().match(/[^.!?]+[.!?]+/g)
  if(matches) return matches.length
  return text.trim() ? text.split(/\n+/).filter(Boolean).length : 0
}

function getWords(text){
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .match(/[a-záéíóúñü]+/gi) || []
}

function capitalizeSentence(sentence){
  const trimmed = sentence.trim()
  if(!trimmed) return ''
  return trimmed.charAt(0).toUpperCase() + trimmed.slice(1)
}

function applyAccentFixes(text){
  return text.replace(/\b(cafe|pais|manana|sabado|comi)\b/gi, match => {
    const fixed = accentFixes[match.toLowerCase()] || match
    return match[0] === match[0].toUpperCase() ? fixed.charAt(0).toUpperCase() + fixed.slice(1) : fixed
  })
}

function polishText(text, prompt){
  const normalized = applyAccentFixes(text)
    .replace(/\bi am\b/gi, 'soy')
    .replace(/\bmy name is\b/gi, 'me llamo')
    .replace(/\bi like\b/gi, 'me gusta')
    .replace(/\bplease\b/gi, 'por favor')
    .replace(/\bthanks\b/gi, 'gracias')

  const sentences = normalized
    .split(/(?<=[.!?])\s+|\n+/)
    .map(sentence => sentence.trim())
    .filter(Boolean)
    .map(sentence => {
      const withPunctuation = /[.!?]$/.test(sentence) ? sentence : `${sentence}.`
      return capitalizeSentence(withPunctuation)
    })

  const nextSentences = [...sentences]
  prompt.sentenceBank.forEach(sentence => {
    if(nextSentences.length < prompt.goal && !nextSentences.some(existing => existing.toLowerCase() === sentence.toLowerCase())){
      nextSentences.push(sentence)
    }
  })

  return nextSentences.join(' ')
}

function buildFeedback(text, prompt){
  const trimmed = text.trim()
  if(!trimmed){
    return {
      status: 'Start with one short Spanish sentence, then use the sentence starters to build the rest.',
      items: ['Write your answer in the text box first.', `Target: ${prompt.goal} sentences.`],
      score: 0,
    }
  }

  const words = getWords(trimmed)
  const sentenceCount = countSentences(trimmed)
  const plainText = words.join(' ')
  const usedVocabulary = prompt.vocabulary.filter(word => {
    const plainWord = getWords(word)[0]
    return plainWord && plainText.includes(plainWord)
  })
  const usedStarters = prompt.starters.filter(starter => {
    const root = starter.replace('...', '').replace('.', '').toLowerCase()
    return trimmed.toLowerCase().includes(root)
  })

  const items = []
  if(sentenceCount >= prompt.goal){
    items.push(`Good length: ${sentenceCount} sentences.`)
  } else {
    items.push(`Add ${prompt.goal - sentenceCount} more sentence${prompt.goal - sentenceCount === 1 ? '' : 's'} to reach the prompt goal.`)
  }

  if(usedStarters.length){
    items.push(`Starter phrases used: ${usedStarters.join(', ')}`)
  } else {
    items.push('Try one starter phrase to make the answer sound more complete.')
  }

  if(usedVocabulary.length){
    items.push(`Vocabulary included: ${usedVocabulary.join(', ')}`)
  } else {
    items.push(`Add one target word, for example: ${prompt.vocabulary[0]}.`)
  }

  if(/\b(cafe|pais|manana|sabado|comi)\b/i.test(trimmed)){
    items.push('Accent check: some words may need accents, such as café, país, mañana, sábado, or comí.')
  }

  if(/\bsoy en\b/i.test(trimmed)){
    items.push('Grammar note: use "soy de" for origin, not "soy en".')
  }

  if(/\bme gusta(n)?\b/i.test(trimmed)){
    items.push('Nice use of gustar. For one thing use "me gusta"; for plural things use "me gustan".')
  }

  const score = Math.min(100, Math.round(
    (Math.min(sentenceCount / prompt.goal, 1) * 45) +
    (Math.min(usedVocabulary.length / Math.max(prompt.vocabulary.length, 1), 1) * 30) +
    (Math.min(usedStarters.length / 2, 1) * 25)
  ))

  return {
    status: score >= 80 ? 'Strong draft' : score >= 50 ? 'Good start' : 'Keep building',
    items,
    score,
  }
}

export default function WritingPractice(){
  const [selectedPrompt, setSelectedPrompt] = useState(beginnerPrompts[0])
  const [writingText, setWritingText] = useState('')
  const [feedback, setFeedback] = useState(null)
  const [improvedText, setImprovedText] = useState('')
  const [showExample, setShowExample] = useState(false)

  const stats = useMemo(() => ({
    words: getWords(writingText).length,
    sentences: countSentences(writingText),
    characters: writingText.length,
  }), [writingText])

  function choosePrompt(title){
    const nextPrompt = beginnerPrompts.find(prompt => prompt.title === title) || beginnerPrompts[0]
    setSelectedPrompt(nextPrompt)
    setFeedback(null)
    setImprovedText('')
    setShowExample(false)
  }

  function checkGrammar(){
    setFeedback(buildFeedback(writingText, selectedPrompt))
    setShowExample(false)
  }

  function improveText(){
    const nextText = polishText(writingText || selectedPrompt.example, selectedPrompt)
    setImprovedText(nextText)
    setFeedback(buildFeedback(nextText, selectedPrompt))
    setShowExample(false)
  }

  function insertStarter(starter){
    const phrase = starter.replace('...', ' ')
    setWritingText(current => `${current}${current.trim() ? '\n' : ''}${phrase}`)
    setFeedback(null)
    setImprovedText('')
  }

  return (
    <div>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',gap:12,flexWrap:'wrap'}}>
        <h2>Writing Practice</h2>
        <div className="badge level-badge">{selectedPrompt.level}</div>
      </div>

      <div className="panel" style={{marginTop:12}}>
        <div className="writing-grid">
          <div>
            <label>
              Practice prompt
              <select value={selectedPrompt.title} onChange={e=>choosePrompt(e.target.value)}>
                {beginnerPrompts.map(prompt => <option key={prompt.title} value={prompt.title}>{prompt.title}</option>)}
              </select>
            </label>
            <div className="card" style={{marginTop:12}}>
              <div style={{fontWeight:900}}>Topic: {selectedPrompt.title}</div>
              <div className="badge" style={{marginTop:8}}>{selectedPrompt.level}</div>
              <div style={{marginTop:8}} className="muted">{selectedPrompt.task}</div>
            </div>
            <div style={{display:'flex',gap:8,flexWrap:'wrap',marginTop:12}}>
              {selectedPrompt.vocabulary.map(word => <div className="badge" key={word}>vocab: {word}</div>)}
            </div>
            <div className="card" style={{marginTop:12}}>
              <strong>Sentence starters</strong>
              <div className="starter-list">
                {selectedPrompt.starters.map(starter => (
                  <button className="starter-chip" key={starter} type="button" onClick={()=>insertStarter(starter)}>
                    {starter}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div>
            <textarea
              className="writing-area"
              value={writingText}
              onChange={e=>{
                setWritingText(e.target.value)
                setFeedback(null)
                setImprovedText('')
              }}
              placeholder="Write your Spanish answer here."
            />
            <div className="writing-stats" aria-live="polite">
              <span>{stats.words} words</span>
              <span>{stats.sentences}/{selectedPrompt.goal} sentences</span>
              <span>{stats.characters} characters</span>
            </div>
            <div className="writing-actions">
              <button className="btn" type="button" onClick={checkGrammar}>CHECK GRAMMAR</button>
              <button className="btn" type="button" onClick={improveText}>IMPROVE TEXT</button>
              <button className="btn primary" type="button" onClick={()=>{ setShowExample(value => !value); setImprovedText('') }}>
                {showExample ? 'HIDE EXAMPLE' : 'SHOW EXAMPLE'}
              </button>
              <button className="btn" type="button" onClick={()=>{ setWritingText(''); setFeedback(null); setImprovedText(''); setShowExample(false) }}>CLEAR</button>
            </div>

            {feedback && (
              <div className="writing-result" style={{marginTop:12}}>
                <div className="writing-result-header">
                  <strong>{feedback.status}</strong>
                  <span className="badge">{feedback.score}%</span>
                </div>
                <ul>
                  {feedback.items.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}
                </ul>
              </div>
            )}

            {improvedText && (
              <div className="writing-result" style={{marginTop:12}}>
                <strong>Improved draft</strong>
                <p>{improvedText}</p>
                <button className="btn success" type="button" onClick={()=>setWritingText(improvedText)}>USE THIS DRAFT</button>
              </div>
            )}

            {showExample && (
              <div className="writing-result" style={{marginTop:12}}>
                <strong>Example answer</strong>
                <p>{selectedPrompt.example}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
