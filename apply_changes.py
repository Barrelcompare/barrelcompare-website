#!/usr/bin/env python3
"""Apply May 11 full update to all HTML files."""
import re, os

REPO = '/Users/kidunknown/Desktop/barrelcompare-website'

SEARCH_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'

PAGE_ACTIVE = {
    'index.html': '/',
    'about.html': '/about/',
    'compare.html': '/compare/',
    'contact.html': '/contact/',
    'quote.html': '/quote/',
    'blog-index.html': '/blog/',
    'blog-article.html': '/blog/',
}

NAV_SCROLL_CSS = '''
/* ---- MOBILE SCROLL NAV ---- */
.nav-scroll-bar {
  display: flex;
  overflow-x: auto;
  scrollbar-width: none;
  white-space: nowrap;
  background: var(--navy-900);
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.nav-scroll-bar::-webkit-scrollbar { display: none; }
.nav-scroll-bar a, .nav-scroll-bar button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 13px 18px;
  font-size: 0.88rem;
  color: var(--text-muted-dark);
  border-bottom: 2px solid transparent;
  white-space: nowrap;
  text-decoration: none;
  background: none;
  border-top: none;
  border-left: none;
  border-right: none;
  cursor: pointer;
  font-family: var(--font);
}
.nav-scroll-bar a.active { color: var(--orange-500); border-bottom-color: var(--orange-500); }
.nav-scroll-bar a:hover { color: var(--white); }
@media (min-width: 900px) { .nav-scroll-bar { display: none; } }
'''

SEARCH_OVERLAY = '''<!-- Site search overlay -->
<div class="search-overlay" id="searchOverlay" role="dialog" aria-label="Site search">
  <div class="search-box">
    <div class="search-input-row">
      <input type="text" class="search-input" id="searchInput" placeholder="Search pages, destinations, guides..." autocomplete="off">
      <button class="search-close" id="searchClose" aria-label="Close search">Close</button>
    </div>
    <ul class="search-results" id="searchResults"></ul>
  </div>
</div>'''

