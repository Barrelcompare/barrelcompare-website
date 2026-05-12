#!/usr/bin/env python3
"""Apply all 12-section amendments to BarrelCompare website."""

import os
import re
import shutil

BASE = '/Users/kidunknown/Desktop/barrelcompare-website'

# ── helpers ────────────────────────────────────────────────────────────────────

def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  wrote {path.replace(BASE, "")}')

# ── 1. Fix blog/index.html ────────────────────────────────────────────────────

def fix_blog_index():
    src = read(f'{BASE}/blog-index.html')
    # Remove the dangling <ul class="search-results"...></div></div> stanza
    # that appears before the search overlay (lines 829-831 in the source)
    src = src.replace(
        '\n    <ul class="search-results" id="searchResults"></ul>\n  </div>\n</div>\n\n<!-- Site search overlay -->',
        '\n\n<!-- Site search overlay -->'
    )
    write(f'{BASE}/blog/index.html', src)

# ── 2. Fix blog article page ──────────────────────────────────────────────────

def fix_blog_article():
    src = read(f'{BASE}/blog-article.html')
    write(f'{BASE}/blog/barrel-shipping-costs-uk-caribbean-2026/index.html', src)

# ── CSS / HTML snippets for sitewide sticky header ────────────────────────────

STICKY_CSS = '.sticky-header-group { position: sticky; top: 0; z-index: 100; }\n'

def make_sticky_header(content):
    """Wrap welcome-banner + alerts-bar + site-header in a sticky group."""
    # Add CSS after welcome-banner CSS block
    css_marker = '/* ---- WELCOME BANNER ---- */'
    if '.sticky-header-group' not in content and css_marker in content:
        # Insert sticky CSS before the welcome-banner CSS comment
        content = content.replace(
            css_marker,
            f'/* ---- STICKY HEADER GROUP ---- */\n{STICKY_CSS}\n{css_marker}'
        )
        # Remove individual sticky positioning from alerts-bar
        content = re.sub(
            r'(\.alerts-bar \{[^}]*?)  position: sticky;\n  top: 0;\n  z-index: 90;\n',
            r'\1',
            content
        )
        # Remove individual sticky positioning from site-header
        content = re.sub(
            r'(\.site-header \{[^}]*?)  position: sticky;\n  top: 40px;\n  z-index: 100;\n',
            r'\1',
            content
        )

    # Wrap HTML structure – only if not already wrapped
    if 'class="sticky-header-group"' not in content:
        # Find the <!-- Welcome message --> comment and the closing </header>
        # Strategy: wrap from welcome-banner div to closing </header>
        open_tag = '<!-- Welcome message -->\n<div class="welcome-banner">'
        close_tag = '</header>'
        start = content.find(open_tag)
        end = content.find(close_tag, start) + len(close_tag) if start != -1 else -1
        if start != -1 and end > start:
            original = content[start:end]
            wrapped = '<div class="sticky-header-group">\n' + original + '\n</div>'
            content = content[:start] + wrapped + content[end:]
    return content


def fix_search_placeholder(content):
    old = 'placeholder="Search pages, destinations, guides..."'
    new = 'placeholder="Search by postcode, destination or supplier..."'
    return content.replace(old, new)


def remove_em_dashes(content):
    # Replace em dash with comma-space in typical sentence contexts
    # Also handle HTML entity &#8212; and &mdash;
    content = content.replace('—', ', ')
    content = content.replace('&mdash;', ', ')
    content = content.replace('&#8212;', ', ')
    # Clean up ", ," double comma artifacts
    content = re.sub(r',\s*,', ',', content)
    # Clean up excessive spaces
    content = re.sub(r'  +', ' ', content)
    return content


# ── 3. Sitewide: apply to all pages ──────────────────────────────────────────

SKIP_FILES = {'old-index.html', 'blog-index.html', 'blog-article.html'}

