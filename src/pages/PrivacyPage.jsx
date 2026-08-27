import { useState } from 'react'
import AppShell from '../components/AppShell'
import { api } from '../lib/api'

export default function PrivacyPage() {
  const [form, setForm] = useState({ email: '', reason: '' })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  async function submit(e) {
    e.preventDefault(); setMessage(''); setError('')
    try { const data = await api('/privacy/deletion-request', { method: 'POST', body: JSON.stringify(form) }); setMessage(`${data.message} Reference: ${data.request_id}`); setForm({ email: '', reason: '' }) } catch (err) { setError(err.message) }
  }
  return (
    <AppShell title="Privacy and Biometric Controls" subtitle="Consent, event-level access, limited processing purpose and deletion requests are part of the system design.">
      {message && <div className="alert-success">{message}</div>}{error && <div className="alert-error">{error}</div>}
      <div className="grid gap-6 xl:grid-cols-2">
        <section className="panel"><h2 className="font-bold">Implemented Safeguards</h2><div className="mt-5 space-y-4 text-sm text-gray-600">{[
          ['Explicit consent', 'Selfie search is blocked until the participant accepts the biometric-processing notice.'],
          ['Event-scoped search', 'Face vectors are searched only within the selected authorised event.'],
          ['No selfie retention', 'The selfie endpoint processes the image in memory and does not create a stored selfie record.'],
          ['Role-based access', 'Photographer and administrator operations require JWT role checks.'],
          ['Data minimisation', 'The configured database stores metadata and biometric vectors while media remains in the configured local or cloud media store. Temporary unclaimed vectors have retention deadlines.'],
          ['Deletion workflow', 'A participant can record a personal-data deletion request for administrator review.'],
        ].map(([title, text]) => <div key={title} className="rounded-xl bg-slate-50 p-4"><div className="font-semibold text-gray-900">{title}</div><div className="mt-1">{text}</div></div>)}</div></section>
        <form onSubmit={submit} className="panel h-fit space-y-4"><h2 className="font-bold">Request Data Deletion</h2><input className="form-input" type="email" placeholder="Your email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required /><textarea className="form-input min-h-32" placeholder="Describe the event or data to remove" value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} /><button className="btn-primary">Submit Request</button></form>
      </div>
    </AppShell>
  )
}
