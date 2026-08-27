import { useEffect, useState } from 'react'
import { getSession } from '../lib/api'
import { linkHandler } from '../lib/navigation'

const links = [
  { name: 'Home', href: '#home' },
  { name: 'About', href: '#about' },
  { name: 'Features', href: '#features' },
  { name: 'Workflow', href: '#how-it-works' },
  { name: 'Gallery', href: '#gallery' },
]

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const [active, setActive] = useState('#home')
  const session = getSession()
  useEffect(() => {
    const sections = links.map((item) => document.querySelector(item.href)).filter(Boolean)
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0]
      if (visible) setActive(`#${visible.target.id}`)
    }, { rootMargin: '-25% 0px -60% 0px', threshold: [0.05, 0.25, 0.5] })
    sections.forEach((section) => observer.observe(section))
    return () => observer.disconnect()
  }, [])
  return (
    <header className="fixed left-0 top-0 z-50 w-full border-b border-white/70 bg-[#fffaf5]/85 text-[#2f2940] shadow-sm shadow-violet-100/40 backdrop-blur-xl">
      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6">
        <a href="#home" className="flex items-center gap-3"><div className="grid h-11 w-11 place-items-center rounded-2xl bg-[#2f2940] font-black text-[#fffaf5] shadow-lg shadow-violet-200">SM</div><div><h1 className="text-lg font-black tracking-tight text-[#2f2940]">Smart Media</h1><p className="text-xs font-medium text-[#887ca0]">AI Event Photo Manager</p></div></a>
        <nav className="hidden items-center gap-2 lg:flex">{links.map((item) => <a key={item.name} href={item.href} aria-current={active === item.href ? 'page' : undefined} className={`rounded-full px-4 py-2 text-sm font-semibold transition ${active === item.href ? 'bg-[#e9ddff] text-[#5d467d]' : 'text-[#6e657d] hover:bg-[#f5edff] hover:text-[#5d467d]'}`}>{item.name}</a>)}</nav>
        <div className="hidden items-center gap-3 lg:flex">
          <a href="/search" onClick={linkHandler('/search')} className="btn-outline">Find My Photos</a>
          <a href={session ? '/dashboard' : '/login'} onClick={linkHandler(session ? '/dashboard' : '/login')} className="btn-primary">{session ? 'Dashboard' : 'Login'}</a>
        </div>
        <button onClick={() => setOpen(!open)} className="grid h-12 w-12 place-items-center rounded-xl border border-[#d8cae6] bg-white text-[#2f2940] lg:hidden" aria-label="Toggle navigation"><span className="sr-only">Menu</span><span aria-hidden="true" className="text-xl">{open ? '×' : '≡'}</span></button>
      </div>
      {open && <div className="border-t border-violet-100 bg-[#fffaf5] lg:hidden"><div className="flex flex-col gap-5 p-6">{links.map((item) => <a key={item.name} href={item.href} onClick={() => setOpen(false)} className="font-semibold text-[#6e657d] hover:text-[#5d467d]">{item.name}</a>)}<a href="/search" onClick={linkHandler('/search')} className="btn-outline justify-center">Find My Photos</a><a href={session ? '/dashboard' : '/login'} onClick={linkHandler(session ? '/dashboard' : '/login')} className="btn-primary justify-center">{session ? 'Dashboard' : 'Login'}</a></div></div>}
    </header>
  )
}
