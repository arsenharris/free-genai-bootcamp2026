import React from 'react'

export default function VisualNovel(){
  return (
    <div>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
        <h2>Visual Novel</h2>
        <div className="badge">Scene 1</div>
      </div>

      <div className="panel" style={{marginTop:12}}>
        <div className="card" style={{minHeight:180}}>
          <p style={{fontSize:18}}>“The café smelled of warm bread and rain.”</p>
        </div>

        <div style={{marginTop:12,display:'flex',flexDirection:'column',gap:8}}>
          <button className="tile-btn">☕ Order coffee</button>
          <button className="tile-btn">🍵 Order tea</button>
          <button className="tile-btn">🚪 Leave café</button>
        </div>
      </div>
    </div>
  )
}
