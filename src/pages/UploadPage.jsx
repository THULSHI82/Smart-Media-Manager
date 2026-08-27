import { useEffect, useMemo, useState } from 'react'
import AppShell from '../components/AppShell'
import StatusBadge from '../components/StatusBadge'
import Icon from '../components/Icon'
import { api, uploadPhotos } from '../lib/api'

export default function UploadPage({ eventId }) {
  const [event, setEvent] = useState(null)
  const [files, setFiles] = useState([])
  const [photos, setPhotos] = useState([])
  const [jobs, setJobs] = useState([])
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const previews = useMemo(() => files.slice(0, 8).map((file) => ({ file, url: URL.createObjectURL(file) })), [files])

  async function load() {
    try {
      const events = await api('/events')
      setEvent(events.events.find((item) => item.id === eventId))
      const [photoData, processing] = await Promise.all([api(`/photos/manage/${eventId}`), api(`/processing/events/${eventId}`)])
      setPhotos(photoData.photos || []); setJobs(processing.jobs || [])
    } catch (err) { setError(err.message) }
  }
  useEffect(() => { load(); const timer = setInterval(load, 5000); return () => clearInterval(timer) }, [eventId])

  async function submit(e) {
    e.preventDefault(); setBusy(true); setError(''); setMessage('')
    try {
      const data = await uploadPhotos(eventId, files)
      const metrics = data.summary.accepted ? ` Storage reduced by ${Number(data.summary.storage_saving_percent || 0).toFixed(1)}% for this batch; average preprocessing ${Number(data.summary.average_preprocessing_ms || 0).toFixed(0)} ms/image.` : ''
      setMessage(`${data.summary.accepted} photograph(s) accepted; ${data.summary.rejected} rejected.${metrics} Processing status will update automatically.`)
      setFiles([]); await load()
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  return (
    <AppShell title={event?.title || 'Upload Event Photos'} subtitle="Images are standardised, compressed and queued before configured quality, duplicate, face and workflow-label processing.">
      {message && <div className="alert-success">{message}</div>}
      {error && <div className="alert-error">{error}</div>}
      <form onSubmit={submit} className="panel">
        <div className="rounded-2xl border-2 border-dashed border-indigo-200 bg-indigo-50/40 p-8 text-center">
          <Icon name="upload" className="mx-auto h-10 w-10 text-[#765b98]" /><h2 className="mt-3 font-bold">Batch Upload</h2>
          <p className="mx-auto mt-2 max-w-xl text-sm text-gray-500">JPEG, PNG and WebP files are EXIF-rotated, resized to the configured maximum, compressed and given thumbnails before background processing.</p>
          <input className="mt-5 block w-full text-sm" type="file" accept="image/png,image/jpeg,image/webp" multiple onChange={(e) => setFiles(Array.from(e.target.files || []))} />
          <button disabled={!files.length || busy} className="btn-primary mt-5 disabled:opacity-50">{busy ? 'Uploading…' : `Upload ${files.length || ''} Photo${files.length === 1 ? '' : 's'}`}</button>
        </div>
        {!!previews.length && <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-8">{previews.map(({ file, url }) => <div key={`${file.name}-${file.size}`}><img src={url} className="aspect-square w-full rounded-xl object-cover" /><div className="mt-1 truncate text-xs text-gray-500">{file.name}</div></div>)}</div>}
      </form>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <section className="panel">
          <h2 className="font-bold">Processing Job Status</h2>
          <div className="mt-4 space-y-3">{jobs.slice(0, 10).map((job) => <div key={job.id} className="rounded-xl border p-4"><div className="flex justify-between"><StatusBadge value={job.status} /><span className="text-xs text-gray-500">{job.progress}%</span></div><div className="mt-2 text-xs text-gray-500">{job.message || job.error || job.job_type}</div><div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-indigo-600" style={{ width: `${job.progress}%` }} /></div></div>)}{!jobs.length && <p className="text-sm text-gray-500">No jobs yet.</p>}</div>
        </section>
        <section className="panel">
          <h2 className="font-bold">Processed Photographs</h2>
          <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3">{photos.slice(0, 12).map((photo) => <div key={photo.id} className="rounded-xl border p-2"><img src={photo.thumbnail_url || photo.image_url} className="aspect-square w-full rounded-lg object-cover" /><div className="mt-2 truncate text-xs font-medium">{photo.original_filename}</div><div className="mt-1 flex flex-wrap gap-1"><StatusBadge value={photo.processing_status} />{photo.is_blurry ? <span className="flag">Blurry</span> : null}{photo.is_duplicate ? <span className="flag">Duplicate</span> : null}</div><div className="mt-1 text-[11px] text-gray-500">{photo.classification_label || 'Awaiting classification'}</div></div>)}</div>
        </section>
      </div>
    </AppShell>
  )
}
