/**
 * RepoMind — Frontend Intelligence
 * Logic layer for SSE indexing, agentic Q&A, and obsidian view management.
 */

// ── Configuration ─────────────────────────────────────────────────────────
const API_BASE = window.location.origin;

// ── State ─────────────────────────────────────────────────────────────────
let currentRepo = null;
let isQuerying = false;

// ── DOM References ────────────────────────────────────────────────────────
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const views = {
    landing: $('#landing-view'),
    indexing: $('#indexing-view'),
    chat: $('#chat-view'),
};

const els = {
    repoUrlInput: $('#repo-url-input'),
    btnIndex: $('#btn-index'),
    indexingUrl: $('#indexing-repo-url'),
    progressLog: $('#indexing-log'),
    reposSection: $('#indexed-repos-section'),
    reposList: $('#repos-list'),
    chatMessages: $('#chat-messages'),
    chatWelcome: $('#chat-welcome'),
    chatInput: $('#chat-input'),
    btnSend: $('#btn-send'),
    btnBackHome: $('#btn-back-home'),
    headerRepoBadge: $('#header-repo-badge'),
    headerRepoName: $('.repo-name-text'),
    activeRepoBadge: $('#active-repo-badge'),
    activeRepoName: $('#active-repo-name'),
};

// ── Marked.js Configuration ──────────────────────────────────────────────
if (typeof marked !== 'undefined') {
    const renderer = new marked.Renderer();
    
    // Custom header rendering for Obsidian style
    renderer.heading = (text, level) => {
        const size = level === 1 ? '1.5rem' : level === 2 ? '1.2rem' : '1.1rem';
        return `<h${level} style="color: var(--brand-primary); margin: 20px 0 10px; font-size: ${size}; font-weight: 700;">${text}</h${level}>`;
    };

    marked.setOptions({
        renderer: renderer,
        highlight: function (code, lang) {
            if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
                return hljs.highlight(code, { language: lang }).value;
            }
            return code;
        },
        breaks: true,
        gfm: true,
    });
}

// ── View Management ──────────────────────────────────────────────────────

function showView(name) {
    Object.values(views).forEach((v) => v.classList.remove('active'));
    views[name].classList.add('active');

    if (name === 'chat') {
        els.headerRepoBadge.style.display = 'flex';
        els.activeRepoBadge.style.display = 'flex';
    } else {
        els.headerRepoBadge.style.display = 'none';
        els.activeRepoBadge.style.display = 'none';
    }
}

function goHome() {
    currentRepo = null;
    showView('landing');
    loadRepos();
}

// ── Load Repos ───────────────────────────────────────────────────────────

async function loadRepos() {
    try {
        const res = await fetch(`${API_BASE}/api/repos`);
        const data = await res.json();

        if (data.repos && data.repos.length > 0) {
            els.reposSection.style.display = 'block';
            els.reposList.innerHTML = data.repos
                .map(
                    (repo) => `
                <div class="repo-card" data-repo="${repo.name}">
                    <div class="repo-meta">
                        <span class="repo-title">${escapeHtml(repo.repo_name || repo.name)}</span>
                        <span class="repo-info-sub">${repo.chunk_count} nodes indexed</span>
                    </div>
                    <div class="repo-btn-group">
                        <button class="btn-secondary" onclick="event.stopPropagation(); openChat('${repo.name}')">Launch</button>
                        <button class="btn-danger" onclick="event.stopPropagation(); deleteRepo('${repo.name}')">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18m-2 0v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6m3 0V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                        </button>
                    </div>
                </div>
            `
                )
                .join('');

            $$('.repo-card').forEach((item) => {
                item.addEventListener('click', () => openChat(item.dataset.repo));
            });
        } else {
            els.reposSection.style.display = 'none';
        }
    } catch (e) {
        console.error('Core error: Failed to fetch repositories', e);
    }
}

// ── Delete Repo ──────────────────────────────────────────────────────────

async function deleteRepo(repoName) {
    if (!confirm(`Purge index for "${repoName}"? This action is permanent.`)) return;
    try {
        await fetch(`${API_BASE}/api/repos/${encodeURIComponent(repoName)}`, {
            method: 'DELETE',
        });
        loadRepos();
    } catch (e) {
        console.error('Delete error', e);
    }
}

