import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { DEFAULT_LANGUAGE, LANGUAGES, getLanguageInfo, type LanguageCode } from './languages'
import { translations } from './translations'

const STORAGE_KEY = 'lumi-language'

interface LanguageContextValue {
  language: LanguageCode
  setLanguage: (code: LanguageCode) => void
  languages: typeof LANGUAGES
  speechLocale: string
  /** Translate a key, with optional {{placeholder}} interpolation. */
  t: (key: string, vars?: Record<string, string | number>) => string
}

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined)

function readStoredLanguage(): LanguageCode {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored && LANGUAGES.some((l) => l.code === stored)) return stored as LanguageCode
  return DEFAULT_LANGUAGE
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<LanguageCode>(readStoredLanguage)

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, language)
    document.documentElement.lang = language
  }, [language])

  const setLanguage = useCallback((code: LanguageCode) => setLanguageState(code), [])

  const t = useCallback(
    (key: string, vars?: Record<string, string | number>) => {
      const dict = translations[language] ?? translations[DEFAULT_LANGUAGE]
      let text = dict[key] ?? translations[DEFAULT_LANGUAGE][key] ?? key
      if (vars) {
        for (const [k, v] of Object.entries(vars)) {
          text = text.replace(new RegExp(`{{${k}}}`, 'g'), String(v))
        }
      }
      return text
    },
    [language],
  )

  const value = useMemo(
    () => ({ language, setLanguage, languages: LANGUAGES, speechLocale: getLanguageInfo(language).speechLocale, t }),
    [language, setLanguage, t],
  )

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}

export function useLanguage(): LanguageContextValue {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error('useLanguage must be used within a LanguageProvider')
  return ctx
}
