const tree = document.querySelector('#docs-tree');
const content = document.querySelector('#content');
const currentPath = document.querySelector('#current-path');
const mirrorName = document.querySelector('#mirror-name');
const activePerspective = document.querySelector('#active-perspective');
const chooser = document.querySelector('#chooser');
const warning = document.querySelector('#warning');
const docsPanel = document.querySelector('#docs-panel');
const contentGrid = document.querySelector('.content-grid');
const tabs = [...document.querySelectorAll('[data-view]')];
let currentDocPath = null;
let docsLoaded = false;
let activeView = 'atlas';

async function boot() {
  const shell = await fetchJson('/api/shell');
  mirrorName.textContent = shell.mirror?.name || 'Local Mirror';
  showWarning(shell.warning);

  if (!shell.defaultPerspective) {
    chooser.hidden = true;
    activeView = 'atlas';
    await showView('atlas', { updateHash: false });
  } else {
    chooser.hidden = true;
    activeView = shell.defaultPerspective;
    await showView(activeView, { updateHash: false });
  }
}

function showWarning(message) {
  warning.hidden = !message;
  warning.textContent = message || '';
}

async function chooseDefault(perspective) {
  const result = await fetchJson('/api/preferences/default-perspective', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ defaultPerspective: perspective }),
  });
  showWarning(result.warning);
  chooser.hidden = !!result.defaultPerspective;
  await showView(result.defaultPerspective || perspective);
}

async function showView(view, { updateHash = true } = {}) {
  activeView = view;
  const docsActive = view === 'docs';
  docsPanel.hidden = !docsActive;
  currentPath.hidden = !docsActive;
  contentGrid.classList.toggle('docs-active', docsActive);
  tabs.forEach((tab) => tab.classList.toggle('active', tab.dataset.view === view));
  activePerspective.textContent = view === 'docs' ? 'Docs' : `Perspective · ${perspectiveLabel(view)}`;

  if (updateHash) {
    window.history.replaceState({ view }, '', `#${view}`);
  }

  if (view === 'docs') {
    await loadTree();
    return;
  }

  const surface = await fetchJson(`/api/surface/${view}`);
  currentPath.textContent = view === 'atlas' ? 'Identity' : 'Workspace';
  content.innerHTML = view === 'atlas' ? renderAtlas(surface) : renderWorkspace(surface);
  window.scrollTo({ top: 0 });
}

function renderAtlas(surface) {
  const regions = (surface.regions || []).map(renderAtlasRegion).join('');
  return `
    <section class="surface-intro atlas-hero">
      <p class="eyebrow">Identity Map</p>
      <h2>How your Mirror reflects you today</h2>
      <p>${escapeHtml(surface.synthesis || 'Identity map is ready for Mirror visibility.')}</p>
    </section>
    <div class="atlas-map" aria-label="Identity map">${regions}</div>
  `;
}

function renderWorkspace(surface) {
  const sections = (surface.sections || []).map(renderWorkspaceSection).join('');
  return `
    <section class="surface-intro">
      <p class="eyebrow">Workspace</p>
      <h2>Operational dashboard</h2>
      <p>${escapeHtml(surface.status || 'Read-only operational overview')}</p>
    </section>
    <div class="section-stack">${sections}</div>
  `;
}

function renderAtlasRegion(region) {
  const role = region.metadata?.atlas_role || 'support';
  if (['self', 'ego', 'shadow'].includes(role)) {
    return renderConceptRegion(region, role);
  }
  if (role === 'personas') {
    return renderPersonaRegion(region);
  }

  const readiness = region.metadata?.data_readiness || 'unknown';
  const cards = (region.cards || [])
    .slice(0, 8)
    .map((card) => (card.kind === 'memory-category' ? renderMemoryCategory(card) : renderCard(card)))
    .join('');
  return `
    <section class="atlas-region atlas-${escapeHtml(role)} readiness-${escapeHtml(readiness)}">
      <div>
        <h3>${escapeHtml(region.title)}</h3>
        <p>${escapeHtml(region.description)}</p>
      </div>
      ${cards ? `<div class="card-grid atlas-cards">${cards}</div>` : `<p class="empty-state">${escapeHtml(region.empty_state || 'Nothing to show yet.')}</p>`}
    </section>
  `;
}

