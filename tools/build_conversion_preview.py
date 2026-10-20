#!/usr/bin/env python3
"""Generate the isolated conversion review. Never deploys or updates production.
Run on the preview branch, from the repository root, after reviewing the payload.
Existing fonts, Universe, operator descriptions and form behavior are retained.
"""
from pathlib import Path
import json, re, html, hashlib, os, zlib, base64
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
if os.environ.get('GITHUB_REF') and os.environ['GITHUB_REF'] != 'refs/heads/workfriends-conversion-preview-20261019':
    raise SystemExit('This generator is restricted to the conversion preview branch.')
data = json.loads((ROOT/'tools/conversion_preview_content.json').read_text())
if 'compressed_payload' in data:
    # Normalize one known transport transcription; checksum must still match exactly.
    encoded = data['compressed_payload'].replace('KVisplJ7VDW', 'KVispl7VDW')
    decoded = zlib.decompress(base64.b64decode(encoded, validate=True))
    assert hashlib.sha256(decoded).hexdigest() == '9801d5e8db79d037007c26a76a132f281ae9630de2ce7073add62bc230f7c347', 'Content checksum mismatch'
    data = json.loads(decoded)
    (ROOT/'tools/conversion_preview_content.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
BASE = 'https://www.getworkfriends.co'
original = {}
for op in data['operations']:
    original.setdefault(op['path'], (ROOT/op['path']).read_text())
page_source = (ROOT/data['newpage']['source']).read_text()
for op in data['operations']:
    p=ROOT/op['path']; text=p.read_text()
    if op['after'] in text: continue
    if text.count(op['before']) != op.get('count', 1):
        raise SystemExit('Source changed or target is not unique: '+op['label'])
    p.write_text(text.replace(op['before'], op['after'], op.get('count', 1)))
for path,content in data['newfiles'].items():
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)

def element(text, opening):
    start=text.index(opening); tag=re.match(r'<([a-z]+)', opening)[1]; depth=0
    for match in re.finditer(r'</?'+tag+r'\b[^>]*>',text[start:]):
        depth += -1 if match[0].startswith('</') else 1
        if depth==0: return text[start:start+match.end()]
    raise ValueError('Unclosed '+opening)

def metadata(text,title,description,url,service=None):
    head,body=text.split('</head>',1)
    head=re.sub(r'<title>.*?</title>','<title>'+html.escape(title)+'</title>',head,count=1,flags=re.S)
    for kind,name,value in [('name','description',description),('property','og:title',title),('property','og:description',description),('property','og:url',url)]:
        pattern=r'<meta '+kind+'="'+re.escape(name)+r'" content="[^"]*">'
        head=re.sub(pattern,'<meta '+kind+'="'+name+'" content="'+html.escape(value,quote=True)+'">',head,count=1)
    head=re.sub(r'<link rel="canonical" href="[^"]*">','<link rel="canonical" href="'+url+'">',head,count=1)
    def schema(match):
        doc=json.loads(match[1])
        for node in doc.get('@graph',[]):
            typ=node.get('@type')
            if typ=='WebPage':
                node.update({'@id':url+'#page','url':url,'name':title,'description':description})
                if service:node['mainEntity']={'@id':url+'#service'}
            elif typ=='Service' and service:
                node.update({'@id':url+'#service','url':url,'name':service,'description':description,'serviceType':'Agency channel development and commercial activation'})
        return '<script type="application/ld+json">'+json.dumps(doc,ensure_ascii=False,separators=(',',':'))+'</script>'
    head=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,head,flags=re.S)
    return head+'</head>'+body

