#!/usr/bin/env python3
"""Generate new pages using about.html as template."""
import re, os

REPO = '/Users/kidunknown/Desktop/barrelcompare-website'

with open(os.path.join(REPO, 'about.html'), 'r', encoding='utf-8') as f:
    TEMPLATE = f.read()

def make_page(slug, title, meta_desc, og_title, og_url, active_url, page_content, out_path):
    t = TEMPLATE

    # Title and meta
    t = re.sub(r'<title>[^<]+</title>', f'<title>{title}</title>', t)
    t = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{meta_desc}">', t)
    t = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{og_title}">', t)
    t = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{meta_desc}">', t)
    t = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="https://barrelcompare.co.uk{og_url}">', t)

    # Active nav link
    t = t.replace(' class="active">', '>')  # remove existing active
    t = t.replace(f'href="{active_url}">', f'href="{active_url}" class="active">')

    # Replace body content (between header close and footer)
    t = re.sub(
        r'</header>.*?(<nav class="nav-scroll-bar")',
        r'</header>\n\1',
        t, flags=re.DOTALL
    )
    # Replace everything between nav-scroll-bar and footer with page content
    t = re.sub(
        r'(</nav>)\s*\n<section class="page-header">.*?(?=<footer)',
        r'\1\n\n' + page_content + '\n\n',
        t, flags=re.DOTALL
    )

    # Fix nav scroll bar active for this page
    t = re.sub(r'(<nav class="nav-scroll-bar"[^>]*>.*?</nav>)',
               lambda m: fix_scroll_nav(m.group(1), active_url), t, flags=re.DOTALL)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(t)
    print(f'Created: {out_path.replace(REPO, "")}')

def fix_scroll_nav(nav_html, active_url):
    nav_html = nav_html.replace(' class="active"', '')
    nav_html = nav_html.replace(f'href="{active_url}"', f'href="{active_url}" class="active"')
    return nav_html

SHARED_FOOTER_NOTE = '<p style="margin-top:40px;"><a href="/" style="color:var(--orange-500);">← Back to home</a></p>'

# ── SUPPLIER STANDARDS ────────────────────────────────────────────────────
SUPPLIER_STANDARDS_CONTENT = '''<section class="page-header">
  <div class="container">
    <h1>What good service looks like</h1>
    <p>The standards we believe every customer deserves.</p>
  </div>
</section>

<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container">
    <div class="prose">

      <div style="background:rgba(45,108,223,0.12);border:1px solid rgba(45,108,223,0.3);border-radius:var(--radius);padding:20px 24px;margin-bottom:40px;">
        <p style="margin:0;color:var(--text-on-dark);">Reputable shippers already work to high standards. Our goal is to help make this the norm across the industry, so every customer can book with greater confidence and receive the level of service they deserve.</p>
      </div>

      <h2>1. Treat every customer with courtesy and respect</h2>
      <p>Every customer deserves to be treated with patience and professionalism, regardless of the size of their shipment or how many questions they ask.</p>

      <h2>2. Respond to new quote requests within 48 hours</h2>
      <p>Customers should not be left waiting. A prompt response — even to say more information is needed — sets the tone for the whole relationship.</p>

      <h2>3. Be upfront about pricing from the start</h2>
      <p>All costs should be clearly communicated before a booking is confirmed. Surprises at the end of the process — whether customs fees, fuel surcharges or handling charges — erode trust.</p>

      <h2>4. Keep customers informed throughout the journey</h2>
      <p>From collection to port clearance to final delivery, customers should know where their barrel is and what to expect next. No news is not good news when someone's family is waiting.</p>

      <h2>5. If something goes wrong, own it</h2>
      <p>Delays happen. Problems arise. What matters is how a shipper responds. Acknowledge the issue, communicate clearly, and do what is reasonable to put it right.</p>

      <h2>6. Advise customers on restrictions before they pack</h2>
      <p>Different countries have different rules on what can be imported. A good shipper helps customers avoid costly mistakes before the barrel leaves the house.</p>

      <h2>7. Only accept bookings that can be fulfilled</h2>
      <p>Do not take money for a service that cannot be delivered. If capacity is full, routes change, or a destination cannot be served, customers must be told before they commit.</p>

      <div style="margin-top:56px;padding:32px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:var(--radius-lg);text-align:center;">
        <h3 style="margin-bottom:12px;">Questions or feedback?</h3>
        <p style="color:var(--text-muted-dark);margin-bottom:20px;">We'd love to hear from shippers and customers alike.</p>
        <a href="mailto:hello@barrelcompare.co.uk" class="btn btn-orange">hello@barrelcompare.co.uk</a>
      </div>

    </div>
    ''' + SHARED_FOOTER_NOTE + '''
  </div>
</section>'''