function renderPersonaRegion(region) {
  const people = (region.cards || []).map(renderPersonaToken).join('');
  const chips = (region.metadata?.chips || [])
    .map((chip) => `<span>${escapeHtml(chip)}</span>`)
    .join('');
  return `
    <section class="atlas-region atlas-personas persona-team">
      <div class="team-copy concept-side">
        <div class="concept-icon" aria-label="${escapeHtml(region.title)}">${escapeHtml(region.metadata?.icon || '✣')}</div>
        <p class="concept-kicker">${escapeHtml(region.title)}</p>
        <h3>${escapeHtml(region.metadata?.motif || 'Team')}</h3>
        <p>${escapeHtml(region.description)}</p>
        ${chips ? `<div class="variant-list concept-chips" aria-label="Concepts">${chips}</div>` : ''}
      </div>
      ${people ? `<div class="persona-orbit" aria-label="Persona team">${people}</div>` : `<p class="empty-state">${escapeHtml(region.empty_state || 'No personas are available yet.')}</p>`}
    </section>
  `;
}

function renderPersonaToken(card) {
  const initials = card.metadata?.icon || card.title.slice(0, 2).toUpperCase();
  const label = card.metadata?.display_label || card.title;
  return `
    <button type="button" class="persona-token" title="${escapeHtml(card.title)}" data-object-kind="${escapeHtml(card.kind)}" data-object-id="${escapeHtml(card.id)}">
      <span class="persona-avatar">${escapeHtml(initials)}</span>
      <span>${escapeHtml(label)}</span>
    </button>
  `;
}

function renderConceptRegion(region, role) {
  const card = (region.cards || [])[0];
  const icon = card?.metadata?.icon || conceptFallbackIcon(role);
  const title = card?.title || region.title;
  const description = card?.description || region.description;
  const chips = (card?.metadata?.chips || [])
    .map((chip) => `<span>${escapeHtml(chip)}</span>`)
    .join('');
  const variants = (card?.metadata?.variants || [])
    .map((variant) => `<span>${escapeHtml(variant.label || variant.key)}</span>`)
    .join('');
  const target = objectTargetFromHref(card?.href) || (card ? { kind: card.kind, id: card.id } : null);
  const targetAttrs = target ? ` role="button" tabindex="0" data-object-kind="${escapeHtml(target.kind)}" data-object-id="${escapeHtml(target.id)}"` : '';
  return `
    <section class="atlas-region atlas-concept atlas-${escapeHtml(role)}"${targetAttrs}>
      <div class="concept-icon" aria-label="${escapeHtml(region.title)}">${escapeHtml(icon)}</div>
      <p class="concept-kicker">${escapeHtml(region.title)}</p>
      <h3>${escapeHtml(title)}</h3>
      <p>${escapeHtml(description)}</p>
      ${chips ? `<div class="variant-list concept-chips" aria-label="Concepts">${chips}</div>` : ''}
      ${variants ? `<div class="variant-list concept-chips" aria-label="Available layers">${variants}</div>` : ''}
      ${!card && region.empty_state ? `<p class="empty-state">${escapeHtml(region.empty_state)}</p>` : ''}
    </section>
  `;
}

function conceptFallbackIcon(role) {
  if (role === 'self') return '♛';
  if (role === 'ego') return '◉';
  if (role === 'shadow') return '◐';
  return '◇';
}

function renderWorkspaceSection(section) {
  const cards = (section.cards || []).map(renderCard).join('');
  return `
    <section class="surface-group wide">
      <div>
        <p class="eyebrow">${escapeHtml(section.id)}</p>
        <h3>${escapeHtml(section.title)}</h3>
        ${section.description ? `<p>${escapeHtml(section.description)}</p>` : ''}
      </div>
      ${cards ? `<div class="card-grid compact">${cards}</div>` : `<p class="empty-state">${escapeHtml(section.empty_state || 'Nothing to show yet.')}</p>`}
    </section>
  `;
}

async function loadObject(kind, id) {
  activeView = 'object';
  docsPanel.hidden = true;
  currentPath.hidden = true;
  contentGrid.classList.remove('docs-active');
  tabs.forEach((tab) => tab.classList.remove('active'));
  activePerspective.textContent = 'Perspective · Identity';

  const encodedKind = encodeURIComponent(kind);
  const encodedId = encodeURIComponent(id);
  const response = await fetch(`/api/surface/object?kind=${encodedKind}&id=${encodedId}`);
  const detail = await response.json();
  if (!response.ok) {
    content.innerHTML = renderObjectError(detail.error || 'Object not found');
    return;
  }
  content.innerHTML = renderObjectDetail(detail);
  window.scrollTo({ top: 0 });
}

