#!/usr/bin/env python3
"""Apply Kevin's final launch review on the isolated preview branch.
No production deployment, form submission or main-branch write is performed.
"""
from pathlib import Path
import re, json, os, shutil
from bs4 import BeautifulSoup, NavigableString

ROOT=Path(__file__).resolve().parents[1]
if os.environ.get('GITHUB_REF') not in (None,'refs/heads/workfriends-conversion-preview-20261019'):
    raise SystemExit('Wrong branch for launch preparation')
PRIMARY='Discuss a revenue opportunity'
SECONDARY='How Revenue Builds work'
CREDENTIAL='19 years in digital media, creator marketing and commercial partnerships, with experience at Fullscreen, Tastemade, Influential and Travelzoo.'
ORG='Workfriends builds strategic partnerships and revenue channels for brands, agencies, platforms and IP owners through scoped, paid Revenue Builds.'
PARTNERS={
 'Astra Media':'Social audience development', 'Ampley':'Owned short-form networks',
 'Dubble':'Content amplification', 'Outlandish':'TikTok Shop operations',
 'Get Live':'Creator-commerce operations', 'Social Commerce Fest':'Creator-commerce events',
 'Dimension Studios':'Commerce production', 'Threecolts':'Commerce operations technology',
 'Ticket Rewards':'Ticketing and audience activation', 'Iconically':'Creator and talent commerce',
 'Cruva':'Affiliate technology', 'The Bower Collective':'Live-experience strategy',
 'Trenz.ai':'Social-commerce market intelligence'
}
DROP=[
 r'No new audience or revenue result is guaranteed\.',
 r'This is not a fixed number of introductions or a promise of guaranteed revenue\.',
 r'Revenue outcomes depend on the offer, buyer decisions and delivery as well as commercial execution\.\s*Milestones and responsibilities are agreed up front\.',
 r'Relevant partner compensation is disclosed\.',
 r'No specific (?:revenue|audience|commercial) (?:result|outcome)s? (?:is|are) guaranteed\.',
 r'No (?:guaranteed revenue|revenue guarantee)[^.]*\.',
]

def tidy_text(s):
    for pattern in DROP:s=re.sub(pattern,'',s,flags=re.I)
    s=re.sub(r'All upside\.\s*No overhead\.?','',s,flags=re.I)
    s=re.sub(r'Commercial Sprints?',lambda m:'Revenue Builds' if m[0].lower().endswith('s') else 'Revenue Build',s,flags=re.I)
    s=s.replace('project or sprint fees','Revenue Build fees').replace('sprint fees','Revenue Build fees')
    for name,label in PARTNERS.items():s=s.replace(name,label)
    return s

def fragment(s):return BeautifulSoup(s,'html.parser')
def replace_inner(tag,markup):
    tag.clear()
    for child in list(fragment(markup).contents):tag.append(child)

def schema_walk(x):
    if isinstance(x,str):
        if '$1.4' in x or '100M+' in x or '100 million followers' in x:return ORG
        return tidy_text(x)
    if isinstance(x,list):return [schema_walk(v) for v in x]
    if isinstance(x,dict):
        x={k:schema_walk(v) for k,v in x.items()}
        if x.get('@type')=='Organization' and x.get('name')=='Workfriends':x['description']=ORG
        return x
    return x

# The old standalone authoring/review document is not a production destination.
for name in ['review','preview-checks']:
    if (ROOT/name).exists():shutil.rmtree(ROOT/name)
for name in ['workfriends-universe.html','assets/wf-preview.js']:
    (ROOT/name).unlink(missing_ok=True)