# ── COUNTRY RULES ─────────────────────────────────────────────────────────
def country_table(permitted, prohibited):
    p_rows = ''.join(f'<tr><td style="padding:10px 12px;border-bottom:1px solid rgba(255,255,255,0.06);">✓ {i}</td></tr>' for i in permitted)
    x_rows = ''.join(f'<tr><td style="padding:10px 12px;border-bottom:1px solid rgba(255,255,255,0.06);">✗ {i}</td></tr>' for i in prohibited)
    return f'''<div style="display:grid;gap:16px;grid-template-columns:1fr 1fr;margin-bottom:8px;">
      <div><table style="width:100%;border-collapse:collapse;font-size:0.9rem;background:rgba(37,211,102,0.06);border-radius:var(--radius);">
        <thead><tr><th style="padding:10px 12px;text-align:left;color:#6fe39d;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.06em;">Generally permitted</th></tr></thead>
        <tbody>{p_rows}</tbody></table></div>
      <div><table style="width:100%;border-collapse:collapse;font-size:0.9rem;background:rgba(239,68,68,0.06);border-radius:var(--radius);">
        <thead><tr><th style="padding:10px 12px;text-align:left;color:#ff8888;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.06em;">Generally prohibited</th></tr></thead>
        <tbody>{x_rows}</tbody></table></div>
    </div>'''

COUNTRY_DATA = [
    ('Jamaica', [
        'Clothing and personal effects','Food items (dried, tinned, preserved)','Household goods','Children\'s toys and school supplies','Electrical appliances (used)','Toiletries and cosmetics','Medicines (with prescription where required)',
    ], [
        'Firearms and ammunition (without licence)','Illegal drugs','Fresh meat and produce (restrictions apply)','Items that infringe copyright','Pornographic material','Certain agricultural products',
    ]),
    ('Grenada', [
        'Personal clothing and effects','Household goods and appliances','Tinned and dried food','Toiletries and cosmetics','Toys and gifts','Books and educational materials',
    ], [
        'Firearms without licence','Illegal substances','Live animals (without permit)','Plant material without phytosanitary certificate','Counterfeit goods',
    ]),
    ('Guyana', [
        'Personal clothing','Household items','Non-perishable food','Toiletries','Electrical goods (used)','Medicines (with documentation)',
    ], [
        'Narcotics and controlled substances','Weapons without licence','Prohibited agricultural products','Counterfeit goods','Pornographic material',
    ]),
    ('St Lucia', [
        'Clothing and personal effects','Household goods','Non-perishable food items','Toiletries','Electrical items','Children\'s goods',
    ], [
        'Drugs and narcotics','Firearms (without permit)','Indecent material','Certain agricultural products','Counterfeit items',
    ]),
    ('Barbados', [
        'Personal and household goods','Clothing','Non-perishable foods','Toiletries and cosmetics','Electrical appliances','Toys',
    ], [
        'Controlled substances','Unlicensed firearms','Prohibited agricultural imports','Counterfeit goods','Pornographic material',
    ]),
    ('The Bahamas', [
        'Personal effects and clothing','Household goods','Non-perishable food','Electrical items','Toiletries','Gifts',
    ], [
        'Drugs and narcotics','Weapons without licence','Certain agricultural imports','Counterfeit goods',
    ]),
    ('Trinidad & Tobago', [
        'Clothing and personal effects','Household goods','Tinned and dried food','Toiletries','Electrical goods','Medicines',
    ], [
        'Illegal drugs','Unlicensed firearms','Prohibited plant and agricultural material','Counterfeit items','Pornographic material',
    ]),
    ('Antigua', [
        'Personal clothing and effects','Household goods','Non-perishable food','Toiletries','Electrical appliances','Children\'s goods',
    ], [
        'Controlled substances','Firearms (unlicensed)','Certain agricultural products','Counterfeit goods',
    ]),
    ('St Vincent', [
        'Personal effects','Household goods','Non-perishable food','Toiletries','Electrical items','Toys and gifts',
    ], [
        'Illegal drugs','Unlicensed weapons','Prohibited agricultural imports','Counterfeit goods',
    ]),
    ('Dominica', [
        'Personal clothing and effects','Household goods','Tinned and dried food','Toiletries','Electrical appliances','Gifts',
    ], [
        'Narcotics','Unlicensed firearms','Prohibited agricultural items','Counterfeit goods','Pornographic material',
    ]),
]

