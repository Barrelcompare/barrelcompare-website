#!/usr/bin/env python3
"""
Formspree integration: wires up all forms with proper endpoints, GA4 events,
loading states, honeypot, validation, and timestamp/source tracking.

FORMSPREE ENDPOINT GUIDE FOR DAVE:
  Current endpoint: xrejbkjz  →  hello@barrelcompare.co.uk
  Dave must create separate endpoints at formspree.io for:
    FS_CONTACT   → hello@barrelcompare.co.uk
    FS_REVIEWS   → reviews@barrelcompare.co.uk
    FS_DOWNLOADS → hello@barrelcompare.co.uk  (gate unlocks + newsletter)
    Per-supplier quote endpoints (set data-formid on each supplier card)
  Once created, replace the IDs in each file's FORMSPREE ENDPOINT comment.
"""

import shutil

BASE = '/Users/kidunknown/Desktop/barrelcompare-website'

def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()

def write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  wrote {path.replace(BASE,"")}')


# ── CONTACT FORM ──────────────────────────────────────────────────────────────

CONTACT_FORM_NEW = '''<form id="contactForm" novalidate style="margin-top:8px;">
  <!-- FORMSPREE ENDPOINT: replace xrejbkjz with your contact form ID from formspree.io -->
  <!-- Route: hello@barrelcompare.co.uk -->
  <input type="text" name="_gotcha" style="display:none;" tabindex="-1">
  <input type="hidden" name="_subject" id="contactSubject" value="Contact enquiry, BarrelCompare">
  <input type="hidden" name="_timestamp" id="contactTimestamp">
  <input type="hidden" name="_source" value="/contact/">

  <div class="form-success" id="successMsg" style="display:none;">
    &#x2713; Message received. We aim to respond the same day.
  </div>
  <div class="form-error" id="errorMsg" style="display:none;">
    Something went wrong. Please try again or email <a href="mailto:hello@barrelcompare.co.uk" style="color:var(--orange-500);">hello@barrelcompare.co.uk</a> directly.
  </div>

  <div class="form-row">
    <div class="form-group">
      <label for="name">Your name <span class="required">*</span></label>
      <input type="text" id="name" name="name" class="form-control" required>
    </div>
    <div class="form-group">
      <label for="email">Email <span class="required">*</span></label>
      <input type="email" id="email" name="email" class="form-control" required>
    </div>
  </div>

  <div class="form-group">
    <label for="phone">Phone number <span style="color:var(--text-muted-dark);font-weight:400;">(optional)</span></label>
    <input type="tel" id="phone" name="phone" class="form-control" placeholder="e.g. 07700 900000">
  </div>

  <div class="form-group">
    <label for="department">Which team do you need? <span class="required">*</span></label>
    <select id="department" name="department" class="form-control" required>
      <option value="">Select a department...</option>
      <option value="Customer Support">Customer Support, user issues, complaints, refunds, account help</option>
      <option value="Sales &amp; Partnerships">Sales &amp; Partnerships, vendors, affiliates, advertisers, B2B interest</option>
      <option value="Marketing &amp; PR">Marketing &amp; PR, media enquiries, influencers, collaborations, brand requests</option>
      <option value="Product / Technical">Product / Technical, bugs, feature requests, site issues, comparison errors</option>
      <option value="Finance &amp; Admin">Finance &amp; Admin, invoices, payments, billing queries</option>
      <option value="Legal / Compliance">Legal / Compliance, GDPR requests, takedowns, formal complaints</option>
      <option value="General">General, anything else</option>
    </select>
    <small>Your enquiry will be routed to the right team.</small>
  </div>

  <div class="form-group">
    <label for="message">Your message <span class="required">*</span></label>
    <textarea id="message" name="message" class="form-control" required placeholder="Tell us what's on your mind..."></textarea>
  </div>

  <button type="submit" class="btn btn-orange btn-block" id="contactSubmitBtn">
    <span id="contactBtnText">Send message</span>
    <span id="contactBtnSpinner" style="display:none;">&#9679;&#9679;&#9679;</span>
  </button>
  <p style="text-align:center;color:var(--text-muted-dark);font-size:0.85rem;margin-top:16px;">We never share your details with third parties.</p>
</form>'''