function renderObjectError(message) {
  return `
    <section class="surface-intro">
      <button type="button" class="text-link" data-back-view="atlas">← Back to Identity Map</button>
      <p class="eyebrow">Object detail</p>
      <h2>Object not found</h2>
      <p>${escapeHtml(message)}</p>
    </section>
  `;
}

function renderObjectDetail(detail) {
  const metadata = detail.metadata || {};
  const chips = (metadata.chips || [])
    .map((chip) => `<span>${escapeHtml(chip)}</span>`)
    .join('');
  const relationships = (detail.relationships || [])
    .map(renderRelationship)
    .join('');
  const renderedContent = renderDetailContent(detail.content || 'No content available.');
  const metadataRows = Object.entries(metadata)
    .filter(([key]) => !['chips', 'icon'].includes(key))
    .map(([key, value]) => `<div><span>${escapeHtml(key)}</span><strong>${escapeHtml(value ?? '')}</strong></div>`)
    .join('');
  const source = detail.source || {};
  return `
    <button type="button" class="text-link detail-back" data-back-view="atlas">← Back to Identity Map</button>
    <section class="object-detail">
      <div class="object-summary">
        <div class="concept-icon" aria-label="${escapeHtml(metadata.public_kind || detail.kind)}">${escapeHtml(metadata.icon || '◇')}</div>
        <p class="concept-kicker">${escapeHtml(metadata.public_kind || detail.kind)}</p>
        <h2>${escapeHtml(detail.title)}</h2>
        <p>${escapeHtml(detail.description || '')}</p>
        ${chips ? `<div class="variant-list concept-chips" aria-label="Concepts">${chips}</div>` : ''}
      </div>
      <aside class="source-panel">
        <p class="eyebrow">${escapeHtml(source.label || 'Source')}</p>
        <h3>Where this comes from</h3>
        <p>${escapeHtml(source.description || 'No source context is available yet.')}</p>
        ${source.path ? `<code>${escapeHtml(source.path)}</code>` : ''}
        ${source.provenance_state ? `<p class="source-state">${escapeHtml(source.provenance_state)}</p>` : ''}
      </aside>
      <section class="detail-block detail-content">
        <p class="eyebrow">Content</p>
        <div class="rendered-content">${renderedContent}</div>
      </section>
      <section class="detail-block">
        <p class="eyebrow">Related</p>
        ${relationships ? `<div class="relationship-list">${relationships}</div>` : `<p class="empty-state">No related objects are available yet.</p>`}
      </section>
      <section class="detail-block">
        <p class="eyebrow">Metadata</p>
        ${metadataRows ? `<div class="metadata-list">${metadataRows}</div>` : `<p class="empty-state">No metadata available.</p>`}
      </section>
    </section>
  `;
}

function renderRelationship(link) {
  if (link.kind === 'identity' && link.id) {
    return `<button type="button" class="relationship-pill" data-object-kind="identity" data-object-id="${escapeHtml(link.id)}">${escapeHtml(link.label)}</button>`;
  }
  return `<span class="relationship-pill muted">${escapeHtml(link.label)}</span>`;
}

function renderDetailContent(content) {
  if (!looksLikeMarkdown(content)) {
    return `<pre>${escapeHtml(content)}</pre>`;
  }

  const lines = content.split('\n');
  const blocks = [];
  let paragraph = [];
  let list = [];
  let code = [];
  let inCode = false;

  const flushParagraph = () => {
    if (!paragraph.length) return;
    blocks.push(`<p>${escapeHtml(paragraph.join(' '))}</p>`);
    paragraph = [];
  };
  const flushList = () => {
    if (!list.length) return;
    blocks.push(`<ul>${list.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`);
    list = [];
  };
  const flushCode = () => {
    blocks.push(`<pre><code>${escapeHtml(code.join('\n'))}</code></pre>`);
    code = [];
  };

  for (const line of lines) {
    if (line.trim().startsWith('```')) {
      if (inCode) {
        flushCode();
        inCode = false;
      } else {
        flushParagraph();
        flushList();
        inCode = true;
      }
      continue;
    }
    if (inCode) {
      code.push(line);
      continue;
    }

    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      flushParagraph();
      flushList();
      const level = heading[1].length + 2;
      blocks.push(`<h${level}>${escapeHtml(heading[2])}</h${level}>`);
      continue;
    }

    const bullet = line.match(/^\s*[-*]\s+(.+)$/);
    if (bullet) {
      flushParagraph();
      list.push(bullet[1]);
      continue;
    }

    if (!line.trim()) {
      flushParagraph();
      flushList();
      continue;
    }

    flushList();
    paragraph.push(line.trim());
  }
  flushParagraph();
  flushList();
  if (inCode) flushCode();

  return blocks.join('\n') || `<pre>${escapeHtml(content)}</pre>`;
}

