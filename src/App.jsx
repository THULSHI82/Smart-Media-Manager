import { useEffect, useState } from 'react'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import About from './components/About'
import Features from './components/Features'
import HowItWorks from './components/HowItWorks'
import Gallery from './components/Gallery'
import Footer from './components/Footer'
import AuthPage from './pages/AuthPage'
import Dashboard from './pages/Dashboard'
import EventsPage from './pages/EventsPage'
import UploadPage from './pages/UploadPage'
import SearchPage from './pages/SearchPage'
import AdminPage from './pages/AdminPage'
import PrivacyPage from './pages/PrivacyPage'
import NotFound from './pages/NotFound'
import { getSession } from './lib/api'
import { navigate } from './lib/navigation'

function Landing() {
  useEffect(() => {
    const observer = new IntersectionObserver((entries) => entries.forEach((entry) => entry.isIntersecting && entry.target.classList.add('visible')), { threshold: 0.1 })
    document.querySelectorAll('.fade-up').forEach((element) => observer.observe(element))
    return () => observer.disconnect()
  }, [])
  return <div className="min-h-screen overflow-x-hidden bg-[#fffaf5] text-[#2f2940]"><Navbar /><Hero /><About /><Features /><HowItWorks /><Gallery /><Footer /></div>
}

function Protected({ children, roles }) {
  const session = getSession()
  useEffect(() => { if (!session) navigate('/login') }, [session])
  if (!session) return null
  if (roles && !roles.includes(session.user?.role)) return <div className="grid min-h-screen place-items-center text-center"><div><h1 className="text-2xl font-bold">Access denied</h1><p className="mt-2 text-gray-500">Your account role cannot open this page.</p></div></div>
  return children
}

export default function App() {
  const [location, setLocation] = useState(`${window.location.pathname}${window.location.search}`)
  useEffect(() => {
    const update = () => setLocation(`${window.location.pathname}${window.location.search}`)
    window.addEventListener('popstate', update); window.addEventListener('smm-session', update)
    return () => { window.removeEventListener('popstate', update); window.removeEventListener('smm-session', update) }
  }, [])
  const path = location.split('?')[0]
  const uploadMatch = path.match(/^\/events\/([^/]+)\/upload$/)

  if (path === '/') return <Landing />
  if (path === '/login') return <AuthPage mode="login" />
  if (path === '/register') return <AuthPage mode="register" />
  if (path === '/search') return <SearchPage />
  if (path === '/privacy') return <PrivacyPage />
  if (path === '/dashboard') {
    const session = getSession()
    return session?.user?.role === 'administrator'
      ? <Protected roles={['administrator']}><AdminPage /></Protected>
      : <Protected roles={['photographer']}><Dashboard /></Protected>
  }
  if (path === '/events') return <Protected roles={['photographer', 'administrator']}><EventsPage /></Protected>
  if (uploadMatch) return <Protected roles={['photographer', 'administrator']}><UploadPage eventId={uploadMatch[1]} /></Protected>
  if (path === '/admin') return <Protected roles={['administrator']}><AdminPage /></Protected>
  return <NotFound />
}
