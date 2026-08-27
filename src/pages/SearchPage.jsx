import { useEffect, useState } from 'react'
import AppShell from '../components/AppShell'
import { API_URL, searchWithSelfie } from '../lib/api'

export default function SearchPage() {
  const query = new URLSearchParams(window.location.search)
  const [eventId, setEventId] = useState(query.get('event') || '')
  const [code, setCode] = useState(query.get('code') || '')
  const [event, setEvent] = useState(null)
  const [selfie, setSelfie] = useState(null)
  const [consent, setConsent] = useState(false)
  const [matches, setMatches] = useState([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function lookup() {
    if (!eventId) return
    setError('')
    try {
      const response = await fetch(`${API_URL}/events/${eventId}?access_code=${encodeURIComponent(code)}`)
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || 'Event not found.')
      setEvent(data.event)
    } catch (err) { setEvent(null); setError(err.message) }
  }
  useEffect(() => { if (eventId) lookup() }, [])

  async function submit(e) {
    e.preventDefault(); setError(''); setBusy(true); setMatches([])
    try {
      if (!consent) throw new Error('Please provide consent before biometric matching.')
      if (!selfie) throw new Error('Select a clear selfie image.')
      const data = await searchWithSelfie(eventId, code, selfie)
      setMatches(data.matches || [])
      setEvent(data.event)
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  return (
    <AppShell title="Find My Event Photos" subtitle="Private, event-scoped selfie matching with explicit consent and no permanent selfie retention.">
      {error && <div className="alert-error">{error}</div>}
      <div className="grid gap-6 xl:grid-cols-[390px_1fr]">
        <section className="panel h-fit">
          <h2 className="font-bold">1. Open Event</h2>
          <div className="mt-4 space-y-3">
            <input className="form-input" aria-label="Event ID" placeholder="Event ID" value={eventId} onChange={(e) => setEventId(e.target.value)} />
            <input className="form-input uppercase tracking-widest" aria-label="Event access code" placeholder="Access code" value={code} onChange={(e) => setCode(e.target.value.toUpperCase())} />
            <button onClick={lookup} className="btn-outline w-full justify-center">Check Event</button>
          </div>
          {event && <div className="mt-5 rounded-xl bg-emerald-50 p-4"><div className="font-semibold text-emerald-900">{event.title}</div><div className="mt-1 text-xs text-emerald-700">{event.photo_count || 0} processed photographs · {event.location || 'Location not specified'}</div></div>}

          <form onSubmit={submit} className="mt-6 border-t pt-6">
            <h2 className="font-bold">2. Submit Selfie</h2>
            <input className="mt-4 block w-full text-sm" aria-label="Select a selfie image" type="file" accept="image/png,image/jpeg,image/webp" onChange={(e) => setSelfie(e.target.files?.[0] || null)} />
            <label className="mt-4 flex items-start gap-3 text-xs leading-relaxed text-gray-600"><input className="mt-1" type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} /><span>I consent to temporary biometric processing for this event-photo search. I understand that results are similarity matches and may contain errors.</span></label>
            <button disabled={!event || busy} className="btn-primary mt-5 w-full justify-center disabled:opacity-50">{busy ? 'Searching…' : 'Find My Photos'}</button>
          </form>
        </section>

        <section>
          <div className="mb-4 flex items-center justify-between"><h2 className="text-xl font-bold">Personalised Gallery</h2><span className="text-sm text-gray-500">{matches.length} match(es)</span></div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{matches.map((photo) => <article key={photo.image_id} className="overflow-hidden rounded-2xl border bg-white"><img src={photo.thumbnail_url || photo.image_url} className="aspect-[4/3] w-full object-cover" /><div className="p-4"><div className="flex items-center justify-between"><span className="text-sm font-semibold">{photo.category || 'Event photo'}</span><span className="text-xs font-semibold text-indigo-600">{photo.confidence_percent}% similarity</span></div><a className="btn-outline mt-4 w-full justify-center" href={`${API_URL}/photos/${photo.image_id}/download?access_code=${encodeURIComponent(code)}`}>Download</a></div></article>)}</div>
          {!matches.length && <div className="panel text-center text-sm text-gray-500">Enter the event details and upload one clear selfie. The system searches only embeddings belonging to that event.</div>}
        </section>
      </div>
    </AppShell>
  )
}
