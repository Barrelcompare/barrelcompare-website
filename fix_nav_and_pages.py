#!/usr/bin/env python3
"""Fix scroll nav insertion and regenerate new pages correctly."""
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

def make_scroll_nav(active_url):
    links = [('/compare/', 'Compare options'), ('/quote/', 'Get a quote'),
             ('/faq/', 'FAQ'), ('/about/', 'About'), ('/blog/', 'Blogs')]
    items = []
    for url, label in links:
        cls = ' class="active"' if url == active_url else ''
        items.append(f'  <a href="{url}"{cls}>{label}</a>')
    items.append(f'  <button class="search-toggle" id="searchToggleMobile" aria-label="Search">{SEARCH_SVG} Search</button>')
    items.append('  <a href="https://wa.me/+447542539430" style="color:#25d366;">WhatsApp Us</a>')
    return '<nav class="nav-scroll-bar" aria-label="Mobile navigation">\n' + '\n'.join(items) + '\n</nav>'

# ── PART 1: Add scroll nav HTML to existing 7 files ──────────────────────
existing = ['index.html','about.html','compare.html','contact.html','quote.html','blog-index.html','blog-article.html']

for fn in existing:
    fp = os.path.join(REPO, fn)
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    # Only add if HTML element isn't already there
    if '<nav class="nav-scroll-bar"' not in content:
        active_url = PAGE_ACTIVE.get(fn, '/')
        scroll_nav = make_scroll_nav(active_url)
        content = content.replace('</header>\n', '</header>\n' + scroll_nav + '\n', 1)
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed scroll nav: {fn}')
    else:
        print(f'Scroll nav already present: {fn}')

# ── PART 2: Build new pages properly ─────────────────────────────────────
with open(os.path.join(REPO, 'about.html'), 'r', encoding='utf-8') as f:
    TEMPLATE = f.read()

# Split template into HEAD (everything up to and including scroll nav) and TAIL (footer onward)
# Find the scroll nav close tag, then split there
scroll_end = TEMPLATE.find('</nav>\n', TEMPLATE.find('<nav class="nav-scroll-bar"'))
head_part = TEMPLATE[:scroll_end + len('</nav>\n')]
tail_start = TEMPLATE.find('\n<footer')
tail_part = TEMPLATE[tail_start:]

def make_page(title, meta_desc, og_title, og_url, active_url, page_content, out_path):
    head = head_part
    # Title and meta
    head = re.sub(r'<title>[^<]+</title>', f'<title>{title}</title>', head)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{meta_desc}">', head)
    head = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{og_title}">', head)
    head = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{meta_desc}">', head)
    head = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="https://barrelcompare.co.uk{og_url}">', head)

    # Fix active nav link in desktop nav
    head = re.sub(r'(<a href="[^"]+") class="active"', r'\1', head)  # clear old active
    head = head.replace(f'href="{active_url}"', f'href="{active_url}" class="active"', 1)

    # Fix active link in scroll nav
    head = re.sub(r'(<nav class="nav-scroll-bar".*?)(class="active" )?href="([^"]+)"',
                  lambda m: m.group(0), head, flags=re.DOTALL)  # handled below

    # Rebuild scroll nav with correct active
    def fix_scroll(m):
        nav = m.group(0)
        nav = re.sub(r' class="active"', '', nav)
        nav = nav.replace(f'href="{active_url}"', f'href="{active_url}" class="active"', 1)
        return nav
    head = re.sub(r'<nav class="nav-scroll-bar".*?</nav>', fix_scroll, head, flags=re.DOTALL)

    full = head + '\n' + page_content + '\n' + tail_part
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(full)
    print(f'Created: {out_path.replace(REPO, "")}')

# ── PAGE CONTENT ──────────────────────────────────────────────────────────
BACK = '<p style="margin-top:40px;"><a href="/" style="color:var(--orange-500);">← Back to home</a></p>'

