const $ = id => document.getElementById(id);
const esc = s => s == null ? '' : String(s)
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

function normalizeUrl(raw) {
  raw = (raw || '').trim();
  if (!raw) return null;
  if (/^https?:\/\//i.test(raw)) return raw;
  return 'https://' + raw;
}

function cls(status) {
  if (!status) return 'info';
  const s = status.toUpperCase();
  if (s.includes('✅') || s.includes('ХОРОШО') || s.includes('ЗАЩИЩЕН') || s.includes('ОТСУТСТВУЕТ')) return 'ok';
  if (s.includes('❌') || s.includes('КРИТИЧНО') || s.includes('УТЕЧКА') || s.includes('ОШИБКА')) return 'crit';
  if (s.includes('⚠') || s.includes('ВНИМАНИЕ') || s.includes('ПУБЛИЧНЫЙ')) return 'warn';
  return 'info';
}

const TAG = { ok:'ЗАЩИЩЕНО', crit:'КРИТИЧНО', warn:'ПРЕДУПРЕЖДЕНИЕ', info:'ИНФОРМАЦИЯ' };

function mkCard(name, status, risk, exploit, fix, critical, value) {
  const c   = cls(status);
  const safe = c === 'ok';
  let body = '';
  if (value)            body += mkRow('Значение', value);
  if (!safe && risk)    body += mkRow('Риск', risk);
  if (!safe && exploit) body += mkRow('Вектор атаки', exploit);
  const fixHtml = (!safe && fix) ? `<div class="c-fix">${esc(fix)}</div>` : '';
  return `<div class="card ${c}">
    <div class="c-tag">${TAG[c]}</div>
    <div class="c-name">${esc(name)}</div>
    ${body}${fixHtml}
  </div>`;
}

function mkRow(lbl, val) {
  return `<div class="c-row">
    <div class="c-row-lbl">${esc(lbl)}</div>
    <div class="c-row-val">${esc(val)}</div>
  </div>`;
}

const PHASES = [
  'Разрешение имени хоста...',
  'Проверка доступности...',
  'Анализ HTTP-заголовков...',
  'Зондирование открытых портов...',
  'Проверка SSL-сертификата...',
  'Поиск утечек информации...',
  'Определение технологий...',
  'Формирование отчёта...',
];

let phaseTimer = null, phaseIdx = 0;
const REDUCED_MOTION = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
let revealObserver = null;

function startPhaseAnim() {
  phaseIdx = 0;
  $('progFill').style.width = '5%';
  $('progTxt').textContent = PHASES[0];
  phaseTimer = setInterval(() => {
    phaseIdx = Math.min(phaseIdx + 1, PHASES.length - 1);
    $('progTxt').textContent = PHASES[phaseIdx];
    $('progFill').style.width = Math.min(5 + phaseIdx / (PHASES.length - 1) * 88, 93) + '%';
  }, 900);
}

function stopPhaseAnim() {
  clearInterval(phaseTimer);
  $('progFill').style.width = '100%';
  setTimeout(() => { $('progFill').style.width = '0%'; }, 700);
}

function resetBtn() {
  $('scanBtn').disabled    = false;
  $('scanBtn').textContent = 'Сканировать';
  $('scanProgress').classList.remove('on');
}

function showErr(msg) {
  const el = $('errMsg');
  el.textContent   = '— ' + msg;
  el.style.display = 'block';
}

async function startScan() {
  const raw = $('urlInput').value.trim();
  const url = normalizeUrl(raw);

  if (!url) { showErr('Введите адрес сайта'); return; }
  $('errMsg').style.display = 'none';

  $('scanBtn').disabled    = true;
  $('scanBtn').textContent = 'Сканирование...';
  $('scanProgress').classList.add('on');
  $('results').classList.remove('on');
  $('downArrow').classList.remove('vis');
  startPhaseAnim();

  try {
    const res  = await fetch('/scan', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ url }),
    });
    const data = await res.json();
    stopPhaseAnim();

    if (!res.ok || data.error) {
      showErr(data.error || 'Ошибка сканирования');
      resetBtn(); return;
    }
    renderResults(data);
  } catch (e) {
    stopPhaseAnim();
    showErr('Ошибка соединения — убедитесь, что сервер запущен');
    resetBtn();
  }
}

