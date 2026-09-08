// Star colorization — 课程页中裸写的 ★ 文本统一显示为主题金色
(function () {
  function processStars(root) {
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var nodes = [];
    var n;
    while ((n = walker.nextNode())) {
      if (
        n.nodeValue.indexOf('★') !== -1 &&
        !(n.parentElement && n.parentElement.closest('.star-rating'))
      ) {
        nodes.push(n);
      }
    }
    nodes.forEach(function (node) {
      var span = document.createElement('span');
      span.className = 'star-rating';
      node.parentNode.replaceChild(span, node);
      span.textContent = node.nodeValue;
    });
  }

  function run() {
    processStars(document.querySelector('.md-typeset') || document.body);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }

  // Re-run when MkDocs instant navigation swaps content
  var observer = new MutationObserver(function () { setTimeout(run, 100); });
  observer.observe(document.body, { childList: true, subtree: true });
})();

// Intercept external nav links -> open confirmation page in new tab
(function () {
  var internalHosts = ['localhost', '127.0.0.1', 'www.pass3exceed4.com', 'pass3exceed4.com'];

  function processLinks() {
    // Target both sidebar nav links AND page content links
    var selectors = '.md-nav__link[href^="http"], .md-typeset a[href^="http"]';
    document.querySelectorAll(selectors).forEach(function (link) {
      if (link.hasAttribute('data-external')) return;
      var href = link.getAttribute('href');
      try {
        var url = new URL(href);
        if (internalHosts.indexOf(url.hostname) === -1) {
          link.setAttribute('data-external', href);
          link.setAttribute('href', '/redirect.html?url=' + encodeURIComponent(href));
          link.setAttribute('target', '_blank');
          link.setAttribute('rel', 'noopener');
        }
      } catch (e) {}
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', processLinks);
  } else {
    processLinks();
  }

  // Re-run when MkDocs instant navigation swaps content
  var observer = new MutationObserver(function () { setTimeout(processLinks, 100); });
  observer.observe(document.body, { childList: true, subtree: true });
})();

// ICP 备案号栏
(function () {
  var cfg = window.__SITE_CONFIG__ || {};
  var icpNumber = cfg.icpNumber;
  if (!icpNumber || icpNumber === '__ICP_NUMBER__') return;

  var chinaOnly = cfg.icpChinaOnly;

  function showBar() {
    if (document.querySelector('.gb-icp-bar')) return;
    var bar = document.createElement('div');
    bar.className = 'gb-icp-bar';
    bar.innerHTML = '<a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">' + icpNumber + '</a>';
    document.body.appendChild(bar);
  }

  // fetch with hard timeout — without this, a hung request (typical when
  // the API is blocked on the mainland) never resolves or rejects, so the
  // .catch fallback never fires and the ICP bar never appears.
  function fetchWithTimeout(url, ms) {
    return new Promise(function (resolve, reject) {
      var ctrl = window.AbortController ? new AbortController() : null;
      var timer = setTimeout(function () {
        if (ctrl) ctrl.abort();
        reject(new Error('timeout'));
      }, ms);
      fetch(url, ctrl ? { signal: ctrl.signal } : {})
        .then(function (r) { clearTimeout(timer); resolve(r); })
        .catch(function (e) { clearTimeout(timer); reject(e); });
    });
  }

  // Probe several geo-IP sources in parallel; resolve to the first success.
  // ipapi.co is frequently unreachable from mainland China, so geojs.io
  // (Cloudflare-backed) is tried first.
  function detectCountry() {
    var tasks = [
      fetchWithTimeout('https://get.geojs.io/v1/ip/country.json', 4000)
        .then(function (r) { return r.json(); })
        .then(function (d) { return (d.country || '').toUpperCase(); }),
      fetchWithTimeout('https://ipapi.co/json/', 4000)
        .then(function (r) { return r.json(); })
        .then(function (d) { return (d.country_code || '').toUpperCase(); })
    ];
    if (typeof Promise.any === 'function') {
      return Promise.any(tasks).catch(function () { return ''; });
    }
    return tasks[0].catch(function () { return ''; });
  }

  function checkCountryAndShow() {
    var cacheKey = 'gb_ip_country';
    var cacheTs = cacheKey + '_ts';
    var cached = localStorage.getItem(cacheKey);
    var ts = parseInt(localStorage.getItem(cacheTs), 10);
    // Successful detection cached 24h; a failed/unknown result only 10min so
    // we retry sooner instead of hiding the bar for a full day.
    if (cached !== null && ts) {
      // Treat both the legacy empty-string cache and 'UNKNOWN' as failures
      // so old clients migrate cleanly instead of waiting out a 24h TTL.
      var isUnknown = !cached || cached === 'UNKNOWN';
      var ttl = isUnknown ? 600000 : 86400000;
      if (Date.now() - ts < ttl) {
        if (cached === 'CN' || isUnknown) showBar();
        return;
      }
    }
    detectCountry().then(function (cc) {
      var val = cc || 'UNKNOWN';
      localStorage.setItem(cacheKey, val);
      localStorage.setItem(cacheTs, String(Date.now()));
      // CN -> show. UNKNOWN (all probes failed) -> show as a fallback,
      // because the most likely cause is the mainland network blocking the
      // geo-IP APIs; missing the ICP notice for a real mainland visitor is
      // a compliance risk, while showing it to a non-target user is harmless.
      if (val === 'CN' || val === 'UNKNOWN') showBar();
    });
  }

  if (!chinaOnly) {
    showBar();
  } else {
    checkCountryAndShow();
  }
})();

// SD Tooltip - positioned at body level to avoid table overflow clipping
(function () {
  var tip = document.createElement('div');
  tip.id = 'sd-tooltip-box';
  document.body.appendChild(tip);

  document.addEventListener('mouseover', function (e) {
    var el = e.target.closest('.sd-tip');
    if (!el) return;
    var content = el.querySelector('.sd-tip-content');
    if (!content) return;
    tip.innerHTML = content.innerHTML;
    tip.style.display = 'block';

    var rect = el.getBoundingClientRect();
    var tipRect = tip.getBoundingClientRect();
    var left = rect.left + rect.width / 2 - tipRect.width / 2;
    if (left < 8) left = 8;
    if (left + tipRect.width > window.innerWidth - 8) left = window.innerWidth - tipRect.width - 8;
    tip.style.left = left + 'px';
    tip.style.top = (rect.top - tipRect.height - 8) + 'px';
  });

  document.addEventListener('mouseout', function (e) {
    var el = e.target.closest('.sd-tip');
    if (el) tip.style.display = 'none';
  });
})();