SUPPLIER_STANDARDS = '''<section class="page-header">
  <div class="container">
    <h1>What good service looks like</h1>
    <p>The standards we believe every customer deserves.</p>
  </div>
</section>
<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container"><div class="prose">
    <div style="background:rgba(45,108,223,0.12);border:1px solid rgba(45,108,223,0.3);border-radius:var(--radius);padding:20px 24px;margin-bottom:40px;">
      <p style="margin:0;">Reputable shippers already work to high standards. Our goal is to help make this the norm across the industry, so every customer can book with greater confidence and receive the level of service they deserve.</p>
    </div>
    <h2>1. Treat every customer with courtesy and respect</h2>
    <p>Every customer deserves patience and professionalism, regardless of the size of their shipment or how many questions they ask.</p>
    <h2>2. Respond to new quote requests within 48 hours</h2>
    <p>Customers should not be left waiting. A prompt response — even to say more information is needed — sets the tone for the whole relationship.</p>
    <h2>3. Be upfront about pricing from the start</h2>
    <p>All costs should be clearly communicated before a booking is confirmed. Surprises at the end of the process erode trust.</p>
    <h2>4. Keep customers informed throughout the journey</h2>
    <p>From collection to port clearance to final delivery, customers should know where their barrel is and what to expect next.</p>
    <h2>5. If something goes wrong, own it</h2>
    <p>Delays happen. Problems arise. What matters is how a shipper responds. Acknowledge the issue, communicate clearly, and do what is reasonable to put it right.</p>
    <h2>6. Advise customers on restrictions before they pack</h2>
    <p>Different countries have different rules on what can be imported. A good shipper helps customers avoid costly mistakes before the barrel leaves the house.</p>
    <h2>7. Only accept bookings that can be fulfilled</h2>
    <p>Do not take money for a service that cannot be delivered. If capacity is full or routes change, customers must be told before they commit.</p>
    <div style="margin-top:48px;padding:32px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:var(--radius-lg);text-align:center;">
      <h3 style="margin-bottom:12px;">Questions or feedback?</h3>
      <p style="color:var(--text-muted-dark);margin-bottom:20px;">We'd love to hear from shippers and customers alike.</p>
      <a href="mailto:hello@barrelcompare.co.uk" class="btn btn-orange">hello@barrelcompare.co.uk</a>
    </div>
  </div>''' + BACK + '''</div>
</section>'''

def ct(permitted, prohibited):
    pr = ''.join(f'<tr><td style="padding:8px 12px;border-bottom:1px solid rgba(255,255,255,0.06);">✓ {i}</td></tr>' for i in permitted)
    xr = ''.join(f'<tr><td style="padding:8px 12px;border-bottom:1px solid rgba(255,255,255,0.06);">✗ {i}</td></tr>' for i in prohibited)
    return f'<div style="display:grid;gap:12px;grid-template-columns:1fr 1fr;margin-bottom:8px;"><div><table style="width:100%;border-collapse:collapse;font-size:0.88rem;background:rgba(37,211,102,0.06);border-radius:8px;"><thead><tr><th style="padding:8px 12px;text-align:left;color:#6fe39d;font-size:0.78rem;letter-spacing:0.06em;">Permitted</th></tr></thead><tbody>{pr}</tbody></table></div><div><table style="width:100%;border-collapse:collapse;font-size:0.88rem;background:rgba(239,68,68,0.06);border-radius:8px;"><thead><tr><th style="padding:8px 12px;text-align:left;color:#ff8888;font-size:0.78rem;letter-spacing:0.06em;">Prohibited</th></tr></thead><tbody>{xr}</tbody></table></div></div>'