country_sections = ''
for name, permitted, prohibited in COUNTRY_DATA:
    country_sections += f'''
      <h2>{name}</h2>
      {country_table(permitted, prohibited)}
      <p style="font-size:0.82rem;color:var(--text-muted-dark);margin-bottom:32px;">Rules change. Always confirm current restrictions with your shipper before packing.</p>
'''

COUNTRY_RULES_CONTENT = f'''<section class="page-header">
  <div class="container">
    <h1>Country rules</h1>
    <p>What you can and cannot send to each destination. Always confirm with your shipper before packing.</p>
  </div>
</section>

<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container">
    <div style="background:rgba(245,166,35,0.08);border:1px solid rgba(245,166,35,0.2);border-radius:var(--radius);padding:16px 20px;margin-bottom:40px;">
      <p style="margin:0;font-size:0.9rem;color:var(--text-muted-dark);">⚠️ This guide is for general reference only. Import rules change. Always verify with your shipper and the destination country's customs authority before packing your barrel.</p>
    </div>
    <div class="prose">
      {country_sections}
    </div>
    {SHARED_FOOTER_NOTE}
  </div>
</section>'''

# ── HIDDEN FEES ───────────────────────────────────────────────────────────
FEES = [
    ('Customs duty', 'Charged by the destination country on goods above a certain value. The rate depends on what you are sending and where.', 'Ask: Is customs duty included in the quoted price, or will I be charged separately on arrival?'),
    ('Port handling charges', 'Fees charged by the port authority for handling your barrel when it arrives. Sometimes called "landing fees" or "port fees".', 'Ask: Are port handling charges included, or are they paid separately by the recipient?'),
    ('Fuel surcharges', 'Shippers may add a variable surcharge to cover fuel costs. This is not always shown in the headline price.', 'Ask: Does the quoted price include any fuel surcharges? Are these fixed or variable?'),
    ('Storage fees', 'If your barrel cannot be collected promptly on arrival, daily storage charges may apply.', 'Ask: How long is the barrel held before storage charges apply, and how much are those charges?'),
    ('Empty barrel cost', 'If you are buying a barrel from the shipper, the cost is sometimes separate from the shipping fee.', 'Ask: Is the barrel included in the price, or do I need to purchase it separately?'),
    ('Overweight charges', 'Most shippers have weight limits. Exceeding them can result in significant additional charges.', 'Ask: What is the maximum weight included, and what is the charge per kg above that limit?'),
    ('Collection charges', 'Some shippers quote a port-to-port price. Home collection and delivery to the destination may cost extra.', 'Ask: Is home collection included? Is door-to-door delivery included, or do I pay extra for that?'),
]

fee_items = ''
for title, desc, question in FEES:
    fee_items += f'''
      <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:var(--radius-lg);padding:28px;margin-bottom:16px;">
        <h3 style="margin-bottom:8px;color:var(--white);">{title}</h3>
        <p style="color:var(--text-muted-dark);margin-bottom:16px;">{desc}</p>
        <div style="background:rgba(245,166,35,0.08);border-left:3px solid var(--orange-500);padding:12px 16px;border-radius:0 8px 8px 0;">
          <p style="margin:0;font-size:0.9rem;color:var(--text-on-dark);"><strong>Question to ask:</strong> {question}</p>
        </div>
      </div>'''

