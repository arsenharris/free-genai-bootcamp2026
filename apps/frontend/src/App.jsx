import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import ListeningComp from './pages/ListeningComp'
import VisualNovel from './pages/VisualNovel'
import WritingPractice from './pages/WritingPractice'

export default function App(){
return (
    <div style={{padding:20,fontFamily:'Arial'}}>
    <h1>Free GenAI Frontend</h1>
    <nav style={{marginBottom:20}}>
        <Link to="/">Listening Comp</Link> | 
        <Link to="/visual"> Visual Novel</Link> | 
        <Link to="/writing"> Writing Practice</Link>
    </nav>
    <Routes>
        <Route path="/" element={<ListeningComp/>} />
        <Route path="/visual" element={<VisualNovel/>} />
        <Route path="/writing" element={<WritingPractice/>} />
    </Routes>
    </div>
)
}