spec=data['newpage']
visual=element(page_source,'<div class="rc-visual rc-hero-network"')
oldmain=re.search(r'<main\b.*?</main>',page_source,re.S)[0]
animations=''.join(re.findall(r'<script>.*?</script>',oldmain,re.S))
main=spec['main'].replace('__EXISTING_HERO_VISUAL__',visual).replace('</main>',animations+'</main>')
newpage=page_source.replace(oldmain,main,1)
newpage=metadata(newpage,spec['title'],spec['description'],BASE+'/agency-channel-build/',spec['service'])
p=ROOT/spec['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_text(newpage)
p=ROOT/'revenue-channels/index.html';text=p.read_text()
text=text.replace('href="/contact/?topic=Build+a+Revenue+Channel#inquiry-form" data-contact-topic="Build a Revenue Channel">Build a revenue channel →','href="/contact/?topic=Revenue+opportunity#inquiry-form" data-contact-topic="Revenue opportunity">Discuss a revenue opportunity →')
p.write_text(text)
meta_updates={
'index.html':('Workfriends | Strategic Partnerships & Revenue Builds','Workfriends develops brand opportunities, strategic partnerships and revenue channels for brands, agencies, platforms and IP owners through paid Revenue Builds.','/'),
'revenue-channels/index.html':('Partnerships, Brand Opportunities & Revenue Builds | Workfriends','Win brand business, activate complementary partners or build a new offering. Workfriends leads scoped, paid Revenue Builds with clear commercial responsibilities.','/revenue-channels/'),
'contact/index.html':('Discuss a Revenue Opportunity | Workfriends','Bring a brand opportunity, a partnership idea or a business ready for its next move. Start with a free 20-minute Workfriends fit call.','/contact/')}
for path,(title,desc,url) in meta_updates.items():
 p=ROOT/path;p.write_text(metadata(p.read_text(),title,desc,BASE+url))
for path in data['changed_html']:
    p=ROOT/path;text=p.read_text()
    if '/assets/wf-conversion.css' not in text:text=text.replace('</head>','<link rel="stylesheet" href="/assets/wf-conversion.css"></head>',1)
    if '/assets/wf-preview.js' not in text:text=text.replace('</body>','<script src="/assets/wf-preview.js" defer></script></body>',1)
    p.write_text(text)
p=ROOT/'sitemap.xml';text=p.read_text()
if BASE+'/agency-channel-build/' not in text:
 text=text.replace('</urlset>','<url><loc>'+BASE+'/agency-channel-build/</loc><lastmod>2026-10-19</lastmod></url>\n</urlset>')
for path in data['changed_html']:
 url='/' if path=='index.html' else '/'+path.replace('index.html','')
 text=re.sub(r'(<loc>'+re.escape(BASE+url)+r'</loc><lastmod>)[^<]*(</lastmod>)',r'\g<1>2026-10-19\2',text)
p.write_text(text)
hub='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><link rel="canonical" href="https://www.getworkfriends.co/review/"><title>Workfriends | Conversion preview</title><style>body{margin:0;background:#fbfbf8;color:#050505;font:16px/1.6 Arial,sans-serif}main{max-width:1000px;margin:auto;padding:65px 6%}a{color:#086b5a}header{border-bottom:1px solid #d9d9d3;padding-bottom:25px}.label{color:#086b5a;font-size:12px;letter-spacing:.08em;font-weight:bold;text-transform:uppercase}h1{font-size:clamp(36px,6vw,58px);line-height:1.05;letter-spacing:-.04em;max-width:850px}h2{font-size:26px;line-height:1.2}p{max-width:760px;color:#515852}.pages{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin:40px 0}.pages a{display:block;padding:25px;border:1px solid #d9d9d3;text-decoration:none}.pages strong{display:block;font-size:21px;line-height:1.3}.pages span{display:block;margin-top:12px;font-size:14px;color:#515852}aside{border-left:3px solid #086b5a;padding:5px 25px;background:#f0f2ec}footer{margin-top:30px;font-size:13px}@media(max-width:650px){main{padding:35px 6%}.pages{grid-template-columns:1fr}}</style></head><body><main><header><div class="label">Workfriends / Review preview</div><h1>The same Workfriends.<br>A clearer way to buy.</h1><p>This preview makes brands, partner-led growth and paid Revenue Builds explicit. The existing design, Universe, operating-partner descriptions and decision tools remain in place. The live site has not been changed by this update.</p></header><div class="pages"><a href="/"><strong>01 / Homepage →</strong><span>Three capability paths, followed by the paid Revenue Build model.</span></a><a href="/revenue-channels/"><strong>02 / Partnerships &amp; Channels →</strong><span>Brand-direct opportunities, productive partnerships and new offerings.</span></a><a href="/agency-channel-build/"><strong>03 / Agency Channel Build →</strong><span>A specific engagement for agencies, operators and platforms, with brands at the center.</span></a><a href="/creator-commerce/"><strong>04 / Creator Commerce →</strong><span>A clearer route from assessment to scoped execution.</span></a><a href="/audience-development/"><strong>05 / Audience Development →</strong><span>A paid engagement path for brands, talent and media/IP businesses.</span></a><a href="/contact/"><strong>06 / Contact →</strong><span>A commercial goal, a few lines of context and the existing fit-call process.</span></a></div><aside><h2>The review question</h2><p>Can a brand executive, an agency founder and a talent or media business each recognize their situation and understand what they could hire Workfriends to do?</p><p>No new client claims, named prospect examples, standard price, fixed team or guaranteed results have been added.</p></aside><footer><a href="/for-ai.html#revenue-builds-reference">Review the aligned business reference →</a><p>This is a review environment. The inquiry form is connected to the existing Workfriends endpoint; submitting it sends a real inquiry. No test inquiry was sent during the local checks.</p></footer></main></body></html>'''
p=ROOT/'review/index.html';p.parent.mkdir(exist_ok=True);p.write_text(hub)
notes='''\n\n## Conversion preview, 2026-10-19
Branch: `workfriends-conversion-preview-20261019`. Review only; do not merge or promote without Kevin's approval.

Updated Home, Partnerships & Channels, Creator Commerce, Audience Development, Contact and the public business reference. Added one Agency Channel Build page, shared conversion styles, and a preview-only review hub. Existing Universe, typography, verified form endpoint/behavior and approved partner descriptions are preserved. No public price, named new team commitment, prospect identity or client result was added.

The preview badge is disabled on the two production Workfriends hostnames. Before publication remove the preview-only review hub, badge script references and branch build workflow. Keep the production canonicals and confirm preview noindex behavior at the deployment layer. Run static content and browser tests, then do one authorized delivered-inquiry smoke test after launch. Local intercepted tests do not establish inbox delivery.
'''
p=ROOT/'README.md';text=p.read_text()
if '## Conversion preview, 2026-10-19' not in text:p.write_text(text+notes)
for path,old in original.items():
    new=(ROOT/path).read_text()
    oldscripts=re.findall(r'<script(?![^>]*application/ld\+json)\b[^>]*>.*?</script>',old,re.S)
    assert all(s in new for s in oldscripts), 'Script changed: '+path
    if '<form' in old:
        assert 'https://formspree.io/f/mvkglbdw' in new, 'Form provider changed'
    for match in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',new,re.S):json.loads(match[1])
assert (ROOT/'agency-channel-build/index.html').exists()
assert '/review/' not in (ROOT/'sitemap.xml').read_text()
print('Preview generated. No main branch, production deployment, domain or provider setting changed.')
