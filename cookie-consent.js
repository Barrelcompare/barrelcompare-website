/* BarrelCompare — Cookie Consent (Consent Mode v2)
   Injected on every page. Works alongside GA4 gtag already loaded in <head>.
   CSS vars from the shared design system are defined inline here so this file
   is fully self-contained and safe to load on pages with or without styles.css. */
(function () {
  'use strict';

  var STORAGE_KEY = 'bc_cookie_consent';

  function updateGtag(state) {
    if (typeof gtag === 'function') {
      gtag('consent', 'update', { analytics_storage: state, ad_storage: state });
    }
  }

  /* Apply any previously stored consent decision immediately on load */
  var stored = localStorage.getItem(STORAGE_KEY);
  if (stored === 'accepted') {
    updateGtag('granted');
    return; /* banner not needed */
  }
  if (stored === 'declined') {
    return; /* banner not needed */
  }

  /* Inject CSS once */
  if (!document.getElementById('bc-consent-style')) {
    var style = document.createElement('style');
    style.id = 'bc-consent-style';
    style.textContent = [
      '#bc-cookie-banner{position:fixed;bottom:0;left:0;right:0;',
      'background:#112a4d;border-top:2px solid #f5a623;z-index:9999;',
      'padding:16px 20px;box-shadow:0 -4px 24px rgba(0,0,0,.3);}',
      '#bc-cookie-inner{max-width:1180px;margin:0 auto;display:flex;',
      'align-items:center;gap:20px;flex-wrap:wrap;}',
      '#bc-cookie-text{flex:1;min-width:200px;margin:0;font-size:.88rem;',
      'color:rgba(255,255,255,.65);font-family:-apple-system,BlinkMacSystemFont,',
      '"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;}',
      '#bc-cookie-text a{color:#f5a623;}',
      '#bc-cookie-btns{display:flex;gap:10px;flex-shrink:0;}',
      '.bc-btn{display:inline-flex;align-items:center;justify-content:center;',
      'padding:10px 20px;border-radius:12px;font-weight:600;font-size:.9rem;',
      'min-height:40px;cursor:pointer;border:none;font-family:inherit;}',
      '.bc-btn-accept{background:#f5a623;color:#0a1f3d;}',
      '.bc-btn-decline{background:transparent;color:#fff;',
      'border:1.5px solid rgba(255,255,255,.3);}'
    ].join('');
    document.head.appendChild(style);
  }

  /* Inject banner HTML */
  var banner = document.createElement('div');
  banner.id = 'bc-cookie-banner';
  banner.setAttribute('role', 'dialog');
  banner.setAttribute('aria-label', 'Cookie consent');
  banner.innerHTML = [
    '<div id="bc-cookie-inner">',
    '<p id="bc-cookie-text">We use cookies to analyse traffic and improve your experience.',
    ' Only essential cookies are set by default.',
    ' <a href="/privacy/">Privacy policy</a></p>',
    '<div id="bc-cookie-btns">',
    '<button class="bc-btn bc-btn-accept" id="bc-accept">Accept cookies</button>',
    '<button class="bc-btn bc-btn-decline" id="bc-decline">Decline</button>',
    '</div></div>'
  ].join('');

  function removeBanner() {
    if (banner.parentNode) banner.parentNode.removeChild(banner);
  }

  document.getElementById('bc-accept') && void 0; /* ensure no stale ref */

  function onAccept() {
    localStorage.setItem(STORAGE_KEY, 'accepted');
    updateGtag('granted');
    removeBanner();
  }

  function onDecline() {
    localStorage.setItem(STORAGE_KEY, 'declined');
    removeBanner();
  }

  function mount() {
    document.body.appendChild(banner);
    document.getElementById('bc-accept').addEventListener('click', onAccept);
    document.getElementById('bc-decline').addEventListener('click', onDecline);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
})();