def get_all_html_files():
    files = []
    for root, dirs, filenames in os.walk(BASE):
        # Skip .git
        dirs[:] = [d for d in dirs if d != '.git']
        for fn in filenames:
            if fn.endswith('.html') and fn not in SKIP_FILES:
                files.append(os.path.join(root, fn))
    return files


def apply_sitewide(files):
    for path in files:
        content = read(path)
        original = content

        content = remove_em_dashes(content)
        content = fix_search_placeholder(content)
        content = make_sticky_header(content)

        if content != original:
            write(path, content)
        else:
            print(f'  no change: {path.replace(BASE, "")}')


# ── 4. index.html specific changes ───────────────────────────────────────────

REVIEWS_CAROUSEL_CSS = """
/* ---- REVIEWS CAROUSEL ---- */
.reviews-carousel-wrap { position: relative; overflow: hidden; }
.reviews-carousel-track { display: flex; gap: 20px; transition: transform 0.4s ease; }
.reviews-carousel-track .review-card { flex: 0 0 calc(25% - 15px); min-width: 220px; }
@media (max-width: 1024px) { .reviews-carousel-track .review-card { flex: 0 0 calc(33.333% - 14px); } }
@media (max-width: 768px) { .reviews-carousel-track .review-card { flex: 0 0 calc(50% - 10px); } }
@media (max-width: 500px) { .reviews-carousel-track .review-card { flex: 0 0 90%; } }
.carousel-controls { display: flex; align-items: center; justify-content: space-between; margin-top: 20px; }
.carousel-btn {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  color: var(--text-on-dark);
  border-radius: 8px;
  padding: 10px 18px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}
.carousel-btn:hover { background: rgba(255,255,255,0.15); }
.carousel-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.star-legend { display: flex; flex-wrap: wrap; gap: 12px 24px; font-size: 0.8rem; color: var(--text-muted-dark); }
.star-legend span { display: inline-flex; align-items: center; gap: 4px; }
.reviews-filter-row { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; margin-bottom: 24px; }
.reviews-filter-row label { font-size: 0.88rem; color: var(--text-muted-dark); }
.reviews-filter-row select {
  background: var(--navy-900); color: var(--text-on-dark);
  border: 1px solid rgba(255,255,255,0.12);
  padding: 8px 12px; border-radius: 8px; font-size: 0.88rem;
  cursor: pointer;
}
"""

