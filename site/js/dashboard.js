/* Featured: Data & BI. A small Power BI-style report in vanilla JS.
   ALL numbers are synthetic and generated here from a fixed seed. They are not ODDO BHF data. */
(function () {
  'use strict';
  var dash = document.getElementById('dash');
  if (!dash) return;

  var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  var DOMAINS = ['Operations', 'Finance', 'IT', 'Risk', 'Retail'];

  /* Deterministic PRNG so the sample data never changes between visits. */
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  var rand = mulberry32(20260618);
  var rows = [];
  DOMAINS.forEach(function (d, di) {
    var size = 50 + di * 14;
    MONTHS.forEach(function (m, mi) {
      var wave = Math.sin((mi / 12) * Math.PI * 2 - 1);
      var season = 1 + 0.3 * wave;
      var enrolled = Math.round(size * season * (0.85 + rand() * 0.3));
      var rate = Math.min(0.98, 0.70 + di * 0.04 + 0.07 * wave + mi * 0.006 + rand() * 0.07);
      var attended = Math.round(enrolled * rate);
      var hours = Math.round(attended * (2.4 + rand() * 2.2));
      var responses = Math.max(5, Math.round(attended * (0.45 + rand() * 0.3)));
      var score = Math.min(4.9, 3.3 + di * 0.12 + 0.25 * wave + rand() * 0.7);
      rows.push({ d: d, m: mi, enrolled: enrolled, attended: attended, hours: hours, responses: responses, scoreSum: score * responses });
    });
  });

  var METRICS = {
    att: {
      label: 'Attendance', axis: function () { return 100; }, ticks: ['100%', '50%', '0'],
      value: function (r) { var e = sum(r, 'enrolled'); return e ? (sum(r, 'attended') / e) * 100 : 0; },
      fmt: function (v) { return v.toFixed(1) + '%'; },
      dax: [['Attendance % =', ''], ['DIVIDE (', ''], ['    SUM ( Training[Attended] ),', ''], ['    SUM ( Training[Enrolled] )', ''], [')', '']]
    },
    hrs: {
      label: 'Training hours', axis: function (max) { return niceMax(max); },
      ticks: null,
      value: function (r) { return sum(r, 'hours'); },
      fmt: function (v) { return Math.round(v).toLocaleString('en-US') + ' h'; },
      dax: [['Training Hours =', ''], ['SUM ( Training[Hours] )', '']]
    },
    sat: {
      label: 'Satisfaction', axis: function () { return 5; }, ticks: ['5', '2.5', '0'],
      value: function (r) { var n = sum(r, 'responses'); return n ? sum(r, 'scoreSum') / n : 0; },
      fmt: function (v) { return v.toFixed(2) + ' / 5'; },
      dax: [['Satisfaction =', ''], ['DIVIDE (', ''], ['    SUMX ( Feedback, Feedback[Score] * Feedback[Responses] ),', ''], ['    SUM ( Feedback[Responses] )', ''], [')', '']]
    }
  };
  function sum(list, key) { var s = 0; for (var i = 0; i < list.length; i++) s += list[i][key]; return s; }
  function niceMax(v) {
    var p = Math.pow(10, Math.floor(Math.log10(v || 1))), n = v / p;
    return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10) * p;
  }
  function shortNum(v) { return v >= 1000 ? (v / 1000).toFixed(v % 1000 ? 1 : 0).replace('.0', '') + 'k' : String(v); }

  var state = { metric: 'att', month: null, domain: null };
  var el = {
    kpis: document.getElementById('kpis'), scope: document.getElementById('scope'), clear: document.getElementById('clear'),
    months: document.getElementById('months'), xl: document.getElementById('xl'), yax: document.getElementById('yax'),
    domains: document.getElementById('domains'), dax: document.getElementById('dax'), tbl: document.getElementById('tbl'),
    live: document.getElementById('live'), tip: document.getElementById('tip')
  };

  function select(domain, month) {
    return rows.filter(function (r) { return (domain === null || r.d === domain) && (month === null || r.m === month); });
  }

  /* ---- Build static pieces once ---- */
  Object.keys(METRICS).forEach(function (k) {
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'kpi'; b.dataset.metric = k;
    b.innerHTML = '<span class="kpi-l"></span><span class="kpi-v"></span>';
    el.kpis.appendChild(b);
  });
  MONTHS.forEach(function (m, i) {
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'col'; b.dataset.month = i;
    b.innerHTML = '<span class="bar-fill"></span>';
    el.months.appendChild(b);
    var s = document.createElement('span'); s.textContent = m.charAt(0); s.title = m; el.xl.appendChild(s);
  });
  DOMAINS.forEach(function (d) {
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'row'; b.dataset.domain = d;
    b.innerHTML = '<span class="row-l"></span><span class="row-t"><span class="row-f"></span></span><span class="row-v"></span>';
    b.querySelector('.row-l').textContent = d;
    el.domains.appendChild(b);
  });
  for (var i = 0; i < 3; i++) { el.yax.appendChild(document.createElement('span')); }

  /* ---- Render ---- */
  function render() {
    var M = METRICS[state.metric];

    // KPI cards respect both filters
    var scoped = select(state.domain, state.month);
    el.kpis.querySelectorAll('.kpi').forEach(function (b) {
      var m = METRICS[b.dataset.metric];
      b.querySelector('.kpi-l').textContent = m.label;
      b.querySelector('.kpi-v').textContent = m.fmt(m.value(scoped));
      b.setAttribute('aria-pressed', String(b.dataset.metric === state.metric));
    });

    // Month chart: filtered by domain only
    var monthVals = MONTHS.map(function (_, i) { return M.value(select(state.domain, i)); });
    var axis = M.axis(Math.max.apply(null, monthVals));
    var cols = el.months.children;
    for (var i = 0; i < cols.length; i++) {
      var c = cols[i];
      c.style.setProperty('--h', (monthVals[i] / axis * 100).toFixed(1));
      c.classList.toggle('dim', state.month !== null && state.month !== i);
      c.setAttribute('aria-pressed', String(state.month === i));
      c.setAttribute('aria-label', MONTHS[i] + ': ' + M.fmt(monthVals[i]));
      c.dataset.tip = MONTHS[i] + '  ' + M.fmt(monthVals[i]);
    }
    var ticks = M.ticks || [shortNum(axis), shortNum(axis / 2), '0'];
    var yl = el.yax.children;
    for (var t = 0; t < 3; t++) { yl[t].textContent = ticks[t]; yl[t].style.bottom = (t === 0 ? 100 : t === 1 ? 50 : 0) + '%'; }

    // Domain chart: filtered by month only
    var domVals = DOMAINS.map(function (d) { return M.value(select(d, state.month)); });
    var domAxis = M.axis(Math.max.apply(null, domVals));
    var rowsEl = el.domains.children;
    DOMAINS.forEach(function (d, j) {
      var r = rowsEl[j];
      r.style.setProperty('--w', (domVals[j] / domAxis * 100).toFixed(1));
      r.classList.toggle('dim', state.domain !== null && state.domain !== d);
      r.setAttribute('aria-pressed', String(state.domain === d));
      r.querySelector('.row-v').textContent = M.fmt(domVals[j]);
      r.setAttribute('aria-label', d + ': ' + M.fmt(domVals[j]));
      r.dataset.tip = d + '  ' + M.fmt(domVals[j]);
    });

    // Scope line, clear button, DAX
    var scope = (state.domain || 'All domains') + ' / ' + (state.month === null ? 'all months' : MONTHS[state.month]);
    el.scope.textContent = 'Showing: ' + scope;
    el.clear.disabled = state.domain === null && state.month === null;
    el.dax.innerHTML = M.dax.map(function (l) { return highlight(l[0]); }).join('\n');

    // Table view mirrors the month chart
    var head = '<thead><tr><th scope="col">Month</th><th scope="col">Enrolled</th><th scope="col">Attended</th><th scope="col">Attendance</th><th scope="col">Hours</th><th scope="col">Satisfaction</th></tr></thead>';
    var body = MONTHS.map(function (m, i) {
      var r = select(state.domain, i);
      return '<tr><th scope="row">' + m + '</th><td>' + sum(r, 'enrolled') + '</td><td>' + sum(r, 'attended') + '</td><td>' + METRICS.att.fmt(METRICS.att.value(r)) + '</td><td>' + sum(r, 'hours').toLocaleString('en-US') + '</td><td>' + METRICS.sat.value(r).toFixed(2) + '</td></tr>';
    }).join('');
    el.tbl.innerHTML = '<caption class="sr-only">Synthetic monthly sample data. ' + scope + '.</caption>' + head + '<tbody>' + body + '</tbody>';

    el.live.textContent = M.label + ' for ' + scope.toLowerCase().replace('all domains', 'all domains') + ': ' + M.fmt(M.value(scoped)) + '.';
  }
  function highlight(line) {
    var safe = line.replace(/&/g, '&amp;').replace(/</g, '&lt;');
    return safe.replace(/\b(DIVIDE|SUMX|SUM)\b/g, '<span class="kw">$1</span>');
  }

  /* ---- Interaction ---- */
  el.kpis.addEventListener('click', function (e) {
    var b = e.target.closest('.kpi'); if (!b) return;
    state.metric = b.dataset.metric; render();
  });
  el.months.addEventListener('click', function (e) {
    var b = e.target.closest('.col'); if (!b) return;
    var i = Number(b.dataset.month); state.month = state.month === i ? null : i; render();
  });
  el.domains.addEventListener('click', function (e) {
    var b = e.target.closest('.row'); if (!b) return;
    state.domain = state.domain === b.dataset.domain ? null : b.dataset.domain; render();
  });
  el.clear.addEventListener('click', function () { state.month = null; state.domain = null; render(); el.kpis.firstChild.focus(); });

  /* Tooltip (pointer + keyboard focus). Purely a visual aid: values are also in aria-labels and the table. */
  function showTip(target) {
    if (!target || !target.dataset.tip) return;
    var box = dash.getBoundingClientRect(), r = target.getBoundingClientRect();
    el.tip.textContent = target.dataset.tip; el.tip.hidden = false;
    var w = el.tip.offsetWidth;
    var left = r.left - box.left + r.width / 2 - w / 2;
    left = Math.max(8, Math.min(left, box.width - w - 8));
    el.tip.style.left = left + 'px';
    el.tip.style.top = (r.top - box.top - el.tip.offsetHeight - 6) + 'px';
  }
  function hideTip() { el.tip.hidden = true; }
  [el.months, el.domains].forEach(function (c) {
    c.addEventListener('pointerover', function (e) { showTip(e.target.closest('button')); });
    c.addEventListener('pointerleave', hideTip);
    c.addEventListener('focusin', function (e) { showTip(e.target.closest('button')); });
    c.addEventListener('focusout', hideTip);
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') hideTip(); });

  dash.hidden = false;
  render();
})();
