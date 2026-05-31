import React, {useState} from 'react'

const beginnerPrompts = [
  {
    title: 'Introduce Yourself',
    level: 'A1',
    task: 'Write 4 short sentences about your name, nationality, city, and one thing you like.',
    starters: ['Me llamo...', 'Soy de...', 'Vivo en...', 'Me gusta...'],
    vocabulary: ['nombre', 'ciudad', 'país', 'gustar'],
  },
  {
    title: 'My Daily Routine',
    level: 'A1',
    task: 'Write 5 sentences about what you do in the morning.',
    starters: ['Me despierto a las...', 'Desayuno...', 'Voy a...', 'Estudio...'],
    vocabulary: ['mañana', 'desayuno', 'escuela', 'trabajo'],
  },
  {
    title: 'At the Cafe',
    level: 'A1',
    task: 'Write a short cafe order using polite Spanish.',
    starters: ['Quiero...', 'Para mí...', 'Por favor...', 'Gracias.'],
    vocabulary: ['café', 'té', 'agua', 'bocadillo'],
  },
  {
    title: 'My Weekend',
    level: 'A2',
    task: 'Write a short paragraph about what you did last weekend.',
    starters: ['El sábado...', 'Fui a...', 'Comí...', 'Fue...'],
    vocabulary: ['fin de semana', 'fui', 'comí', 'divertido'],
  },
]

const flashcardCategories = [
  'Food & Drink',
  'Animals',
  'Family & People',
  'Everyday Objects',
  'Places',
  'Clothing',
  'Weather',
  'Colours',
  'Numbers',
  'Body Parts',
  'Emotions & Feelings',
  'Common Verbs',
  'Common Adjectives',
  'Daily Routine',
  'Transportation',
  'Nature',
  'Travel',
  'Common Phrases',
  'Question Words',
  'Prepositions',
  'Directions & Location',
  'House & Rooms',
  'Furniture',
  'Kitchen Vocabulary',
  'Bathroom Vocabulary',
  'School Vocabulary',
  'Jobs & Professions',
  'Shopping',
  'Restaurant Vocabulary',
  'Technology',
  'Health & Illness',
  'Sports & Hobbies',
  'Time & Dates',
  'Days of the Week',
  'Months',
  'Seasons',
]

function SongVocabSpec(){
  return (
    <div className="spec-stack">
      <h3>Song Vocab</h3>
      <div className="card">
        <h4>Business Goal</h4>
        <p>Find lyrics off the internet for a target song in a specific language and produce vocabulary to be imported into the database.</p>
      </div>
      <div className="card">
        <h4>Technical Requirements</h4>
        <ul>
          <li>FastAPI</li>
          <li>Ollama via the Ollama Python SDK using Mistral 7B</li>
          <li>Instructor for structured JSON output</li>
          <li>SQLite3 for database storage</li>
          <li>duckduckgo-search to search for lyrics</li>
        </ul>
      </div>
      <div className="card">
        <h4>GetLyrics POST /api/agent</h4>
        <p>This endpoint goes to an agent using the ReAct framework so it can search the internet, find multiple possible lyric versions, extract the correct lyrics, and format the lyrics into vocabulary.</p>
        <p><strong>Tools available:</strong> tools/extract_vocabulary.py, tools/get_page_content.py, tools/search_web.py</p>
        <p><strong>Request:</strong> <code>message_request</code>, a string describing the song and/or artist.</p>
        <p><strong>Response:</strong> <code>lyrics</code> string and <code>vocabulary</code> list.</p>
      </div>
    </div>
  )
}