// ── Index Repository (SSE) ───────────────────────────────────────────────

function indexRepository(url) {
    els.indexingUrl.textContent = url;
    els.progressLog.innerHTML = '';
    showView('indexing');

    // Reset step indicators
    ['clone', 'parse', 'embed'].forEach((step) => {
        const el = $(`#step-${step}`);
        el.className = 'step-item';
        el.querySelector('.icon').textContent = '○';
    });

    els.btnIndex.disabled = true;

    fetch(`${API_BASE}/api/index`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
    })
        .then((response) => {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            function read() {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        els.btnIndex.disabled = false;
                        return;
                    }

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop();

                    for (const line of lines) {
                        if (line.startsWith('event:')) {
                            var currentEvent = line.substring(6).trim();
                        }
                        if (line.startsWith('data:')) {
                            try {
                                const data = JSON.parse(line.substring(5));
                                handleIndexEvent(currentEvent, data);
                            } catch (e) { /* skip */ }
                        }
                    }
                    read();
                });
            }
            read();
        })
        .catch((err) => {
            console.error('Index failed', err);
            els.btnIndex.disabled = false;
            showView('landing');
        });
}

function handleIndexEvent(event, data) {
    switch (event) {
        case 'progress':
            if (data.step) {
                const stepEl = $(`#step-${data.step}`);
                if (stepEl) {
                    stepEl.className = 'step-item active';
                    stepEl.querySelector('.icon').textContent = '⚡';

                    const order = ['clone', 'parse', 'embed'];
                    const idx = order.indexOf(data.step);
                    for (let i = 0; i < idx; i++) {
                        const prev = $(`#step-${order[i]}`);
                        prev.className = 'step-item done';
                        prev.querySelector('.icon').textContent = '●';
                    }
                }
            }
            if (data.message) {
                addProgressLog(data.message);
            }
            break;

        case 'complete':
            ['clone', 'parse', 'embed'].forEach((step) => {
                const el = $(`#step-${step}`);
                el.className = 'step-item done';
                el.querySelector('.icon').textContent = '●';
            });

            addProgressLog(`Verification complete: ${data.stats?.chunks || 0} nodes persisted.`);

            setTimeout(() => {
                els.btnIndex.disabled = false;
                openChat(data.repo_name);
            }, 1000);
            break;

        case 'error':
            els.btnIndex.disabled = false;
            setTimeout(() => showView('landing'), 2000);
            break;
    }
}

function addProgressLog(message) {
    const p = document.createElement('div');
    p.style.marginBottom = '2px';
    p.textContent = `> ${message}`;
    els.progressLog.appendChild(p);
    els.progressLog.scrollTop = els.progressLog.scrollHeight;
}

// ── Open Chat ────────────────────────────────────────────────────────────

function openChat(repoName) {
    currentRepo = repoName;
    const cleanName = repoName.replace('__', '/');
    els.headerRepoName.textContent = cleanName;
    els.activeRepoName.textContent = cleanName;
    els.chatMessages.innerHTML = '';
    els.chatMessages.appendChild(els.chatWelcome);
    els.chatWelcome.style.display = 'block';
    showView('chat');
    els.chatInput.focus();
}

// ── Send Query (SSE) ─────────────────────────────────────────────────────