COUNTRIES = [
    ('Jamaica', ['Clothing and personal effects','Tinned and dried food','Household goods','Children\'s toys','Electrical appliances (used)','Toiletries','Medicines (with prescription)'],['Firearms (without licence)','Illegal drugs','Fresh meat (restrictions apply)','Copyright-infringing items','Pornographic material','Certain agricultural products']),
    ('Grenada', ['Personal clothing','Household goods','Tinned and dried food','Toiletries','Toys and gifts','Books'],['Firearms without licence','Illegal substances','Live animals (without permit)','Plant material without certificate','Counterfeit goods']),
    ('Guyana', ['Personal clothing','Household items','Non-perishable food','Toiletries','Electrical goods (used)','Medicines'],['Narcotics','Weapons without licence','Prohibited agricultural products','Counterfeit goods','Pornographic material']),
    ('St Lucia', ['Clothing and effects','Household goods','Non-perishable food','Toiletries','Electrical items','Children\'s goods'],['Drugs and narcotics','Firearms (without permit)','Indecent material','Certain agricultural products','Counterfeit items']),
    ('Barbados', ['Personal and household goods','Clothing','Non-perishable foods','Toiletries','Electrical appliances','Toys'],['Controlled substances','Unlicensed firearms','Prohibited agricultural imports','Counterfeit goods','Pornographic material']),
    ('The Bahamas', ['Personal effects and clothing','Household goods','Non-perishable food','Electrical items','Toiletries','Gifts'],['Drugs and narcotics','Weapons without licence','Certain agricultural imports','Counterfeit goods']),
    ('Trinidad &amp; Tobago', ['Clothing and personal effects','Household goods','Tinned and dried food','Toiletries','Electrical goods','Medicines'],['Illegal drugs','Unlicensed firearms','Prohibited plant material','Counterfeit items','Pornographic material']),
    ('Antigua', ['Personal clothing','Household goods','Non-perishable food','Toiletries','Electrical appliances','Children\'s goods'],['Controlled substances','Firearms (unlicensed)','Certain agricultural products','Counterfeit goods']),
    ('St Vincent', ['Personal effects','Household goods','Non-perishable food','Toiletries','Electrical items','Toys and gifts'],['Illegal drugs','Unlicensed weapons','Prohibited agricultural imports','Counterfeit goods']),
    ('Dominica', ['Personal clothing','Household goods','Tinned and dried food','Toiletries','Electrical appliances','Gifts'],['Narcotics','Unlicensed firearms','Prohibited agricultural items','Counterfeit goods','Pornographic material']),
]

country_html = ''
for name, p, x in COUNTRIES:
    country_html += f'<h2>{name}</h2>{ct(p,x)}<p style="font-size:0.82rem;color:var(--text-muted-dark);margin-bottom:32px;">Always confirm current rules with your shipper before packing.</p>\n'

COUNTRY_RULES = f'''<section class="page-header">
  <div class="container">
    <h1>Country rules</h1>
    <p>What you can and cannot send. Always confirm with your shipper before packing.</p>
  </div>
</section>
<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container">
    <div style="background:rgba(245,166,35,0.08);border:1px solid rgba(245,166,35,0.2);border-radius:var(--radius);padding:16px 20px;margin-bottom:40px;"><p style="margin:0;font-size:0.88rem;color:var(--text-muted-dark);">⚠️ For general reference only. Import rules change — always verify with your shipper and the destination customs authority.</p></div>
    <div class="prose">{country_html}</div>
    {BACK}
  </div>
</section>'''

FEES_DATA = [
    ('Customs duty','Charged by the destination country on goods above a certain value.','Is customs duty included in the quoted price, or charged separately on arrival?'),
    ('Port handling charges','Fees charged by the port for handling your barrel when it arrives.','Are port handling charges included, or paid separately by the recipient?'),
    ('Fuel surcharges','Variable surcharge to cover fuel costs, not always in the headline price.','Does the quoted price include fuel surcharges? Are they fixed or variable?'),
    ('Storage fees','If your barrel cannot be collected promptly, daily storage charges may apply.','How long is the barrel held before storage charges apply, and how much are they?'),
    ('Empty barrel cost','If you are buying the barrel from the shipper, the cost may be separate.','Is the barrel included, or do I need to purchase it separately?'),
    ('Overweight charges','Most shippers have weight limits. Exceeding them can result in significant extra charges.','What is the maximum weight included, and the charge per kg above that?'),
    ('Collection charges','Some shippers quote port-to-port only. Home collection may cost extra.','Is home collection included? Is door-to-door delivery included or extra?'),
]
fee_html = ''.join(f'<div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:var(--radius-lg);padding:24px;margin-bottom:16px;"><h3 style="margin-bottom:8px;color:var(--white);">{t}</h3><p style="color:var(--text-muted-dark);margin-bottom:12px;">{d}</p><div style="background:rgba(245,166,35,0.08);border-left:3px solid var(--orange-500);padding:10px 14px;border-radius:0 8px 8px 0;"><p style="margin:0;font-size:0.88rem;"><strong>Ask:</strong> {q}</p></div></div>' for t,d,q in FEES_DATA)