REVIEWS_SECTION_HTML = """<!-- Reviews carousel -->
<section class="reviews-strip">
  <div class="container">
    <div class="section-eyebrow">Community reviews</div>
    <h2 style="font-size:1.75rem;margin-bottom:8px;">What our community says about their shippers</h2>
    <p class="section-lede">Real reviews submitted after barrels arrived. Moderated before publication.</p>

    <div class="reviews-filter-row">
      <label for="reviewThemeFilter">Filter by topic:</label>
      <select id="reviewThemeFilter" onchange="filterReviews()">
        <option value="">All topics</option>
        <option value="shipping-speed">Shipping speed</option>
        <option value="collection-reliability">Collection reliability</option>
        <option value="customer-service">Customer service</option>
        <option value="barrel-condition">Barrel condition</option>
        <option value="customs-support">Customs support</option>
        <option value="pricing-transparency">Pricing transparency</option>
        <option value="delivery-communication">Delivery communication</option>
        <option value="damage-handling">Damage handling</option>
      </select>
    </div>

    <div class="reviews-carousel-wrap" id="reviewsCarouselWrap">
      <div class="reviews-carousel-track" id="reviewsCarouselTrack">

        <div class="review-card" data-themes="shipping-speed,collection-reliability">
          <div class="stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
          <p class="review-text">"Barrel collected on time, arrived in Jamaica in just under 3 weeks. Everything intact. Very happy."</p>
          <div class="reviewer"><strong>M. Campbell</strong> &middot; Jamaica &middot; West Indies Direct</div>
        </div>

        <div class="review-card" data-themes="customer-service,pricing-transparency">
          <div class="stars">&#9733;&#9733;&#9733;&#9733;&#9734;</div>
          <p class="review-text">"Good communication throughout. Price was what I was quoted, no surprises at the other end."</p>
          <div class="reviewer"><strong>T. Francis</strong> &middot; Trinidad &middot; West Indies Direct</div>
        </div>

        <div class="review-card" data-themes="barrel-condition,damage-handling">
          <div class="stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
          <p class="review-text">"Barrel arrived sealed and undamaged. My family in Barbados were very pleased. Will use again."</p>
          <div class="reviewer"><strong>P. Alleyne</strong> &middot; Barbados &middot; West Indies Direct</div>
        </div>

        <div class="review-card" data-themes="customs-support,delivery-communication">
          <div class="stars">&#9733;&#9733;&#9733;&#9734;&#9734;</div>
          <p class="review-text">"Bit slow to update on customs clearance but they did sort it. Would appreciate more tracking updates."</p>
          <div class="reviewer"><strong>R. Beckford</strong> &middot; Jamaica &middot; West Indies Direct</div>
        </div>

        <div class="review-card" data-themes="collection-reliability,shipping-speed">
          <div class="stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
          <p class="review-text">"They came on the Saturday morning as promised, no fuss. Arrived before Christmas with time to spare."</p>
          <div class="reviewer"><strong>D. Thomas</strong> &middot; Jamaica &middot; West Indies Direct</div>
        </div>

        <div class="review-card" data-themes="pricing-transparency,customer-service">
          <div class="stars">&#9733;&#9733;&#9733;&#9733;&#9734;</div>
          <p class="review-text">"Clear pricing, helpful on the phone. Got a 10% discount for booking two barrels together."</p>
          <div class="reviewer"><strong>Y. Morrison</strong> &middot; Trinidad &middot; West Indies Direct</div>
        </div>

      </div>
    </div>

    <div class="carousel-controls">
      <button class="carousel-btn" id="carouselPrev" onclick="carouselStep(-1)" disabled>&larr; Previous</button>
      <div class="star-legend">
        <span>&#9733; Poor</span>
        <span>&#9733;&#9733; Fair</span>
        <span>&#9733;&#9733;&#9733; Good</span>
        <span>&#9733;&#9733;&#9733;&#9733; Very good</span>
        <span>&#9733;&#9733;&#9733;&#9733;&#9733; Excellent</span>
      </div>
      <button class="carousel-btn" id="carouselNext" onclick="carouselStep(1)">Next &rarr;</button>
    </div>

    <p class="rating-note">Reviews are moderated before publication. Our rating criteria covers multiple aspects of the shipping experience.</p>
  </div>
</section>

<script>
// Reviews carousel
let carouselIndex = 0;
let carouselAutoInterval;
const VISIBLE = 4;

function getVisibleCount() {
  const w = window.innerWidth;
  if (w <= 500) return 1;
  if (w <= 768) return 2;
  if (w <= 1024) return 3;
  return 4;
}

function getCards() {
  return Array.from(document.querySelectorAll('#reviewsCarouselTrack .review-card'))
    .filter(c => c.style.display !== 'none');
}

function updateCarousel() {
  const track = document.getElementById('reviewsCarouselTrack');
  const cards = getCards();
  const vis = getVisibleCount();
  const maxIndex = Math.max(0, cards.length - vis);
  carouselIndex = Math.min(carouselIndex, maxIndex);

  if (!track || !cards.length) return;
  const cardWidth = cards[0].offsetWidth + 20; // gap
  track.style.transform = `translateX(-${carouselIndex * cardWidth}px)`;

  const prev = document.getElementById('carouselPrev');
  const next = document.getElementById('carouselNext');
  if (prev) prev.disabled = carouselIndex <= 0;
  if (next) next.disabled = carouselIndex >= maxIndex;
}

function carouselStep(dir) {
  carouselIndex += dir;
  updateCarousel();
  resetAutoScroll();
}

function resetAutoScroll() {
  clearInterval(carouselAutoInterval);
  carouselAutoInterval = setInterval(() => {
    const cards = getCards();
    const vis = getVisibleCount();
    const maxIndex = Math.max(0, cards.length - vis);
    if (carouselIndex >= maxIndex) { carouselIndex = 0; } else { carouselIndex++; }
    updateCarousel();
  }, 5000);
}

function filterReviews() {
  const theme = document.getElementById('reviewThemeFilter').value;
  const allCards = document.querySelectorAll('#reviewsCarouselTrack .review-card');
  allCards.forEach(c => {
    const themes = c.dataset.themes || '';
    c.style.display = (!theme || themes.includes(theme)) ? '' : 'none';
  });
  carouselIndex = 0;
  updateCarousel();
}

window.addEventListener('resize', updateCarousel);
document.addEventListener('DOMContentLoaded', () => {
  updateCarousel();
  resetAutoScroll();
});
</script>"""

