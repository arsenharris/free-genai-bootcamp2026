import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import ListeningComp from './pages/ListeningComp'
import VisualNovel from './pages/VisualNovel'
import WritingPractice from './pages/WritingPractice'
import './styles.css'

export default function App(){
    return (
        <div className="app-container">
            <div className="topbar">
                <div style={{display:'flex',gap:12,alignItems:'center'}}>
                    <div className="app-title">Free GenAI Language Lab</div>
                    <div className="badge level-badge">beta</div>
                </div>
                <div style={{display:'flex',gap:8,alignItems:'center'}}>
                    <button className="profile-btn">LY</button>
                </div>
            </div>

            <div className="layout">
                <div className="sidebar">
                    <Link to="/" className="link-as-tile">
                        <div className="tile-btn"><span className="emoji">🎧</span><span>Listening</span></div>
                    </Link>
                    <Link to="/visual" className="link-as-tile">
                        <div className="tile-btn"><span className="emoji">📖</span><span>Visual Novel</span></div>
                    </Link>
                    <Link to="/writing" className="link-as-tile">
                        <div className="tile-btn"><span className="emoji">✍️</span><span>Writing</span></div>
                    </Link>
                </div>

                <div className="main">
                    <Routes>
                        <Route path="/" element={<ListeningComp/>} />
                        <Route path="/visual" element={<VisualNovel/>} />
                        <Route path="/writing" element={<WritingPractice/>} />
                    </Routes>
                </div>
            </div>
        </div>
    )
}