HIDDEN_FEES = f'''<section class="page-header">
  <div class="container">
    <h1>Hidden fees guide</h1>
    <p>Common extra charges — and the questions to ask before you book.</p>
  </div>
</section>
<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container">
    <p style="color:var(--text-muted-dark);max-width:640px;margin-bottom:40px;font-size:1.05rem;">Barrel shipping prices are not always what they first appear. Here are the most common additional charges and how to spot them.</p>
    {fee_html}{BACK}
  </div>
</section>'''

GLOSSARY_TERMS = [
    ('Barrel','A large plastic drum used to ship goods to the Caribbean. Standard barrels are typically 85–90 cm tall.'),
    ('Bill of Lading','A legal document issued by the carrier detailing goods being shipped. Acts as a receipt and title document.'),
    ('Break bulk','Cargo shipped as individual units rather than in containers. Most barrel shipments are consolidated break bulk freight.'),
    ('CARICOM','Caribbean Community — a trade bloc. CARICOM members may receive preferential customs treatment for certain goods.'),
    ('Carrier liability','The legal responsibility of the shipper for loss or damage during transit. Check the level of cover before booking.'),
    ('CIF','Cost, Insurance and Freight — the quoted price includes goods cost, insurance and freight to the destination port.'),
    ('Consolidation','Combining multiple customers\' barrels into one shipment. Most UK Caribbean barrel shippers operate on a consolidated basis.'),
    ('Customs duty','A tax levied by the destination country on imported goods. The rate varies by country and goods type.'),
    ('Customs clearance','Obtaining permission to import goods into a country. Your barrel must clear customs before it can be delivered.'),
    ('Door-to-door','The shipper collects from your home in the UK and delivers to an address in the destination country.'),
    ('Drop-off','You deliver the barrel to the shipper\'s depot yourself, rather than having it collected.'),
    ('FCL','Full Container Load — you book an entire container. Rarely used for single barrel shipments.'),
    ('Freight forwarder','A company that arranges transportation on behalf of customers, using a network of carriers and agents.'),
    ('LCL','Less than Container Load — your goods share a container with other customers. Most barrel shipping is LCL.'),
    ('Manifest','A document listing shipment contents, required by customs. You may need to declare what is in your barrel.'),
    ('Port of entry','The port in the destination country where your barrel arrives and passes through customs.'),
    ('Port-to-port','The shipper covers transportation between ports only. Collection and local delivery are not included.'),
    ('Sea freight','Goods transported by ship. The majority of Caribbean barrel shipments travel by sea freight.'),
    ('Storage fee','A charge applied when goods are held at port or warehouse beyond the free storage period.'),
    ('Transit time','Time from collection to arrival at the destination port. Does not include customs clearance time.'),
    ('TRN','Taxpayer Registration Number — required in some Caribbean countries (particularly Jamaica) for customs clearance.'),
    ('Waybill','A document describing the shipment and destination. Similar to a Bill of Lading but not a title document.'),
]
gloss_html = ''.join(f'<div style="padding:16px 0;border-bottom:1px solid rgba(255,255,255,0.08);"><h3 style="font-size:1.05rem;color:var(--orange-500);margin-bottom:4px;">{t}</h3><p style="color:var(--text-muted-dark);margin:0;font-size:0.95rem;">{d}</p></div>' for t,d in GLOSSARY_TERMS)

GLOSSARY = f'''<section class="page-header">
  <div class="container">
    <h1>Barrel shipping glossary</h1>
    <p>Key terms explained — from Bill of Lading to waybill.</p>
  </div>
</section>
<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container"><div style="max-width:720px;">{gloss_html}</div>{BACK}</div>
</section>'''

