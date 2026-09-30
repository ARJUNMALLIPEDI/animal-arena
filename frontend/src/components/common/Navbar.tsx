import { NavLink } from 'react-router-dom'
import clsx from 'clsx'

const links = [
  { to: '/', label: 'Arena', end: true },
  { to: '/animals', label: 'Bestiary' },
  { to: '/tournament', label: 'Tournament' },
  { to: '/dashboard', label: 'Stats' },
]

export function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-arena-border/80 bg-arena-bg/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        <NavLink to="/" className="flex items-center gap-2">
          <span className="font-display text-2xl tracking-wide text-arena-text">
            ANIMAL <span className="text-arena-ember text-glow-ember">ARENA</span>
          </span>
        </NavLink>
        <nav className="flex items-center gap-1 sm:gap-2">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                clsx(
                  'rounded-md px-2.5 py-1.5 text-sm font-medium transition-colors sm:px-3',
                  isActive
                    ? 'bg-arena-panel-light text-arena-ember'
                    : 'text-arena-muted hover:bg-arena-panel-light hover:text-arena-text',
                )
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  )
}
