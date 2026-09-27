import { NavLink } from 'react-router-dom'
import { Logo } from './Logo'
import { LanguageSwitcher } from './LanguageSwitcher'
import { useLanguage } from '../i18n/LanguageContext'

function ChatIcon() {
  return (
    <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M4 5h16v11H8l-4 4V5Z" strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  )
}
function MemoryIcon() {
  return (
    <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M12 3a5 5 0 0 0-5 5c0 1.6.7 2.6 1.5 3.6.6.8 1 1.4 1 2.4v2a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-2c0-1 .4-1.6 1-2.4.8-1 1.5-2 1.5-3.6a5 5 0 0 0-5-5Z" strokeLinejoin="round" />
      <path d="M10 20h4" strokeLinecap="round" />
    </svg>
  )
}
function DataIcon() {
  return (
    <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <ellipse cx="12" cy="6" rx="7" ry="3" />
      <path d="M5 6v12c0 1.7 3.1 3 7 3s7-1.3 7-3V6" strokeLinecap="round" />
      <path d="M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3" />
    </svg>
  )
}
function SettingsIcon() {
  return (
    <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <circle cx="12" cy="12" r="3" />
      <path d="M19 12a7 7 0 0 0-.1-1.2l2-1.5-2-3.4-2.3.9a7 7 0 0 0-2-1.2L14 3h-4l-.6 2.6a7 7 0 0 0-2 1.2l-2.3-.9-2 3.4 2 1.5A7 7 0 0 0 5 12c0 .4 0 .8.1 1.2l-2 1.5 2 3.4 2.3-.9c.6.5 1.3.9 2 1.2L10 21h4l.6-2.6c.7-.3 1.4-.7 2-1.2l2.3.9 2-3.4-2-1.5c.1-.4.1-.8.1-1.2Z" strokeLinejoin="round" />
    </svg>
  )
}

export function NavBar() {
  const { t } = useLanguage()
  const links = [
    { to: '/chat', label: t('nav.chat'), icon: <ChatIcon /> },
    { to: '/memory', label: t('nav.memory'), icon: <MemoryIcon /> },
    { to: '/data', label: t('nav.data'), icon: <DataIcon /> },
    { to: '/settings', label: t('nav.settings'), icon: <SettingsIcon /> },
  ]

  return (
    <nav className="nav-rail" aria-label="Main navigation">
      <div className="nav-mark">
        <Logo size={34} />
      </div>
      <div className="nav-links">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          >
            {link.icon}
            {link.label}
          </NavLink>
        ))}
      </div>
      <div className="nav-bottom-space">
        <LanguageSwitcher />
      </div>
    </nav>
  )
}
