import React, {useEffect, useState} from 'react'
import sampleData from '../data/flashcards_sample.json'

function slugify(text){
    return text.toString().toLowerCase()
        .normalize('NFD').replace(/\p{Diacritic}/gu, '')
        .replace(/[^a-z0-9 ]/g,'')
        .trim().replace(/\s+/g,'-')
}

function Card({item}){
    const [flipped,setFlipped] = useState(false)
    const fileName = slugify(item.spanish) + '.svg'
    const imgSrc = `/flashcards_neo/${fileName}`
    return (
        <div className={`card ${flipped? 'flipped':''}`} onClick={()=>setFlipped(!flipped)}>
            {!flipped ? (
                <div className="card-front">
                    <div className="card-image" aria-hidden style={{background:'#fff',borderRadius:8,display:'flex',alignItems:'center',justifyContent:'center',height:120,boxShadow:'0 1px 4px rgba(0,0,0,0.08)'}}>
                        <img src={imgSrc} alt="" style={{maxHeight:110,maxWidth:'100%'}} onError={(e)=>{e.target.style.display='none'}} />
                        <div style={{fontSize:28,color:'#333'}} aria-hidden>{item.spanish}</div>
                    </div>
                    <div className="card-main">
                        <div className="card-title">{item.spanish} {item.article? <span className="article">({item.article})</span>:null}</div>
                        <div className="card-meta">{item.pos} • {item.difficulty}</div>
                    </div>
                </div>
            ) : (
                <div className="card-back">
                    <div style={{fontWeight:700,fontSize:18}}>{item.spanish} — {item.english}</div>
                    <div style={{marginTop:8}}><strong>POS:</strong> {item.pos} {item.gender? `• ${item.gender}`:''}</div>
                    {item.plural? <div><strong>Plural:</strong> {item.plural}</div>:null}
                    {item.ipa? <div><strong>IPA:</strong> {item.ipa}</div>:null}
                    {item.pronunciation? <div><strong>Pronunciation:</strong> {item.pronunciation}</div>:null}
                    <div style={{marginTop:8,fontStyle:'italic'}}>{item.example_es}</div>
                    <div style={{color:'#555'}}>{item.example_en}</div>
                </div>
            )}
        </div>
    )
}

export default function FlashcardNeo(){
    const [cards,setCards] = useState([])
    const [filter,setFilter] = useState('All')

    useEffect(()=>{
        // Try to load a complete dataset if available, otherwise use sample
        async function load(){
            try{
                // dynamic import if `flashcards_all.json` exists in same folder
                const mod = await import('../data/flashcards_all.json')
                // if the imported file is empty, fall back to sampleData
                if(Array.isArray(mod.default) && mod.default.length>0){
                    setCards(mod.default)
                }else{
                    setCards(sampleData)
                }
            }catch(e){
                setCards(sampleData)
            }
        }
        load()
    },[])

    const categories = Array.from(new Set(cards.map(c=>c.category))).sort()

    const visible = filter === 'All' ? cards : cards.filter(c=>c.category === filter)

    return (
        <div>
            <h2>Flashcard Neo</h2>
            <div style={{display:'flex',gap:12,alignItems:'center',marginBottom:12}}>
                <label style={{fontWeight:600}}>Category:</label>
                <select value={filter} onChange={e=>setFilter(e.target.value)}>
                    <option value="All">All</option>
                    {categories.map(cat=> <option key={cat} value={cat}>{cat}</option>)}
                </select>
                <div style={{marginLeft:'auto'}}>{visible.length} cards</div>
            </div>

            {visible.length === 0 ? (
                <div style={{padding:20,border:'2px dashed #ccc',borderRadius:8,background:'#fff'}}>
                    No cards found for the selected category. If you expect the full deck to appear, add the full JSON dataset to <strong>src/data/flashcards_all.json</strong>.
                </div>
            ) : (
                <div className="cards-grid">
                    {visible.map((item,idx)=> (
                        <Card key={idx} item={item} />
                    ))}
                </div>
            )}
        </div>
    )
}