CONTACT_FORM_JS = '''
<script>
// ── Contact form ──────────────────────────────────────────────────────────────
// FORMSPREE ENDPOINT: replace xrejbkjz with your dedicated contact form ID
var FS_CONTACT = 'xrejbkjz';

document.getElementById('contactTimestamp').value = new Date().toISOString();

var contactForm = document.getElementById('contactForm');
var contactSubmitBtn = document.getElementById('contactSubmitBtn');
var contactBtnText = document.getElementById('contactBtnText');
var contactBtnSpinner = document.getElementById('contactBtnSpinner');
var contactSuccess = document.getElementById('successMsg');
var contactError = document.getElementById('errorMsg');

if (contactForm) {
  // Update subject line based on department selection
  var deptSelect = document.getElementById('department');
  if (deptSelect) {
    deptSelect.addEventListener('change', function() {
      var subj = document.getElementById('contactSubject');
      if (subj) subj.value = 'Contact: ' + (this.value || 'General') + ' | BarrelCompare';
    });
  }

  contactForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    contactError.style.display = 'none';

    // Validate required fields
    var fields = ['name', 'email', 'department', 'message'];
    var valid = true;
    fields.forEach(function(id) {
      var el = document.getElementById(id);
      if (!el || !el.value.trim()) {
        if (el) el.style.borderColor = 'var(--red-500)';
        valid = false;
      } else {
        if (el) el.style.borderColor = '';
      }
    });
    if (!valid) {
      contactError.textContent = 'Please fill in all required fields.';
      contactError.style.display = 'block';
      return;
    }

    // Honeypot check
    var hp = contactForm.querySelector('input[name="_gotcha"]');
    if (hp && hp.value) return;

    // Loading state
    contactSubmitBtn.disabled = true;
    contactBtnText.style.display = 'none';
    contactBtnSpinner.style.display = 'inline';

    try {
      var res = await fetch('https://formspree.io/f/' + FS_CONTACT, {
        method: 'POST',
        body: new FormData(contactForm),
        headers: { 'Accept': 'application/json' }
      });

      if (res.ok) {
        contactForm.style.display = 'none';
        contactSuccess.style.display = 'block';
        contactSuccess.scrollIntoView({ behavior: 'smooth', block: 'center' });
        // GA4 event
        if (typeof gtag !== 'undefined') {
          gtag('event', 'contact_submit', {
            event_category: 'Forms',
            event_label: document.getElementById('department') ? document.getElementById('department').value : 'unknown'
          });
        }
      } else {
        throw new Error('failed');
      }
    } catch(err) {
      contactError.textContent = 'Something went wrong. Please try again or email hello@barrelcompare.co.uk directly.';
      contactError.style.display = 'block';
      contactSubmitBtn.disabled = false;
      contactBtnText.style.display = 'inline';
      contactBtnSpinner.style.display = 'none';
    }
  });
}
</script>
'''


def fix_contact():
    path = f'{BASE}/contact.html'
    content = read(path)

    # Replace old form element
    old_form_start = ' <form id="contactForm" action="https://formspree.io/f/xrejbkjz" method="POST" novalidate style="margin-top:8px;">'
    old_form_end = ' </form>\n\n </div>\n </div>\n</section>'
    si = content.find(old_form_start)
    ei = content.find(old_form_end, si) + len(old_form_end)
    if si != -1 and ei > si:
        content = content[:si] + CONTACT_FORM_NEW + '\n\n </div>\n </div>\n</section>' + content[ei:]
        print('  replaced contact form HTML')
    else:
        print('  WARNING: contact form HTML not found, trying alternate match')

    # Insert contact form JS just before the search script block
    content = content.replace(
        '\n<script>\nconst SEARCH_INDEX',
        CONTACT_FORM_JS + '\n<script>\nconst SEARCH_INDEX'
    )

    write(path, content)


