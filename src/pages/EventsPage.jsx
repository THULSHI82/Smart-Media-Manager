import { useEffect, useState } from 'react'
import AppShell from '../components/AppShell'
import { api } from '../lib/api'
import { linkHandler } from '../lib/navigation'
import Icon from '../components/Icon'

const emptyForm = { title: '', description: '', event_date: '', location: '', is_public: false, retention_days: 90, face_indexing_enabled: true, unclaimed_embedding_days: 30 }

export default function EventsPage() {
  const [events, setEvents] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [qr, setQr] = useState(null)

  async function load() {
    try { const data = await api('/events'); setEvents(data.events || []) } catch (err) { setError(err.message) }
  }
  useEffect(() => { load() }, [])

  async function create(event) {
    event.preventDefault(); setError(''); setMessage('')
    try {
      const data = await api('/events', { method: 'POST', body: JSON.stringify(form) })
      setMessage(`Event created. Access code: ${data.event.access_code}`)
      setForm(emptyForm); load()
    } catch (err) { setError(err.message) }
  }

  async function showQr(eventId) {
    try { setQr(await api(`/events/${eventId}/qr`)) } catch (err) { setError(err.message) }
  }

  return (
    <AppShell title="Event Management" subtitle="Create event-specific galleries with private access codes, retention boundaries and QR access.">
      {message && <div className="alert-success">{message}</div>}
      {error && <div className="alert-error">{error}</div>}
      <div className="grid gap-6 xl:grid-cols-[380px_1fr]">
        <form onSubmit={create} className="panel h-fit space-y-4">
          <h2 className="text-lg font-bold">Create Event</h2>
          <input className="form-input" placeholder="Event title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
          <textarea className="form-input min-h-24" placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <input className="form-input" type="date" value={form.event_date} onChange={(e) => setForm({ ...form, event_date: e.target.value })} />
          <input className="form-input" placeholder="Location" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
          <label className="block text-sm font-medium text-gray-600">Retention period (days)<input className="form-input mt-2" type="number" min="1" max="3650" value={form.retention_days} onChange={(e) => setForm({ ...form, retention_days: Number(e.target.value) })} /></label>
          <label className="block text-sm font-medium text-gray-600">Unclaimed face-vector retention (days)<input className="form-input mt-2" type="number" min="1" max="365" value={form.unclaimed_embedding_days} onChange={(e) => setForm({ ...form, unclaimed_embedding_days: Number(e.target.value) })} /></label>
          <label className="flex items-center gap-3 text-sm text-gray-600"><input type="checkbox" checked={form.face_indexing_enabled} onChange={(e) => setForm({ ...form, face_indexing_enabled: e.target.checked })} /> Enable face indexing for this event</label>
          <label className="flex items-center gap-3 text-sm text-gray-600"><input type="checkbox" checked={form.is_public} onChange={(e) => setForm({ ...form, is_public: e.target.checked })} /> Public event (private is recommended)</label>
          <button className="btn-primary w-full justify-center">Create Event</button>
        </form>

        <section className="space-y-4">
          {events.map((event) => (
            <article key={event.id} className="panel">
              <div className="flex flex-col justify-between gap-5 md:flex-row md:items-start">
                <div>
                  <div className="flex flex-wrap items-center gap-3"><h2 className="text-lg font-bold">{event.title}</h2><span className="rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-semibold text-indigo-700">{event.is_public ? 'Public' : 'Private'}</span></div>
                  <p className="mt-2 text-sm text-gray-500">{event.description || 'No description'} </p>
                  <div className="mt-4 flex flex-wrap gap-4 text-xs text-gray-500"><span className="inline-flex items-center gap-1.5"><Icon name="location" className="h-4 w-4" />{event.location || 'Not specified'}</span><span className="inline-flex items-center gap-1.5"><Icon name="calendar" className="h-4 w-4" />{event.event_date || 'Not specified'}</span><span className="inline-flex items-center gap-1.5"><Icon name="image" className="h-4 w-4" />{event.photo_count || 0} photos</span></div>
                  <div className="mt-3 text-sm">Access code: <b className="tracking-widest">{event.access_code}</b></div>
                </div>
                <div className="flex flex-wrap gap-2">
                  <a href={`/events/${event.id}/upload`} onClick={linkHandler(`/events/${event.id}/upload`)} className="btn-primary">Upload Photos</a>
                  <a href={`/search?event=${event.id}&code=${event.access_code}`} onClick={linkHandler(`/search?event=${event.id}&code=${event.access_code}`)} className="btn-outline">Test Selfie Search</a>
                  <button type="button" onClick={() => showQr(event.id)} className="btn-outline">QR Access</button>
                </div>
              </div>
            </article>
          ))}
          {!events.length && <div className="panel text-sm text-gray-500">No events have been created.</div>}
        </section>
      </div>
      {qr && <div className="fixed inset-0 z-50 grid place-items-center bg-slate-900/60 p-5"><div className="w-full max-w-md rounded-3xl bg-white p-7 text-center"><h2 className="text-xl font-bold">Event QR Access</h2>{qr.qr_data_url ? <img src={qr.qr_data_url} className="mx-auto mt-5 h-56 w-56" /> : <div className="mt-5 rounded-xl bg-amber-50 p-4 text-sm text-amber-700">Install the Python qrcode package to render the QR image.</div>}<div className="mt-4 break-all text-xs text-gray-500">{qr.access_url}</div><div className="mt-3 text-sm">Access code: <b className="tracking-widest">{qr.access_code}</b></div><button onClick={() => setQr(null)} className="btn-primary mt-5">Close</button></div></div>}
    </AppShell>
  )
}
