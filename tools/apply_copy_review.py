#!/usr/bin/env python3
"""Apply the October 20 copy request. No production or domain writes."""
from pathlib import Path
import re, json, html, subprocess, shutil, os
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
BRANCH='workfriends-copy-review-20261020'
assert os.environ.get('GITHUB_REF') in (None, 'refs/heads/'+BRANCH)
ORIGIN='cef24e9e6f5f4a231c4b2947b2039dcc25bee63b'
CONVERSION='04bb460f2deed0863f200e32d342434c172b504f'
PRIMARY='Discuss a revenue opportunity'
COMMERCE='TikTok Shop, Amazon and live shopping.'
LABEL='Illustrative build. Not a client case study or a claim of completed results.'
HEADLINE='Senior commercial leadership, without the hire.'
PARAS=[
"Not an employee. No recruiting, no ramp-up, no permanent headcount. You get a senior operator and an existing network on day one.",
"Not an agency. We have no delivery team to keep busy. We bring in the specialists your objective needs and lead the commercial work around them.",
"Not a consultant. We don't hand over a deck and leave. We stay in the work, and where it makes sense, part of our upside rides on the revenue it produces."]
CARDS=[
'Win new brand business, or build the partner channel that sources it. We map the accounts, open the doors and move deals toward contract.',
'Launch or fix TikTok Shop, Amazon and live shopping. We size the opportunity, select the right operator and stand up the program.',
'Turn content, talent and IP into owned audiences and new revenue. We assemble the channel operators and build the monetization around them.']
BUILD='A Revenue Build starts with a fixed fee, one growth objective, a named team and milestones you can hold us to. Some are short sprints to open a market or close a first deal. Others become long-term partnerships that keep the channel producing. It might deliver a qualified pipeline of target brand accounts, a TikTok Shop operator selected and launched, or a sponsorship program taken to market.'
REMOVE=[
'No new audience or revenue result is guaranteed.',
'The final scope, team, timeline and scorecard follow the opportunity.',
'This is not a fixed number of introductions or a promise of guaranteed revenue.',
'Revenue outcomes depend on the offer, buyer decisions and delivery as well as commercial execution. Milestones and responsibilities are agreed up front.']
DASH=re.compile(r'[ \t]*(?:\u2014|&mdash;|&#0*8212;|&#x0*2014;|\\u2014)[ \t]*',re.I)

def norm(s):return re.sub(r'\s+',' ',s).strip()
def soup(s):return BeautifulSoup(s,'html.parser')
def section(raw,id):
    pattern=r'<section\b[^>]*\bid="'+re.escape(id)+r'"[^>]*>.*?</section>'
    matches=list(re.finditer(pattern,raw,re.S))
    assert len(matches)==1,('Unique section required',id,len(matches))
    return matches[0].group()
def apply_section(raw,id,edit):
    old=section(raw,id);doc=soup(old);edit(doc.section)
    return raw.replace(old,str(doc.section),1)
def markup_text(value):return html.escape(value,quote=False)

pages={str(p.relative_to(ROOT)):p.read_text() for p in ROOT.rglob('*.html') if '.git' not in p.parts}
page_set=set(pages)
base_home=soup(pages['index.html'])
fee_before=str(base_home.select_one('#revenue-builds .wf-note'))
headings_before=[h.get_text(' ',strip=True) for h in base_home.select('#what-we-do article h2')]
links_before=[str(a) for a in base_home.select('#what-we-do article a')]
network_link_before=str(base_home.select_one('#revenue-network a[href="/network/"]'))
# Restore exactly the conversion-page source, then apply the requested shared consistency edits.
conversion=subprocess.check_output(['git','show',CONVERSION+':revenue-channels/index.html'],cwd=ROOT,text=True)
assert 'Build partnerships that produce revenue.' in conversion
assert 'We need to win more brand business.' in conversion
(ROOT/'revenue-channels/index.html').write_text(conversion)

p=ROOT/'index.html';raw=p.read_text()
def cards(block):
    articles=block.select('.buyer-paths article');assert len(articles)==3
    for article,copy in zip(articles,CARDS):article.find('p').string=copy
raw=apply_section(raw,'what-we-do',cards)
def differentiation(block):
    wrap=block.select_one('.wrap');wrap.h2.string=HEADLINE
    for para in list(wrap.find_all('p',recursive=False)):para.decompose()
    link=wrap.find('a',href='/network/');assert link
    for copy in PARAS:
        para=soup('<p></p>').p;para.string=copy;link.insert_before(para)