function FlashcardSpec({styleName}){
  return (
    <div className="spec-stack">
      <h3>Flashcard {styleName}</h3>
      <div className="card">
        <p>Create a comprehensive Spanish vocabulary flashcard system for beginner learners at A1-A2 level.</p>
        <p><strong>Generate 100 words for each category:</strong></p>
        <div className="tag-grid">
          {flashcardCategories.map(category => <span className="badge" key={category}>{category}</span>)}
        </div>
      </div>

      <div className="card">
        <h4>For Each Flashcard</h4>
        <p><strong>Front Side:</strong> Spanish word, definite article when applicable, and high-quality illustration.</p>
        <p><strong>Back Side:</strong> Spanish word, English translation, part of speech, gender, plural form, IPA pronunciation, simplified English pronunciation guide, category name, and A1 or A2 difficulty level.</p>
        <p><strong>Example Usage:</strong> one simple Spanish example sentence and its English translation.</p>
        <p><strong>Learning Support:</strong> three collocations, related word or synonym when appropriate, and opposite word when appropriate.</p>
      </div>

      <div className="card">
        <h4>Special Rules</h4>
        <p><strong>Verbs:</strong> include infinitive form, English meaning, present tense yo form, present tense él/ella form, one simple example sentence, and three common collocations.</p>
        <p><strong>Adjectives:</strong> include masculine form, feminine form, English meaning, opposite adjective, and one simple example sentence.</p>
      </div>

      <div className="card">
        <h4>Image Requirements</h4>
        <p>Generate a unique illustration for every flashcard. Use {styleName} style and keep the same style throughout the entire deck.</p>
        <p>Maintain a consistent colour palette, perspective, illustration technique, and visual identity across all categories. Use bright, memorable, beginner-friendly visuals with simple recognizable subjects, large central focus, minimal clutter, light background, and high contrast.</p>
        <p>No text, letters, words, numbers, captions, logos, or watermarks in images.</p>
      </div>

      <div className="card">
        <h4>Quality Requirements</h4>
        <p>Avoid duplicate words. Prioritize the most common and useful vocabulary first. Use modern everyday Spanish. Keep example sentences short and natural. Ensure vocabulary progresses from easier to more challenging within each category. Make all flashcards suitable for long-term spaced repetition learning.</p>
      </div>

      <div className="card">
        <h4>Output Format</h4>
        <p>Category | Spanish Word | Article | English Translation | Part of Speech | Gender | Plural | IPA | Pronunciation Guide | Example Sentence (Spanish) | Example Translation (English) | Collocation 1 | Collocation 2 | Collocation 3 | Related Word | Opposite Word | Difficulty Level | Image Prompt</p>
      </div>
    </div>
  )
}

export default function WritingPractice(){
  const [category, setCategory] = useState('beginner')
  const [selectedPrompt, setSelectedPrompt] = useState(beginnerPrompts[0])
  const [writingText, setWritingText] = useState('')

  return (
    <div>
      <h2>Writing Practice</h2>

      <div className="category-tabs" style={{marginTop:12}}>
        <button className={`btn ${category === 'beginner' ? 'primary' : ''}`} onClick={()=>setCategory('beginner')}>Beginner Writing</button>
        <button className={`btn ${category === 'song' ? 'primary' : ''}`} onClick={()=>setCategory('song')}>Song Vocab</button>
        <button className={`btn ${category === 'neo' ? 'primary' : ''}`} onClick={()=>setCategory('neo')}>Flashcard Neobrutal</button>
        <button className={`btn ${category === 'boho' ? 'primary' : ''}`} onClick={()=>setCategory('boho')}>Flashcard Boho</button>
      </div>

      {category === 'beginner' && (
        <div className="panel" style={{marginTop:12}}>
          <div className="writing-grid">
            <div>
              <label>
                Practice prompt
                <select value={selectedPrompt.title} onChange={e=>setSelectedPrompt(beginnerPrompts.find(prompt => prompt.title === e.target.value))}>
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
                <ul>
                  {selectedPrompt.starters.map(starter => <li key={starter}>{starter}</li>)}
                </ul>
              </div>
            </div>

            <div>
              <textarea className="writing-area" value={writingText} onChange={e=>setWritingText(e.target.value)} placeholder="Write your Spanish answer here." />
              <div style={{display:'flex',gap:8,marginTop:8,flexWrap:'wrap'}}>
                <button className="btn">CHECK GRAMMAR</button>
                <button className="btn">IMPROVE TEXT</button>
                <button className="btn primary">SHOW EXAMPLE</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {category === 'song' && (
        <div className="panel" style={{marginTop:12}}>
          <SongVocabSpec />
        </div>
      )}

      {category === 'neo' && (
        <div className="panel" style={{marginTop:12}}>
          <FlashcardSpec styleName="Neo-Brutalist" />
        </div>
      )}

      {category === 'boho' && (
        <div className="panel" style={{marginTop:12}}>
          <FlashcardSpec styleName="Boho" />
        </div>
      )}
    </div>
  )
}