REVIEWS_CAROUSEL_JS = ""  # Already embedded in REVIEWS_SECTION_HTML above


def fix_index_html():
    path = f'{BASE}/index.html'
    content = read(path)

    # 1. Remove green glow from hero badge (two occurrences in CSS)
    content = content.replace(
        '.hero-badge {\n  display: inline-flex;\n  align-items: center;\n  gap: 8px;\n  background: rgba(37, 211, 102, 0.12);\n  color: #6fe39d;',
        '.hero-badge {\n  display: inline-flex;\n  align-items: center;\n  gap: 8px;\n  background: rgba(255, 255, 255, 0.08);\n  color: var(--text-muted-dark);'
    )
    # Also fix the duplicate in homepage-specific CSS
    content = content.replace(
        '.hero .hero-badge { background: rgba(37,211,102,0.12); color: #6fe39d; }',
        '.hero .hero-badge { background: rgba(255,255,255,0.08); color: var(--text-muted-dark); }'
    )
    # Tone down the dot - change from green to subtle white
    content = content.replace(
        '.hero-badge .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green-500); animation: pulse 2s ease-in-out infinite; }',
        '.hero-badge .dot { width: 8px; height: 8px; border-radius: 50%; background: rgba(255,255,255,0.5); }'
    )
    # Also fix the inline hero CSS override
    content = content.replace(
        '.hero .hero-badge .dot { background: var(--green-500); animation: pulse 2s ease-in-out infinite; }',
        '.hero .hero-badge .dot { background: rgba(255,255,255,0.4); }'
    )

    # 2. Add reviews carousel CSS before closing </style>
    content = content.replace(
        '\n</style>\n</head>',
        f'\n{REVIEWS_CAROUSEL_CSS}\n</style>\n</head>'
    )

    # 3. Move TrustPilot widget above territory-chips
    # The TrustPilot block is currently:
    #   <p class="hero-meta">...</p>
    #   <div class="trustpilot-widget" ...>...</div>
    #   <script ...trustpilot...></script>
    #   <div class="trustpilot-strip">...</div>
    # We want it before the territory-chips div
    tp_block = '''    <div class="trustpilot-widget" data-locale="en-GB" data-template-id="5419b6a8b0d04a076446a9ad" data-businessunit-id="69d3d7b3ea7a3bcec15beabd" data-style-height="24px" data-style-width="100%" data-theme="dark">
      <a href="https://uk.trustpilot.com/review/barrelcompare.co.uk" target="_blank" rel="noopener">Trustpilot</a>
    </div>
    <script type="text/javascript" src="https://widget.trustpilot.com/bootstrap/v5/tp.widget.bootstrap.min.js" async></script>

    <div class="trustpilot-strip">
      <span class="trustpilot-star">&#9733;&#9733;&#9733;&#9733;&#9733;</span>
      <span>Independent &middot; Powered by community-verified data</span>
    </div>'''

    tp_block_old = '''    <div class="trustpilot-widget" data-locale="en-GB" data-template-id="5419b6a8b0d04a076446a9ad" data-businessunit-id="69d3d7b3ea7a3bcec15beabd" data-style-height="24px" data-style-width="100%" data-theme="dark">
      <a href="https://uk.trustpilot.com/review/barrelcompare.co.uk" target="_blank" rel="noopener">Trustpilot</a>
    </div>
    <script type="text/javascript" src="https://widget.trustpilot.com/bootstrap/v5/tp.widget.bootstrap.min.js" async></script>

    <div class="trustpilot-strip">
      <span class="trustpilot-star">★★★★★</span>
      <span>Independent · Powered by community-verified data</span>
    </div>'''

    chips_div = '    <div class="territory-chips" role="group" aria-label="Choose destination">'

    if tp_block_old in content and chips_div in content:
        # Remove TP block from its current position
        content = content.replace('\n\n' + tp_block_old, '')
        # Re-insert before chips
        content = content.replace(
            chips_div,
            tp_block + '\n\n' + chips_div
        )

    # 4. Preserve postcode after search + update label
    # The postcode input already keeps its value; add display of the searched postcode in results header
    old_local_label = "    localLabel.textContent = `✅ Collecting in ${district} area:`;"
    new_local_label = "    localLabel.textContent = `✅ Suppliers collecting near ${raw}:`;"
    content = content.replace(old_local_label, new_local_label)

    old_no_local = "    localLabel.textContent = `No local suppliers confirmed for ${district}, see nationwide options below.`;"
    new_no_local = "    localLabel.textContent = `No local suppliers confirmed for ${raw} area. Nationwide options:`;"
    content = content.replace(old_no_local, new_no_local)

    # 5. Replace the existing reviews-strip section with carousel
    # Find and replace the reviews-strip section
    reviews_start = '<!-- Reviews strip -->\n<section class="reviews-strip">'
    reviews_end = '</section>\n\n<!-- Barrel sizes -->'
    start_idx = content.find(reviews_start)
    end_idx = content.find(reviews_end, start_idx) + len(reviews_end) if start_idx != -1 else -1

    if start_idx != -1 and end_idx > start_idx:
        content = content[:start_idx] + REVIEWS_SECTION_HTML + '\n\n<!-- Barrel sizes -->' + content[end_idx:]

    # 6. Fix duplicate searchResults - remove the dangling HTML before search overlay
    content = content.replace(
        '\n    <ul class="search-results" id="searchResults"></ul>\n  </div>\n</div>\n\n<!-- Site search overlay -->',
        '\n\n<!-- Site search overlay -->'
    )

    write(path, content)


