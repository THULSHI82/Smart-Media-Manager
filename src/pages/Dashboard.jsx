import { useEffect, useState } from 'react'
import AppShell from '../components/AppShell'
import StatusBadge from '../components/StatusBadge'
import { api } from '../lib/api'
import { linkHandler } from '../lib/navigation'
import Icon from '../components/Icon'

function formatBytes(value = 0) {
  if (!value) return '0 MB'
  const units = ['B', 'KB', 'MB', 'GB']
  let size = Number(value)
  let index = 0
  while (size >= 1024 && index < units.length - 1) { size /= 1024; index += 1 }
  return `${size.toFixed(index > 1 ? 1 : 0)} ${units[index]}`
}

function formatMs(value) {
  const ms = Number(value || 0)
  if (!ms) return '—'
  return ms >= 1000 ? `${(ms / 1000).toFixed(2)} s` : `${ms.toFixed(0)} ms`
}

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api('/dashboard/summary').then(setData).catch((err) => setError(err.message))
  }, [])

  const stats = data?.stats || {}
  const cards = [
    ['Events', stats.events || 0, 'calendar'],
    ['Photos', stats.photos || 0, 'image'],
    ['AI Processing', stats.processing || 0, 'sparkles'],
    ['Optimised Storage', formatBytes(stats.storage_bytes), 'cloud'],
    ['Storage Saved', `${Number(stats.storage_saving_percent || 0).toFixed(1)}%`, 'chart'],
  ]

  return (
    <AppShell title="Photographer Dashboard" subtitle="Create events, monitor background processing and manage event galleries.">
      {error && <div className="alert-error">{error}</div>}
      <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-5">
        {cards.map(([label, value, icon]) => (
          <div key={label} className="panel">
            <div className="flex items-start justify-between"><span className="text-sm text-gray-500">{label}</span><span className="grid h-10 w-10 place-items-center rounded-xl bg-[#f0ebff] text-[#6747e8]"><Icon name={icon} className="h-5 w-5" /></span></div>
            <div className="mt-4 text-3xl font-extrabold">{value}</div>
          </div>
        ))}
      </div>

      <div className="mt-5 rounded-2xl border border-indigo-100 bg-indigo-50/60 p-4 text-sm text-indigo-900">
        Measured local averages: preprocessing <b>{formatMs(stats.avg_preprocessing_ms)}</b> per image and processing <b>{formatMs(stats.avg_processing_ms)}</b> per completed image. These values are calculated from the current local database rather than estimated.
      </div>

      <div className="mt-7 grid gap-6 xl:grid-cols-2">
        <section className="panel">
          <div className="flex items-center justify-between">
            <h2 className="font-bold">Recent Events</h2>
            <a href="/events" onClick={linkHandler('/events')} className="text-sm font-semibold text-indigo-600">Manage events →</a>
          </div>
          <div className="mt-4 space-y-3">
            {(data?.recent_events || []).map((event) => (
              <div key={event.id} className="rounded-xl bg-slate-50 p-4">
                <div className="flex items-center justify-between gap-3"><div className="font-semibold">{event.title}</div><span className="text-xs text-gray-500">{event.photo_count} photos</span></div>
                <div className="mt-2 text-xs text-gray-500">Access code: <b>{event.access_code}</b> · {event.completed_count}/{event.photo_count} processed</div>
                <a href={`/events/${event.id}/upload`} onClick={linkHandler(`/events/${event.id}/upload`)} className="mt-3 inline-block text-xs font-semibold text-indigo-600">Upload and review →</a>
              </div>
            ))}
            {!data?.recent_events?.length && <p className="text-sm text-gray-500">No events yet. Create the first event from the Events page.</p>}
          </div>
        </section>

        <section className="panel">
          <h2 className="font-bold">Processing Activity</h2>
          <div className="mt-4 space-y-3">
            {(data?.recent_jobs || []).map((job) => (
              <div key={job.id} className="flex items-center justify-between gap-4 rounded-xl border border-slate-100 p-4">
                <div className="min-w-0"><div className="truncate text-sm font-semibold">{job.event_title}</div><div className="mt-1 text-xs text-gray-500">{job.message || job.job_type}</div></div>
                <div className="text-right"><StatusBadge value={job.status} /><div className="mt-1 text-xs text-gray-400">{job.progress}%{job.duration_ms ? ` · ${formatMs(job.duration_ms)}` : ''}</div></div>
              </div>
            ))}
            {!data?.recent_jobs?.length && <p className="text-sm text-gray-500">No processing jobs have been created yet.</p>}
          </div>
        </section>
      </div>

      {(stats.blurry > 0 || stats.duplicates > 0) && (
        <div className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-5 text-sm text-amber-900">
          Review flags: {stats.blurry || 0} blurry and {stats.duplicates || 0} duplicate photographs. Flags are shown for photographer review; images are not automatically destroyed.
        </div>
      )}
    </AppShell>
  )
}
