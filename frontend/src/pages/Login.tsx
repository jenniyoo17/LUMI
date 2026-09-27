import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useLanguage } from '../i18n/LanguageContext'
import { Logo } from '../components/Logo'
import { LanguageSwitcher } from '../components/LanguageSwitcher'

export function Login() {
  const { login, error, clearError } = useAuth()
  const { t } = useLanguage()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname ?? '/chat'

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    const ok = await login(email, password)
    setSubmitting(false)
    if (ok) navigate(from, { replace: true })
  }

  return (
    <div className="onboard-shell">
      <div style={{ position: 'absolute', top: 20, right: 20, zIndex: 1 }}>
        <LanguageSwitcher />
      </div>
      <div className="onboard-card">
        <div className="onboard-mark">
          <Logo size={44} />
        </div>
        <h1>{t('login.title')}</h1>
        <p className="onboard-lede">{t('login.subtitle')}</p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="auth-field">
            <span>{t('login.email')}</span>
            <input
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => {
                setEmail(e.target.value)
                if (error) clearError()
              }}
              placeholder="you@example.com"
            />
          </label>

          <label className="auth-field">
            <span>{t('login.password')}</span>
            <input
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => {
                setPassword(e.target.value)
                if (error) clearError()
              }}
              placeholder="••••••••"
            />
          </label>

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" className="btn btn-primary" disabled={submitting} style={{ marginTop: 8 }}>
            {submitting ? t('login.submitting') : t('login.submit')}
          </button>
        </form>

        <p className="onboard-note">
          {t('login.noAccount')} <Link to="/signup">{t('login.createAccount')}</Link>
        </p>
        <p className="onboard-note">{t('login.demoHint')}</p>
      </div>
    </div>
  )
}
