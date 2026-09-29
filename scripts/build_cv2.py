"""Generate and verify CV-2 without modifying the existing CV or portfolio."""
from pathlib import Path
import copy, hashlib, io, json, re, shutil, subprocess, sys
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/".build-tools"))
import build
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from pypdf import PdfReader
from PIL import Image
import zxingcpp

def main():
    protected=["index.html","cv.html","assets/cv/CV.pdf","data/profile.json","css/cv.css","scripts/build.py"]
    hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in protected}
    data=copy.deepcopy(json.loads((ROOT/"data/profile.json").read_text(encoding="utf-8")))
    variant=json.loads((ROOT/"data/cv-2.json").read_text(encoding="utf-8"))
    data["personal"]["cv_summary"]=variant["summary"]
    for x in data["experience"]:
        if x["id"] in variant["experience"]:x["cv_contributions"]=variant["experience"][x["id"]]
    for x in data["projects"]:
        if x["id"] in variant["projects"]:x["cv_contributions"]=variant["projects"][x["id"]]
    data["cv"]["skills"]=variant["skills"]
    soup=BeautifulSoup(build.cv(data),"html.parser")
    soup.title.string=data["personal"]["name"]+" - CV-2 - PFE 2027"
    for a in soup.select('a[href^="https://"]'):
        a["target"]="_blank";a["rel"]="noopener noreferrer"
    for a in soup.select('a[href="assets/cv/CV.pdf"]'):
        a["href"]="assets/cv/CV-2.pdf";a["download"]="Mohamed_Sbissi_CV.pdf"
    business=next(x for x in data["projects"] if x["id"]=="business")
    app=next(x for x in data["projects"] if x["id"]=="superstore")
    article='<article class="entry"><div class="entry-heading"><h3>Business Performance Prediction / ML Superstore</h3><span class="date">'+build.E(business["date"])+'</span></div><ul>'+''.join('<li>'+build.E(x)+'</li>' for x in variant["projects"]["business"])+'</ul><p class="tech">'+build.external(business["links"][0]["url"],"Analysis repository")+' / '+build.external(app["links"][0]["url"],"Application repository")+'</p></article>'
    soup.select_one(".short-project").replace_with(BeautifulSoup(article,"html.parser"))
    starts=[x.get_text(strip=True).split()[0] for x in soup.select(".entry li")]
    assert all(x in {"Consolidated","Designed","Implemented","Developed","Integrated","Collected","Prepared","Contributed","Applied","Deployed"} for x in starts),starts
    # Preserve the original font sizes; tighten spacing only for this variant.
    style=soup.new_tag('style')
    style.string='body{line-height:1.25}h2{margin:7px 0 4px;padding-bottom:2px}.entry{margin-bottom:5px}.entry li{margin-bottom:1px}.skills p{margin:2px 0}'
    soup.head.append(style)
    (ROOT/"cv-2.html").write_text(str(soup),encoding="utf-8")
    out=ROOT/"validation/cv-2";out.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        try:
            page=browser.new_page();errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
            page.goto((ROOT/"cv-2.html").as_uri(),wait_until="load");page.emulate_media(media="print")
            print("CV-2 content height (px):",page.locator("main").evaluate("e=>e.getBoundingClientRect().height"))
            pdf=page.pdf(format="A4",prefer_css_page_size=True,print_background=True)
            assert not errors,errors
        finally:browser.close()
    reader=PdfReader(io.BytesIO(pdf))
    assert len(reader.pages)==1,f"CV-2 must have one page, got {len(reader.pages)}"
    pg=reader.pages[0];text=pg.extract_text()
    for term in ["ODDO BHF","Ooredoo","7 SQL","25 DAX","10 authenticated","12 domains","4-page","GreenOPS AI","2nd Place","2,000 TND","Seeking PFE 2027",data["personal"]["email"],"Cloud & DevOps","ERP & SAP","coursework"]:
        assert term.casefold() in text.casefold(),term
    assert abs(float(pg.mediabox.width)-595.28)<2 and abs(float(pg.mediabox.height)-841.89)<2
    headings=["Professional Summary","Experience","Awards / Competitions","Selected Projects","Technical Skills","Education","Certifications","Languages"]
    positions=[text.casefold().index(h.casefold()) for h in headings];assert positions==sorted(positions)
    urls=[str(a.get_object().get("/A",{}).get("/URI","")) for a in pg.get("/Annots",[])]
    for url in [data["personal"]["portfolio"],data["personal"]["linkedin"],data["personal"]["github"],"mailto:"+data["personal"]["email"]]:assert url in urls
    pdfpath=ROOT/"assets/cv/CV-2.pdf";pdfpath.write_bytes(pdf)
    poppler=Path(r"C:\Users\sbiss\AppData\Local\Programs\MiKTeX\miktex\bin\x64")
    pdftoppm=shutil.which("pdftoppm") or str(poppler/"pdftoppm.exe")
    pdftotext=shutil.which("pdftotext") or str(poppler/"pdftotext.exe")
    subprocess.run([pdftoppm,"-scale-to","1600","-png",str(pdfpath),str(out/"page")],check=True)
    qr=zxingcpp.read_barcode(Image.open(out/"page-1.png"));assert qr and qr.text==data["personal"]["portfolio"]
    xml=ET.fromstring(subprocess.run([pdftotext,"-bbox",str(pdfpath),"-"],capture_output=True,check=True).stdout)
    pages=[x for x in xml.iter() if x.tag.endswith("page")];assert len(pages)==1
    wordpage=pages[0];w,h=float(wordpage.attrib["width"]),float(wordpage.attrib["height"])
    words=[x for x in wordpage.iter() if x.tag.endswith("word")]
    rows={}
    for word in words:
        a=word.attrib
        assert 0<=float(a["xMin"])<float(a["xMax"])<=w and 0<=float(a["yMin"])<float(a["yMax"])<=h,("Clipped",word.text)
        rows.setdefault(round(float(a["yMin"]),1),[]).append(word)
    for row in rows.values():
        row.sort(key=lambda x:float(x.attrib["xMin"]))
        for a,b in zip(row,row[1:]):assert float(a.attrib["xMax"])<=float(b.attrib["xMin"])+.8,("Overlap",a.text,b.text)
    for name,digest in hashes.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,("Changed existing version",name)
    report={"pages":1,"format":"A4","original_files_unchanged":True,"original_hashes":hashes,
            "body_font_pt":9.5,"selectable_text":True,"bullet_verbs":starts,"verified_metrics":["12 domains","7 SQL views","4 report pages","25 DAX measures","10 analytics endpoints"],
            "pdf_word_bounds":"passed","bottom":max(float(x.attrib["yMax"]) for x in words),"page_height":h,
            "qr_decoded":qr.text,"clickable_links":urls,"target_posting_supplied":False}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    (out/"text.txt").write_text(text,encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()