raw=apply_section(raw,'revenue-network',differentiation)
new_section=section(raw,'revenue-network')
raw=raw.replace(new_section,'',1)
path_section=section(raw,'what-we-do')
raw=raw.replace(path_section,path_section+'\n'+new_section,1)
def build(block):
    first=block.select_one('.wrap').find('p',recursive=False);assert first
    first.string=BUILD
raw=apply_section(raw,'revenue-builds',build)
p.write_text(raw)

changes=[]
for p in sorted(ROOT.rglob('*.html')):
    if '.git' in p.parts:continue
    rel=str(p.relative_to(ROOT));raw=p.read_text()
    if rel.startswith('review/'):
        p.unlink();continue
    # Leave all styles and functional code intact except requested punctuation in text literals.
    for sentence in REMOVE:
        raw=raw.replace(sentence,'').replace(html.escape(sentence,quote=False),'')
    raw=re.sub(r'All\s+upside\.\s*No\s+overhead\.?','',raw,flags=re.I)
    raw=re.sub(r'Commercial Sprints?',lambda m:'Revenue Builds' if m[0].lower().endswith('s') else 'Revenue Build',raw,flags=re.I)
    raw=raw.replace('nearly two decades','19 years').replace('over two decades of experience','19 years of experience').replace('two decades of experience','19 years of experience')
    raw=re.sub(r'\b(?:18|20|21)\+? years(?= (?:of experience|in digital media|in media|in advertising|in creator marketing))','19 years',raw)
    raw=DASH.sub(', ',raw)
    raw=re.sub(r'<p\b[^>]*>\s*</p>','',raw)
    def nav_edit(match):
        doc=soup(match[0]);nav=doc.nav
        for a in nav.find_all('a',href=True):
            path=a['href'].split('?')[0].split('#')[0]
            if path.rstrip('/')=='/revenue-channels':
                title=a.find('strong') or a.find('span')
                if title:title.string='Partnerships & Channels'
                elif norm(a.get_text()) in ('Revenue Channels','Partnerships & Channels'):a.string='Partnerships & Channels'
            if path.rstrip('/')=='/creator-commerce':
                if a.find('strong') and a.find('span'):a.find('span').string=COMMERCE
            if 'nav-cta' in a.get('class',[]):
                a.string=PRIMARY
                if a.has_attr('aria-label'):a['aria-label']=PRIMARY
        return str(nav)
    raw=re.sub(r'<nav\b[^>]*>.*?</nav>',nav_edit,raw,flags=re.S)
    raw=re.sub(r'(<div\b[^>]*class="footer-tagline"[^>]*>).*?(</div>)',r'\g<1>People outlast companies.\2',raw,flags=re.S)
    if rel=='creator-commerce/index.html':
        # Only change the hero description, not the heading, layout or service scope.
        doc=soup(raw);lead=doc.select_one('.page-heading .lead');assert lead
        old=str(lead);lead.string=COMMERCE
        assert old in raw
        raw=raw.replace(old,str(lead),1)
    if rel=='agency-channel-build/index.html':
        def label_edit(block):
            para=block.select_one('.wrap').find('p',recursive=False);assert para
            para.string=LABEL
        raw=apply_section(raw,'example',label_edit)
    p.write_text(raw)
    if raw!=pages.get(rel):changes.append(rel)
# Text references and authored scripts use the same terminology and punctuation.
for p in list(ROOT.glob('*.txt'))+list((ROOT/'assets').glob('wf*.js')):
    raw=p.read_text();new=DASH.sub(', ',raw)
    new=re.sub(r'Commercial Sprints?',lambda m:'Revenue Builds' if m[0].lower().endswith('s') else 'Revenue Build',new,flags=re.I)
    new=re.sub(r'All\s+upside\.\s*No\s+overhead\.?','',new,flags=re.I)
    for sentence in REMOVE:new=new.replace(sentence,'')
    if new!=raw:p.write_text(new);changes.append(str(p.relative_to(ROOT)))
if (ROOT/'review').exists():shutil.rmtree(ROOT/'review')
# No review page or temporary tooling may be deployed, including after approval.
p=ROOT/'.vercelignore';ignore=p.read_text() if p.exists() else ''
for item in ('review/','tools/','.github/','tests/','preview-checks/'):
    if item not in ignore.splitlines():ignore+=item+'\n'
