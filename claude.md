# Claude Handoff Notes

## Project Snapshot
- **Repository:** TradeSignal (FastAPI + React/TypeScript)
- **Current Phase:** Phase 3 – Frontend Dashboard (in progress)
- **Savepoints:** `UNDO`, `codex-undo-20251027031834`
- **Local services:** Backend via Docker on http://localhost:8000 (WS endpoint `/api/v1/trades/stream`); Frontend dev server expected on http://localhost:5174 (start with `npm run dev`).

## Request Timeline & Outcomes
1. **Initial bug report** – Dashboard and Trades pages showed placeholder IDs (`Company #2`, `Insider #11`).
   - Returned nested company/insider data from backend and updated UI to display names + ticker with working links.
2. **Feature request** – Implement trade filtering, richer stats, and visual polish.
   - Added filter controls (ticker, type, min/max USD, start/end date), stats summary cards, derived value formatting, and trend visualization.
3. **Phase 3 continuation (Option 3)** – Add real-time behaviour.
   - Implemented WebSocket streaming so Dashboard/Trades auto-refresh when trades are created or updated.

## Backend Work Completed
- Updated trade routes (`/trades`, `/trades/recent`, `/companies/:ticker/trades`, `/insiders/:id/trades`) to return `TradeWithDetails` (company + insider).
- Cleaned up Pydantic schema forward references (direct imports, PEP-604 unions).
- Added `TradeEventManager` (async in-memory broadcaster) and integrated into `TradeService.create` / `.update` to emit `trade_created` / `trade_updated` messages.
- Added `/api/v1/trades/stream` WebSocket endpoint, acknowledged initial connection, and handles disconnects gracefully.
- Restarted Docker backend (`docker restart tradesignal-backend`) after schema and router changes.

## Frontend Work Completed
- Surfaced nested company/insider info in TradeList with dynamic routing (`/companies/:ticker`, `/insiders/:id`).
- Hardened API client (30s timeout, richer error logging) and added `vite-env.d.ts` for TypeScript.
- Extended `Trade`, `TradeStats`, and `TradeFilters` types to align with backend payloads/params.
- Built `/trades` filter panel with validation, reset button, and state management that resyncs pagination when filters change.
- Hooked filters into React Query keys; stats and tables respect `ticker`, `transaction_type`, `min_value`, `max_value`, `transaction_date_from`, `transaction_date_to`.
- Added derived price/value fallbacks in `TradeList` to minimize `N/A` output when filings provide enough data.
- Introduced summary cards plus `TradeValueSparkline` (Recharts) to visualize aggregate values for the current result set.
- Created `useTradeStream` hook; both Dashboard and Trades pages subscribe to `/trades/stream`, push fresh trades into cache, and invalidate relevant queries.
- Dashboard stats query updated to new `getTradeStats` signature so cards stay accurate under live updates.

## Tooling, Builds & Environment Notes
- `npm run build` continues to succeed (bundle now ~680 kB because of Recharts/WebSocket helpers; Rollup emits warning only).
- Backend health check `GET http://localhost:8000/health` returns `healthy` post-restart.
- Frontend dev server is not auto-started; run `npm run dev` under `frontend/` before manual QA.

## Current Progress Snapshot
- Dashboard & Trades tables show real data, filtered views update stats, sparkline, and pagination in sync.
- Live trades received over WebSocket instantly update Dashboard recent list, summary cards, sparkline, and filter-dependent tables.
- Remaining `N/A` values occur only when SEC Form 4 filings omit both price and total value (common for derivative transactions); fallbacks already compute value when either component is available.

## QA / Verification Performed
- Manual filter testing at http://localhost:5174/trades (Ticker, Type, Min/Max Value, Start/End Date) verifying data + summary alignment.
- Observed `Refreshing summary...` indicator while stats refetch under active filters.
- Sparkline verified to shrink/grow with filters and new trades.
- Simulated live trade events (API insert) -> Dashboard “Recent Trades” and Trades table updated without reload; network tab confirms open WebSocket.
- Backend `/health` endpoint checked after Docker restart.

## Outstanding / Recommended Next Steps
1. **Filter UX Enhancements**
   - Add insider/company dropdowns (autocomplete), preset date ranges, and persist selections to URL query params for shareable views.
2. **Data Visualization Expansion**
   - Build dashboard charts (buy vs sell split, sector/insider heatmaps), add tooltip-rich panels, and consider dark mode styling.
3. **Real-Time Infrastructure Hardening**
   - Replace in-memory broadcaster with Redis/pub-sub or similar for multi-instance deployments; layer in authentication/authorization for WebSocket consumers.
4. **Performance**
   - Consider code-splitting Recharts into async chunk or lazy-load sparkline to tame bundle warning.
5. **Testing**
   - Add unit tests for filter helpers, WebSocket hook, and backend broadcast manager; ensure CI covers new modules.

## Operational Reminders
- Backend uses Dockerized Postgres and FastAPI (see `docker-compose.yml`).
- When running locally without Docker, ensure env vars match `.env.example` and start uvicorn with reload.
- WebSocket path: `ws://localhost:8000/api/v1/trades/stream` (switch to `wss://` if hosting behind TLS).

## Quick Reference – Key Files Updated
- Backend: `app/routers/trades.py`, `app/services/trade_service.py`, `app/services/trade_event_manager.py`.
- Frontend: `src/pages/TradesPage.tsx`, `src/pages/Dashboard.tsx`, `src/components/trades/TradeList.tsx`, `src/components/trades/TradeValueSparkline.tsx`, `src/hooks/useTradeStream.ts`, `src/types/index.ts`, `src/api/trades.ts`.
- Docs/Handoff: `claude.md` (this file).

## Contact & Context
- All previous work assumed seed/demo data; derivative trades may lack price/value in the dataset – noted in UI.
- If new trades are posted while frontend disconnected, a manual refresh re-syncs data (React Query refetch on mount).

