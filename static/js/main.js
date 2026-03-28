/* =============================================
   FinTrack — main.js
   Interações frontend: confirmações, clipboard,
   sidebar ativa, Chart.js, presets de data
   ============================================= */

// ── SIDEBAR: marcar item ativo com base na URL ──
document.addEventListener('DOMContentLoaded', function () {
  var path = window.location.pathname;
  document.querySelectorAll('.sb-item[data-page]').forEach(function (el) {
    var page = el.getAttribute('data-page');
    if (path.includes(page)) {
      el.classList.add('on');
    } else {
      el.classList.remove('on');
    }
  });

  // ── FLASH: auto-esconder após 4s ──
  document.querySelectorAll('.flash').forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity .4s';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 400);
    }, 4000);
  });

  // ── CONFIRMAÇÃO de exclusão ──
  document.querySelectorAll('[data-confirm]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      if (!confirm(btn.getAttribute('data-confirm'))) {
        e.preventDefault();
      }
    });
  });

  // ── COPIAR código de barras ──
  document.querySelectorAll('.btn-copy-cod').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var cod = btn.getAttribute('data-cod');
      if (!cod) return;
      navigator.clipboard.writeText(cod).then(function () {
        var orig = btn.textContent;
        btn.textContent = '✓ Copiado';
        setTimeout(function () { btn.textContent = orig; }, 2000);
      });
    });
  });

  // ── PRESET de datas (Exportar por período) ──
  initPresets();

  // ── CHARTS do dashboard ──
  initDashboardChart();
});

// ── PRESETS DE DATA ──
function initPresets() {
  var presets = document.querySelectorAll('.pr-b[data-preset]');
  if (!presets.length) return;

  var dtI = document.getElementById('dt-i');
  var dtF = document.getElementById('dt-f');
  if (!dtI || !dtF) return;

  presets.forEach(function (btn) {
    btn.addEventListener('click', function () {
      presets.forEach(function (b) { b.classList.remove('on'); });
      btn.classList.add('on');

      var p = btn.getAttribute('data-preset');
      var isCustom = p === 'custom';

      setLock(!isCustom, dtI, dtF);

      if (!isCustom) {
        var dates = calcPreset(p);
        dtI.value = dates[0];
        dtF.value = dates[1];
      }
    });
  });
}

function calcPreset(p) {
  var h = new Date();
  var i, f = h;
  if (p === 'mes')  { i = new Date(h.getFullYear(), h.getMonth(), 1); }
  else if (p === '30')  { i = new Date(h); i.setDate(i.getDate() - 30); }
  else if (p === '90')  { i = new Date(h); i.setDate(i.getDate() - 90); }
  else if (p === 'ano') { i = new Date(h.getFullYear(), 0, 1); }
  else if (p === 'tudo'){ i = new Date('2020-01-01'); f = new Date('2030-12-31'); }
  return [i.toISOString().slice(0, 10), f.toISOString().slice(0, 10)];
}

function setLock(locked, dtI, dtF) {
  [
    { inp: dtI, lockEl: document.getElementById('dt-i-lock'), lblEl: document.getElementById('dt-lock-i') },
    { inp: dtF, lockEl: document.getElementById('dt-f-lock'), lblEl: document.getElementById('dt-lock-f') },
  ].forEach(function (item) {
    if (!item.inp) return;
    if (locked) {
      item.inp.setAttribute('readonly', '');
      item.inp.style.cssText = 'cursor:default;color:var(--text2);pointer-events:none';
      if (item.lockEl) item.lockEl.style.display = '';
      if (item.lblEl) { item.lblEl.textContent = '🔒 Automático'; item.lblEl.style.color = 'var(--text3)'; }
    } else {
      item.inp.removeAttribute('readonly');
      item.inp.style.cssText = 'cursor:text;color:var(--text0);pointer-events:auto;border-color:rgba(232,168,56,.3)';
      if (item.lockEl) item.lockEl.style.display = 'none';
      if (item.lblEl) { item.lblEl.textContent = '✏ Editável'; item.lblEl.style.color = 'var(--amber)'; }
    }
  });
}

// ── CHART DO DASHBOARD ──
function initDashboardChart() {
  var el = document.getElementById('chartDashboard');
  if (!el || typeof Chart === 'undefined') return;

  var labels = JSON.parse(el.getAttribute('data-labels') || '[]');
  var values = JSON.parse(el.getAttribute('data-values') || '[]');
  var colors = JSON.parse(el.getAttribute('data-colors') || '[]');

  Chart.defaults.color = '#717a9a';

  new Chart(el, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: colors,
        borderWidth: 0,
        hoverOffset: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            font: { family: 'Outfit', size: 12 },
            padding: 14,
            boxWidth: 10,
            boxHeight: 10,
            borderRadius: 5,
            usePointStyle: true,
          },
        },
        tooltip: {
          backgroundColor: '#1e2232',
          borderColor: '#252a3a',
          borderWidth: 1,
          padding: 12,
          titleFont: { family: 'Outfit', size: 13 },
          bodyFont: { family: 'JetBrains Mono', size: 12 },
          callbacks: {
            label: function (ctx) {
              return '  R$ ' + ctx.parsed.toFixed(2).replace('.', ',');
            },
          },
        },
      },
      cutout: '64%',
    },
  });
}

// ── TOGGLE MARCAR/DESMARCAR checkbox visual ──
function togCk(id) {
  var b = document.getElementById('ck-' + id);
  if (!b) return;
  var on = b.classList.contains('on');
  b.classList.toggle('on', !on);
  b.textContent = !on ? '✓' : '';
  var inp = document.querySelector('input[name="modulos"][value="' + id + '"]');
  if (inp) inp.checked = !on;
}

function saAll(v) {
  document.querySelectorAll('.ckb').forEach(function (b) {
    b.classList.toggle('on', v);
    b.textContent = v ? '✓' : '';
  });
  document.querySelectorAll('input[name="modulos"]').forEach(function (inp) {
    inp.checked = v;
  });
}
