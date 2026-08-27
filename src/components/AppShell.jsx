import { getSession, setSession } from '../lib/api'
import { linkHandler, navigate } from '../lib/navigation'
import Icon from './Icon'

const photographerLinks = [
  ['Dashboard', '/dashboard', 'dashboard'],
  ['Events', '/events', 'calendar'],
  ['Find My Photos', '/search', 'face'],
  ['Privacy', '/privacy', 'lock'],
]

export default function AppShell({ title, subtitle, children }) {
  const session = getSession()
  const currentPath = window.location.pathname
  const isPublic = !session && (currentPath === '/search' || currentPath === '/privacy')
  const links = session?.user?.role === 'administrator'
    ? [['Admin', '/admin', 'shield'], ['Events', '/events', 'calendar'], ['Find My Photos', '/search', 'face'], ['Privacy', '/privacy', 'lock']]
    : photographerLinks

  function logout() {
    setSession(null)
    navigate('/')
  }

  if (isPublic) return (
    <div className="app-canvas min-h-screen text-[#2f2940]">
      <header className="border-b border-[#e4d6ef] bg-[#fffaf5]/95 px-5 py-4"><div className="mx-auto flex max-w-6xl items-center justify-between gap-4"><a href="/" onClick={linkHandler('/')} className="flex items-center gap-3"><div className="grid h-11 w-11 place-items-center rounded-xl bg-[#2f2940] font-black text-white">SM</div><div><div className="font-black">Smart Media Manager</div><div className="text-xs text-[#765b98]">Protected event-photo prototype</div></div></a><a href="/login" onClick={linkHandler('/login')} className="btn-outline">Photographer login</a></div></header>
      <main className="mx-auto max-w-6xl p-5 md:p-8"><header className="mb-8 rounded-2xl border border-[#ece7f7] bg-white p-6 shadow-sm md:p-8"><div className="mb-3 text-xs font-bold uppercase tracking-[.22em] text-[#6747e8]">Participant access</div><h1 className="text-3xl font-black tracking-tight md:text-4xl">{title}</h1>{subtitle && <p className="mt-2 max-w-3xl text-sm text-gray-500">{subtitle}</p>}</header>{children}</main>
    </div>
  )

  return (
    <div className="app-canvas min-h-screen text-[#2f2940] lg:flex">
      <aside className="border-b border-[#e4d6ef] bg-[#f2eaff] p-5 text-[#2f2940] lg:sticky lg:top-0 lg:min-h-screen lg:w-72 lg:self-start lg:border-b-0 lg:border-r">
        <a href="/" onClick={linkHandler('/')} className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-2xl bg-[#2f2940] font-black text-white shadow-lg shadow-violet-200">S</div>
          <div><div className="font-black">Smart Media Manager</div><div className="text-xs text-[#765b98]">Event-photo workspace</div></div>
        </a>
        <nav className="mt-7 grid grid-cols-2 gap-2 lg:grid-cols-1">
          {links.map(([label, path, icon]) => (
            <a key={path} href={path} onClick={linkHandler(path)} aria-current={(currentPath === path || (path === '/events' && currentPath.startsWith('/events/'))) ? 'page' : undefined} className={`flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-semibold transition ${(currentPath === path || (path === '/events' && currentPath.startsWith('/events/'))) ? 'bg-[#5d467d] text-white shadow-md shadow-violet-200' : 'text-[#675f74] hover:bg-white hover:text-[#5637c8]'}`}>
              <Icon name={icon} className="h-5 w-5" />{label}
            </a>
          ))}
        </nav>
        <div className="mt-7 rounded-3xl border border-white bg-white/60 p-5 text-[#2f2940] shadow-sm">
          <div className="text-sm font-semibold">{session?.user?.name || 'User'}</div>
          <div className="mt-1 text-xs capitalize text-[#765b98]">{session?.user?.role || 'guest'}</div>
          <button onClick={logout} className="mt-4 text-xs font-semibold underline">Sign out</button>
        </div>
      </aside>

      <main className="min-w-0 flex-1 p-5 md:p-8">
        <header className="mb-8 rounded-2xl border border-[#ece7f7] bg-white p-6 shadow-sm md:p-8">
          <div className="mb-3 text-xs font-bold uppercase tracking-[.22em] text-[#6747e8]">Smart workspace</div>
          <h1 className="text-3xl font-black tracking-tight md:text-4xl">{title}</h1>
          {subtitle && <p className="mt-2 text-sm text-gray-500">{subtitle}</p>}
        </header>
        {children}
      </main>
    </div>
  )
}