BARREL_SIZES = '''<section class="page-header">
  <div class="container">
    <h1>Barrel sizes</h1>
    <p>Dimensions, weight limits and what to ask your shipper.</p>
  </div>
</section>
<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container">
    <div style="display:grid;gap:24px;grid-template-columns:1fr;max-width:860px;">
      <div style="background:var(--navy-700);border:1px solid rgba(255,255,255,0.08);border-radius:var(--radius-lg);padding:36px;">
        <div class="section-eyebrow">Most common</div>
        <h2 style="font-size:1.6rem;margin-bottom:16px;">Standard barrel</h2>
        <div style="display:grid;gap:16px;grid-template-columns:1fr 1fr;margin-bottom:20px;">
          <div style="background:rgba(255,255,255,0.04);border-radius:var(--radius);padding:16px;text-align:center;"><div style="font-size:1.6rem;font-weight:800;color:var(--orange-500);">85–90 cm</div><div style="font-size:0.82rem;color:var(--text-muted-dark);margin-top:4px;">Height</div></div>
          <div style="background:rgba(255,255,255,0.04);border-radius:var(--radius);padding:16px;text-align:center;"><div style="font-size:1.6rem;font-weight:800;color:var(--orange-500);">55–57 cm</div><div style="font-size:0.82rem;color:var(--text-muted-dark);margin-top:4px;">Diameter</div></div>
        </div>
        <p style="color:var(--text-muted-dark);">The most widely used barrel size. Suitable for clothing, food, household goods and personal effects. Weight limits vary by shipper — typically 50–60 kg maximum.</p>
      </div>
      <div style="background:var(--navy-700);border:1px solid rgba(255,255,255,0.08);border-radius:var(--radius-lg);padding:36px;">
        <div class="section-eyebrow">Larger capacity</div>
        <h2 style="font-size:1.6rem;margin-bottom:16px;">Large barrel</h2>
        <div style="display:grid;gap:16px;grid-template-columns:1fr 1fr;margin-bottom:20px;">
          <div style="background:rgba(255,255,255,0.04);border-radius:var(--radius);padding:16px;text-align:center;"><div style="font-size:1.6rem;font-weight:800;color:var(--orange-500);">100–107 cm</div><div style="font-size:0.82rem;color:var(--text-muted-dark);margin-top:4px;">Height</div></div>
          <div style="background:rgba(255,255,255,0.04);border-radius:var(--radius);padding:16px;text-align:center;"><div style="font-size:1.6rem;font-weight:800;color:var(--orange-500);">57–60 cm</div><div style="font-size:0.82rem;color:var(--text-muted-dark);margin-top:4px;">Diameter</div></div>
        </div>
        <p style="color:var(--text-muted-dark);">Used when you need to send more. Not all shippers offer large barrels — confirm availability when requesting a quote.</p>
      </div>
      <div style="background:var(--navy-700);border:1px solid rgba(255,255,255,0.08);border-radius:var(--radius-lg);padding:36px;">
        <div class="section-eyebrow">Alternative</div>
        <h2 style="font-size:1.6rem;margin-bottom:12px;">Box shipping</h2>
        <p style="color:var(--text-muted-dark);">Some shippers accept large cardboard boxes. Useful for bulkier or oddly shaped items. Pricing and availability varies — ask your shipper.</p>
      </div>
    </div>
    <div style="background:rgba(245,166,35,0.08);border:1px solid rgba(245,166,35,0.2);border-radius:var(--radius);padding:16px 20px;max-width:720px;margin-top:32px;"><p style="margin:0;font-size:0.88rem;color:var(--text-muted-dark);">⚠️ <strong style="color:var(--white);">Weight limits vary by shipper.</strong> Always confirm the maximum weight and overweight charge before you pack.</p></div>
    ''' + BACK + '''
  </div>
</section>'''

COSTS = '''<section class="page-header">
  <div class="container">
    <h1>Costs and pricing</h1>
    <p>Why we don\'t publish fixed prices — and what affects what you pay.</p>
  </div>
</section>
<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container"><div class="prose">
    <h2>Why we don\'t publish fixed prices</h2>
    <p>Barrel shipping prices change regularly. Fuel costs, port fees, exchange rates and seasonal demand all affect what shippers charge. A price published today may be out of date by the time you book. We help you understand what drives the cost so you can ask the right questions and compare quotes fairly.</p>
    <h2>What affects the price</h2>
    <ul>
      <li><strong>Destination</strong> — shipping to Jamaica is priced differently from shipping to Dominica or Guyana.</li>
      <li><strong>Collection vs drop-off</strong> — home collection typically costs more than dropping the barrel at the shipper\'s depot.</li>
      <li><strong>Door-to-door vs port-to-port</strong> — door-to-door includes delivery to an address in the destination country.</li>
      <li><strong>Barrel size and weight</strong> — larger or heavier barrels cost more. Overweight charges add up quickly.</li>
      <li><strong>Season</strong> — prices rise around Christmas and Easter as demand increases.</li>
      <li><strong>Customs and port fees</strong> — some quotes include all charges to the door; others quote the shipping fee only.</li>
    </ul>
    <h2>Typical price range</h2>
    <p>For a standard barrel shipped door-to-door from London to Jamaica, typical prices range from approximately <strong style="color:var(--orange-500);">£90 to £180</strong>. This is a guide only.</p>
    <h2>Getting the best value</h2>
    <ul>
      <li>Request quotes from at least two or three shippers before deciding.</li>
      <li>Ask exactly what is included — and what is not.</li>
      <li>Find out when the next sailing is, so you can plan ahead.</li>
      <li>Book early during peak seasons.</li>
    </ul>
  </div>''' + BACK + '''</div>
</section>'''

