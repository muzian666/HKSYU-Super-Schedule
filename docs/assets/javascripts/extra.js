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
