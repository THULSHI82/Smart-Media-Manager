import { linkHandler } from '../lib/navigation'

const capabilities = [
  { value: 'Efficient', label: 'Background image processing' },
  { value: 'Reviewable', label: 'Quality and duplicate flags' },
  { value: 'Private', label: 'Consent-based photo search' },
]

export default function Hero() {
  return (
    <section id="home" className="pastel-hero relative overflow-hidden px-6 pb-24 pt-32 text-[#2f2940]">
      <div className="pastel-blob pastel-blob-one" /><div className="pastel-blob pastel-blob-two" />
      <div className="relative mx-auto grid max-w-7xl items-center gap-16 lg:grid-cols-2">
        <div>
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-[#dac8f6] bg-white/70 px-4 py-2 text-sm font-bold text-[#665080] shadow-sm backdrop-blur">Smart event-photo workflow</div>
          <h1 className="mb-6 text-4xl font-black leading-[1.08] tracking-[-.04em] text-[#2f2940] md:text-6xl">Organise every event. Help every guest <span className="pastel-marker">find their moment.</span></h1>
          <p className="mb-8 max-w-xl text-lg leading-relaxed text-[#6e657d]">A focused workspace for photographers to create protected events, upload photographs, review processing flags and provide optional consent-based selfie search.</p>
          <div className="mb-10 flex flex-wrap gap-4"><a href="/register" onClick={linkHandler('/register')} className="btn-primary">Create Photographer Account</a><a href="/search" onClick={linkHandler('/search')} className="btn-outline">Find My Photos</a></div>
          <div className="grid gap-3 sm:grid-cols-3">{capabilities.map((item, index) => <div key={item.label} className={`pastel-stat pastel-stat-${index + 1}`}><h3 className="text-lg font-black text-[#2f2940]">{item.value}</h3><p className="mt-1 text-xs font-medium text-[#6e657d]">{item.label}</p></div>)}</div>
        </div>
        <div className="pastel-photo-card relative overflow-hidden rounded-[2.5rem] border-[10px] border-white bg-white text-[#2f2940] shadow-2xl shadow-[#cbb9dc]/40">
          <div className="absolute right-5 top-5 z-10 rounded-full bg-[#f3ecf8] px-4 py-3 text-xs font-black text-[#5d467d] shadow-lg">EVENT WORKFLOW</div>
          <div className="relative h-72 overflow-hidden bg-[#e9ddff]"><img src="/images/group-event.jpg" alt="A group gathered together at an event" className="h-full w-full object-cover" /><div className="absolute inset-0 bg-gradient-to-t from-[#2f2940]/80 to-transparent" /><div className="absolute bottom-5 left-6 text-white"><p className="text-xs font-semibold uppercase tracking-widest text-[#eee7f4]">Illustrative event collection</p><p className="mt-1 text-xl font-black">A private path from upload to discovery</p></div></div>
          <div className="p-7">
          <div className="mb-6 flex flex-wrap justify-between gap-3"><div><p className="text-sm text-gray-500">Example Event Pipeline</p><h2 className="text-2xl font-bold">University Function</h2></div><div className="rounded-xl bg-indigo-50 px-4 py-2 text-sm font-semibold text-indigo-700">Background Processing</div></div>
          <div className="space-y-3">{[
            ['1', 'Upload and optimise event photos'],
            ['2', 'Review quality, duplicate and processing flags'],
            ['3', 'Provide protected gallery and search access'],
          ].map(([step, text]) => <div key={step} className="flex items-center gap-4 rounded-xl bg-slate-50 p-4"><div className="grid h-9 w-9 place-items-center rounded-full bg-indigo-600 text-sm font-bold text-white">{step}</div><span className="text-sm font-medium text-gray-700">{text}</span></div>)}</div>
          <div className="mt-6 flex items-center gap-3 rounded-xl bg-[#2f2940] p-4 text-white"><div className="h-3 w-3 rounded-full bg-[#cbb5df]" />Processing runs in the configured background or local fallback mode.</div>
          </div>
        </div>
      </div>
    </section>
  )
}
