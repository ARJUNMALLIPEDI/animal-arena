import { Route, Routes } from 'react-router-dom'
import { Navbar } from './components/common/Navbar'
import { DisclaimerBanner } from './components/common/DisclaimerBanner'
import { Home } from './pages/Home'
import { AnimalDatabase } from './pages/AnimalDatabase'
import { TournamentPage } from './pages/TournamentPage'
import { Dashboard } from './pages/Dashboard'

function App() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <DisclaimerBanner />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/animals" element={<AnimalDatabase />} />
          <Route path="/tournament" element={<TournamentPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </main>
      <footer className="border-t border-arena-border/60 py-6 text-center text-xs text-arena-muted">
        Animal Arena — a hypothetical, entertainment simulation. Not scientific fact.
      </footer>
    </div>
  )
}

export default App