SEARCH_JS = '''<script>
const SEARCH_INDEX = [
  { title: 'Compare barrel shippers', desc: 'Side-by-side comparison of UK barrel shipping companies', url: '/compare/' },
  { title: 'Get a quote', desc: 'Request a quote from a barrel shipper', url: '/quote/' },
  { title: 'FAQ', desc: 'Frequently asked questions about barrel shipping', url: '/faq/' },
  { title: 'About BarrelCompare', desc: 'Who we are and how BarrelCompare works', url: '/about/' },
  { title: 'Blogs', desc: 'Guides, packing tips, costs and more', url: '/blog/' },
  { title: 'Contact us', desc: 'Get in touch with BarrelCompare', url: '/contact/' },
  { title: 'Barrel sizes', desc: 'Standard vs large barrel, dimensions and capacity', url: '/barrel-sizes/' },
  { title: 'Country rules', desc: 'Country-by-country rules for barrel contents', url: '/country-rules/' },
  { title: 'Costs and pricing', desc: 'How barrel shipping is priced and what to expect', url: '/costs-and-pricing/' },
  { title: 'Hidden fees guide', desc: 'Common hidden fees in barrel shipping and how to avoid them', url: '/hidden-fees/' },
  { title: 'Barrel shipping glossary', desc: 'Key terms: LCL, FCL, manifest, Bill of Lading', url: '/glossary/' },
  { title: 'What does BarrelCompare do?', desc: 'How the platform works', url: '/what-does-barrelcompare-do/' },
  { title: 'Privacy policy', desc: 'How we handle your data', url: '/privacy/' },
  { title: 'Terms of use', desc: 'Our terms of service', url: '/terms/' },
  { title: 'Jamaica shipping', desc: 'Compare shippers to Jamaica', url: '/compare/?destination=jamaica' },
  { title: 'Trinidad shipping', desc: 'Compare shippers to Trinidad', url: '/compare/?destination=trinidad' },
  { title: 'Guyana shipping', desc: 'Compare shippers to Guyana', url: '/compare/?destination=guyana' },
  { title: 'Barbados shipping', desc: 'Compare shippers to Barbados', url: '/compare/?destination=barbados' },
  { title: 'Grenada shipping', desc: 'Compare shippers to Grenada', url: '/compare/?destination=grenada' },
  { title: 'St Lucia shipping', desc: 'Compare shippers to St Lucia', url: '/compare/?destination=stlucia' },
  { title: 'Dominica shipping', desc: 'Compare shippers to Dominica', url: '/compare/?destination=dominica' },
  { title: 'Antigua shipping', desc: 'Compare shippers to Antigua', url: '/compare/?destination=antigua' },
  { title: 'St Vincent shipping', desc: 'Compare shippers to St Vincent', url: '/compare/?destination=stvincent' },
  { title: 'The Bahamas shipping', desc: 'Compare shippers to The Bahamas', url: '/compare/?destination=bahamas' },
];
const DEFAULT_SUGGESTIONS = [
  { title: 'Compare barrel shippers', desc: 'Side-by-side comparison', url: '/compare/' },
  { title: 'Get a quote', desc: 'Request a quote from a barrel shipper', url: '/quote/' },
  { title: 'Country rules', desc: 'What can I send?', url: '/country-rules/' },
  { title: 'FAQ', desc: 'Frequently asked questions', url: '/faq/' },
  { title: 'Barrel sizes', desc: 'Standard and large barrel dimensions', url: '/barrel-sizes/' },
];
const searchOverlay = document.getElementById('searchOverlay');
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');
const searchClose = document.getElementById('searchClose');
const searchToggle = document.getElementById('searchToggle');
const searchToggleMobile = document.getElementById('searchToggleMobile');
function renderResults(items) {
  if (!searchResults) return;
  searchResults.innerHTML = '';
  items.forEach(item => {
    const li = document.createElement('li');
    li.innerHTML = '<a href="' + item.url + '"><strong>' + item.title + '</strong><span class="result-desc">' + item.desc + '</span></a>';
    searchResults.appendChild(li);
  });
}
function openSearch() {
  if (!searchOverlay) return;
  searchOverlay.classList.add('open');
  renderResults(DEFAULT_SUGGESTIONS);
  setTimeout(() => { if (searchInput) searchInput.focus(); }, 50);
}
function closeSearch() {
  if (!searchOverlay) return;
  searchOverlay.classList.remove('open');
  if (searchInput) searchInput.value = '';
  if (searchResults) searchResults.innerHTML = '';
}
if (searchToggle) searchToggle.addEventListener('click', openSearch);
if (searchToggleMobile) searchToggleMobile.addEventListener('click', openSearch);
if (searchClose) searchClose.addEventListener('click', closeSearch);
if (searchOverlay) searchOverlay.addEventListener('click', e => { if (e.target === searchOverlay) closeSearch(); });
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeSearch();
  if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) { e.preventDefault(); openSearch(); }
});
if (searchInput) {
  searchInput.addEventListener('input', () => {
    const q = searchInput.value.trim().toLowerCase();
    if (!q) { renderResults(DEFAULT_SUGGESTIONS); return; }
    const hits = SEARCH_INDEX.filter(i => i.title.toLowerCase().includes(q) || i.desc.toLowerCase().includes(q)).slice(0, 8);
    if (!hits.length) { searchResults.innerHTML = '<li class="search-no-results">No results found.</li>'; return; }
    renderResults(hits);
  });
}
</script>'''

TRUSTPILOT = '''    <div class="trustpilot-widget" data-locale="en-GB" data-template-id="5419b6a8b0d04a076446a9ad" data-businessunit-id="69d3d7b3ea7a3bcec15beabd" data-style-height="24px" data-style-width="100%" data-theme="dark">
      <a href="https://uk.trustpilot.com/review/barrelcompare.co.uk" target="_blank" rel="noopener">Trustpilot</a>
    </div>
    <script type="text/javascript" src="https://widget.trustpilot.com/bootstrap/v5/tp.widget.bootstrap.min.js" async></script>'''

def make_scroll_nav(active_url):
    links = [
        ('/compare/', 'Compare options'),
        ('/quote/', 'Get a quote'),
        ('/faq/', 'FAQ'),
        ('/about/', 'About'),
        ('/blog/', 'Blogs'),
    ]
    items = []
    for url, label in links:
        cls = ' class="active"' if url == active_url else ''
        items.append(f'  <a href="{url}"{cls}>{label}</a>')
    items.append(f'  <button class="search-toggle" id="searchToggleMobile" aria-label="Search">{SEARCH_SVG} Search</button>')
    items.append('  <a href="https://wa.me/+447542539430" style="color:#25d366;">WhatsApp Us</a>')
    return '<nav class="nav-scroll-bar" aria-label="Mobile navigation">\n' + '\n'.join(items) + '\n</nav>'