HIDDEN_FEES_CONTENT = f'''<section class="page-header">
  <div class="container">
    <h1>Hidden fees guide</h1>
    <p>The charges that can catch customers out — and the questions to ask before you book.</p>
  </div>
</section>

<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container">
    <p style="color:var(--text-muted-dark);max-width:640px;margin-bottom:40px;font-size:1.05rem;">Barrel shipping prices are not always what they first appear. Here are the most common additional charges — and how to make sure you know about them before you commit.</p>
    {fee_items}
    {SHARED_FOOTER_NOTE}
  </div>
</section>'''

# ── GLOSSARY ──────────────────────────────────────────────────────────────
TERMS = [
    ('Barrel', 'A large plastic drum used to ship goods to the Caribbean. Standard barrels are typically 55 gallon (around 85–90 cm tall).'),
    ('Bill of Lading', 'A legal document issued by a carrier that details the type, quantity and destination of the goods being shipped. Acts as a receipt and title document.'),
    ('Break bulk', 'Cargo shipped as individual units rather than in containers. Many barrel shipments are consolidated break bulk freight.'),
    ('CARICOM', 'Caribbean Community — a trade bloc of Caribbean nations. CARICOM members may receive preferential customs treatment for certain goods.'),
    ('Carrier liability', 'The legal responsibility of the shipper for loss or damage to your goods during transit. Check the level of cover before booking.'),
    ('CIF', 'Cost, Insurance and Freight — a pricing term meaning the quoted price includes the cost of goods, shipping insurance and freight charges to the destination port.'),
    ('Consolidation', 'Combining multiple customers\' barrels into a single shipment to reduce costs. Most UK Caribbean barrel shippers operate on a consolidated basis.'),
    ('Customs duty', 'A tax levied by the destination country on imported goods. The rate varies by country and by the type of goods.'),
    ('Customs clearance', 'The process of obtaining permission from customs authorities to import goods into a country. Your barrel must clear customs before it can be delivered.'),
    ('Door-to-door', 'A service where the shipper collects the barrel from your home in the UK and delivers it to an address in the destination country.'),
    ('Drop-off', 'A service where you deliver the barrel to the shipper\'s depot yourself, rather than having it collected from your home.'),
    ('FCL', 'Full Container Load — a shipment where you book an entire shipping container. Rarely used for single barrel shipments.'),
    ('Freight forwarder', 'A company that arranges the transportation of goods on behalf of customers, often using a network of carriers and agents.'),
    ('LCL', 'Less than Container Load — your goods share a container with other customers\' shipments. Most barrel shipping is LCL.'),
    ('Manifest', 'A document listing the contents of a shipment, required by customs authorities. You may need to declare what is in your barrel.'),
    ('Port of entry', 'The port in the destination country where your barrel arrives and passes through customs.'),
    ('Port-to-port', 'A service where the shipper is responsible only for transportation between ports. Collection at the UK end and delivery at the destination end are not included.'),
    ('Sea freight', 'Goods transported by ship. The majority of barrel shipments to the Caribbean travel by sea freight.'),
    ('Storage fee', 'A charge applied when goods are held at the destination port or warehouse beyond the free storage period.'),
    ('Transit time', 'The time from when your barrel is collected or accepted by the shipper to when it arrives at the destination port. Does not include customs clearance time.'),
    ('TRN', 'Taxpayer Registration Number — required in some Caribbean countries (particularly Jamaica) for customs clearance.'),
    ('Waybill', 'A document issued by the carrier describing the shipment and its destination. Similar to a Bill of Lading but not a title document.'),
]

term_items = ''.join(f'''
      <div style="padding:20px 0;border-bottom:1px solid rgba(255,255,255,0.08);">
        <h3 style="font-size:1.05rem;color:var(--orange-500);margin-bottom:6px;">{term}</h3>
        <p style="color:var(--text-muted-dark);margin:0;font-size:0.95rem;">{defn}</p>
      </div>''' for term, defn in TERMS)