# ── QUOTE FORM ────────────────────────────────────────────────────────────────

WID_SUPPLIER_CARD = '''         <label class="supplier-select-card" id="card_wid">
           <input type="radio" name="supplier_select" value="wid"
             data-formid="xrejbkjz"
             data-suppliername="West Indies Direct">
           <!-- FORMSPREE: replace xrejbkjz above with West Indies Direct's dedicated endpoint -->
           <div>
             <div class="supplier-label">West Indies Direct</div>
             <div class="supplier-sub">Jamaica, Trinidad, Barbados, Guyana and more &middot; London &amp; Home Counties collection</div>
           </div>
           <span class="verified-badge">Verified</span>
         </label>'''

QUOTE_HIDDEN_FIELDS = '''         <input type="hidden" name="_timestamp" id="quoteTimestamp">
         <input type="hidden" name="_source" id="quoteSource">'''

QUOTE_GA4 = '''        // GA4 event
        if (typeof gtag !== 'undefined') {
          gtag('event', 'quote_submit', {
            event_category: 'Forms',
            event_label: selectedSupplierName,
            destination: document.getElementById('hiddenDestination') ? document.getElementById('hiddenDestination').value : ''
          });
        }
'''


def fix_quote():
    path = f'{BASE}/quote.html'
    content = read(path)

    # Replace placeholder supplier card(s) with West Indies Direct
    old_cards = ''' <label class="supplier-select-card" id="card_supplier1">
 <input type="radio" name="supplier_select" value="supplier1" data-formid="FORM_ID_HERE" data-suppliername="Supplier Name Here">
 <div>
 <div class="supplier-label">Supplier Name Here</div>
 <div class="supplier-sub">Destinations covered · e.g. Jamaica, Trinidad</div>
 </div>
 <span class="verified-badge">Verified</span>
 </label>

 <label class="supplier-select-card" id="card_supplier2">
 <input type="radio" name="supplier_select" value="supplier2" data-formid="FORM_ID_HERE" data-suppliername="Supplier Name Here">
 <div>
 <div class="supplier-label">Supplier Name Here</div>
 <div class="supplier-sub">Destinations covered · e.g. Guyana, Barbados</div>
 </div>
 <span class="verified-badge">Verified</span>
 </label>

 <!-- Add more supplier blocks above this line -->'''
    if old_cards in content:
        content = content.replace(old_cards, WID_SUPPLIER_CARD + '\n         <!-- Add more supplier cards here as suppliers are verified -->')
        print('  replaced supplier cards')
    else:
        print('  WARNING: supplier cards not found with expected whitespace')

    # Add timestamp + source hidden fields just after the honeypot line in the quoteForm
    honeypot_line = ' <input class="hp-field" type="text" name="_gotcha" tabindex="-1" autocomplete="off">'
    if honeypot_line in content:
        content = content.replace(
            honeypot_line,
            honeypot_line + '\n' + QUOTE_HIDDEN_FIELDS
        )
        print('  added timestamp/source hidden fields')

    # Populate timestamp + source on page load — add before step management script
    init_js = "  // ---- Step management ----\n  function showSection(n)"
    if init_js in content:
        content = content.replace(
            init_js,
            "  // Set timestamp and source on load\n  var qts = document.getElementById('quoteTimestamp');\n  if (qts) qts.value = new Date().toISOString();\n  var qsrc = document.getElementById('quoteSource');\n  if (qsrc) qsrc.value = window.location.href;\n\n  " + init_js.lstrip()
        )

    # Add GA4 event after sessionStorage.setItem line in quote success handler
    old_success = "         sessionStorage.setItem(rateKey, 'true');"
    if old_success in content:
        content = content.replace(
            old_success,
            old_success + '\n' + QUOTE_GA4
        )
        print('  added GA4 event to quote form')

    write(path, content)