function renderResults(data) {
  resetBtn();

  $('sumUrl').textContent = data.url || '—';

  const rl = (data.risk_level || '').toUpperCase();
  let rkey = 'LOW';
  if (rl.includes('КРИТИЧЕСК') || rl.includes('CRITICAL')) rkey = 'CRITICAL';
  else if (rl.includes('ВЫСОК') || rl.includes('HIGH'))     rkey = 'HIGH';
  else if (rl.includes('СРЕДН') || rl.includes('MEDIUM'))   rkey = 'MEDIUM';

  const RISK_RU = { CRITICAL:'КРИТИЧЕСКИЙ', HIGH:'ВЫСОКИЙ', MEDIUM:'СРЕДНИЙ', LOW:'НИЗКИЙ' };
  const pill = $('riskPill');
  pill.className   = 'risk-pill rp-' + rkey;
  pill.textContent = RISK_RU[rkey] + ' РИСК';

  const badH  = (data.security_headers || []).filter(h => h.status?.includes('❌')).length;
  // ИСПРАВЛЕНО: считаем только опасные открытые порты
  const openP = (data.ports || []).filter(p => p.open && p.dangerous).length;
  const leaks = (data.info_disclosure || []).filter(i => String(i.status).includes('УТЕЧКА')).length;

  $('st-h').textContent = badH;
  $('st-p').textContent = openP;
  $('st-l').textContent = leaks;
  $('st-c').textContent = data.critical_count ?? '—';

  /* Заголовки */
  const gh = $('grid-h'); gh.innerHTML = '';
  (data.security_headers || []).forEach(h =>
    gh.innerHTML += mkCard(h.name, h.status, h.risk, h.exploit, h.fix, h.critical, h.value || h.message));
  $('cnt-h').textContent = (data.security_headers || []).length + ' проверок';

  /* SSL */
  const gs = $('grid-s'); gs.innerHTML = '';
  (data.ssl_security || []).forEach(s =>
    gs.innerHTML += mkCard(s.name, s.status, s.risk, s.exploit, s.fix, false, null));
  $('cnt-s').textContent = (data.ssl_security || []).length + ' проверок';

  /* Порты */
  const lp = $('list-p'); lp.innerHTML = '';
  (data.ports || []).forEach(p => {
    const isDangerous = p.open && p.dangerous;
    const isOpenSafe  = p.open && !p.dangerous;

    let badgeClass, badgeLabel;
    if (isDangerous)  { badgeClass = 'p-open';    badgeLabel = 'ОПАСЕН'; }
    else if (isOpenSafe) { badgeClass = 'p-warn';  badgeLabel = 'ОТКРЫТ'; }
    else               { badgeClass = 'p-closed'; badgeLabel = 'ЗАКРЫТ'; }

    lp.innerHTML += `<div class="port-row">
      <div class="p-num">${p.port}</div>
      <span class="p-badge ${badgeClass}">${badgeLabel}</span>
      <div>
        <div class="p-svc">${esc(p.service)}</div>
        ${p.open ? `<div class="p-risk">${esc(p.risk)}</div>` : ''}
      </div>
    </div>`;
  });
  $('cnt-p').textContent = openP + ' опасных';

  /* Технологии */
  const gt = $('grid-t'); gt.innerHTML = '';
  if ((data.technologies || []).length === 0) {
    gt.innerHTML = '<div class="no-data">Технологии не определены</div>';
  } else {
    (data.technologies || []).forEach(t =>
      gt.innerHTML += mkCard(t.name, t.type, t.risk, t.exploit, t.fix, false, null));
  }
  $('cnt-t').textContent = (data.technologies || []).length + ' найдено';

  /* Утечки */
  const li = $('list-i'); li.innerHTML = '';
  (data.info_disclosure || []).forEach(i => {
    const isLeak      = String(i.status).includes('УТЕЧКА');
    const isProtected = String(i.status).includes('ЗАЩИЩЕН') || String(i.status).includes('ОТСУТСТВУЕТ');
    const isPublic    = String(i.status).includes('ПУБЛИЧНЫЙ');

    let label, col;
    if (isLeak)      { label = 'УТЕЧКА';    col = 'var(--red)';   }
    else if (isPublic) { label = 'ПУБЛИЧНЫЙ'; col = 'var(--blue)'; }
    else             { label = 'ЗАЩИЩЁН';   col = 'var(--green)'; }

    li.innerHTML += `<div class="path-row">
      <div class="path-name">${esc(i.path)}</div>
      <div class="path-st" style="color:${col}">${label}</div>
      <div class="path-risk">${esc(i.risk || '')}</div>
    </div>`;
  });
  $('cnt-i').textContent = leaks + ' утечек';

  $('results').classList.add('on');

  const show = (id, ms) => setTimeout(() => { const el=$(id); el&&el.classList.add('show'); }, ms);
  show('summaryBar',  80);
  show('statsRow',   160);
  show('sec-headers', 280);
  show('sec-ssl',     400);
  show('sec-ports',   520);
  show('sec-tech',    640);
  show('sec-info',    760);

  setTimeout(() => {
    $('downArrow').classList.add('vis');
    scrollToResults();
  }, 200);

  setTimeout(() => {
    initScrollReveal($('results'));
  }, 100);
}

