export type LanguageCode = 'en' | 'hi' | 'kn' | 'ta' | 'te'

export interface LanguageInfo {
  code: LanguageCode
  /** Name shown to a reader of that language, in that language. */
  nativeLabel: string
  /** BCP-47 tag used for the Web Speech API (India locale where available). */
  speechLocale: string
}

export const LANGUAGES: LanguageInfo[] = [
  { code: 'en', nativeLabel: 'English', speechLocale: 'en-IN' },
  { code: 'hi', nativeLabel: 'हिन्दी', speechLocale: 'hi-IN' },
  { code: 'kn', nativeLabel: 'ಕನ್ನಡ', speechLocale: 'kn-IN' },
  { code: 'ta', nativeLabel: 'தமிழ்', speechLocale: 'ta-IN' },
  { code: 'te', nativeLabel: 'తెలుగు', speechLocale: 'te-IN' },
]

export const DEFAULT_LANGUAGE: LanguageCode = 'en'

export function getLanguageInfo(code: LanguageCode): LanguageInfo {
  return LANGUAGES.find((l) => l.code === code) ?? LANGUAGES[0]
}
