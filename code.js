// ═══════════════════════════════════════════════════════════════════
// GraVITas '26 — Event Components Studio v9
// Robust rebuild: pre-warmed fonts, 5-tier image fallback,
// image validation, health checks, and graceful error recovery.
// ═══════════════════════════════════════════════════════════════════

figma.showUI(__html__, { width: 430, height: 860, themeColors: true });

// ── Utilities ──────────────────────────────────────────────────────

function hex(s) {
  s = String(s || '').replace('#', '');
  if (s.length === 3) s = s.split('').map(x => x + x).join('');
  const n = parseInt(s, 16);
  return {
    r: ((n >> 16) & 255) / 255,
    g: ((n >> 8) & 255) / 255,
    b: (n & 255) / 255,
  };
}

function solid(hexColor, opacity = 1) {
  return { type: 'SOLID', color: hex(hexColor), opacity };
}

function cleanName(s) {
  return String(s || 'Event')
    .replace(/[\\/:*?"<>|]/g, '-')
    .replace(/\s+/g, ' ')
    .trim();
}

function formatDate(v) {
  if (!v) return '';
  const d = new Date(v);
  if (isNaN(d.getTime())) return String(v).slice(0, 10);
  const months = [
    'JANUARY','FEBRUARY','MARCH','APRIL','MAY','JUNE',
    'JULY','AUGUST','SEPTEMBER','OCTOBER','NOVEMBER','DECEMBER',
  ];
  return `${String(d.getDate()).padStart(2, '0')} ${months[d.getMonth()]}`;
}

// ── Font Management (pre-warming) ─────────────────────────────────

let fontsWarmed = false;

async function warmFonts() {
  if (fontsWarmed) return;
  await Promise.all([
    figma.loadFontAsync({ family: 'Inter', style: 'Medium' }),
    figma.loadFontAsync({ family: 'Inter', style: 'Regular' }),
  ]);
  fontsWarmed = true;
}

async function makeText(parent, chars, size, color, weight) {
  await warmFonts();
  const n = figma.createText();
  parent.appendChild(n);
  n.fontName = { family: 'Inter', style: weight };
  n.fontSize = size;
  n.characters = String(chars || '').trim();
  n.fills = [solid(color)];
  n.textAutoResize = 'WIDTH_AND_HEIGHT';
  return n;
}

// ── Session State ─────────────────────────────────────────────────

let session = null;
let masterId = null;
let organizer = null;
let nextY = 0;
let masterOptions = null;

function resetSession() {
  session = null;
  masterId = null;
  organizer = null;
  nextY = 0;
  masterOptions = null;
  fontsWarmed = false;
}

// ── Organizer Frame ───────────────────────────────────────────────

async function ensureOrganizer() {
  if (organizer && !organizer.removed) return organizer;
  organizer = figma.createFrame();
  organizer.name = "GraVITas '26 — Generated Event Instances";
  organizer.fills = [];
  organizer.strokes = [];
  organizer.clipsContent = false;
  organizer.layoutMode = 'NONE';
  organizer.resize(1000, 10);
  const c = figma.viewport.center;
  organizer.x = c.x - 500;
  organizer.y = c.y - 40;
  organizer.setPluginData('generator', 'gravitas-event-components-studio-v9');
  return organizer;
}

// ── Master Component ──────────────────────────────────────────────

async function createMaster(options) {
  // Reuse existing master if it still exists
  if (masterId) {
    const existing = await figma.getNodeByIdAsync(masterId);
    if (existing && !existing.removed && existing.type === 'COMPONENT') return existing;
  }
  masterOptions = options;
  const iconSize  = Math.max(12, Number(options.iconSize) || 25);
  const gap       = Math.max(0,  Number(options.gap) || 6);
  const titleSize = Math.max(4,  Number(options.titleSize) || 8);
  const dateSize  = Math.max(4,  Number(options.dateSize) || 8);
  const titleColor = options.titleColor || '#8FEAFF';
  const dateColor  = options.dateColor || '#FFFFFF';

  const master = figma.createComponent();
  master.name = 'EVENT COMPONENT — MASTER';
  master.layoutMode = 'HORIZONTAL';
  master.primaryAxisSizingMode = 'AUTO';
  master.counterAxisSizingMode = 'AUTO';
  master.itemSpacing = gap;
  master.paddingTop = 0; master.paddingRight = 0;
  master.paddingBottom = 0; master.paddingLeft = 0;
  master.fills = []; master.strokes = [];
  master.clipsContent = false;
  master.x = 12; master.y = 0;
  master.setPluginData('role', 'master');
  master.setPluginData('generator', 'gravitas-event-components-studio-v9');

  // Logo placeholder rectangle
  const logo = figma.createRectangle();
  master.appendChild(logo);
  logo.name = 'Event Logo';
  logo.resize(iconSize, iconSize);
  logo.cornerRadius = Math.min(3, iconSize / 4);
  logo.fills = [solid('#FFFFFF', 0.10)];
  logo.strokes = [];
  logo.setPluginData('role', 'logo');

  // Text container (vertical auto-layout)
  const copy = figma.createFrame();
  master.appendChild(copy);
  copy.name = 'Event Text';
  copy.layoutMode = 'VERTICAL';
  copy.primaryAxisSizingMode = 'AUTO';
  copy.counterAxisSizingMode = 'AUTO';
  copy.itemSpacing = 1;
  copy.paddingTop = 0; copy.paddingRight = 0;
  copy.paddingBottom = 0; copy.paddingLeft = 0;
  copy.fills = []; copy.strokes = [];
  copy.clipsContent = false;

  const title = await makeText(copy, 'EVENT NAME', titleSize, titleColor, 'Medium');
  title.name = 'Event Name';
  const date = await makeText(copy, '01 JANUARY', dateSize, dateColor, 'Regular');
  date.name = 'Date';

  masterId = master.id;
  return master;
}

// ── Instance Creation ─────────────────────────────────────────────

function findChild(node, name, type) {
  return node.findOne(n => n.name === name && (!type || n.type === type));
}

async function createEventInstance(e, options, index) {
  const master = await createMaster(options);
  const parent = await ensureOrganizer();
  const instance = master.createInstance();
  parent.appendChild(instance);
  instance.name = `Event — ${cleanName(e.event_name)}`;
  instance.x = 12;
  instance.y = nextY;

  const title = findChild(instance, 'Event Name', 'TEXT');
  const date  = findChild(instance, 'Date', 'TEXT');
  const logo  = findChild(instance, 'Event Logo', 'RECTANGLE');
  if (!title || !date || !logo) {
    throw new Error('Master component structure is incomplete — expected Event Name, Date, and Event Logo children.');
  }

  await warmFonts(); // Already cached from session prep, this is a no-op
  title.characters = String(e.event_name || '').replace(/\s+/g, ' ').trim().toUpperCase();
  date.characters = formatDate(e.slot_start_datetime);

  title.setPluginData('event_index', String(index));
  date.setPluginData('event_index', String(index));
  logo.setPluginData('event_index', String(index));

  const h = Math.max(Number(options.iconSize) || 25, title.height + date.height + 1);
  nextY += h + 10;
  parent.resize(1000, Math.max(10, nextY));

  instance.setPluginData('event_name', String(e.event_name || ''));
  instance.setPluginData('image_url', String(e.image_url || ''));
  instance.setPluginData('slot_start_datetime', String(e.slot_start_datetime || ''));
  instance.setPluginData('slot_end_datetime', String(e.slot_end_datetime || ''));
  instance.setPluginData('source_index', String(index));
  instance.setPluginData('role', 'instance');
  instance.setPluginData('image_status', 'pending');

  if (options.follow !== false) {
    figma.currentPage.selection = [instance];
    figma.viewport.scrollAndZoomIntoView([instance]);
  }
  return { instanceId: instance.id, logoNodeId: logo.id, masterId: master.id };
}

// ── Image Byte Validation ─────────────────────────────────────────
// Validates raw bytes before passing them to figma.createImage().
// Catches corrupt downloads, HTML error pages, and truncated data.

function validateImageBytes(bytes) {
  if (!bytes || bytes.length < 67) {
    return { valid: false, reason: `Image too small (${bytes?.length || 0} bytes) — likely an error page, empty response, or truncated download.` };
  }
  const a = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);

  // PNG: 89 50 4E 47 0D 0A 1A 0A
  const isPng = a[0] === 0x89 && a[1] === 0x50 && a[2] === 0x4E && a[3] === 0x47;
  // JPEG: FF D8 FF
  const isJpeg = a[0] === 0xFF && a[1] === 0xD8 && a[2] === 0xFF;
  // GIF: 47 49 46 38
  const isGif = a[0] === 0x47 && a[1] === 0x49 && a[2] === 0x46 && a[3] === 0x38;
  // WebP: RIFF....WEBP
  const isWebP = a.length > 11 &&
    a[0] === 0x52 && a[1] === 0x49 && a[2] === 0x46 && a[3] === 0x46 &&
    a[8] === 0x57 && a[9] === 0x45 && a[10] === 0x42 && a[11] === 0x50;
  // BMP: 42 4D
  const isBmp = a[0] === 0x42 && a[1] === 0x4D;
  // SVG: starts with < (XML/SVG preamble)
  const isSvg = a[0] === 0x3C && String.fromCharCode(...a.slice(0, 100)).includes('<svg');

  if (isPng || isJpeg || isGif || isWebP || isBmp) {
    const format = isPng ? 'PNG' : isJpeg ? 'JPEG' : isGif ? 'GIF' : isWebP ? 'WebP' : 'BMP';
    return { valid: true, format };
  }

  if (isSvg) {
    // SVGs can't be directly used with figma.createImage — they need rasterization
    return { valid: false, reason: 'Image is SVG — requires rasterization before use in Figma. Will be handled by proxy.' };
  }

  // Check if response is actually HTML (common for error pages / 403s)
  const head = String.fromCharCode(...a.slice(0, Math.min(200, a.length)));
  if (head.includes('<!') || head.includes('<html') || head.includes('<HTML') || head.includes('<!DOCTYPE')) {
    return { valid: false, reason: 'Response is an HTML page (likely an error page, 403, or redirect), not an image.' };
  }

  return { valid: false, reason: 'Unrecognized file format (not PNG, JPEG, GIF, WebP, or BMP).' };
}

// ── Apply Logo from Raw Bytes (UI sends bytes — Tiers 1-3) ───────

async function applyLogo(nodeId, bytes) {
  if (!nodeId) throw new Error('Missing logo node ID.');
  if (!bytes || !bytes.length) throw new Error('No image bytes received.');

  const node = await figma.getNodeByIdAsync(nodeId);
  if (!node) throw new Error('Logo node was deleted or could not be found. It may have been removed from the canvas.');
  if (node.type !== 'RECTANGLE') throw new Error(`Expected logo rectangle, got ${node.type}.`);

  const validation = validateImageBytes(bytes);
  if (!validation.valid) throw new Error(`Image validation failed: ${validation.reason}`);

  let image;
  try {
    image = figma.createImage(new Uint8Array(bytes));
  } catch (err) {
    throw new Error(`figma.createImage failed: ${err?.message || err} — the image data may be corrupt or in an unsupported format.`);
  }
  if (!image || !image.hash) {
    throw new Error('figma.createImage returned no image hash — the image data may be corrupt.');
  }

  node.fills = [{ type: 'IMAGE', imageHash: image.hash, scaleMode: 'FIT' }];
  node.setPluginData('image_status', 'ready');
  node.setPluginData('image_format', validation.format || 'unknown');

  // Bubble status up to the instance
  const instance = node.parent?.type === 'INSTANCE' ? node.parent : null;
  if (instance) instance.setPluginData('image_status', 'ready');

  return { imageHash: image.hash, nodeId: node.id, format: validation.format, source: 'ui-bytes' };
}

// ── Import Image via Figma Runtime (Tiers 4 & 5) ─────────────────
// Uses figma.createImageAsync — a different network stack than the
// UI iframe. This bypasses CORS entirely and works when the browser
// fetch fails but the image URL is otherwise valid.

function proxyImageUrl(url) {
  return `https://images.weserv.nl/?url=${encodeURIComponent(url)}&output=png`;
}

async function importImageViaFigma(nodeId, url, useProxy) {
  if (!nodeId) throw new Error('Missing logo node ID.');
  if (!url) throw new Error('No image URL.');

  const node = await figma.getNodeByIdAsync(nodeId);
  if (!node) throw new Error('Logo node was deleted or could not be found.');
  if (node.type !== 'RECTANGLE') throw new Error(`Expected logo rectangle, got ${node.type}.`);

  const fetchUrl = useProxy ? proxyImageUrl(url) : url;
  const source = useProxy ? 'figma-proxy' : 'figma-direct';

  let image;
  try {
    image = await figma.createImageAsync(fetchUrl);
  } catch (err) {
    throw new Error(`figma.createImageAsync (${source}) failed: ${err?.message || err}`);
  }
  if (!image || !image.hash) {
    throw new Error(`figma.createImageAsync (${source}) returned no image hash.`);
  }

  node.fills = [{ type: 'IMAGE', imageHash: image.hash, scaleMode: 'FIT' }];
  node.setPluginData('image_status', 'ready');
  node.setPluginData('image_source', source);
  node.setPluginData('image_url', String(url));

  const instance = node.parent?.type === 'INSTANCE' ? node.parent : null;
  if (instance) instance.setPluginData('image_status', 'ready');

  return { imageHash: image.hash, nodeId: node.id, source };
}

// ── Node Selection ────────────────────────────────────────────────

async function selectNode(nodeId) {
  try {
    const n = await figma.getNodeByIdAsync(nodeId);
    if (n) {
      figma.currentPage.selection = [n];
      figma.viewport.scrollAndZoomIntoView([n]);
    }
  } catch (_) {
    // Node may have been deleted — silently ignore
  }
}

// ── Message Handler ───────────────────────────────────────────────
// All UI ↔ code.js communication goes through this single handler.
// Every case has try/catch for graceful failure reporting.

figma.ui.onmessage = async (msg) => {
  try {
    switch (msg.type) {

      // ── Health check (connection monitor) ──
      case 'health-check':
        figma.ui.postMessage({ type: 'health-ok', ts: Date.now() });
        break;

      // ── Session lifecycle ──
      case 'prepare-session':
        resetSession();
        await warmFonts(); // Pre-warm fonts during preparation
        session = { id: Date.now().toString(), started: false, options: msg.options || {} };
        figma.ui.postMessage({ type: 'session-prepared' });
        break;

      case 'new-session':
        resetSession();
        figma.ui.postMessage({ type: 'session-reset' });
        break;

      // ── Component creation ──
      case 'create-skeleton': {
        if (!session) throw new Error('Session is not prepared. Press "Prepare session" first.');
        const result = await createEventInstance(msg.event, msg.options || {}, msg.index);
        figma.ui.postMessage({ type: 'skeleton-created', index: msg.index, ...result });
        break;
      }

      // ── Image application: raw bytes from UI (Tiers 1-3) ──
      case 'apply-logo-bytes': {
        const result = await applyLogo(msg.logoNodeId, msg.bytes || []);
        figma.ui.postMessage({ type: 'logo-applied', index: msg.index, ...result });
        break;
      }

      // ── Image import: Figma runtime fetch (Tiers 4 & 5) ──
      case 'import-logo': {
        const url = String(msg.url || '');
        let result, tier4Error;

        // Tier 4: Direct fetch via Figma's network stack
        try {
          result = await importImageViaFigma(msg.logoNodeId, url, false);
        } catch (err) {
          tier4Error = err;
          // Tier 5: Proxy fetch via Figma's network stack
          try {
            result = await importImageViaFigma(msg.logoNodeId, url, true);
          } catch (proxyErr) {
            throw new Error(
              `All Figma-runtime tiers failed.\n` +
              `  Tier 4 (figma-direct): ${tier4Error?.message || tier4Error}\n` +
              `  Tier 5 (figma-proxy): ${proxyErr?.message || proxyErr}`
            );
          }
        }
        figma.ui.postMessage({ type: 'logo-applied', index: msg.index, ...result });
        break;
      }

      // ── Misc ──
      case 'select-node':
        await selectNode(msg.nodeId);
        break;

      case 'close':
        figma.closePlugin();
        break;
    }
  } catch (err) {
    console.error('[GraVITas v9]', err);
    figma.ui.postMessage({
      type: 'plugin-error',
      index: msg.index,
      code: err.code || 'UNKNOWN',
      message: err?.message || String(err),
    });
  }
};