def process(content, filename):
    active_url = PAGE_ACTIVE.get(filename, '/')

    # ── 1. CSS variable changes ──────────────────────────────────────────
    content = content.replace('--navy-900: #061327', '--navy-900: #0a1f3d')
    content = content.replace('--grey-100: #f5f7fa', '--grey-100: #0a1f3d')
    # Preserve step-card bg (section-white uses var(--grey-100) which is now dark)
    content = content.replace(
        '.section-white .step-card { background: var(--grey-100);',
        '.section-white .step-card { background: #f5f7fa;'
    )

    # ── 2. Remove hardcoded white bg on section classes ──────────────────
    # .section-white and .hero-white (but NOT --white: #ffffff variable)
    content = re.sub(r'(\.section-white\s*\{[^}]*)background:\s*#ffffff', r'\1background: var(--navy-800)', content)
    content = re.sub(r'(\.hero-white\s*\{[^}]*)background:\s*#ffffff', r'\1background: var(--navy-800)', content)
    # preview-banner white bg
    content = re.sub(r'(\.preview-banner\s*\{[^}]*)background:\s*#ffffff', r'\1background: var(--navy-700)', content)

    # ── 3. Welcome banner CSS ────────────────────────────────────────────
    content = re.sub(
        r'\.welcome-banner \{[^}]+\}',
        '''.welcome-banner {
  background: #2d6cdf;
  color: var(--white);
  padding: 14px 20px;
  font-size: 0.88rem;
  line-height: 1.5;
  text-align: center;
}''',
        content
    )

    # ── 4. Welcome banner HTML – remove dismiss button, fix text ─────────
    content = re.sub(
        r'<!-- Welcome message.*?</div>\s*\n?</div>',
        '''<!-- Welcome message -->
<div class="welcome-banner">
  <div class="container">
    You&#x2019;re viewing a preview of our new website. Welcome, and well done on finding us so early. We&#x2019;ll continue refining and enhancing the experience over the coming weeks, and we&#x2019;d love to hear your feedback along the way.
  </div>
</div>''',
        content,
        flags=re.DOTALL
    )

    # ── 5. Ticker sticky ────────────────────────────────────────────────
    content = content.replace(
        '  overflow: hidden;\n  position: relative;\n}',
        '  overflow: hidden;\n  position: sticky;\n  top: 0;\n  z-index: 90;\n}'
    )

    # ── 6. Header top: 40px ─────────────────────────────────────────────
    content = content.replace(
        '  position: sticky;\n  top: 0;\n  z-index: 100;',
        '  position: sticky;\n  top: 40px;\n  z-index: 100;'
    )

    # ── 7. Add mobile scroll nav CSS ────────────────────────────────────
    if 'nav-scroll-bar' not in content:
        content = content.replace(
            ':focus-visible { outline: 3px solid var(--orange-500); outline-offset: 3px; border-radius: 4px; }',
            NAV_SCROLL_CSS + '\n:focus-visible { outline: 3px solid var(--orange-500); outline-offset: 3px; border-radius: 4px; }'
        )

    # ── 8. Rename Caribbean shipping guides → Blogs ──────────────────────
    content = content.replace('>Caribbean shipping guides<', '>Blogs<')

    # ── 9. Desktop WhatsApp: remove btn styling ──────────────────────────
    content = re.sub(
        r'<a href="https://wa\.me/\+447542539430[^"]*"\s+class="btn btn-whatsapp"[^>]*>WhatsApp Us</a>',
        '<a href="https://wa.me/+447542539430" style="color:#25d366;">WhatsApp Us</a>',
        content
    )

    # ── 10. Remove hamburger button div ──────────────────────────────────
    content = re.sub(
        r'\s*<div style="display:flex;align-items:center;gap:10px;">\s*<button class="search-toggle" id="searchToggleMobile"[^>]*>.*?</button>\s*<button class="menu-toggle"[^>]*>.*?</button>\s*</div>',
        '',
        content,
        flags=re.DOTALL
    )

    # ── 11. Remove mobile nav drawer ─────────────────────────────────────
    content = re.sub(
        r'\s*<nav class="nav-mobile"[^>]*>.*?</nav>',
        '',
        content,
        flags=re.DOTALL
    )

    # ── 12. Remove hamburger JS ──────────────────────────────────────────
    content = re.sub(
        r'<script>\s*const toggle = document\.getElementById\(\'menuToggle\'\);.*?</script>\s*',
        '',
        content,
        flags=re.DOTALL
    )

    # ── 13. Add mobile scroll nav after </header> ────────────────────────
    scroll_nav = make_scroll_nav(active_url)
    if 'nav-scroll-bar' not in content:
        content = content.replace('</header>\n', '</header>\n' + scroll_nav + '\n')
    else:
        content = re.sub(
            r'<nav class="nav-scroll-bar"[^>]*>.*?</nav>',
            scroll_nav,
            content,
            flags=re.DOTALL
        )

    # ── 14. Replace search overlay + JS ─────────────────────────────────
    # Remove old overlay
    content = re.sub(
        r'<!-- Site search overlay -->.*?</div>\s*\n',
        '',
        content,
        flags=re.DOTALL
    )
    # Remove old search script
    content = re.sub(
        r'<script>\s*(?://[^\n]*)?\s*const SEARCH_INDEX.*?</script>\s*',
        '',
        content,
        flags=re.DOTALL
    )
    # Insert new overlay + JS before </body>
    content = content.replace('</body>', SEARCH_OVERLAY + '\n\n' + SEARCH_JS + '\n</body>')

    # ── 15. index.html specific ──────────────────────────────────────────
    if filename == 'index.html':
        # Hero: dark background (was white)
        content = content.replace(
            '.hero { background: #ffffff; padding: 64px 0 80px; text-align: center; }',
            '.hero { background: var(--navy-800); padding: 64px 0 80px; text-align: center; }'
        )
        content = content.replace(
            '.hero .hero-badge { background: rgba(6,19,39,0.08); color: var(--navy-700); }',
            '.hero .hero-badge { background: rgba(37,211,102,0.12); color: #6fe39d; }'
        )
        content = content.replace(
            '.hero .hero-badge .dot { background: var(--green-500); }',
            '.hero .hero-badge .dot { background: var(--green-500); animation: pulse 2s ease-in-out infinite; }'
        )
        content = content.replace(
            '.hero h1 { color: var(--navy-900); }',
            '.hero h1 { color: var(--white); }'
        )
        content = content.replace(
            '.hero p.lede { color: var(--navy-800); }',
            '.hero p.lede { color: var(--text-on-dark); }'
        )
        content = content.replace(
            '.hero p.sub { color: var(--grey-600); }',
            '.hero p.sub { color: var(--text-muted-dark); }'
        )
        content = content.replace(
            '.hero .hero-meta { color: var(--grey-600); }',
            '.hero .hero-meta { color: var(--text-muted-dark); }'
        )
        content = content.replace(
            '.hero .trustpilot-strip { background: rgba(6,19,39,0.05); color: var(--grey-600); }',
            '.hero .trustpilot-strip { background: rgba(255,255,255,0.04); color: var(--text-muted-dark); }'
        )
        content = content.replace(
            '.hero .chip { background: rgba(6,19,39,0.06); border-color: rgba(6,19,39,0.15); color: var(--navy-800); }',
            '.hero .chip { background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.12); color: var(--text-on-dark); }'
        )
        content = content.replace(
            '.hero .chip:hover { background: rgba(6,19,39,0.1); border-color: rgba(6,19,39,0.3); }',
            '.hero .chip:hover { border-color: rgba(255,255,255,0.3); background: rgba(255,255,255,0.1); }'
        )
        # How-section: dark background
        content = content.replace(
            '.how-section { background: #ffffff; }',
            '.how-section { background: var(--navy-800); }'
        )
        content = content.replace(
            '.how-section .section-title { color: var(--navy-900); }',
            '.how-section .section-title { color: var(--white); }'
        )
        content = content.replace(
            '.how-section .section-lede { color: var(--grey-600); }',
            '.how-section .section-lede { color: var(--text-muted-dark); }'
        )
        content = content.replace(
            '.how-section .step-card { background: rgba(6,19,39,0.04); border-color: rgba(6,19,39,0.1); }',
            '.how-section .step-card { background: rgba(255,255,255,0.04); border-color: rgba(255,255,255,0.08); }'
        )
        content = content.replace(
            '.how-section .step-card h3 { color: var(--navy-900); }',
            '.how-section .step-card h3 { color: var(--white); }'
        )
        content = content.replace(
            '.how-section .step-card p { color: var(--grey-600); }',
            '.how-section .step-card p { color: var(--text-muted-dark); }'
        )
        # Supplier cards: align-self:stretch
        content = content.replace(
            'display: flex; flex-direction: column;\n  transition: border-color 0.2s, transform 0.2s;',
            'display: flex; flex-direction: column; align-self: stretch;\n  transition: border-color 0.2s, transform 0.2s;'
        )
        # Remove `, ` placeholder from pending card price
        content = content.replace(
            '<span class="price">, </span>',
            '<span class="price">TBC</span>'
        )
        # Add TrustPilot widget after hero-meta
        content = content.replace(
            '    <p class="hero-meta">Free service · No obligation · Independent of shipping companies</p>\n\n    <div class="trustpilot-strip">',
            '    <p class="hero-meta">Free service · No obligation · Independent of shipping companies</p>\n\n' + TRUSTPILOT + '\n\n    <div class="trustpilot-strip">'
        )

    return content

files = ['index.html', 'about.html', 'compare.html', 'contact.html', 'quote.html', 'blog-index.html', 'blog-article.html']

for fn in files:
    fp = os.path.join(REPO, fn)
    if not os.path.exists(fp):
        print(f'SKIP (not found): {fn}')
        continue
    with open(fp, 'r', encoding='utf-8') as f:
        original = f.read()
    result = process(original, fn)
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f'OK: {fn}')

print('\nAll files processed.')