PRIVACY = '''<section class="page-header">
  <div class="container">
    <h1>Privacy policy</h1>
    <p>How we collect, use and protect your information.</p>
  </div>
</section>
<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container"><div class="prose">
    <h2>What data we collect</h2>
    <ul>
      <li>Information you submit via quote request or contact forms (name, email, destination, message).</li>
      <li>Anonymous usage data via Google Analytics (pages visited, browser type). This does not identify you personally.</li>
      <li>Community reviews submitted voluntarily, including your first name and review content.</li>
    </ul>
    <h2>How we use it</h2>
    <ul>
      <li>To forward your quote request to relevant shipping companies.</li>
      <li>To respond to contact form enquiries.</li>
      <li>To understand how the site is used and improve it.</li>
      <li>To publish verified community reviews (first name only).</li>
    </ul>
    <h2>What we don\'t do</h2>
    <ul>
      <li>We do not sell your data to third parties.</li>
      <li>We do not share your details beyond what is needed to process your quote.</li>
      <li>We do not use your data for advertising.</li>
    </ul>
    <h2>Your rights</h2>
    <p>You have the right to access, correct or delete your personal data. Contact us at <a href="mailto:hello@barrelcompare.co.uk" style="color:var(--orange-500);">hello@barrelcompare.co.uk</a>.</p>
    <h2>Cookies</h2>
    <p>We use Google Analytics cookies only — no advertising or tracking cookies. You can disable cookies in your browser settings.</p>
    <h2>ICO registration</h2>
    <p>ICO registration pending. We are committed to complying with UK data protection law.</p>
    <p style="color:var(--text-muted-dark);font-size:0.85rem;">Last updated: May 2026</p>
  </div>''' + BACK + '''</div>
</section>'''

TERMS_PAGE = '''<section class="page-header">
  <div class="container">
    <h1>Terms of use</h1>
    <p>Using BarrelCompare means you\'ve accepted these terms.</p>
  </div>
</section>
<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container"><div class="prose">
    <h2>What BarrelCompare is</h2>
    <p>BarrelCompare is an independent comparison service. We are not a shipping company, freight forwarder or agent. Any contract for shipping services is between you and the shipper you choose. BarrelCompare is not a party to that contract.</p>
    <h2>Your responsibilities</h2>
    <ul>
      <li>Ensure barrel contents comply with UK export regulations and destination country import rules.</li>
      <li>Provide accurate information when requesting a quote or submitting a review.</li>
      <li>Submit honest reviews based on genuine experience. Do not submit false, misleading or defamatory content.</li>
      <li>Do not use BarrelCompare for any unlawful purpose.</li>
    </ul>
    <h2>Our liability</h2>
    <p>BarrelCompare provides information on an "as is" basis. We cannot guarantee all details — including prices, availability and service descriptions — are current at the time you read them. We are not liable for any loss arising from your use of this site or your dealings with any shipping company found through it.</p>
    <h2>Changes to these terms</h2>
    <p>We may update these terms at any time. Continued use of the site constitutes acceptance of the updated terms.</p>
    <h2>Contact</h2>
    <p>Questions? Email <a href="mailto:hello@barrelcompare.co.uk" style="color:var(--orange-500);">hello@barrelcompare.co.uk</a>.</p>
    <p style="color:var(--text-muted-dark);font-size:0.85rem;">Last updated: May 2026</p>
  </div>''' + BACK + '''</div>
</section>'''

