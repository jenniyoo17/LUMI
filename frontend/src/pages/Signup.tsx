import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useLanguage } from '../i18n/LanguageContext'
import { Logo } from '../components/Logo'
import { LanguageSwitcher } from '../components/LanguageSwitcher'

export function Signup() {
  const { signup, error, clearError } = useAuth()
  const { t } = useLanguage()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [confirmError, setConfirmError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setConfirmError(null)
    if (password !== confirm) {
      setConfirmError(t('signup.passwordMismatch'))
      return
    }
    setSubmitting(true)
    const ok = await signup(email, password, name)
    setSubmitting(false)
    if (ok) navigate('/onboarding', { replace: true })
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
        <h1>{t('signup.title')}</h1>
        <p className="onboard-lede">{t('signup.subtitle')}</p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="auth-field">
            <span>{t('signup.name')}</span>
            <input
              type="text"
              autoComplete="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t('signup.namePlaceholder')}
            />
          </label>

          <label className="auth-field">
            <span>{t('signup.email')}</span>
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
            <span>{t('signup.password')}</span>
            <input
              type="password"
              autoComplete="new-password"
              required
              minLength={8}
              value={password}
              onChange={(e) => {
                setPassword(e.target.value)
                if (error) clearError()
              }}
              placeholder="••••••••"
            />
          </label>

          <label className="auth-field">
            <span>{t('signup.confirmPassword')}</span>
            <input
              type="password"
              autoComplete="new-password"
              required
              value={confirm}
              onChange={(e) => {
                setConfirm(e.target.value)
                setConfirmError(null)
              }}
              placeholder="••••••••"
            />
          </label>

          {(error || confirmError) && <div className="auth-error">{error ?? confirmError}</div>}

          <button type="submit" className="btn btn-primary" disabled={submitting} style={{ marginTop: 8 }}>
            {submitting ? t('signup.submitting') : t('signup.submit')}
          </button>
        </form>

        <p className="onboard-note">
          {t('signup.haveAccount')} <Link to="/login">{t('signup.login')}</Link>
        </p>
      </div>
    </div>
  )
}