changed=[]
for p in sorted(ROOT.rglob('*.html')):
    if any(x in p.parts for x in ('.git','node_modules','.venv')):continue
    original=p.read_text();soup=BeautifulSoup(original,'html.parser')
    rel=str(p.relative_to(ROOT))
    if soup.body is None:continue
    for s in list(soup.select('script[src*="wf-preview.js"], .wf-review-badge')):s.decompose()
    # Maintain platform breadth consistently; this does not claim a platform affiliation.
    for a in soup.select('.nav-dropdown-panel a[href="/creator-commerce/"] span'):
        a.string='TikTok Shop, Amazon and live shopping.'
    if rel=='creator-commerce/index.html':
        lead=soup.select_one('.page-heading .lead')
        assert lead is not None
        lead.string='Workfriends helps brands and agencies build creator-led commerce across TikTok Shop, Amazon and live shopping. We assess the opportunity, define the operating model and assemble the people to deliver it.'
        for p2 in soup.find_all('p'):
            if p2.decomposed:continue
            if 'Founder-led partner Outlandish' in p2.get_text():
                p2.string='Connect shop operations, affiliate creators, content, live production, technology and creator relationships around the brand and its commercial goals.'
    if rel=='audience-development/index.html':
        lead=soup.select_one('.page-heading .lead')
        lead.string='Workfriends helps brands, talent and media businesses turn content and attention into an audience business. We assemble the right capabilities across channel strategy, social operations, owned distribution, amplification and monetization.'
        for grid in soup.select('.participation-grid'):
            if 'Astra Media' in grid.get_text() or 'Ampley' in grid.get_text():
                replace_inner(grid,'<article class="participation-anchor"><div><div class="partner-kicker">/ End-to-end audience development</div><h3>Build and operate the channels.</h3></div><div><p class="partner-role">Strategy, operations and monetization</p><p>Programming, channel operations, audience growth and monetization across YouTube, TikTok and Meta.</p></div></article><article><div class="partner-kicker">/ Owned distribution</div><h3>Build media assets.</h3><p class="partner-role">Owned short-form networks</p><p>Create and operate channels around content, talent and IP, with ownership and a long-term commercial plan.</p></article><article><div class="partner-kicker">/ Amplification</div><h3>Expand the reach.</h3><p class="partner-role">Content distribution campaigns</p><p>Take strong content into additional relevant channels and communities, with a defined audience and campaign objective.</p></article>')
    # Remove unsupported scale and acquisition claims, retaining actual career context.
    for tag in list(soup.find_all(['p','h2','h3','span','div'])):
        if tag.decomposed:continue
        text=tag.get_text(' ',strip=True)
        if tag.name=='p' and ('100M+' in text or '100 million followers' in text):
            tag.string='Owned and operated short-form channels that build distribution around content, talent and IP.'
        elif tag.name=='p' and ('$1.4' in text or 'acquisitions' in text.lower()):
            tag.string=CREDENTIAL
        elif not tag.find(['p','h1','h2','h3','div']) and ('$1.4' in text or '100M+' in text):
            tag.string='Senior commercial experience' if '$1.4' in text else 'Owned distribution'
        elif tag.name=='p' and 'Founder-led operating partners include' in text:
            tag.string='Workfriends assembles specialist operators across creator commerce, audience development, media, technology and live experiences.'
        elif tag.name=='p' and ('Known Workfriends ecosystem relationships include' in text or 'These are not all identical or exclusive' in text):
            tag.decompose()
    # Structured data is transformed as JSON, not regex-ed markup.
    for script in soup.select('script[type="application/ld+json"]'):
        doc=schema_walk(json.loads(script.string or script.get_text()))
        script.string=json.dumps(doc,ensure_ascii=False,separators=(',',':'))
    for text in list(soup.find_all(string=True)):
        if not text.parent or text.parent.name in ('script','style'):continue
        new=tidy_text(str(text))
        if new!=str(text):text.replace_with(NavigableString(new))
    # Remove empty footnotes; privacy and submitted-data explanations remain.
    for tag in list(soup.select('p.wf-note, p.hero-note, p.participation-note')):
        if tag.decomposed:continue
        txt=tag.get_text(' ',strip=True)
        if not txt:tag.decompose()
        elif re.search(r'not (?:a |the )?(?:guarantee|promise)|guaranteed revenue|revenue (?:is |results are )not guaranteed',txt,re.I):
            if 'illustrative' not in txt.lower():tag.decompose()
    for a in list(soup.find_all('a',href=True)):
        href=a['href'];label=a.get_text(' ',strip=True)
        if href.startswith('/review'):
            a.decompose();continue
        if href.startswith('/contact/') or href.startswith('https://www.getworkfriends.co/contact/'):
            a.string=PRIMARY+('' if 'nav-cta' in a.get('class',[]) else ' →')
            if a.has_attr('aria-label'):a['aria-label']=PRIMARY
        elif '/revenue-channels/#engagements' in href or (href=='#engagements' and rel=='revenue-channels/index.html'):
            a.string=SECONDARY+' →'
        # Named providers are introduced in a qualified conversation, not a public roster.
        if any(d in href.lower() for d in ('ampley','dubble','outlandish','astra-media','astramedia','getlive','iconically','threecolts','socialcommercefest','trenz.ai')):
            a.unwrap()
    for btn in soup.select('form button[type="submit"]'):
        btn.string=PRIMARY+' →'
    for tag in soup.select('.footer-tagline'):tag.string='People outlast companies.'
    for badge in soup.select('.founder-led-badge'):badge.decompose()
    # Keep the required sample label, without an extra legalistic headline.
    for text in list(soup.find_all(string=True)):
        if text.parent and text.parent.name not in ('script','style'):
            t=str(text)
            if 'Illustrative build. Not a client case study' in t:
                text.replace_with(t.replace('Illustrative build. Not a client case study','Illustrative build'))
    if rel=='index.html':
        hero=soup.select_one('section.focused-home-hero')
        assert hero is not None,'Homepage hero source changed'
        newhero=fragment('<section class="wf-launch-hero" aria-labelledby="home-title"><div class="wrap"><div class="eyebrow">Workfriends / A Revenue Network</div><h1 id="home-title">Build your next<br>revenue channel.</h1><p class="wf-launch-audience">For brands, agencies, platforms and IP owners.</p><p class="wf-launch-copy">Win new brand business. Build complementary partnerships. Turn content, audiences and capabilities into new revenue. Workfriends leads the commercial work and brings the right people around it.</p><div class="wf-launch-actions"><a class="primary" href="/contact/?topic=Revenue+opportunity#inquiry-form" data-contact-topic="Revenue opportunity">Discuss a revenue opportunity →</a><a class="text-link" href="/revenue-channels/#engagements">How Revenue Builds work →</a></div><p class="wf-launch-fee">Free 20-minute fit call. Defined scope. Paid execution.</p></div></section>').section
        hero.replace_with(newhero)
        # The Universe remains on its dedicated page. Do not ship a hidden tag catalogue on Home.
        for tag in list(soup.select('#scene-concepts, #path-data, .universe-words, #scene-panel, .universe-legend, .scene-bottom, .encounter, .universe-tools')):tag.decompose()
        for script in list(soup.find_all('script')):
            if script.get('type')=='application/ld+json' or script.get('src'):continue
            code=script.string or script.get_text()
            if any(token in code for token in ("getElementById('scene-panel')","getElementById('network')","getElementById('scene-concepts')","from '/assets/three",'from "/assets/three')):
                script.decompose()
        main=soup.select_one('main')
        assert main is not None
        paths=soup.select_one('#what-we-do');assert paths is not None
        paths.extract();main.insert(0,paths)
        # Keep branding within existing colors; no Universe chrome above the offer.
        for mast in soup.select('header.masthead'):
            for attr in ('data-theme','data-universe-surface'):mast.attrs.pop(attr,None)
        founder=soup.select_one('.short-founder')
        if founder:
            credit=founder.select_one('.founder-credit')
            if credit:replace_inner(credit,'<strong>19 years</strong> in digital media, creator marketing and commercial partnerships.<br>Experience at Fullscreen, Tastemade, Influential and Travelzoo.<br><a href="https://www.linkedin.com/in/kpmcclain" target="_blank" rel="noopener noreferrer">Kevin McClain on LinkedIn ↗</a>')
        # Align entity and search preview with the actual hero and offer.
        soup.title.string='Workfriends | Build Your Next Revenue Channel'
        for meta in soup.select('meta[name="description"], meta[property="og:description"]'):meta['content']=ORG
        for meta in soup.select('meta[property="og:title"]'):meta['content']='Workfriends | Build Your Next Revenue Channel'
        for script in soup.select('script[type="application/ld+json"]'):
            doc=json.loads(script.string)
            for node in doc.get('@graph',[]):
                if node.get('@type')=='WebPage':node.update(name=soup.title.string,description=ORG)
            script.string=json.dumps(doc,ensure_ascii=False,separators=(',',':'))
    # A single compact launch stylesheet also protects the long shared CTA at tablet widths.
    if not soup.select_one('link[href="/assets/wf-launch.css"]'):
        link=soup.new_tag('link',rel='stylesheet',href='/assets/wf-launch.css');soup.head.append(link)
    # Refresh FAQ text from the visible corresponding answer after the editorial edits.
    headings=soup.find_all(['h3','summary'])
    def visible_answer(q):
        for h in headings:
            if h.get_text(' ',strip=True)==q:
                para=h.find_next_sibling('p')
                if para:return para.get_text(' ',strip=True)
        return None
    for script in soup.select('script[type="application/ld+json"]'):
        doc=json.loads(script.string)
        for node in doc.get('@graph',[]):
            if node.get('@type')=='FAQPage':
                for q in node.get('mainEntity',[]):
                    ans=visible_answer(q.get('name',''))
                    if ans:q['acceptedAnswer']['text']=ans
        script.string=json.dumps(doc,ensure_ascii=False,separators=(',',':'))
    if rel=='index.html':
        # Homepage Universe's original inline controller also owned the mobile menu.
        # Restore the standalone progressive navigation after removing the Universe.
        mobile_menu = '''document.documentElement.classList.add('js');
(()=>{const nav=document.getElementById('main-nav'),toggle=document.querySelector('.nav-toggle');
if(!nav||!toggle)return;const dropdown=nav.querySelector('details');toggle.hidden=false;
const close=()=>{nav.classList.remove('is-open');toggle.setAttribute('aria-expanded','false');if(dropdown)dropdown.open=false;};
toggle.addEventListener('click',()=>{const open=!nav.classList.contains('is-open');nav.classList.toggle('is-open',open);toggle.setAttribute('aria-expanded',String(open));if(!open&&dropdown)dropdown.open=false;});
document.addEventListener('click',e=>{if(!nav.contains(e.target)&&!toggle.contains(e.target))close();});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&(dropdown?.open||nav.classList.contains('is-open'))){const target=matchMedia('(max-width:900px)').matches?toggle:dropdown.querySelector('summary');close();target?.focus();}});
nav.addEventListener('click',e=>{if(e.target.closest('a'))close();});
nav.addEventListener('focusout',()=>{setTimeout(()=>{if(!nav.contains(document.activeElement)&&document.activeElement!==toggle)close();},0);});
matchMedia('(max-width:900px)').addEventListener('change',close);})();'''
        script=soup.new_tag('script')
        script.string=mobile_menu
        soup.body.append(script)
    out=str(soup)
    p.write_text(out)
    if out!=original:changed.append(rel)

