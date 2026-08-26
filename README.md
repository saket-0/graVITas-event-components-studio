# GraVITas '26 — Event Components Studio v9

Control-first Figma plugin for generating editable event component instances from one or more Excel files. Robust rebuild of v8 with fail-safe image fetching and zero-resolution-loss guarantees.

## v9 changes

### 5-Tier Image Pipeline (with retry)
Every image goes through up to 5 fallback strategies, each with 2 attempts and exponential backoff:
1. **Direct fetch** (UI browser) — fastest path, ~200ms
2. **Postimg og:image recovery** — fixes 403s and page URLs from postimg.cc
3. **CORS proxy** (images.weserv.nl) — bypasses CORS blocks
4. **`figma.createImageAsync` (direct)** — Figma's own network stack, completely different from the browser
5. **`figma.createImageAsync` + proxy** — last resort, Figma runtime via proxy

### Resolution Preservation
- **PNG and JPEG images pass through raw** — zero processing, zero re-encoding, zero resolution change
- **WebP/GIF/BMP/other formats** are converted to PNG at **full native resolution** via canvas using `naturalWidth`/`naturalHeight`
- **No resize parameters** are ever added to proxy URLs
- Resolution is logged when format conversion occurs for transparency

### Fail-Safe Mechanisms
- **Image byte validation**: checks PNG/JPEG magic bytes before sending to Figma; catches corrupt downloads, HTML error pages, and truncated data
- **Font pre-warming**: Inter Medium and Inter Regular are loaded once at session preparation, not per-instance
- **Health check monitor**: pings Figma bridge every 10s, shows ⚠ Disconnected if unresponsive
- **Deduplication**: skips duplicate events (same name + URL) when loading the same Excel file twice
- **Graceful node-not-found**: if a component is deleted mid-run, the error is caught and logged rather than crashing
- **Prefetch error logging**: prefetch failures are logged instead of silently swallowed

### UX Improvements
- **Batch summary** at end of run — succeeded/failed counts, tier breakdown, list of failures
- **ETA display** based on rolling average of processing times
- **Color-coded activity log** — green for success, red for errors, yellow for warnings
- **Tier badges** on queue items showing which fetch method succeeded
- **Connection status indicator** in header
- **Refetch failed** now tries all 5 tiers (was limited to UI tiers in v8)

### Preserved from v8
- Multiple Excel files, CSV/TSV support, self-contained XLSX parser (no dependencies)
- Chronological sorting, date cutoff filter
- Master component + instances pattern
- Auto-stream / one-at-a-time modes
- Pause / Stop / Reset session
- Live progress with preview
- Rolling prefetch window (3 events ahead)
- No bundled data, no automatic work at launch
