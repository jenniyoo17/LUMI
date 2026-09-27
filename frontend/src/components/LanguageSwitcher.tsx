import { useLanguage } from '../i18n/LanguageContext'
import type { LanguageCode } from '../i18n/languages'

interface Props {
  className?: string
}

export function LanguageSwitcher({ className }: Props) {
  const { language, setLanguage, languages } = useLanguage()
  return (
    <select
      className={`lang-select${className ? ` ${className}` : ''}`}
      value={language}
      onChange={(e) => setLanguage(e.target.value as LanguageCode)}
      aria-label="Choose language"
    >
      {languages.map((l) => (
        <option key={l.code} value={l.code}>
          {l.nativeLabel}
        </option>
      ))}
    </select>
  )
}