# ── 5. costs-and-pricing copy edit ───────────────────────────────────────────

def fix_costs_and_pricing():
    path = f'{BASE}/costs-and-pricing/index.html'
    content = read(path)
    old = '<li>Request quotes from at least two or three shippers before deciding.</li>'
    new = '<li>Request quotes from 2-3 shippers before deciding.</li>'
    content = content.replace(old, new)
    write(path, content)


# ── 6. Soft gate for hidden-fees, glossary, country-rules ────────────────────

GATE_CSS = """
/* ---- CONTENT GATE ---- */
.gate-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10,31,61,0.88);
  z-index: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.gate-box {
  background: var(--navy-700);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: var(--radius-lg);
  padding: 40px 32px;
  max-width: 480px;
  width: 100%;
  text-align: center;
}
.gate-box h2 { font-size: 1.5rem; margin-bottom: 12px; }
.gate-box p { color: var(--text-muted-dark); margin-bottom: 24px; font-size: 0.95rem; }
.gate-box .gate-input {
  width: 100%;
  background: rgba(255,255,255,0.06);
  border: 1.5px solid rgba(255,255,255,0.12);
  color: var(--text-on-dark);
  padding: 14px 16px;
  border-radius: var(--radius);
  font-size: 1rem;
  margin-bottom: 12px;
}
.gate-box .gate-input:focus { outline: none; border-color: var(--orange-500); }
.gate-error { color: #ff8888; font-size: 0.85rem; margin-bottom: 12px; display: none; }
.gate-skip { color: var(--text-muted-dark); font-size: 0.8rem; margin-top: 16px; cursor: pointer; text-decoration: underline; }
"""