p.write_text(ignore)
# Update lastmod only for genuinely changed, existing public pages.
p=ROOT/'sitemap.xml';xml=p.read_text()
for rel in changes:
    if not rel.endswith('.html'):continue
    route='/' if rel=='index.html' else '/'+rel.removesuffix('index.html')
    url='https://www.getworkfriends.co'+route
    xml=re.sub(r'(<loc>'+re.escape(url)+r'</loc><lastmod>)[^<]+(</lastmod>)',r'\g<1>2026-10-20\2',xml)
p.write_text(xml)

# Exact-copy acceptance. Existing design and behavior are separate regression checks.
home=soup((ROOT/'index.html').read_text())
assert home.select_one('#revenue-network h2').get_text()==HEADLINE
assert [p.get_text() for p in home.select('#revenue-network .wrap > p')]==PARAS
assert [p.get_text() for p in home.select('#what-we-do article p')]==CARDS
assert [h.get_text(' ',strip=True) for h in home.select('#what-we-do article h2')]==headings_before
assert [str(a) for a in home.select('#what-we-do article a')]==links_before
assert str(home.select_one('#revenue-network a[href="/network/"]'))==network_link_before
assert home.select_one('#revenue-builds .wrap > p').get_text()==BUILD
assert str(home.select_one('#revenue-builds .wf-note'))==fee_before
assert home.select_one('#what-we-do').find_next_sibling('section').get('id')=='revenue-network'
assert home.select_one('#revenue-network').find_next_sibling('section').get('id')=='revenue-builds'
assert soup((ROOT/'agency-channel-build/index.html').read_text()).select_one('#example .wrap > p').get_text()==LABEL
assert soup((ROOT/'creator-commerce/index.html').read_text()).select_one('.page-heading .lead').get_text()==COMMERCE
assert set(str(p.relative_to(ROOT)) for p in ROOT.rglob('*.html') if '.git' not in p.parts)==page_set-set(x for x in page_set if x.startswith('review/'))
assert not (ROOT/'review/index.html').exists()
assert '/review/' not in (ROOT/'sitemap.xml').read_text()
experience=[]
for rel in sorted(page_set):
    if rel.startswith('review/'):continue
    raw=(ROOT/rel).read_text();doc=soup(raw)
    assert not DASH.search(raw),rel
    assert not re.search(r'Commercial Sprints?|All\s+upside\.\s*No\s+overhead',raw,re.I),rel
    for sentence in REMOVE:assert sentence not in raw,(rel,sentence)
    assert all(n.get_text(' ',strip=True)=='People outlast companies.' for n in doc.select('.footer-tagline')),rel
    for nav in doc.select('header nav'):
        for a in nav.select('a[href="/revenue-channels/"]'):
            assert (a.find('strong') or a.find('span') or a).get_text(strip=True)=='Partnerships & Channels',rel
        assert all(a.get_text(strip=True)==PRIMARY for a in nav.select('.nav-cta')),rel
        assert all(a.select_one('span').get_text()==COMMERCE for a in nav.select('.nav-dropdown-panel a[href="/creator-commerce/"]')),rel
    for s in doc.select('script[type="application/ld+json"]'):json.loads(s.string)
    old=soup(pages[rel])
    assert [str(x) for x in old.select('style,link[rel="stylesheet"]')]==[str(x) for x in doc.select('style,link[rel="stylesheet"]')],('Design changed',rel)
    # Only requested punctuation may change existing functional script content.
    old_scripts=[DASH.sub(', ',str(x)) for x in old.select('script:not([type="application/ld+json"])')]
    new_scripts=[str(x) for x in doc.select('script:not([type="application/ld+json"])')]
    assert old_scripts==new_scripts,('Functional scripts changed',rel)
    for t in doc.select('p'):
        value=t.get_text(' ',strip=True)
        if re.search(r'years|decades',value,re.I) and re.search(r'experience|career|digital media',value,re.I):experience.append([rel,value])
OUT=ROOT/'preview-checks';OUT.mkdir(exist_ok=True)
(OUT/'copy-acceptance.json').write_text(json.dumps({'status':'passed','base':ORIGIN,'conversion_source':CONVERSION,'pages_checked':len(page_set),'changed_files':changes,'exact_copy':True,'fee_line_unchanged':True,'design_unchanged':True,'no_new_pages':True,'production_changed':False,'experience_mentions':experience},indent=2))
print('COPY_ACCEPTANCE_PASSED',json.dumps({'pages':len(page_set),'changed_files':changes,'experience':experience}))