GLOSSARY_CONTENT = f'''<section class="page-header">
  <div class="container">
    <h1>Barrel shipping glossary</h1>
    <p>Key terms explained — from Bill of Lading to waybill.</p>
  </div>
</section>

<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container">
    <div style="max-width:720px;">
      {term_items}
    </div>
    {SHARED_FOOTER_NOTE}
  </div>
</section>'''

# ── BARREL SIZES ──────────────────────────────────────────────────────────
BARREL_SIZES_CONTENT = '''<section class="page-header">
  <div class="container">
    <h1>Barrel sizes</h1>
    <p>Standard dimensions, weight limits and what to expect.</p>
  </div>
</section>

<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container">

    <div style="display:grid;gap:24px;grid-template-columns:1fr;max-width:900px;">

      <div style="background:var(--navy-700);border:1px solid rgba(255,255,255,0.08);border-radius:var(--radius-lg);padding:36px;">
        <div class="section-eyebrow">Most common</div>
        <h2 style="font-size:1.6rem;margin-bottom:12px;">Standard barrel</h2>
        <div style="display:grid;gap:16px;grid-template-columns:1fr 1fr;margin-bottom:20px;">
          <div style="background:rgba(255,255,255,0.04);border-radius:var(--radius);padding:16px;text-align:center;">
            <div style="font-size:1.6rem;font-weight:800;color:var(--orange-500);">85–90 cm</div>
            <div style="font-size:0.82rem;color:var(--text-muted-dark);margin-top:4px;">Height</div>
          </div>
          <div style="background:rgba(255,255,255,0.04);border-radius:var(--radius);padding:16px;text-align:center;">
            <div style="font-size:1.6rem;font-weight:800;color:var(--orange-500);">55–57 cm</div>
            <div style="font-size:0.82rem;color:var(--text-muted-dark);margin-top:4px;">Diameter</div>
          </div>
        </div>
        <p style="color:var(--text-muted-dark);">The most widely used barrel size for Caribbean shipments. Suitable for clothing, food, household goods and personal effects. Weight limits vary by shipper — typically 50–60 kg maximum.</p>
      </div>

      <div style="background:var(--navy-700);border:1px solid rgba(255,255,255,0.08);border-radius:var(--radius-lg);padding:36px;">
        <div class="section-eyebrow">Larger capacity</div>
        <h2 style="font-size:1.6rem;margin-bottom:12px;">Large barrel</h2>
        <div style="display:grid;gap:16px;grid-template-columns:1fr 1fr;margin-bottom:20px;">
          <div style="background:rgba(255,255,255,0.04);border-radius:var(--radius);padding:16px;text-align:center;">
            <div style="font-size:1.6rem;font-weight:800;color:var(--orange-500);">100–107 cm</div>
            <div style="font-size:0.82rem;color:var(--text-muted-dark);margin-top:4px;">Height</div>
          </div>
          <div style="background:rgba(255,255,255,0.04);border-radius:var(--radius);padding:16px;text-align:center;">
            <div style="font-size:1.6rem;font-weight:800;color:var(--orange-500);">57–60 cm</div>
            <div style="font-size:0.82rem;color:var(--text-muted-dark);margin-top:4px;">Diameter</div>
          </div>
        </div>
        <p style="color:var(--text-muted-dark);">Used when you need to send more. Heavier and bulkier to handle. Not all shippers offer large barrels, so confirm availability when requesting a quote.</p>
      </div>

      <div style="background:var(--navy-700);border:1px solid rgba(255,255,255,0.08);border-radius:var(--radius-lg);padding:36px;">
        <div class="section-eyebrow">Alternative</div>
        <h2 style="font-size:1.6rem;margin-bottom:12px;">Box shipping</h2>
        <p style="color:var(--text-muted-dark);">Some shippers accept large cardboard boxes instead of barrels. Useful for bulkier or oddly shaped items that do not fit in a standard barrel. Pricing and availability varies — ask your shipper for details.</p>
      </div>

    </div>

    <div style="background:rgba(245,166,35,0.08);border:1px solid rgba(245,166,35,0.2);border-radius:var(--radius);padding:20px 24px;max-width:720px;margin-top:32px;">
      <p style="margin:0;font-size:0.9rem;color:var(--text-muted-dark);">⚠️ <strong style="color:var(--white);">Weight limits vary by shipper.</strong> Always confirm the maximum weight included in your quote and the charge for exceeding it before you pack.</p>
    </div>

    ''' + SHARED_FOOTER_NOTE + '''
  </div>
</section>'''