GATE_HTML = """
<!-- Content gate overlay -->
<div class="gate-overlay" id="contentGate">
  <div class="gate-box">
    <div style="font-size:2rem;margin-bottom:12px;">&#128274;</div>
    <h2>Get free access</h2>
    <p>Enter your email to unlock this guide. Free forever, no spam, unsubscribe any time.</p>
    <input type="email" class="gate-input" id="gateEmail" placeholder="Your email address">
    <div class="gate-error" id="gateError">Please enter a valid email address.</div>
    <button class="btn btn-orange btn-block" onclick="unlockContent()">Unlock free guide</button>
    <p class="gate-skip" onclick="skipGate()">I'll browse without unlocking</p>
  </div>
</div>
<style>body.gate-open { overflow: hidden; }</style>
"""

GATE_JS = """
<script>
(function() {
  var key = 'bc_gate_unlocked';
  if (!localStorage.getItem(key)) {
    document.body.classList.add('gate-open');
  } else {
    var g = document.getElementById('contentGate');
    if (g) g.style.display = 'none';
  }
})();

function unlockContent() {
  var email = document.getElementById('gateEmail').value.trim();
  var err = document.getElementById('gateError');
  if (!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(email)) {
    err.style.display = 'block';
    return;
  }
  err.style.display = 'none';
  localStorage.setItem('bc_gate_unlocked', '1');
  // Silently log to Formspree
  fetch('https://formspree.io/f/xrejbkjz', {
    method: 'POST',
    body: JSON.stringify({ email: email, _subject: 'Guide unlock - BarrelCompare', source: window.location.pathname }),
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }
  }).catch(() => {});
  var g = document.getElementById('contentGate');
  if (g) g.style.display = 'none';
  document.body.classList.remove('gate-open');
}

function skipGate() {
  var g = document.getElementById('contentGate');
  if (g) g.style.display = 'none';
  document.body.classList.remove('gate-open');
}
</script>
"""

def add_gate(path):
    content = read(path)
    if 'gate-overlay' in content:
        print(f'  gate already present: {path.replace(BASE, "")}')
        return

    # Add gate CSS before closing </style>
    content = content.replace('\n</style>\n</head>', f'\n{GATE_CSS}\n</style>\n</head>')

    # Add gate HTML + JS just after <body> open or after first <div> / after </nav> scroll bar
    # Insert just before the first <section class="page-header">
    insert_before = '<section class="page-header">'
    if insert_before in content:
        content = content.replace(insert_before, GATE_HTML + '\n' + insert_before, 1)

    # Add gate JS before </body>
    content = content.replace('</body>\n</html>', GATE_JS + '\n</body>\n</html>')

    write(path, content)


def apply_gates():
    for page in ['hidden-fees/index.html', 'glossary/index.html', 'country-rules/index.html']:
        add_gate(f'{BASE}/{page}')


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print('\n=== 1. Fix blog/index.html ===')
    fix_blog_index()

    print('\n=== 2. Fix blog article ===')
    fix_blog_article()

    print('\n=== 3. Fix index.html specific changes ===')
    fix_index_html()

    print('\n=== 4. Fix costs-and-pricing copy ===')
    fix_costs_and_pricing()

    print('\n=== 5. Apply sitewide changes (em dashes, placeholder, sticky header) ===')
    all_files = get_all_html_files()
    print(f'  Found {len(all_files)} HTML files')
    apply_sitewide(all_files)

    print('\n=== 6. Add content gates ===')
    apply_gates()

    print('\nDone.')