WHAT = '''<section class="page-header">
  <div class="container">
    <h1>What does BarrelCompare do?</h1>
    <p>How the platform works and what we stand for.</p>
  </div>
</section>
<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container"><div class="prose">
    <h2>How the platform works</h2>
    <p>BarrelCompare brings together information on UK barrel shipping companies so you can compare them side by side. We gather details on pricing, transit times, destinations, collection options and customer experiences — and present them clearly in one place.</p>
    <p>When you use our quote form, we connect your request with relevant shippers so they can respond to you directly. We do not mark up quotes or add hidden charges.</p>
    <p>We also publish guides, glossaries and country rules to help you understand the process — whether you\'re shipping for the first time or the hundredth time.</p>
    <h2>Our independence policy</h2>
    <p>BarrelCompare is independent of every shipping company on the platform. We are not owned by, funded by, or affiliated with any shipper. Our goal is to give you an honest, unbiased picture so you can make the best decision for your family.</p>
    <p>Shippers do not pay to appear higher in results or to receive better reviews. We publish what we find.</p>
    <h2>What we hold ourselves to</h2>
    <ul>
      <li>We only publish information we have verified or can stand behind.</li>
      <li>We present shippers fairly and without commercial bias.</li>
      <li>We update information when we learn it has changed.</li>
      <li>We respond to complaints and remove shippers who consistently fail the community.</li>
    </ul>
    <h2>Get in touch</h2>
    <p>Email us at <a href="mailto:hello@barrelcompare.co.uk" style="color:var(--orange-500);">hello@barrelcompare.co.uk</a>.</p>
  </div>''' + BACK + '''</div>
</section>'''

pages = [
    ('supplier-standards.html', 'What good service looks like | BarrelCompare', 'The standards BarrelCompare believes every barrel shipper should meet.', 'What good service looks like | BarrelCompare', '/supplier-standards/', '/about/', SUPPLIER_STANDARDS),
    ('country-rules/index.html', 'Country rules, what can I send? | BarrelCompare', 'Country-by-country guide to what you can and cannot send in a barrel to the Caribbean.', 'Country rules | BarrelCompare', '/country-rules/', '/', COUNTRY_RULES),
    ('hidden-fees/index.html', 'Hidden fees guide | BarrelCompare', 'Common extra charges in barrel shipping and the questions to ask before you book.', 'Hidden fees guide | BarrelCompare', '/hidden-fees/', '/', HIDDEN_FEES),
    ('glossary/index.html', 'Barrel shipping glossary | BarrelCompare', 'Key barrel shipping terms explained — from Bill of Lading to waybill.', 'Barrel shipping glossary | BarrelCompare', '/glossary/', '/', GLOSSARY),
    ('barrel-sizes/index.html', 'Barrel sizes and dimensions | BarrelCompare', 'Standard and large barrel dimensions for UK Caribbean shipping.', 'Barrel sizes | BarrelCompare', '/barrel-sizes/', '/', BARREL_SIZES),
    ('costs-and-pricing/index.html', 'Barrel shipping costs and pricing | BarrelCompare', 'Why barrel shipping prices vary and what affects your quote.', 'Costs and pricing | BarrelCompare', '/costs-and-pricing/', '/', COSTS),
    ('privacy/index.html', 'Privacy policy | BarrelCompare', 'How BarrelCompare collects, uses and protects your personal data.', 'Privacy policy | BarrelCompare', '/privacy/', '/', PRIVACY),
    ('terms/index.html', 'Terms of use | BarrelCompare', 'Terms of use for BarrelCompare.', 'Terms of use | BarrelCompare', '/terms/', '/', TERMS_PAGE),
    ('what-does-barrelcompare-do/index.html', 'What does BarrelCompare do? | BarrelCompare', 'How BarrelCompare works and our independence policy.', 'What does BarrelCompare do? | BarrelCompare', '/what-does-barrelcompare-do/', '/', WHAT),
]

for fn, title, meta, og, og_url, active, content in pages:
    make_page(title, meta, og, og_url, active, content, os.path.join(REPO, fn))

print('\nAll done.')
