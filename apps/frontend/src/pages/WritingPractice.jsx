import React from 'react'

export default function WritingPractice(){
  return (
    <div>
      <h2>Writing Practice</h2>

      <div className="panel" style={{marginTop:12}}>
        <div className="card">
          <div style={{fontWeight:900}}>Topic: My Weekend</div>
          <div style={{marginTop:8}} className="muted">Write a short paragraph about what you did last weekend.</div>
        </div>

        <div style={{marginTop:12}}>
          <div style={{display:'flex',gap:8,flexWrap:'wrap'}}>
            <div className="badge">vocab: picnic</div>
            <div className="badge">vocab: relaxed</div>
          </div>

          <textarea className="writing-area" style={{marginTop:8}} />

          <div style={{display:'flex',gap:8,marginTop:8}}>
            <button className="btn">CHECK GRAMMAR</button>
            <button className="btn">IMPROVE TEXT</button>
            <button className="btn primary">SHOW EXAMPLE</button>
          </div>
        </div>
      </div>
    </div>
  )
}
