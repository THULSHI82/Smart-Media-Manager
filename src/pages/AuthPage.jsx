import { useState } from 'react'
import { api, setSession } from '../lib/api'
import { linkHandler, navigate } from '../lib/navigation'

export default function AuthPage({ mode = 'login' }) {
  const registering = mode === 'register'
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'photographer' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await api(`/auth/${registering ? 'register' : 'login'}`, {
        method: 'POST',
        body: JSON.stringify(registering ? form : { email: form.email, password: form.password }),
      })
      setSession({ token: data.token, user: data.user })
      navigate(data.user.role === 'administrator' ? '/admin' : '/dashboard')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-canvas grid min-h-screen place-items-center p-5">
      <div className="w-full max-w-md rounded-3xl border border-[#ece7f7] bg-white p-8 shadow-xl shadow-violet-100/60">
        <a href="/" onClick={linkHandler('/')} className="text-sm font-semibold text-[#6747e8]">← Smart Media Manager</a>
        <h1 className="mt-5 text-3xl font-extrabold">{registering ? 'Create your account' : 'Welcome back'}</h1>
        <p className="mt-2 text-sm text-gray-500">Manage events, process photographs and retrieve personalised galleries.</p>
        {error && <div className="mt-5 rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{error}</div>}
        <form onSubmit={submit} className="mt-6 space-y-4">
          {registering && <input className="form-input" aria-label="Full name" autoComplete="name" placeholder="Full name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />}
          <input className="form-input" aria-label="Email address" autoComplete="email" type="email" placeholder="Email address" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          <input className="form-input" aria-label="Password" autoComplete={registering ? 'new-password' : 'current-password'} type="password" placeholder="Password (8+ characters, letters and numbers)" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
          {registering && (
            <select className="form-input" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
              <option value="photographer">Photographer</option>
              <option value="participant">Event participant</option>
            </select>
          )}
          <button disabled={loading} className="btn-primary w-full justify-center disabled:opacity-60">{loading ? 'Please wait…' : registering ? 'Register' : 'Sign in'}</button>
        </form>
        <p className="mt-6 text-center text-sm text-gray-500">
          {registering ? 'Already registered?' : 'Need an account?'}{' '}
          <a href={registering ? '/login' : '/register'} onClick={linkHandler(registering ? '/login' : '/register')} className="font-semibold text-[#6747e8]">
            {registering ? 'Sign in' : 'Register'}
          </a>
        </p>
      </div>
    </div>
  )
}
