import Icon from './Icon'

const features = [
  ['calendar', 'Event Management', 'Create private or public events with dates, retention settings and controlled access.'],
  ['upload', 'Batch Photo Upload', 'Upload JPEG, PNG and WebP photographs for resizing, optimisation and thumbnail creation.'],
  ['quality', 'Blur and Duplicate Review', 'Surface quality and similarity flags for photographer review without automatically deleting images.'],
  ['image', 'Workflow Categorisation', 'Apply event-workflow labels and display processing outcomes clearly in the workspace.'],
  ['face', 'Consent-Based Selfie Search', 'Search for likely matches only within an authorised event after explicit participant consent.'],
  ['lock', 'Privacy and Deletion Requests', 'Support event-scoped access, limited selfie processing and a traceable deletion-request workflow.'],
  ['qr', 'QR and Access-Code Entry', 'Provide a convenient route into a protected event gallery using an access code or QR link.'],
  ['chart', 'Processing Status', 'Track accepted uploads, queued work, progress and review flags from the photographer dashboard.'],
]

export default function Features() {
  return <section id="features" className="pastel-section pastel-lilac px-5 py-20 text-[#2f2940]"><div className="mx-auto max-w-6xl"><div className="fade-up mb-12 text-center"><span className="section-tag">Core capabilities</span><h2 className="section-title">One connected event-photo workspace</h2><p className="section-sub mx-auto">Each capability supports a defined part of the prototype workflow, from event setup to participant privacy.</p></div><div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">{features.map(([icon, title, desc]) => <article key={title} className="card fade-up group"><div className="mb-4 grid h-11 w-11 place-items-center rounded-xl bg-[#f0e8f7] transition group-hover:bg-[#5d467d]"><Icon name={icon} className="h-6 w-6 text-[#765b98] transition group-hover:text-white" /></div><h3 className="mb-2 text-sm font-bold text-[#2f2940]">{title}</h3><p className="text-xs leading-relaxed text-[#6e657d]">{desc}</p></article>)}</div></div></section>
}
