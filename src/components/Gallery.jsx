import { linkHandler } from '../lib/navigation'

const items = [
  ['Annual Gala', '/images/gallery-gala.jpg'], ['University Sports Day', '/images/gallery-sport.jpg'], ['Workshop', '/images/gallery-workshop.jpg'],
  ['Community Event', '/images/gallery-community.jpg'], ['Award Ceremony', '/images/gallery-awards.jpg'], ['Club Gathering', '/images/gallery-club.jpg'],
]

export default function Gallery() {
  return <section id="gallery" className="pastel-gallery px-5 py-20 text-[#2f2940]"><div className="mx-auto max-w-6xl"><div className="fade-up mb-12 text-center"><span className="section-tag">Illustrative event gallery</span><h2 className="section-title">Different events, one consistent gallery experience</h2><p className="section-sub mx-auto">These sample collections demonstrate the intended presentation. They are illustrative images, not live database totals.</p></div><div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">{items.map(([label, image]) => <figure key={label} className="fade-up overflow-hidden rounded-2xl border border-[#e8ddf2] bg-white shadow-sm"><img src={image} alt={`${label} sample event`} loading="lazy" className="aspect-[4/3] w-full object-cover" /><figcaption className="p-4"><div className="text-sm font-bold">{label}</div><div className="mt-1 text-xs text-[#81768d]">Sample collection</div></figcaption></figure>)}</div><div className="fade-up mx-auto mt-10 max-w-2xl text-center"><p className="mb-5 text-sm leading-relaxed text-[#6e657d]">Have an event code? Open the participant search to check the event and submit a selfie only after reviewing the consent notice.</p><a href="/search" onClick={linkHandler('/search')} className="btn-primary">Open personal photo search</a></div></div></section>
}
