#!/usr/bin/env python3
"""Isolated browser QA. Serves repository locally; intercepts every external request.
No real Formspree request, email, analytics event or production mutation is made.
"""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'preview-checks';OUT.mkdir(exist_ok=True)
PATHS=['/','/revenue-channels/','/agency-channel-build/','/creator-commerce/','/audience-development/','/contact/','/for-ai.html','/review/']
report={'layout':[],'forms':[],'links':[],'script_errors':[],'external_requests_blocked':[], 'real_inquiries_sent':0}

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
class Links(HTMLParser):
    def __init__(self,text):
        super().__init__();self.links=[];self.ids=set();self.feed(text)
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if d.get('id'):self.ids.add(d['id'])
        if tag=='a' and d.get('href'):self.links.append(d['href'])

def file_for(path):
    path=unquote(path).lstrip('/')
    p=ROOT/path
    return p/'index.html' if p.is_dir() or not path else p

server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
BASE='http://127.0.0.1:'+str(server.server_port)
try:
    # Validate local navigation destinations and anchor targets in the edited pages.
    for path in PATHS:
        parser=Links(file_for(path).read_text())
        for link in parser.links:
            u=urlsplit(link)
            if u.scheme or u.netloc or not link.startswith(('/', '#')):continue
            target=file_for(u.path or path)
            assert target.exists(), f'Missing local link {path}: {link}'
            if u.fragment and target.suffix=='.html':
                assert unquote(u.fragment) in Links(target.read_text()).ids, f'Missing anchor {path}: {link}'
        report['links'].append({'path':path,'status':'passed'})
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
        for width,height,label in [(1440,1000,'desktop'),(390,844,'mobile')]:
            ctx=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce')
            def local_only(route):
                if route.request.url.startswith(BASE) or route.request.url.startswith(('data:', 'blob:')):route.continue_()
                else:
                    report['external_requests_blocked'].append(route.request.url)
                    route.abort()
            ctx.route('**/*',local_only)
            page=ctx.new_page();page.on('pageerror',lambda error:report['script_errors'].append(str(error)))
            for path in PATHS:
                resp=page.goto(BASE+path,wait_until='domcontentloaded')
                assert resp.status==200, f'Bad response: {path}'
                page.wait_for_timeout(300)
                assert page.locator('h1').count()==1, f'Expected one h1: {path}'
                overflow=page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
                assert not overflow, f'Horizontal overflow at {width}px: {path}'
                assert page.locator('h1').is_visible(), f'Hidden heading: {path}'
                if path!='/review/' and width==390:
                    menu=page.locator('.nav-toggle')
                    assert menu.is_visible(), f'Missing mobile menu: {path}'
                    menu.click();assert menu.get_attribute('aria-expanded')=='true'
                    assert page.locator('#main-nav').is_visible()
                    menu.click();assert menu.get_attribute('aria-expanded')=='false'
                if path in ['/','/revenue-channels/','/agency-channel-build/','/creator-commerce/','/audience-development/','/contact/']:
                    name=path.strip('/').replace('/','-') or 'home'
                    page.screenshot(path=str(OUT/(name+'-'+label+'.png')),full_page=True,animations='disabled')
                report['layout'].append({'path':path,'width':width,'status':'passed'})
            ctx.close()
        # Form tests use synthetic data and a local interceptor; never reach provider.
        ctx=browser.new_context(viewport={'width':1280,'height':900})
        mode={'status':500,'body':{'ok':False}};requests=[]
        def form_route(route):
            u=route.request.url
            if u.startswith('https://formspree.io/'):
                requests.append(route.request.post_data or '')
                route.fulfill(status=mode['status'],content_type='application/json',body=json.dumps(mode['body']))
            elif u.startswith(BASE):route.continue_()
            else:route.abort()
        ctx.route('**/*',form_route)
        page=ctx.new_page()
        page.goto(BASE+'/contact/?topic=Agency+Channel+Build&utm_source=preview_test',wait_until='domcontentloaded')
        assert page.locator('#contact-topic').input_value()=='Agency Channel Build'
        page.locator('#contact-name').fill('Preview QA')
        page.locator('#contact-email').fill('preview-qa@example.invalid')
        text='Synthetic validation only; do not send.'
        page.locator('#contact-situation').fill(text)
        submit=page.locator('#inquiry-form button[type=submit]')
        submit.click()
        page.locator('.form-status[data-state=error]').wait_for()
        assert page.locator('#contact-situation').input_value()==text
        assert submit.is_enabled()
        assert page.locator('.form-recovery').is_visible()
        assert len(requests)==1
        report['forms'].append({'case':'HTTP failure preserves inquiry and recovery','status':'passed'})
        mode.update(status=200,body={'unexpected':True});submit.click()
        page.locator('.form-status[data-state=error]').wait_for()
        assert page.locator('#contact-situation').input_value()==text
        assert len(requests)==2
        report['forms'].append({'case':'Unconfirmed response never shows success','status':'passed'})
        mode.update(status=200,body={'ok':True});submit.click()
        page.wait_for_url(BASE+'/thanks/')
        assert len(requests)==3
        assert 'preview_test' in requests[0] and 'Agency Channel Build' in requests[0]
        report['forms'].append({'case':'Confirmed response redirects to local thanks; context retained','status':'passed'})
        ctx.close()
        ctx=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
        ctx.route('**/*',lambda route:route.continue_() if route.request.url.startswith(BASE) else route.abort())
        page=ctx.new_page();page.goto(BASE+'/contact/')
        assert page.locator('form').get_attribute('action')=='https://formspree.io/f/mvkglbdw'
        assert page.locator('form').get_attribute('method').upper()=='POST'
        assert page.locator('#contact-situation').is_visible()
        report['forms'].append({'case':'Native POST fallback retained; not submitted','status':'passed'})
        ctx.close();browser.close()
    assert not report['script_errors'], 'Browser script errors: '+str(report['script_errors'])
    report['status']='passed'
finally:
    server.shutdown()
    (OUT/'report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
