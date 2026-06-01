import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
plugins: [react()],
server: {
    port: 5173,
    proxy: {
    '/generate_audio': 'http://localhost:8000',
    '/audio': 'http://localhost:8000',
    '/generate_question': 'http://localhost:8000',
    '/get_feedback': 'http://localhost:8000',
    '/api/visual-novel': 'http://localhost:8000',
    '/visual-novel-assets': 'http://localhost:8000',
    '/api/agent': 'http://localhost:8001'
    }
}
})
