"""Contact, sharing, consent/timing and dashboard checks; no real telemetry uploads."""
import base64,io,json,sys,threading
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'.build-tools'))
from PIL import Image
from playwright.sync_api import sync_playwright

def main():
    raw=(ROOT/'assets/contact/Mohamed-Sbissi.vcf').read_bytes()
    assert b'\r\n' in raw and all(len(line)<=75 for line in raw.split(b'\r\n'))
    card=raw.replace(b'\r\n ',b'').decode()
    for field in ['VERSION:3.0','FN:Mohamed Sbissi','N:Sbissi;Mohamed;;;','TEL;TYPE=CELL:+21629785051','EMAIL;TYPE=INTERNET,WORK:sbissi.mohamed@esprit.tn']:
        assert field in card,field
    photo=next(line.split(':',1)[1] for line in card.splitlines() if line.startswith('PHOTO;'))
    image=Image.open(io.BytesIO(base64.b64decode(photo)));assert max(image.size)<=320
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin=f'http://127.0.0.1:{server.server_port}';out=ROOT/'validation'
    report={};errors=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            try:
                context=browser.new_context(viewport={'width':390,'height':900},reduced_motion='reduce')
                context.add_init_script("localStorage.setItem('ms-portfolio-language','en');Object.defineProperty(navigator,'share',{value:undefined,configurable:true});")
                page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(origin+'/index.html',wait_until='networkidle')
                assert page.locator('.analytics-consent').is_hidden()
                assert page.locator('a[href="assets/contact/Mohamed-Sbissi.vcf"]').count()==3
                assert page.locator('a[href="tel:+21629785051"]').count()==2
                for width in [1600,1280,1024,820,768,390,320]:
                    page.set_viewport_size({'width':width,'height':900});assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),width
                page.locator('.share-button').click();assert page.locator('.share-dialog').is_visible()
                assert page.locator('#share-url').input_value()=='https://mohasbissi01.github.io/cv/'
                page.screenshot(path=str(out/'share-mobile.png'));page.keyboard.press('Escape')
                assert page.locator('.share-button').evaluate('e=>e===document.activeElement')
                page.evaluate("Object.defineProperty(navigator,'share',{configurable:true,value:async data=>{window.sharedPayload=data}})")
                page.locator('.share-button').click();assert page.evaluate('window.sharedPayload.url')=='https://mohasbissi01.github.io/cv/'
                assert page.locator('.share-dialog').is_hidden();context.close()
                # Config is mocked HTTPS, and every collector request is intercepted locally.
                context=browser.new_context(viewport={'width':390,'height':900},reduced_motion='reduce')
                context.add_init_script("localStorage.setItem('ms-portfolio-language','en');")
                context.route('**/js/analytics-config.js',lambda route:route.fulfill(content_type='application/javascript',body='window.MS_ANALYTICS={enabled:true,endpoint:"https://collector.test"};'))
                requests=[]
                def collect(route):
                    requests.append({'path':route.request.url,'body':json.loads(route.request.post_data or '{}')})
                    route.fulfill(status=200,content_type='application/json',headers={'Access-Control-Allow-Origin':origin},body='{"ok":true}')
                context.route('https://collector.test/**',collect)
                page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
                page.clock.install()
                page.goto(origin+'/index.html',wait_until='networkidle');assert not requests
                assert page.locator('.analytics-consent').is_visible()
                page.screenshot(path=str(out/'consent-mobile.png'))
                page.locator('[data-consent="no"]').click();page.reload(wait_until='networkidle');assert not requests
                page.locator('.privacy-settings').click();page.locator('[data-consent="yes"]').click()
                page.wait_for_timeout(150);assert len(requests)==1 and requests[0]['body']['consent'] is True
                page.clock.run_for(30000);page.wait_for_timeout(100)
                assert sum(r['body'].get('active_ms',0) for r in requests)>0
                # Hidden tab and idle time cannot add unlimited viewing time.
                page.clock.run_for(90000);page.wait_for_timeout(100)
                elapsed=sum(r['body'].get('active_ms',0) for r in requests);assert elapsed<=65000,elapsed
                page.locator('[data-action="save_contact"]').first.evaluate("e=>e.addEventListener('click',event=>event.preventDefault())")
                page.locator('[data-action="save_contact"]').first.click();page.clock.run_for(5000);page.wait_for_timeout(100)
                assert any(e['action']=='save_contact' for r in requests for e in r['body'].get('events',[]))
                page.locator('.privacy-settings').click();page.locator('[data-consent="no"]').click();before=len(requests)
                page.clock.run_for(30000);page.wait_for_timeout(100);assert len(requests)==before
                page.locator('.privacy-settings').click();page.locator('.delete-visit').click();page.wait_for_timeout(100)
                assert requests[-1]['path'].endswith('/erase');assert page.locator('.delete-visit').is_hidden()
                assert 'deleted' in page.locator('.privacy-status').inner_text();context.close()
                # Native privacy signals disable collection even with a prior opt-in.
                context=browser.new_context()
                context.add_init_script("localStorage.setItem('ms-portfolio-language','en');localStorage.setItem('ms-statistics-choice-v1',JSON.stringify({value:'yes',at:Date.now()}));Object.defineProperty(navigator,'globalPrivacyControl',{value:true});")
                context.route('**/js/analytics-config.js',lambda route:route.fulfill(content_type='application/javascript',body='window.MS_ANALYTICS={enabled:true,endpoint:"https://collector.test"};'))
                blocked=[];context.route('https://collector.test/**',lambda route:(blocked.append(route.request.url),route.abort()))
                p=context.new_page();p.goto(origin+'/index.html',wait_until='networkidle');assert not blocked;context.close()
                # Private dashboard consumes only authenticated data, with no seed/demo data.
                page=browser.new_page(viewport={'width':1280,'height':900})
                page.on('pageerror',lambda e:errors.append(str(e)))
                fixture={'totals':{'visits':1,'active_ms':45000},'visits':[{'id':'22222222-2222-4222-8222-222222222222','started':1700000000000,'updated':1700000045000,'active_ms':45000}],
                         'events':[{'visit':'22222222-2222-4222-8222-222222222222','at':1700000045000,'action':'download_cv'}],'buttons':[{'action':'download_cv','count':1}],'as_of':1700000045000}
                admin_requests=[]
                def summary(route):
                    admin_requests.append(route.request.url)
                    assert route.request.headers['authorization']=='Bearer '+'t'*40
                    route.fulfill(content_type='application/json',body=json.dumps(fixture))
                page.route('**/api/admin/summary',summary)
                page.goto(origin+'/analytics/public/index.html',wait_until='networkidle')
                assert page.locator('#dashboard').is_hidden()
                page.locator('#view-prototype').click()
                assert page.locator('#demo-notice').is_visible()
                assert page.locator('#visits').inner_text()=='3'
                page.locator('#refresh').click();assert not admin_requests
                page.screenshot(path=str(out/'dashboard-prototype.png'),full_page=True)
                page.locator('#logout').click();assert page.locator('#demo-notice').is_hidden()
                page.locator('#token').fill('t'*40);page.get_by_role('button',name='Unlock dashboard',exact=True).click();page.wait_for_timeout(100)
                assert page.locator('#visits').inner_text()=='1';assert page.locator('#active').inner_text()=='45s'
                page.locator('#sessions button').click();assert 'CV link' in page.locator('#timeline').inner_text()
                # This screenshot explicitly contains test-fixture data, never production stats.
                page.screenshot(path=str(out/'dashboard-test-fixture.png'),full_page=True)
                page.locator('#logout').click();assert page.locator('#dashboard').is_hidden();assert page.locator('#events').inner_text()==''
                assert not errors,errors
                report={'vcard':'prefilled fields, CRLF folding and embedded JPEG verified','share':'native API and keyboard-accessible fallback verified','consent':'no upload before opt-in or after refusal; erasure and GPC verified','time':'active clock and idle cap verified','dashboard':'authenticated request, rendering and logout verified','javascript_errors':errors}
            finally:browser.close()
    finally:server.shutdown();server.server_close()
    (out/'engagement-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
