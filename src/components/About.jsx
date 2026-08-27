import Icon from './Icon'

const pillars = [
  {
    icon: 'ai',
    title: 'Assisted Photo Processing',
    desc: 'Standardise uploads and surface blur, duplicate and processing information for photographer review.',
  },
  {
    icon: 'lock',
    title: 'Protected Event Gallery',
    desc: 'Create event-scoped galleries with access codes, QR entry and role-based controls.',
  },
  {
    icon: 'bolt',
    title: 'Consent-Based Discovery',
    desc: 'Allow guests to search for likely photo matches within one authorised event.',
  },
]

export default function About() {
  return (
    <section id="about" className="pastel-section pastel-peach py-24 px-5 text-[#2f2940]">
      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">

        {/* Text */}
        <div className="fade-up">

          <span className="section-tag">
            About Smart Media Manager
          </span>

          <h2 className="section-title">
            A practical workflow for modern event photography
          </h2>

          <p className="section-sub mb-6">
            Smart Media Manager connects event creation, batch upload, image
            preprocessing, review flags and private gallery access in one clear
            photographer workspace.
          </p>

          <p className="text-gray-500 text-base leading-relaxed mb-8">
            Built for photographers, universities, clubs, and event organizers,
            the prototype reduces repetitive photo-management work while keeping
            access, consent and photographer review visible throughout the workflow.
          </p>

          <a href="#features" className="btn-primary">
            Explore capabilities
          </a>

        </div>


        {/* Feature Pillars */}
        <div className="fade-up">
          <div className="group relative mb-5 overflow-hidden rounded-[2rem] shadow-2xl shadow-indigo-100">
            <img
              src="/images/photographer-event.jpg"
              alt="Professional event photographer capturing a celebration"
              loading="lazy"
              className="h-72 w-full object-cover transition duration-700 group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-950/85 via-transparent to-transparent" />
            <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
              <div className="mb-2 inline-flex rounded-full bg-[#f3ecf8] px-3 py-1 text-[10px] font-black uppercase tracking-widest text-[#5d467d]">Designed for event workflows</div>
              <p className="text-sm font-semibold">From capture to a searchable, privacy-aware gallery.</p>
            </div>
          </div>
          <div className="grid grid-cols-1 gap-4">

          {pillars.map((p) => (

            <div
              key={p.title}
              className="
              flex gap-4 items-start p-5 rounded-2xl
              border border-white/70 bg-white/65 backdrop-blur
              hover:border-[#cbb5ef]
              hover:shadow-lg hover:shadow-[#d9c9ee]/40
              transition-all
              "
            >

              <div
                className="
                w-10 h-10 min-w-[40px]
                rounded-xl
                bg-indigo-50
                flex items-center justify-center
                text-xl
                "
              >
                <Icon name={p.icon} className="h-5 w-5 text-[#765b98]" />
              </div>


              <div>

                <h4 className="font-semibold text-slate-900 text-sm mb-1">
                  {p.title}
                </h4>

                <p className="text-slate-500 text-xs leading-relaxed">
                  {p.desc}
                </p>

              </div>

            </div>

          ))}

          </div>
        </div>

      </div>
    </section>
  )
}