function sendQuery(question) {
    if (!question.trim() || !currentRepo || isQuerying) return;

    isQuerying = true;
    els.btnSend.disabled = true;
    els.chatWelcome.style.display = 'none';

    addMessage('user', question);
    const loadingEl = addMessage('loading', '');

    els.chatInput.value = '';
    autoResizeTextarea();

    fetch(`${API_BASE}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_name: currentRepo, question }),
    })
        .then((response) => {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let answerData = null;
            const steps = [];

            function read() {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        loadingEl.remove();
                        if (answerData) {
                            addMessage('assistant', answerData.content, steps);
                        }
                        isQuerying = false;
                        els.btnSend.disabled = false;
                        els.chatInput.focus();
                        return;
                    }

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop();

                    let currentEvent = '';
                    for (const line of lines) {
                        if (line.startsWith('event:')) {
                            currentEvent = line.substring(6).trim();
                        }
                        if (line.startsWith('data:')) {
                            try {
                                const data = JSON.parse(line.substring(5));
                                if (currentEvent === 'step') {
                                    steps.push(data);
                                } else if (currentEvent === 'answer') {
                                    answerData = data;
                                }
                            } catch (e) { /* skip */ }
                        }
                    }
                    read();
                });
            }
            read();
        })
        .catch((err) => {
            loadingEl.remove();
            isQuerying = false;
            els.btnSend.disabled = false;
        });
}

// ── Message Rendering ────────────────────────────────────────────────────

function addMessage(type, content, steps = []) {
    const msgWrapper = document.createElement('div');
    msgWrapper.className = `msg-wrapper ${type}`;

    if (type === 'user') {
        msgWrapper.innerHTML = `<div class="chat-bubble">${escapeHtml(content)}</div>`;
    } else if (type === 'loading') {
        msgWrapper.classList.add('assistant');
        msgWrapper.innerHTML = `
            <div class="avatar">🧠</div>
            <div class="chat-bubble" style="display: flex; align-items: center; gap: 8px; color: var(--text-mid);">
                <div class="typing-dots"><span></span><span></span><span></span></div>
                Indexing state...
            </div>`;
    } else if (type === 'assistant') {
        const renderedContent = renderMarkdown(content);
        let stepsHtml = '';

        if (steps.length > 0) {
            const stepsItems = steps
                .map(
                    (s) => `
                <div style="padding: 10px; border-bottom: 1px solid var(--border-subtle); font-size: 11px;">
                    <div style="color: var(--brand-primary); font-weight: 700; font-family: var(--font-mono); margin-bottom: 4px;">🔧 ${escapeHtml(s.tool)}</div>
                    <div style="color: var(--text-mid); margin-bottom: 4px;">Input: ${escapeHtml(typeof s.input === 'string' ? s.input : JSON.stringify(s.input))}</div>
                    <div style="color: var(--text-low); white-space: pre-wrap; font-family: var(--font-mono); max-height: 100px; overflow-y: auto;">${escapeHtml(s.output || '')}</div>
                </div>`
                )
                .join('');

            stepsHtml = `
                <div class="reasoning-box">
                    <div class="reasoning-header" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">
                        ↳ Agentic Reasoning (${steps.length} steps)
                    </div>
                    <div class="reasoning-details" style="display: none;">${stepsItems}</div>
                </div>`;
        }

        msgWrapper.innerHTML = `
            <div class="avatar">🧠</div>
            <div class="chat-bubble">
                ${renderedContent}
                ${stepsHtml}
            </div>`;
    }

    els.chatMessages.appendChild(msgWrapper);
    scrollToBottom();

    msgWrapper.querySelectorAll('pre code').forEach((block) => {
        if (typeof hljs !== 'undefined') hljs.highlightElement(block);
    });

    return msgWrapper;
}

function renderMarkdown(text) {
    if (typeof marked !== 'undefined') return marked.parse(text || '');
    return `<p>${escapeHtml(text || '')}</p>`;
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function scrollToBottom() {
    els.chatMessages.scrollTop = els.chatMessages.scrollHeight;
}

function autoResizeTextarea() {
    const ta = els.chatInput;
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 200) + 'px';
}

// ── Event Listeners ──────────────────────────────────────────────────────

els.btnIndex.addEventListener('click', () => {
    const url = els.repoUrlInput.value.trim();
    if (!url || !url.includes('github.com')) return;
    indexRepository(url);
});

els.repoUrlInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') els.btnIndex.click();
});

els.btnSend.addEventListener('click', () => {
    sendQuery(els.chatInput.value.trim());
});

els.chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendQuery(els.chatInput.value.trim());
    }
});

els.chatInput.addEventListener('input', autoResizeTextarea);
els.btnBackHome.addEventListener('click', goHome);

$$('.example-q').forEach((btn) => {
    btn.addEventListener('click', () => {
        const q = btn.dataset.q;
        els.chatInput.value = q;
        sendQuery(q);
    });
});

// Initial load
loadRepos();
