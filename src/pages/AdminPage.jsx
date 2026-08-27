import { useEffect, useState } from 'react'
import AppShell from '../components/AppShell'
import { api } from '../lib/api'

export default function AdminPage() {
  const [data, setData] = useState(null)
  const [requests, setRequests] = useState([])
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  async function load() {
    try {
      const [summary, privacy] = await Promise.all([api('/admin/summary'), api('/admin/deletion-requests')])
      setData(summary); setRequests(privacy.deletion_requests || [])
    } catch (err) { setError(err.message) }
  }
  useEffect(() => { load() }, [])

  async function setRequestStatus(id, status) {
    setError(''); setMessage('')
    try {
      await api(`/admin/deletion-requests/${id}`, { method: 'PUT', body: JSON.stringify({ status }) })
      setMessage(`Deletion request marked ${status}.`); await load()
    } catch (err) { setError(err.message) }
  }

  async function purgeExpired() {
    setError(''); setMessage('')
    try {
      const result = await api('/admin/privacy/purge-expired-embeddings', { method: 'POST' })
      setMessage(`${result.deleted_embeddings} expired unclaimed embedding(s) removed.`)
    } catch (err) { setError(err.message) }
  }

  const stats = data?.stats || {}
  return (
    <AppShell title="Administrator Dashboard" subtitle="Monitor users, events, processing failures, downloads and privacy requests.">
      {message && <div className="alert-success">{message}</div>}
      {error && <div className="alert-error">{error}</div>}
      <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-6">{[['Users', stats.users], ['Events', stats.events], ['Images', stats.images], ['Downloads', stats.downloads], ['Failed Jobs', stats.failed_jobs], ['Deletion Requests', stats.deletion_requests]].map(([label, value]) => <div key={label} className="panel"><div className="text-sm text-gray-500">{label}</div><div className="mt-3 text-3xl font-extrabold">{value || 0}</div></div>)}</div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <section className="panel"><h2 className="font-bold">Recent Activity</h2><div className="mt-4 overflow-x-auto"><table className="w-full min-w-[650px] text-left text-sm"><thead className="text-xs uppercase text-gray-400"><tr><th className="p-3">Time</th><th className="p-3">User</th><th className="p-3">Action</th><th className="p-3">Entity</th></tr></thead><tbody>{(data?.activity || []).map((item) => <tr key={item.id} className="border-t"><td className="p-3 text-gray-500">{new Date(item.created_at).toLocaleString()}</td><td className="p-3">{item.user_name || 'Participant/anonymous'}</td><td className="p-3 font-medium">{item.action}</td><td className="p-3 text-gray-500">{item.entity_type}</td></tr>)}</tbody></table></div></section>

        <section className="panel"><div className="flex items-center justify-between gap-3"><h2 className="font-bold">Privacy Requests</h2><button className="btn-outline" onClick={purgeExpired}>Purge expired vectors</button></div><div className="mt-4 space-y-3">{requests.slice(0, 10).map((item) => <div key={item.id} className="rounded-xl border p-4"><div className="flex flex-wrap items-start justify-between gap-3"><div><div className="font-semibold">{item.email}</div><div className="mt-1 text-xs text-gray-500">{item.reason || 'No reason supplied'} · {item.status}</div></div>{item.status === 'pending' && <div className="flex gap-2"><button className="btn-outline" onClick={() => setRequestStatus(item.id, 'resolved')}>Resolve</button><button className="btn-outline" onClick={() => setRequestStatus(item.id, 'rejected')}>Reject</button></div>}</div></div>)}{!requests.length && <p className="text-sm text-gray-500">No deletion requests.</p>}</div></section>
      </div>
    </AppShell>
  )
}
