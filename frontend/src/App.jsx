import { useState } from 'react'

const API_URL = 'http://localhost:8000'

export default function App() {
  const [prompt, setPrompt] = useState('')
  const [image, setImage] = useState(null)
  const [loading, setLoading] = useState(false)
  const [jobId, setJobId] = useState(null)

  const generate = async () => {
    setLoading(true)
    const res = await fetch(`${API_URL}/v1/jobs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': 'test-key'
      },
      body: JSON.stringify({ prompt })
    })

    const data = await res.json()
    setJobId(data.job_id)

    poll(data.job_id)
  }

  const poll = async (id) => {
    const interval = setInterval(async () => {
      const res = await fetch(`${API_URL}/v1/jobs/${id}`, {
        headers: { 'x-api-key': 'test-key' }
      })
      const data = await res.json()

      if (data.image_url) {
        setImage(data.image_url)
        setLoading(false)
        clearInterval(interval)
      }
    }, 2000)
  }

  return (
    <div style={{ padding: 20, fontFamily: 'Arial' }}>
      <h1>Tensor Clone</h1>

      <textarea
        placeholder="Describe your image..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        style={{ width: '100%', height: 100 }}
      />

      <button onClick={generate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate'}
      </button>

      {image && (
        <div>
          <h3>Result:</h3>
          <img src={image} style={{ maxWidth: '100%' }} />
        </div>
      )}
    </div>
  )
}
