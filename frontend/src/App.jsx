import { useState } from 'react'
import './styles.css'

const API_URL = 'http://localhost:8000'

const styles = [
  { name: 'Cinematic', suffix: 'cinematic lighting' },
  { name: 'Anime', suffix: 'anime style' },
  { name: 'Realistic', suffix: 'photorealistic' },
  { name: 'Fantasy', suffix: 'fantasy art' }
]

export default function App() {
  const [prompt, setPrompt] = useState('')
  const [image, setImage] = useState(null)
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState([])
  const [selectedStyle, setSelectedStyle] = useState(styles[0])

  const generate = async () => {
    setLoading(true)
    const fullPrompt = `${prompt}, ${selectedStyle.suffix}`

    const res = await fetch(`${API_URL}/v1/jobs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': 'test-key'
      },
      body: JSON.stringify({ prompt: fullPrompt })
    })

    const data = await res.json()

    const interval = setInterval(async () => {
      const r = await fetch(`${API_URL}/v1/jobs/${data.job_id}`, {
        headers: { 'x-api-key': 'test-key' }
      })
      const d = await r.json()

      if (d.image_url) {
        setImage(d.image_url)
        setHistory(prev => [{ url: d.image_url, prompt: fullPrompt }, ...prev])
        setLoading(false)
        clearInterval(interval)
      }
    }, 2000)
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h2>Tensor Clone</h2>

        {styles.map(s => (
          <div key={s.name}
            className={`style-chip ${selectedStyle.name===s.name?'active':''}`}
            onClick={()=>setSelectedStyle(s)}>
            {s.name}
          </div>
        ))}
      </aside>

      <main className="main">
        <textarea
          className="prompt-box"
          value={prompt}
          onChange={(e)=>setPrompt(e.target.value)}
          placeholder="Describe your image..."
        />

        <button className="primary-btn" onClick={generate}>
          {loading ? 'Generating...' : 'Generate'}
        </button>

        <div className="image-stage">
          {image && <img src={image} />}
        </div>

        <div className="gallery-grid">
          {history.map((h,i)=>(
            <div key={i} className="gallery-card">
              <img src={h.url}/>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
