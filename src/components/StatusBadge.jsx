const styles = {
  completed: 'bg-emerald-50 text-emerald-700',
  processing: 'bg-indigo-50 text-indigo-700',
  queued: 'bg-amber-50 text-amber-700',
  failed: 'bg-rose-50 text-rose-700',
}

export default function StatusBadge({ value = 'queued' }) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${styles[value] || 'bg-gray-100 text-gray-700'}`}>
      {value}
    </span>
  )
}
