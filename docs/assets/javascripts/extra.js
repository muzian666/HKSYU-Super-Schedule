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