# ── COSTS AND PRICING ─────────────────────────────────────────────────────
COSTS_CONTENT = '''<section class="page-header">
  <div class="container">
    <h1>Costs and pricing</h1>
    <p>Why we don\'t publish fixed prices — and what affects what you pay.</p>
  </div>
</section>

<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container">
    <div class="prose">

      <h2>Why we don\'t publish fixed prices</h2>
      <p>Barrel shipping prices change regularly. Fuel costs, port fees, exchange rates and seasonal demand all affect what shippers charge. A price published today may be out of date by the time you book. We choose not to show prices that could mislead you.</p>
      <p>Instead, we help you understand what drives the cost, so you can ask the right questions and compare quotes on an equal footing.</p>

      <h2>What affects the price</h2>
      <ul>
        <li><strong>Destination</strong> — shipping to Jamaica is priced differently from shipping to Dominica or Guyana.</li>
        <li><strong>Collection vs drop-off</strong> — having the shipper collect from your home typically costs more than dropping the barrel at their depot yourself.</li>
        <li><strong>Door-to-door vs port-to-port</strong> — door-to-door includes delivery to an address. Port-to-port means the recipient collects from the port.</li>
        <li><strong>Barrel size and weight</strong> — larger or heavier barrels cost more. Overweight charges can add up quickly.</li>
        <li><strong>Season</strong> — prices often increase around Christmas and Easter as demand rises.</li>
        <li><strong>Customs and port fees</strong> — some quotes include all charges to the door; others quote only the shipping fee, with customs and port fees payable separately on arrival.</li>
      </ul>

      <h2>Typical price range</h2>
      <p>For a standard barrel shipped door-to-door from London to Jamaica, typical prices range from approximately <strong style="color:var(--orange-500);">£90 to £180</strong>. This is a guide only — your quote will depend on all the factors above.</p>
      <p>Always ask for a fully itemised quote so you can compare like for like.</p>

      <h2>Getting the best value</h2>
      <ul>
        <li>Request quotes from at least two or three shippers before deciding.</li>
        <li>Ask exactly what is included — and what is not.</li>
        <li>Find out when the next available sailing is, so you can plan your packing.</li>
        <li>Book early during peak seasons.</li>
      </ul>

    </div>
    ''' + SHARED_FOOTER_NOTE + '''
  </div>
</section>'''

# ── PRIVACY ───────────────────────────────────────────────────────────────
PRIVACY_CONTENT = '''<section class="page-header">
  <div class="container">
    <h1>Privacy policy</h1>
    <p>How we collect, use and protect your information.</p>
  </div>
</section>

<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container">
    <div class="prose">

      <h2>What data we collect</h2>
      <p>When you use BarrelCompare, we may collect:</p>
      <ul>
        <li>Information you submit via our quote request or contact forms (name, email, destination, message).</li>
        <li>Anonymous usage data collected via Google Analytics (pages visited, time on site, browser type). This does not identify you personally.</li>
        <li>Community reviews submitted voluntarily, including your first name and the content of your review.</li>
      </ul>

      <h2>How we use it</h2>
      <ul>
        <li>To forward your quote request to relevant shipping companies.</li>
        <li>To respond to contact form enquiries.</li>
        <li>To understand how the site is used and improve it over time.</li>
        <li>To publish verified community reviews (first name only, no contact details).</li>
      </ul>

      <h2>What we don\'t do</h2>
      <ul>
        <li>We do not sell your data to third parties.</li>
        <li>We do not share your personal details with shipping companies beyond what is necessary to process your quote request.</li>
        <li>We do not use your data for advertising purposes.</li>
      </ul>

      <h2>Your rights</h2>
      <p>You have the right to request access to the personal data we hold about you, to ask for it to be corrected or deleted, and to object to its use. To exercise these rights, contact us at <a href="mailto:hello@barrelcompare.co.uk" style="color:var(--orange-500);">hello@barrelcompare.co.uk</a>.</p>

      <h2>Cookies</h2>
      <p>We use cookies for Google Analytics. These are analytics cookies only — we do not use advertising or tracking cookies. You can disable cookies in your browser settings at any time.</p>

      <h2>ICO registration</h2>
      <p>ICO registration pending. We are committed to complying with UK data protection law.</p>

      <h2>Contact</h2>
      <p>Questions about this policy? Email us at <a href="mailto:hello@barrelcompare.co.uk" style="color:var(--orange-500);">hello@barrelcompare.co.uk</a>.</p>

      <p style="color:var(--text-muted-dark);font-size:0.85rem;">Last updated: May 2026</p>

    </div>
    ''' + SHARED_FOOTER_NOTE + '''
  </div>
</section>'''

