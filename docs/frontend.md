# Frontend Notes

## Stack
- React 18 + TypeScript
- MUI (Material UI) for components
- Vite as bundler
- React Router for routing

## Pages
- `CalendarPage` — monthly calendar grid with event cards, navigation prev/next month
- `LoginPage` / `RegisterPage` — JWT auth flow
- `ProfilePage` — user profile
- `HistoryPage` — attendance history list

## Key Components
- `CalendarGrid` — 7-column CSS grid, 42 days (6 weeks), responsive
  - Events limited: xs:2, sm:3, md:4 visible per cell, "+N more" for overflow
  - Uses `minmax(0, 1fr)` to prevent horizontal stretch
- `EventCard` — colored card with time + name, click opens detail sheet
- `EventDetailSheet` — MUI SwipeableDrawer with event details + attendee list
- `SignUpButton` — intention toggle (sign up / cancel for event)
- `AttendeeList` — list of attendees for an event
- `ProtectedRoute` — redirects to login if not authenticated
- `Layout` — app shell with bottom navigation

## API Layer (`frontend/src/api/`)
- `client.ts` — base fetch wrapper (get/post/put/del), adds JWT token from AuthContext
- `auth.ts` — login, register, getProfile
- `events.ts` — event queries
- `intentions.ts` — sign up / cancel intention
- `visits.ts` — attendance history

## Auth
- `AuthContext` — React context, stores JWT token in localStorage
- Token sent as `Authorization: Bearer <token>`

## Conventions
- Time always 24h format (`hour12: false`)
- Vite proxy: `/api` → `http://localhost:8000`
- Dev server listens on `0.0.0.0` (LAN accessible)