# ── REVIEW FORM (index.html) ──────────────────────────────────────────────────

REVIEW_HIDDEN = '''          <input type="hidden" name="_subject" value="New community review, BarrelCompare">
          <input type="hidden" name="_timestamp" id="reviewTimestamp">'''

REVIEW_GA4 = '''        // GA4 event
        if (typeof gtag !== 'undefined') {
          gtag('event', 'review_submit', {
            event_category: 'Forms',
            event_label: document.getElementById('reviewSupplier') ? document.getElementById('reviewSupplier').value : '',
          });
        }
'''


def fix_review():
    path = f'{BASE}/index.html'
    content = read(path)

    # Add hidden fields to review form (after _cc field)
    old_cc = '          <input type="hidden" name="_cc" value="hello@barrelcompare.co.uk">'
    if old_cc in content:
        content = content.replace(old_cc, old_cc + '\n' + REVIEW_HIDDEN)
        print('  added review hidden fields')

    # Populate review timestamp on load — add near DOMContentLoaded or after carousel init
    ts_init = "  var rts = document.getElementById('reviewTimestamp'); if (rts) rts.value = new Date().toISOString();\n"
    if 'reviewTimestamp' not in content:
        content = content.replace(
            "window.addEventListener('resize', updateCarousel);",
            "window.addEventListener('resize', updateCarousel);\n" + ts_init
        )

    # Add GA4 event after review success show
    old_review_success = "        document.getElementById('reviewSuccess').style.display = 'block';"
    if old_review_success in content:
        content = content.replace(
            old_review_success,
            old_review_success + '\n' + REVIEW_GA4
        )
        print('  added GA4 event to review form')

    write(path, content)


# ── GATE FORMS (hidden-fees, glossary, country-rules) ────────────────────────

GATE_HTML_NEW = '''
<!-- Content gate overlay -->
<div class="gate-overlay" id="contentGate">
  <div class="gate-box">
    <div style="font-size:2rem;margin-bottom:12px;">&#128274;</div>
    <h2>Get free access</h2>
    <p>Enter your details to unlock this guide. Free forever, no spam, unsubscribe any time.</p>
    <input type="text" class="gate-input" id="gateName" placeholder="Your first name" style="margin-bottom:8px;">
    <input type="email" class="gate-input" id="gateEmail" placeholder="Your email address">
    <div class="gate-error" id="gateError">Please enter a valid email address.</div>
    <button class="btn btn-orange btn-block" id="gateUnlockBtn" onclick="unlockContent()">
      <span id="gateBtnText">Unlock free guide</span>
      <span id="gateBtnSpinner" style="display:none;">&#9679;&#9679;&#9679;</span>
    </button>
    <p class="gate-skip" onclick="skipGate()">I'll browse without unlocking</p>
  </div>
</div>
<style>body.gate-open { overflow: hidden; }</style>
'''

