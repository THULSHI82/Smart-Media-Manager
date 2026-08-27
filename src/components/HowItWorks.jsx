import Icon from './Icon'
import { linkHandler } from '../lib/navigation'

const steps = [
  ['01', 'calendar', 'Create a protected event', 'Set the event details, access method and retention preferences.'],
  ['02', 'upload', 'Upload and preprocess', 'Batch-upload photographs for standardisation, optimisation and thumbnail creation.'],
  ['03', 'quality', 'Review processing flags', 'Check status, blur indicators, duplicate indicators and workflow categories.'],
  ['04', 'qr', 'Provide event access', 'Share the event-specific access code or QR route with authorised participants.'],
  ['05', 'face', 'Search with consent', 'Participants may submit a selfie to look for likely matches within that event.'],
]

export default function HowItWorks() {
  return <section id="how-it-works" className="pastel-section pastel-sky px-5 py-20 text-[#2f2940]"><div className="mx-auto max-w-6xl"><div className="fade-up mb-12 text-center"><span className="section-tag">Workflow</span><h2 className="section-title">A clear path from event setup to photo discovery</h2><p className="section-sub mx-auto">The interface keeps photographer decisions, processing status and participant consent visible at every stage.</p></div><ol className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">{steps.map(([n, icon, title, desc]) => <li key={n} className="fade-up rounded-2xl border border-[#e5d8ee] bg-white/80 p-5 shadow-sm"><div className="mb-5 flex items-center justify-between"><div className="grid h-11 w-11 place-items-center rounded-xl bg-[#f0e8f7]"><Icon name={icon} className="h-5 w-5 text-[#5d467d]" /></div><span className="text-xs font-black tracking-widest text-[#9b8aa9]">{n}</span></div><h3 className="mb-2 text-sm font-bold">{title}</h3><p className="text-xs leading-relaxed text-[#6e657d]">{desc}</p></li>)}</ol><div className="fade-up mt-10 text-center"><a href="/register" onClick={linkHandler('/register')} className="btn-primary">Start managing an event</a></div></div></section>
}