# ── TERMS ─────────────────────────────────────────────────────────────────
TERMS_CONTENT = '''<section class="page-header">
  <div class="container">
    <h1>Terms of use</h1>
    <p>Using BarrelCompare means you\'ve read and accepted these terms.</p>
  </div>
</section>

<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container">
    <div class="prose">

      <h2>What BarrelCompare is</h2>
      <p>BarrelCompare is an independent comparison service. We help you find and compare barrel shipping companies in the UK. We are not a shipping company, freight forwarder, or agent. We do not handle, insure or take responsibility for any goods.</p>
      <p>Any contract for shipping services is between you and the shipper you choose. BarrelCompare is not a party to that contract.</p>

      <h2>Your responsibilities</h2>
      <ul>
        <li>You are responsible for ensuring the contents of your barrel comply with UK export regulations and the import rules of your destination country.</li>
        <li>You are responsible for providing accurate information when requesting a quote or submitting a review.</li>
        <li>Reviews submitted must be honest and based on your genuine experience. Do not submit false, misleading or defamatory reviews.</li>
        <li>You must not use BarrelCompare for any unlawful purpose.</li>
      </ul>

      <h2>Our liability</h2>
      <p>BarrelCompare provides information on an "as is" basis. While we work to keep information accurate and up to date, we cannot guarantee that all details — including prices, availability and service descriptions — are current at the time you read them.</p>
      <p>We are not liable for any loss or damage arising from your use of this site or your dealings with any shipping company found through it.</p>

      <h2>Links and third parties</h2>
      <p>This site may link to third-party websites. We are not responsible for the content or practices of those sites.</p>

      <h2>Changes to these terms</h2>
      <p>We may update these terms at any time. Continued use of the site constitutes acceptance of the updated terms.</p>

      <h2>Contact</h2>
      <p>Questions? Email <a href="mailto:hello@barrelcompare.co.uk" style="color:var(--orange-500);">hello@barrelcompare.co.uk</a>.</p>

      <p style="color:var(--text-muted-dark);font-size:0.85rem;">Last updated: May 2026</p>

    </div>
    ''' + SHARED_FOOTER_NOTE + '''
  </div>
</section>'''

# ── WHAT DOES BARRELCOMPARE DO ────────────────────────────────────────────
WHAT_CONTENT = '''<section class="page-header">
  <div class="container">
    <h1>What does BarrelCompare do?</h1>
    <p>How the platform works and what we stand for.</p>
  </div>
</section>

<section style="background:var(--navy-800);padding:64px 0;">
  <div class="container">
    <div class="prose">

      <h2>How the platform works</h2>
      <p>BarrelCompare brings together information on UK barrel shipping companies so you can compare them side by side. We gather details on pricing, transit times, destinations covered, collection options and customer experiences — then present them clearly in one place.</p>
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
      <p>We\'re always open to feedback — from customers and shippers alike. Email us at <a href="mailto:hello@barrelcompare.co.uk" style="color:var(--orange-500);">hello@barrelcompare.co.uk</a>.</p>

    </div>
    ''' + SHARED_FOOTER_NOTE + '''
  </div>
</section>'''