GATE_JS_NEW = '''
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

// FORMSPREE ENDPOINT: replace xrejbkjz with your dedicated downloads/newsletter form ID
var FS_DOWNLOADS = 'xrejbkjz';

function unlockContent() {
  var name = (document.getElementById('gateName') || {}).value || '';
  var email = (document.getElementById('gateEmail') || {}).value.trim();
  var err = document.getElementById('gateError');
  var btn = document.getElementById('gateUnlockBtn');
  var btnText = document.getElementById('gateBtnText');
  var btnSpinner = document.getElementById('gateBtnSpinner');

  if (!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(email)) {
    if (err) err.style.display = 'block';
    return;
  }
  if (err) err.style.display = 'none';

  // Loading state
  if (btn) btn.disabled = true;
  if (btnText) btnText.style.display = 'none';
  if (btnSpinner) btnSpinner.style.display = 'inline';

  localStorage.setItem('bc_gate_unlocked', '1');

  // Submit to Formspree
  fetch('https://formspree.io/f/' + FS_DOWNLOADS, {
    method: 'POST',
    body: JSON.stringify({
      name: name,
      email: email,
      _subject: 'Guide unlock | ' + document.title + ' | BarrelCompare',
      source: window.location.pathname,
      _timestamp: new Date().toISOString()
    }),
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }
  }).catch(function() {}).finally(function() {
    var g = document.getElementById('contentGate');
    if (g) g.style.display = 'none';
    document.body.classList.remove('gate-open');
    // GA4 event
    if (typeof gtag !== 'undefined') {
      gtag('event', 'download_unlock', {
        event_category: 'Forms',
        event_label: window.location.pathname
      });
    }
  });
}

function skipGate() {
  var g = document.getElementById('contentGate');
  if (g) g.style.display = 'none';
  document.body.classList.remove('gate-open');
}
</script>
'''


def fix_gates():
    for page in ['hidden-fees/index.html', 'glossary/index.html', 'country-rules/index.html']:
        path = f'{BASE}/{page}'
        content = read(path)

        # Replace old gate HTML (from previous session - single email field version)
        old_gate_start = '\n<!-- Content gate overlay -->\n<div class="gate-overlay" id="contentGate">'
        old_gate_end = '<style>body.gate-open { overflow: hidden; }</style>\n'
        si = content.find(old_gate_start)
        ei = content.find(old_gate_end, si) + len(old_gate_end) if si != -1 else -1

        if si != -1 and ei > si:
            content = content[:si] + GATE_HTML_NEW + '\n' + content[ei:]
            print(f'  replaced gate HTML in {page}')
        else:
            print(f'  WARNING: gate HTML not found in {page}')

        # Replace old gate JS
        old_js_start = '\n<script>\n(function() {\n  var key = \'bc_gate_unlocked\';'
        old_js_end = '</script>\n'
        si2 = content.find(old_js_start)
        if si2 != -1:
            ei2 = content.find(old_js_end, si2) + len(old_js_end)
            content = content[:si2] + '\n' + GATE_JS_NEW + '\n' + content[ei2:]
            print(f'  replaced gate JS in {page}')
        else:
            # Just append before </body>
            content = content.replace('</body>\n</html>', GATE_JS_NEW + '\n</body>\n</html>')
            print(f'  appended gate JS in {page}')

        write(path, content)


# ── GA4 SPINNER CSS (add to all form pages) ───────────────────────────────────

SPINNER_CSS = """
/* ---- FORM LOADING STATES ---- */
.btn[disabled] { opacity: 0.7; cursor: not-allowed; transform: none; }
#contactBtnSpinner, #gateBtnSpinner { letter-spacing: 4px; animation: dotpulse 1s infinite; }
@keyframes dotpulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
"""


def add_spinner_css(path):
    content = read(path)
    if 'dotpulse' not in content:
        content = content.replace('\n</style>\n</head>', f'\n{SPINNER_CSS}\n</style>\n</head>')
        write(path, content)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print('\n=== Contact form ===')
    fix_contact()

    print('\n=== Quote form ===')
    fix_quote()

    print('\n=== Review form ===')
    fix_review()

    print('\n=== Gate forms ===')
    fix_gates()

    print('\n=== Spinner CSS ===')
    for p in ['contact.html', 'quote.html', 'index.html',
              'hidden-fees/index.html', 'glossary/index.html', 'country-rules/index.html']:
        add_spinner_css(f'{BASE}/{p}')

    print('\n=== Syncing subdirectory copies ===')
    for src, dst in [('contact.html', 'contact/index.html'), ('quote.html', 'quote/index.html')]:
        shutil.copy(f'{BASE}/{src}', f'{BASE}/{dst}')
        print(f'  copied {src} -> {dst}')

    print('\nDone.')
