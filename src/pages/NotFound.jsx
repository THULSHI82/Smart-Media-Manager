import { linkHandler } from '../lib/navigation'
import Icon from '../components/Icon'
export default function NotFound() { return <div className="grid min-h-screen place-items-center bg-[#fffaf5] p-6 text-center"><div><Icon name="image" className="mx-auto h-14 w-14 text-[#765b98]" /><h1 className="mt-5 text-3xl font-extrabold">Page not found</h1><a className="btn-primary mt-6" href="/" onClick={linkHandler('/')}>Return Home</a></div></div> }