(ROOT/'assets/wf-launch.css').write_text('''/* Approved offer-first launch. Universe stays on /universe/. */
.wf-launch-hero{background:var(--paper);color:var(--ink);padding:64px 0 52px;border-bottom:1px solid var(--line)}
.wf-launch-hero h1{font-size:clamp(52px,6.8vw,98px);line-height:1.02;letter-spacing:-.045em;max-width:1150px;margin:22px 0 24px}
.wf-launch-audience{font-size:19px;line-height:1.5;font-weight:650;color:var(--green);margin:0 0 14px}
.wf-launch-copy{font-size:19px;line-height:1.6;max-width:770px;color:var(--muted);margin:0 0 26px}
.wf-launch-actions{display:flex;gap:24px;align-items:center;flex-wrap:wrap}.wf-launch-actions .text-link{font-size:13px}
.wf-launch-fee{font-size:12px;line-height:1.6;color:var(--muted);margin:20px 0 0}
.home-focus #what-we-do{border-top:0;padding-top:42px}.home-focus .founder-credit{line-height:1.8}
.path-nav{gap:20px}.path-nav .nav-cta{font-size:11px;white-space:normal;text-align:center;line-height:1.4;max-width:220px}
.footer-nav a{max-width:250px;line-height:1.5}
@media(max-width:900px){.path-nav .nav-cta{max-width:none;font-size:14px}}
@media(max-width:600px){.wf-launch-hero{padding:35px 0 34px}.wf-launch-hero h1{font-size:clamp(39px,10.2vw,60px);line-height:1.04;margin:20px 0}.wf-launch-audience{font-size:15px}.wf-launch-copy{font-size:16px;line-height:1.65}.wf-launch-actions{align-items:flex-start;flex-direction:column;gap:19px}.wf-launch-actions .primary{font-size:12px}.wf-launch-fee{font-size:11px}.home-focus #what-we-do{padding-top:30px}}
''')
# Public AI summary uses the same capability-led policy; no unapproved operator roster.
p=ROOT/'llms.txt';text=p.read_text()
text=re.sub(r'## Partner ecosystem\n.*?(?=\n## |\Z)','## Partner ecosystem\nWorkfriends assembles specialist capabilities in creator commerce, media, audience development, technology and live experiences. Specific operators are selected around the assignment and introduced during qualified commercial conversations.\n',text,flags=re.S)
text=tidy_text(text)
text=re.sub(r'[^\n]*(?:\$1\.4|100M\+)[^\n]*',CREDENTIAL,text)
p.write_text(text)
# Preserve current route behavior and add only an internal-file deployment exclusion.
p=ROOT/'.vercelignore'
p.write_text('review/\npreview-checks/\ntools/\ntests/\n.github/\nREADME.md\nworkfriends-universe.html\n')
# Remove preview machinery from the release tree; these files remain in git history.
for name in ['.github/workflows/conversion-preview.yml','tools/build_conversion_preview.py','tools/conversion_preview_content.json']:
    (ROOT/name).unlink(missing_ok=True)
