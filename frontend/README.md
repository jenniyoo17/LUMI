# Lumi — Frontend

React + TypeScript + Vite frontend for Lumi, the privacy-first personal AI
companion. This directory is fully self-contained and runs on mock data —
it does not depend on `backend/` or `device-hub/` to work.

## Running it

```bash
cd frontend
npm install
npm run dev
```

Open the local URL Vite prints (defaults to `http://localhost:5173`).

First run lands on **Login**. Use the seeded demo account
(`demo@lumi.app` / `lumi1234`) or create a new one from the Sign up link —
new accounts go straight to Onboarding. Toggling a source there or in
**Data Control** takes effect immediately across the app (Chat's context
pills, Settings' counts, etc.), because everything reads from the same
in-memory mock store while the app is open. Refreshing the page keeps you
logged in (the session is restored from `localStorage`) but resets the
mock data (sources, memories, users you created) back to its seeded
state — that's expected.

## Structure

```
src/
  components/   Reusable UI: NavBar, Logo, ChatBubble, DataSourceToggle, MemoryCard,
                LanguageSwitcher, RequireAuth (route guard)...
  pages/        One file per screen: Login, Signup, Onboarding, Chat, Memory,
                DataControl, Settings
  services/     mockApi.ts / mockAuth.ts (fake backend) + lumiService.ts /
                authService.ts (the stable interfaces UI code depends on)
  hooks/        useChat, useMemories, useDataSources, useAuth (auth context),
                useSpeechRecognition (voice input) — state + calls into
                lumiService / authService
  i18n/         languages.ts (supported languages), translations.ts (dictionary),
                LanguageContext.tsx (t() + current language, persisted)
  types/        Shared TypeScript types (DataSource, ChatMessage, Memory, User, ...)
  styles/       tokens.css (design tokens) + global.css (everything else)
```

## Personalization

Lumi greets people by name wherever it makes sense — the onboarding heading
and the Chat page's time-of-day greeting ("Good morning, Samyuktha") both
read from the name given at signup (or the demo account's name). If someone
signed up without a name, it falls back to the part of their email before
the `@`.

## Multilingual support

Lumi's interface ships in English, Hindi, Kannada, Tamil, and Telugu. The
language picker lives in the nav rail, on Login/Signup/Onboarding, and in
Settings — changing it anywhere updates the whole app immediately and is
remembered for next time (`localStorage`, key `lumi-language`).

- `src/i18n/languages.ts` — the list of supported languages and the BCP-47
  locale each one maps to for voice input (e.g. `hi-IN`).
- `src/i18n/translations.ts` — a flat key → string dictionary per language.
  Add a language by adding one more entry here and to `languages.ts`; add a
  string by adding one key to every language's dictionary.
- `src/i18n/LanguageContext.tsx` — exposes `t(key, vars?)` for simple
  `{{placeholder}}` interpolation (used for names and counts).

**Scope note:** this covers the app's own interface text. Lumi's scripted
chat replies in the mock layer are still English-only — teaching the mock
(or eventually the real) assistant to reply in the selected language is
backend/model work, out of scope for this frontend-only mock.

## Voice input

The mic button in Chat uses the browser's built-in Web Speech API
(`SpeechRecognition` / `webkitSpeechRecognition`) — no external service or
API key needed. It respects the existing privacy model: the button stays
locked until **Microphone** is turned on in Data Control (same toggle used
elsewhere), and clicking it while locked takes you straight there. Once
enabled, tapping the mic starts listening in whatever language is
currently selected (`speechLocale` from `useLanguage()`); the transcript is
appended to the message box for review before sending — it never
auto-sends.

Notes:
- Currently best supported in Chromium-based browsers (Chrome, Edge); the
  button shows a "not supported" state elsewhere via `t('chat.micUnsupported')`.
- Turning the in-app toggle on does **not** grant OS/browser microphone
  permission — the browser will still show its own permission prompt the
  first time recognition starts.
- Recognition logic lives entirely in `src/hooks/useSpeechRecognition.ts`,
  isolated from the rest of Chat's state.

## Authentication

Login and signup are built in (`/login`, `/signup`), and every other route
is wrapped in `RequireAuth`, which redirects to `/login` if there's no
session. Sessions are simulated with a fake token in `localStorage` and
restored on page load via `authService.restoreSession()`.

**This mock auth is for the hackathon demo only — email/password are
checked in the browser and the "database" is a JS array that resets on
reload.** It is not secure and should never be treated as production
authentication. It exists so the frontend has a real login flow to build
and demo against while the backend is being built.

### Connecting real authentication

Same pattern as `lumiService`: everything goes through
`src/services/authService.ts`, which currently points at `mockAuth.ts`.
To connect the real backend:

1. Keep the `AuthServiceInterface` shape (or extend it deliberately).
2. Write `realAuth.ts` that calls the backend's actual auth endpoints.
3. Swap the export in `authService.ts` from `mockAuth` to `realAuth`.

When the real backend exists, make sure it (not this frontend) is the
thing actually verifying credentials and issuing tokens: passwords must be
hashed and salted server-side (e.g. bcrypt/argon2), sessions should use
short-lived tokens over HTTPS (or secure httpOnly cookies), and login
attempts should be rate-limited. None of that can be done safely from the
frontend alone — this app should just send credentials to that endpoint
and store whatever token it returns.

## Connecting the real backend

The UI never talks to `mockApi.ts` directly — every page and hook imports
`lumiService` from `src/services/lumiService.ts`. That file is the only
place that needs to change:

1. Keep the `LumiService` interface in `lumiService.ts` as-is (or extend it
   thoughtfully — the pages depend on its exact shape).
2. Write a new implementation, e.g. `realApi.ts`, that calls the actual
   backend endpoints instead of the in-memory store — same method names,
   same return types.
3. Swap the export:

   ```ts
   // before
   export const lumiService: LumiService = mockApi

   // after
   export const lumiService: LumiService = realApi
   ```

No component, page, or hook needs to change. If the backend's data shapes
differ from `src/types/index.ts`, translate them inside the new
`realApi.ts` implementation rather than changing the types everywhere else.

### Where mock behavior lives, if useful for the demo

- `src/services/mockData.ts` — seeded data sources, memories, starter
  message, and the keyword-matched scripted replies (e.g. mentioning
  "stressed" or "exam" triggers Lumi's context-aware reply, but only if
  Notes/Calendar are toggled on).
- `src/services/mockApi.ts` — simulates network latency and mutates the
  in-memory store; this is what `realApi.ts` will eventually replace.

## Design notes

Palette and type are defined once in `src/styles/tokens.css`. The visual
language centers on a signature "glow" gradient (sage green → periwinkle,
`--lumi-glow`) used sparingly for the brand mark, primary buttons, active
nav state, the mic's listening ring, and Lumi's chat avatar — everywhere
else stays a calm off-white with soft, colored (not flat grey) shadows
instead of hard borders. `Fraunces` (including its italic, used for the
Chat greeting) carries headings and warmth; `Public Sans` plus the Noto
Sans script families (Devanagari/Kannada/Tamil/Telugu, loaded in
`index.html`) cover everything else so all five languages render with
proper native glyphs, not tofu boxes. The nav rail is a floating rounded
"dock" rather than a flush sidebar. Keep this intent — calm and personal,
not a clinical dashboard — when extending the UI; avoid hospital
blues/greens, dense data tables, or flat drop-shadow-free cards.