function looksLikeMarkdown(content) {
  return /(^|\n)#{1,6}\s+\S/.test(content)
    || /(^|\n)\s*[-*]\s+\S/.test(content)
    || /(^|\n)```/.test(content);
}

function objectTargetFromHref(href) {
  const match = String(href || '').match(/^\/objects\/([^/]+)\/(.+)$/);
  if (!match) return null;
  return { kind: decodeURIComponent(match[1]), id: decodeURIComponent(match[2]) };
}

function renderMemoryCategory(card) {
  const ratio = Math.max(0.04, Math.min(1, Number(card.metadata?.bar_ratio || 0)));
  return `
    <article class="memory-type">
      <div class="memory-type-head">
        <span class="memory-type-icon" aria-hidden="true">${escapeHtml(card.metadata?.icon || '◫')}</span>
        <span>${escapeHtml(card.title)}</span>
        <strong>${escapeHtml(card.count ?? 0)}</strong>
      </div>
      <div class="memory-bar" aria-hidden="true"><span style="width: ${ratio * 100}%"></span></div>
    </article>
  `;
}

function renderCard(card) {
  const icon = card.metadata?.icon || card.title?.slice(0, 1) || '?';
  const iconKind = card.metadata?.icon_kind || 'glyph';
  const label = card.metadata?.display_label ?? card.title;
  const variants = (card.metadata?.variants || [])
    .map((variant) => `<span>${escapeHtml(variant.label || variant.key)}</span>`)
    .join('');
  const chips = (card.metadata?.chips || [])
    .map((chip) => `<span>${escapeHtml(chip)}</span>`)
    .join('');
  return `
    <article class="surface-card">
      <div class="card-head">
        <div class="card-icon ${escapeHtml(iconKind)}" aria-label="${escapeHtml(card.title)}">${escapeHtml(icon)}</div>
        <div>
          <div class="card-meta">${escapeHtml(card.kind)}${card.status ? ` · ${escapeHtml(card.status)}` : ''}</div>
          ${label ? `<h4>${escapeHtml(label)}</h4>` : ''}
        </div>
      </div>
      <p>${escapeHtml(card.description || '')}</p>
      ${variants ? `<div class="variant-list" aria-label="Available layers">${variants}</div>` : ''}
      ${chips ? `<div class="variant-list" aria-label="Concepts">${chips}</div>` : ''}
    </article>
  `;
}

async function loadTree() {
  if (docsLoaded) {
    if (!currentDocPath) await loadInitialDoc();
    return;
  }

  const nodes = await fetchJson('/api/docs/tree');
  tree.innerHTML = '';
  const list = document.createElement('ul');
  list.className = 'doc-tree';
  for (const node of nodes) {
    list.appendChild(renderNode(node, 0));
  }
  tree.appendChild(list);
  docsLoaded = true;
  await loadInitialDoc(nodes);
}

async function loadInitialDoc(nodes = null) {
  const loadedNodes = nodes || await fetchJson('/api/docs/tree');
  const docsHome = findNodeByPath(loadedNodes, 'docs/index.md');
  const firstFile = findFirstFile(loadedNodes);
  const initialDoc = docsHome || firstFile;
  if (initialDoc) await loadDoc(initialDoc.path, { replace: true });
}

function renderNode(node, depth = 0) {
  const item = document.createElement('li');
  item.className = `tree-node ${node.type}`;

  if (node.type === 'directory') {
    const details = document.createElement('details');
    details.open = depth === 0;
    const summary = document.createElement('summary');
    summary.textContent = node.title;
    if (node.path) {
      summary.title = node.path;
      summary.addEventListener('click', () => loadDoc(node.path));
    }
    details.appendChild(summary);

    const list = document.createElement('ul');
    for (const child of node.children || []) {
      list.appendChild(renderNode(child, depth + 1));
    }
    details.appendChild(list);
    item.appendChild(details);
    return item;
  }

  const button = document.createElement('button');
  button.type = 'button';
  button.textContent = node.title;
  button.title = node.path;
  button.addEventListener('click', () => loadDoc(node.path));
  item.appendChild(button);
  return item;
}

function findFirstFile(nodes) {
  for (const node of nodes) {
    if (node.type === 'file') return node;
    const found = findFirstFile(node.children || []);
    if (found) return found;
  }
  return null;
}

function findNodeByPath(nodes, path) {
  for (const node of nodes) {
    if (node.path === path) return node;
    const found = findNodeByPath(node.children || [], path);
    if (found) return found;
  }
  return null;
}

async function loadDoc(path, { replace = false } = {}) {
  if (currentDocPath === path && !replace) return;

  const response = await fetch(`/api/docs/file?path=${encodeURIComponent(path)}`);
  const doc = await response.json();

  if (!response.ok) {
    currentPath.textContent = path;
    content.innerHTML = `<pre>${escapeHtml(doc.error || 'Could not load document')}</pre>`;
    return;
  }

  currentDocPath = doc.path;
  currentPath.hidden = false;
  currentPath.textContent = doc.path;
  content.innerHTML = doc.html;
  window.scrollTo({ top: 0 });
}

content.addEventListener('click', async (event) => {
  const objectTarget = event.target.closest('[data-object-kind][data-object-id]');
  if (objectTarget) {
    event.preventDefault();
    await loadObject(objectTarget.dataset.objectKind, objectTarget.dataset.objectId);
    return;
  }

  const backTarget = event.target.closest('[data-back-view]');
  if (backTarget) {
    event.preventDefault();
    await showView(backTarget.dataset.backView || 'atlas');
    return;
  }

  const link = event.target.closest('a');
  if (!link || activeView !== 'docs' || !currentDocPath) return;

  const href = link.getAttribute('href');
  if (!href || isExternalLink(href) || href.startsWith('#')) return;

  const resolved = resolveDocHref(currentDocPath, href);
  if (!resolved || !resolved.path.endsWith('.md')) return;

  event.preventDefault();
  await loadDoc(resolved.path);
  if (resolved.hash) {
    document.querySelector(resolved.hash)?.scrollIntoView();
  }
});

content.addEventListener('keydown', async (event) => {
  const objectTarget = event.target.closest('[data-object-kind][data-object-id]');
  if (!objectTarget || !['Enter', ' '].includes(event.key)) return;
  event.preventDefault();
  await loadObject(objectTarget.dataset.objectKind, objectTarget.dataset.objectId);
});

document.querySelectorAll('[data-choose]').forEach((button) => {
  button.addEventListener('click', () => chooseDefault(button.dataset.choose));
});

tabs.forEach((tab) => {
  tab.addEventListener('click', () => {
    if (tab.dataset.view === 'docs') {
      showView('docs');
      return;
    }
    chooseDefault(tab.dataset.view);
  });
});

function isExternalLink(href) {
  return /^(https?:|mailto:|tel:)/.test(href);
}

function resolveDocHref(basePath, href) {
  const [rawPath, rawHash] = href.split('#');
  if (!rawPath) return null;

  const baseParts = basePath.split('/');
  baseParts.pop();
  const parts = rawPath.startsWith('/') ? [] : baseParts;

  for (const part of rawPath.split('/')) {
    if (!part || part === '.') continue;
    if (part === '..') {
      parts.pop();
    } else {
      parts.push(part);
    }
  }

  return {
    path: parts.join('/'),
    hash: rawHash ? `#${CSS.escape(rawHash)}` : null,
  };
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || `Request failed: ${url}`);
  return payload;
}

function perspectiveLabel(value) {
  if (value === 'atlas') return 'Identity';
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

boot().catch((error) => {
  currentPath.textContent = 'Error';
  content.innerHTML = `<pre>${escapeHtml(String(error))}</pre>`;
});