function scrollToResults() {
  window.scrollTo({ top: $('hero').offsetHeight - 60, behavior: 'smooth' });
}

$('urlInput').addEventListener('keydown', e => { if (e.key === 'Enter') startScan(); });

function clamp(v, min, max) {
  return Math.min(max, Math.max(min, v));
}

function initScrollReveal(root = document) {
  const nodes = root.querySelectorAll(
    '.summary-bar, .stats-row, .section, .card, .stat-box, .port-row, .path-row, footer'
  );

  if (!nodes.length) return;

  if (REDUCED_MOTION) {
    nodes.forEach((el) => {
      el.classList.add('reveal-on-scroll', 'in-view');
    });
    return;
  }

  if (!revealObserver) {
    revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('in-view');
        revealObserver.unobserve(entry.target);
      });
    }, {
      root: null,
      threshold: 0.14,
      rootMargin: '0px 0px -8% 0px'
    });
  }

  nodes.forEach((el, idx) => {
    if (el.dataset.revealInit === '1') return;
    el.dataset.revealInit = '1';
    el.classList.add('reveal-on-scroll');
    el.style.setProperty('--reveal-delay', `${Math.min(idx * 28, 280)}ms`);
    revealObserver.observe(el);
  });
}

function initCinematicMotion() {
  if (REDUCED_MOTION) return;

  const hero = $('hero');
  const cardsSelector = '.card, .stat-box';

  document.addEventListener('mousemove', (e) => {
    const mx = (e.clientX / window.innerWidth) * 100;
    const my = (e.clientY / window.innerHeight) * 100;
    document.body.style.setProperty('--mx', `${mx}%`);
    document.body.style.setProperty('--my', `${my}%`);

    const tiltY = ((mx - 50) / 50) * 2.2;
    const tiltX = ((50 - my) / 50) * 1.6;
    document.body.style.setProperty('--tilt-y', `${tiltY.toFixed(2)}deg`);
    document.body.style.setProperty('--tilt-x', `${tiltX.toFixed(2)}deg`);
  }, { passive: true });

  window.addEventListener('scroll', () => {
    const max = Math.max(document.body.scrollHeight - window.innerHeight, 1);
    const p = clamp(window.scrollY / max, 0, 1);
    document.body.style.setProperty('--scroll-p', p.toFixed(4));
    if (hero) {
      hero.style.transform = `translate3d(0, ${Math.round(window.scrollY * -0.05)}px, 0)`;
    }
  }, { passive: true });

  document.addEventListener('mouseover', (e) => {
    const target = e.target.closest(cardsSelector);
    if (!target) return;
    target.classList.add('is-hovered');
  });

  document.addEventListener('mouseout', (e) => {
    const target = e.target.closest(cardsSelector);
    if (!target) return;
    target.classList.remove('is-hovered');
    if (target.classList.contains('card')) {
      target.style.transform = '';
    }
  });

  document.addEventListener('mousemove', (e) => {
    const card = e.target.closest('.card');
    if (!card) return;

    const r = card.getBoundingClientRect();
    const px = ((e.clientX - r.left) / r.width) * 2 - 1;
    const py = ((e.clientY - r.top) / r.height) * 2 - 1;

    const rx = clamp(-py * 4.5, -5, 5);
    const ry = clamp(px * 6, -6, 6);
    card.style.transform = `translateY(-4px) rotateX(${rx.toFixed(2)}deg) rotateY(${ry.toFixed(2)}deg)`;
  }, { passive: true });
}

initCinematicMotion();
initScrollReveal(document);