# ── BUILD ALL PAGES ───────────────────────────────────────────────────────
pages = [
    {
        'out': os.path.join(REPO, 'supplier-standards.html'),
        'title': 'What good service looks like | BarrelCompare',
        'meta': 'The standards BarrelCompare believes every barrel shipper should meet — and every customer deserves.',
        'og_title': 'What good service looks like | BarrelCompare',
        'og_url': '/supplier-standards/',
        'active': '/about/',
        'content': SUPPLIER_STANDARDS_CONTENT,
    },
    {
        'out': os.path.join(REPO, 'country-rules/index.html'),
        'title': 'Country rules, what can I send? | BarrelCompare',
        'meta': 'Country-by-country guide to what you can and cannot send in a barrel to Jamaica, Trinidad, Guyana and across the Caribbean.',
        'og_title': 'Country rules | BarrelCompare',
        'og_url': '/country-rules/',
        'active': '/',
        'content': COUNTRY_RULES_CONTENT,
    },
    {
        'out': os.path.join(REPO, 'hidden-fees/index.html'),
        'title': 'Hidden fees guide | BarrelCompare',
        'meta': 'The most common hidden charges in barrel shipping and the questions to ask before you book.',
        'og_title': 'Hidden fees guide | BarrelCompare',
        'og_url': '/hidden-fees/',
        'active': '/',
        'content': HIDDEN_FEES_CONTENT,
    },
    {
        'out': os.path.join(REPO, 'glossary/index.html'),
        'title': 'Barrel shipping glossary | BarrelCompare',
        'meta': 'Key barrel shipping terms explained — from Bill of Lading and CARICOM to LCL, FCL and transit time.',
        'og_title': 'Barrel shipping glossary | BarrelCompare',
        'og_url': '/glossary/',
        'active': '/',
        'content': GLOSSARY_CONTENT,
    },
    {
        'out': os.path.join(REPO, 'barrel-sizes/index.html'),
        'title': 'Barrel sizes and dimensions | BarrelCompare',
        'meta': 'Standard and large barrel dimensions for UK Caribbean shipping. Weight limits, box shipping and what to ask your shipper.',
        'og_title': 'Barrel sizes | BarrelCompare',
        'og_url': '/barrel-sizes/',
        'active': '/',
        'content': BARREL_SIZES_CONTENT,
    },
    {
        'out': os.path.join(REPO, 'costs-and-pricing/index.html'),
        'title': 'Barrel shipping costs and pricing | BarrelCompare',
        'meta': 'Why barrel shipping prices vary, what affects your quote, and typical price ranges for shipping to Jamaica and the Caribbean.',
        'og_title': 'Costs and pricing | BarrelCompare',
        'og_url': '/costs-and-pricing/',
        'active': '/',
        'content': COSTS_CONTENT,
    },
    {
        'out': os.path.join(REPO, 'privacy/index.html'),
        'title': 'Privacy policy | BarrelCompare',
        'meta': 'How BarrelCompare collects, uses and protects your personal data.',
        'og_title': 'Privacy policy | BarrelCompare',
        'og_url': '/privacy/',
        'active': '/',
        'content': PRIVACY_CONTENT,
    },
    {
        'out': os.path.join(REPO, 'terms/index.html'),
        'title': 'Terms of use | BarrelCompare',
        'meta': 'Terms of use for BarrelCompare — what we are, your responsibilities, and our liability.',
        'og_title': 'Terms of use | BarrelCompare',
        'og_url': '/terms/',
        'active': '/',
        'content': TERMS_CONTENT,
    },
    {
        'out': os.path.join(REPO, 'what-does-barrelcompare-do/index.html'),
        'title': 'What does BarrelCompare do? | BarrelCompare',
        'meta': 'How BarrelCompare works, our independence policy and what we hold ourselves to.',
        'og_title': 'What does BarrelCompare do? | BarrelCompare',
        'og_url': '/what-does-barrelcompare-do/',
        'active': '/',
        'content': WHAT_CONTENT,
    },
]

for p in pages:
    make_page(
        slug=p['out'],
        title=p['title'],
        meta_desc=p['meta'],
        og_title=p['og_title'],
        og_url=p['og_url'],
        active_url=p['active'],
        page_content=p['content'],
        out_path=p['out'],
    )

print('\nDone.')
