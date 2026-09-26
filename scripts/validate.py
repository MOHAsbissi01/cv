"""Check the new portfolio, immutable previous version, and exactly-one-page CV."""
from pathlib import Path
import hashlib, io, json, subprocess, sys, threading, urllib.parse
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/".build-tools"))
from bs4 import BeautifulSoup
from pypdf import PdfReader
from PIL import Image
from playwright.sync_api import sync_playwright
import zxingcpp

def main():
    out=ROOT/"validation";out.mkdir(exist_ok=True)
    data=json.loads((ROOT/"data/profile.json").read_text())
    report={"original_preserved":True,"email":data["personal"]["email"],"browser":[]}
    for name,digest in json.loads((ROOT/"docs/original-version-hashes.json").read_text()).items():
        assert hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest()==digest,("Original file changed",name)
    manifest=json.loads((ROOT/"data/build-manifest.json").read_text())
    assert manifest["profile_sha256"]==hashlib.sha256((ROOT/"data/profile.json").read_bytes()).hexdigest()
    assert data["personal"]["email"]=="sbissi.mohamed@esprit.tn"
    for file in ["index.html","cv.html"]:
        soup=BeautifulSoup((ROOT/file).read_text(encoding="utf-8"),"html.parser")
        text=soup.body.get_text(" ",strip=True)
        ids=[t["id"] for t in soup.select("[id]")];assert len(ids)==len(set(ids))
        assert len(soup.select("h1"))==1 and soup.find("main") and soup.html["lang"]=="en"
        for marker in ["TODO","REVIEW:","Date to confirm","requires confirmation","sbissimohamed9@gmail.com"]:
            assert marker not in text,(file,marker)
        for t in soup.select("a[href],img[src],link[href],script[src]"):
            uri=t.get("href") or t.get("src");parsed=urllib.parse.urlsplit(uri)
            if parsed.scheme:assert parsed.scheme in ["https","mailto"]
            elif uri.startswith("#"):assert uri[1:] in ids
            else:assert (ROOT/urllib.parse.unquote(parsed.path)).exists(),uri
        assert all(t.get("alt") is not None for t in soup.find_all("img"))
        assert data["personal"]["email"] in text
        assert all(a["href"]=="mailto:"+data["personal"]["email"] for a in soup.select('a[href^="mailto:"]'))
    site=BeautifulSoup((ROOT/"index.html").read_text(),"html.parser")
    env=site.select_one("#experience-oddo .technical-environment")
    assert env and "Technical environment / exposure" in env.get_text()
    oddo=next(x for x in data["experience"] if x["id"]=="oddo")
    for cat in oddo["environment"]:
        for term in cat["items"]:assert term in env.get_text()
    oddo_bullets=site.select_one("#experience-oddo .contribution").get_text()
    for term in ["Apache Kafka","Node.js","WebSockets","Spring Batch","Camunda","Helm","Nginx","Keycloak","ELK"]:
        assert term not in oddo_bullets,"Invented implementation: "+term
    green=next(x for x in data["projects"] if x["id"]=="greenops")
    assert not green["stack"] and not green["project_stack"]
    assert site.select_one('meta[property="og:title"]')
    assert site.select_one('meta[property="og:url"]')["content"]==data["personal"]["portfolio"]
    jsonld=json.loads(site.select_one('script[type="application/ld+json"]').string)
    assert jsonld["email"]==data["personal"]["email"]
    qr=zxingcpp.read_barcode(Image.open(ROOT/"assets/qr/portfolio-qr.png"))
    assert qr and qr.text==data["personal"]["portfolio"]
    report["qr"]=qr.text
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin=f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            try:
                page=browser.new_page(accept_downloads=True);errors=[];bad=[]
                page.on("pageerror",lambda e:errors.append(str(e)))
                page.on("response",lambda r:bad.append((r.url,r.status)) if r.status>=400 else None)
                for width in [1600,1280,1024,768,390,320]:
                    page.set_viewport_size({"width":width,"height":1000})
                    page.goto(origin+"/index.html",wait_until="networkidle")
                    assert not page.evaluate("document.documentElement.scrollWidth>innerWidth"),width
                    assert page.locator("h1").is_visible()
                    if width==1280:
                        page.screenshot(path=str(out/"desktop-full.png"),full_page=True)
                        page.screenshot(path=str(out/"desktop-hero.png"))
                    if width==390:
                        page.screenshot(path=str(out/"mobile-full.png"),full_page=True)
                        page.screenshot(path=str(out/"mobile-hero.png"))
                    if width<=780:
                        assert page.locator("#main-navigation").is_hidden()
                        page.get_by_role("button",name="Menu",exact=True).click()
                        assert page.locator("#main-navigation").is_visible()
                        assert page.locator(".menu-toggle").get_attribute("aria-expanded")=="true"
                        page.keyboard.press("Escape")
                        assert page.locator("#main-navigation").is_hidden()
                        page.get_by_role("button",name="Menu",exact=True).click()
                        page.locator('#main-navigation a[href="#projects"]').click()
                        assert page.locator("#main-navigation").is_hidden()
                    report["browser"].append({"width":width,"overflow":False,"menu":"passed" if width<=780 else "desktop"})
                page.get_by_role("button",name="Development",exact=True).click()
                assert page.locator(".project:visible").count()==1
                page.get_by_role("button",name="All",exact=True).click()
                assert page.locator(".project:visible").count()==4
                disclosure=page.locator("#experience-oddo .technical-environment")
                disclosure.locator("summary").click();assert disclosure.get_attribute("open")==""
                assert disclosure.get_by_text("Keycloak",exact=True).is_visible()
                with page.expect_download() as info:
                    page.get_by_role("link",name="Download CV",exact=True).nth(1).click()
                download=info.value
                assert download.suggested_filename=="Mohamed-Sbissi-CV.pdf"
                assert Path(download.path()).read_bytes()==(ROOT/"assets/cv/CV.pdf").read_bytes()
                page.emulate_media(reduced_motion="reduce")
                assert page.evaluate('getComputedStyle(document.documentElement).scrollBehavior')=="auto"
                page.goto(origin+"/cv.html",wait_until="networkidle")
                page.set_viewport_size({"width":794,"height":1123});page.emulate_media(media="print")
                assert page.locator(".cv-toolbar").is_hidden()
                page.screenshot(path=str(out/"cv-print.png"),full_page=True)
                assert not errors,errors;assert not bad,bad
                report["javascript_errors"]=errors;report["http_errors"]=bad
                nojs=browser.new_context(java_script_enabled=False,viewport={"width":390,"height":900})
                p=nojs.new_page();p.goto(origin+"/index.html",wait_until="networkidle")
                assert p.locator("#main-navigation").is_visible()
                assert p.locator(".project:visible").count()==4
                nojs.close()
            finally:browser.close()
    finally:server.shutdown();server.server_close()
    reader=PdfReader(ROOT/"assets/cv/CV.pdf")
    assert len(reader.pages)==1,"STRICT: PDF must be exactly one page"
    pg=reader.pages[0]
    assert abs(float(pg.mediabox.width)-595.28)<2 and abs(float(pg.mediabox.height)-841.89)<2,"Not A4"
    text=pg.extract_text();lower=text.casefold()
    for term in ["Mohamed Sbissi","Seeking PFE 2027","ODDO BHF","Ooredoo","GreenOPS AI","2nd Place","2,000 TND","12 business domains","seven SQL","four-page","Angular","Python","Environment exposure","Apache Kafka","OpenShift","ESPRIT",data["personal"]["email"],"Languages","Certifications"]:
        assert term.casefold() in lower,term
    assert "sbissimohamed9@gmail.com" not in text
    assert "Technical Skills".casefold() in lower
    headers=["Professional Summary","Experience","Awards / Competitions","Selected Projects","Technical Skills","Education","Certifications","Languages"]
    locations=[lower.index(x.casefold()) for x in headers];assert locations==sorted(locations)
    uris=[str(a.get_object().get("/A",{}).get("/URI","")) for a in pg.get("/Annots",[])]
    assert all(x in uris for x in [data["personal"]["portfolio"],data["personal"]["linkedin"],data["personal"]["github"],"mailto:"+data["personal"]["email"]])
    xml=ET.fromstring(subprocess.run(["pdftotext","-bbox",str(ROOT/"assets/cv/CV.pdf"),"-"],capture_output=True,check=True).stdout)
    pages=[x for x in xml.iter() if x.tag.endswith("page")];assert len(pages)==1
    wordpage=pages[0];width,height=float(wordpage.attrib["width"]),float(wordpage.attrib["height"])
    words=[x for x in wordpage.iter() if x.tag.endswith("word")]
    rows={}
    for word in words:
        a=word.attrib
        assert 0<=float(a["xMin"])<float(a["xMax"])<=width and 0<=float(a["yMin"])<float(a["yMax"])<=height,("Clipping",word.text)
        rows.setdefault(round(float(a["yMin"]),1),[]).append(word)
    for row in rows.values():
        row.sort(key=lambda x:float(x.attrib["xMin"]))
        for a,b in zip(row,row[1:]):assert float(a.attrib["xMax"])<=float(b.attrib["xMin"])+.8,("Overlap",a.text,b.text)
    report["pdf"]={"pages":1,"format":"A4","selectable":True,"words":len(words),"section_order_valid":True,
                   "bottom":max(float(x.attrib["yMax"]) for x in words),"height":height,"links":uris}
    report["main_stack_vs_environment"]="passed"
    report["downloads_and_filters"]="passed"
    report["public_placeholders"]="none"
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