# Existing tests adapt to the expressly approved headline and public naming policy.
p=ROOT/'tests/validate_public_content.py';test=p.read_text()
test=test.replace('self.assertIn("The right partnerships", home)','self.assertIn("Build your next", home)').replace('self.assertIn("build bigger businesses.", home)','self.assertIn("revenue channel.", home)')
test=test.replace('"Illustrative build. Not a client case study"','"Illustrative build"')
start=test.index('    def test_partner_references_preserve_approved_operating_partners(self):')
end=test.index('    def test_universe_reference_matches_the_simplified_page(self):',start)
test=test[:start]+'''    def test_partner_names_require_public_approval(self):
        for path in ROOT.rglob("*.html"):
            page = Page(path.relative_to(ROOT))
            for name in ("Outlandish", "Astra Media", "Ampley", "Dubble", "Get Live", "Social Commerce Fest"):
                self.assertNotIn(name, page.visible)
            self.assertNotIn("100M+", page.visible)
            self.assertNotIn("$1.4B", page.visible)
            self.assertNotIn("All upside. No overhead", page.visible)
        self.assertIn("Owned short-form networks", Page("audience-development/index.html").visible)
        self.assertNotIn("Astra Media", (ROOT / "llms.txt").read_text())

'''+test[end:]
p.write_text(test)
# The browser suite is a production-source check now, not a preview-hub check.
p=ROOT/'tests/site_preview_browser.py';test=p.read_text().replace(",'/review/'",'').replace("if path!='/review/' and width==390:","if width==390:")
p.write_text(test)
# Current docs only; no preview change log is deployed.
p=ROOT/'README.md';text=p.read_text();text=text.split('## Conversion preview, 2026-10-19')[0]
text=tidy_text(text)
text+='\n\n## Public launch policy\nThe homepage is offer-first; the Universe is a separate destination. Primary CTA: Discuss a revenue opportunity. Secondary CTA: How Revenue Builds work. Public pages show operating capabilities, not a named partner roster. Named partners and partner metrics require explicit publication approval. Career credibility uses 19 years and actual employers, not an acquisition-dollar aggregate. Review content and preview generators are excluded from production.\n'
p.write_text(text)
# Canonical sitemap dates reflect this content release, never private paths.
p=ROOT/'sitemap.xml';xml=p.read_text();xml=re.sub(r'<lastmod>[^<]+</lastmod>','<lastmod>2026-10-20</lastmod>',xml);p.write_text(xml)
print('LAUNCH_FILES',json.dumps(changed))
print('LAUNCH_COMPLETE: main untouched; source ready for automated checks and review.')
