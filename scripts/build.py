"""Build the new portfolio and exactly-one-page CV from data/profile.json."""
from pathlib import Path
import argparse, hashlib, html, io, json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/".build-tools"))
from bs4 import BeautifulSoup
from render_portfolio import portfolio as render_previous_structure
E=html.escape

def fragment(markup):
    return BeautifulSoup(markup,"html.parser")

def external(url,label,cls=""):
    if not url.startswith(("https://","mailto:")): raise ValueError("Invalid URL")
    return f'<a class="{cls}" href="{E(url,quote=True)}">{E(label)}</a>'

def page_head(d,title,css):
    p=d["personal"]
    description="Computer Engineering student at ESPRIT seeking PFE 2027 in Data Engineering, Business Intelligence, SAP/ERP and Data & AI."
    image=p["portfolio"].rstrip("/")+"/assets/images/portrait.jpg"
    person={"@context":"https://schema.org","@type":"Person","name":p["name"],"jobTitle":p["title"],
            "email":p["email"],"url":p["portfolio"],"sameAs":[p["linkedin"],p["github"]]}
    metadata=f'<meta name="description" content="{E(description)}"><meta name="theme-color" content="#10262d"><meta property="og:type" content="website"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}"><meta property="og:url" content="{E(p["portfolio"])}"><meta property="og:image" content="{E(image)}"><meta property="og:image:alt" content="Portrait of Mohamed Sbissi"><meta name="twitter:card" content="summary"><link rel="canonical" href="{E(p["portfolio"])}">'
    styles="".join(f'<link rel="stylesheet" href="{x}">' for x in css)
    return '<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+E(title)+'</title>'+metadata+styles+'<script type="application/ld+json">'+json.dumps(person).replace("</","<\\/")+'</script></head>'

def portfolio(d):
    p=d["personal"]
    soup=BeautifulSoup(render_previous_structure(d),"html.parser")
    # Reuse the existing semantic structure and factual content, then upgrade presentation.
    soup.head.clear()
    head=BeautifulSoup(page_head(d,p["name"]+" | Data Engineering - BI - SAP",["css/style.css","css/responsive.css","css/print.css"]),"html.parser")
    soup.head.replace_with(head.head)
    for script in soup.select("script[src]"):script.decompose()
    soup.body.append(fragment('<script src="js/main.js" defer></script>').script)
    brand=soup.select_one(".brand")
    brand.clear()
    brand.append(fragment(f'<span class="brand-mark" aria-hidden="true">MS</span><span class="brand-name">{E(p["name"])}<span class="brand-subtitle">Data / BI / SAP</span></span>'))
    nav=soup.select_one("nav");nav["id"]="main-navigation"
    nav.clear()
    for id,label in [("experience","Experience"),("projects","Projects"),("skills","Skills"),("education","Education")]:
        nav.append(fragment(f'<a href="#{id}">{label}</a>'))
    nav.append(fragment('<a class="nav-download" href="assets/cv/CV.pdf" download="Mohamed-Sbissi-CV.pdf">Download CV</a>'))
    nav.insert_before(fragment('<button class="menu-toggle" type="button" aria-controls="main-navigation" aria-expanded="false">Menu</button>'))
    name=soup.select_one("h1");first,last=p["name"].split(" ",1);name.clear();name.append(first+" ");name.append(fragment("<span>"+E(last)+"</span>"))
    intro=soup.select_one(".hero-intro");intro.string="Turning data into reliable pipelines, decision-ready insights and enterprise solutions."
    domains=fragment('<div class="domain-tags" aria-label="Core domains"><span>Data Engineering</span><span>Business Intelligence</span><span>SAP / ERP</span><span>AI / ML</span></div>')
    soup.select_one(".hero-focus").insert_after(domains)
    portrait=soup.select_one(".portrait")
    visual=fragment(f'<aside class="hero-visual" aria-label="Profile and internship evidence"><div class="visual-frame"><div class="frame-top"><span>Computer Engineering / ESPRIT</span><span aria-hidden="true"></span></div><img class="portrait" src="assets/images/portrait.jpg" width="340" height="330" alt="Portrait of {E(p["name"])}"><div class="frame-caption"><strong>Engineering with data.</strong><span>Tunis, Tunisia</span></div></div><div class="visual-note"><div><strong>7 SQL views</strong><small>ODDO BHF reporting</small></div><div><strong>4 BI pages</strong><small>Training analytics</small></div></div></aside>')
    portrait.replace_with(visual)
    for a in soup.select('a[href="CV.pdf"]'):
        a["href"]="assets/cv/CV.pdf";a["download"]="Mohamed-Sbissi-CV.pdf"
    for a in soup.select(".hero .actions a"):
        if a.get("href")==p["linkedin"] or a.get("href")==p["github"]:a["class"]=["button","social"]
    # Hide owner review notes from public UI; retain them in canonical data and Markdown.
    for item in soup.select(".review-details,.review-links,.review"):
        item.decompose()
    for section in list(soup.select("main > .section")):
        if not section.get("id") and not section.get_text(strip=True):section.decompose()
    for element in list(soup.select(".date")):
        if "confirm" in element.get_text().lower():element.decompose()
    for idx,(article,x) in enumerate(zip(soup.select(".experience"),d["experience"])):
        article["id"]="experience-"+x["id"]
        body=article.select_one(".meta").find_next_sibling("div");body["class"]=["experience-body"]
        if not x["contributions"]:
            for label in list(body.select(".label")):label.decompose()
        if x["id"]=="oddo":
            article["class"].append("featured-experience")
            body.select_one(".context").insert_after(fragment('<div class="delivery-flow" aria-label="Delivered analytics workflow"><span>HR data preparation</span><span>PostgreSQL / SQL</span><span>Power BI / DAX</span><span>API / ML integration</span></div>'))
            for label in body.select(".label"):
                if label.get_text()=="Technologies used":label.string="Main implementation tools"
            env='<details class="technical-environment"><summary>Technical environment / exposure</summary><p>'+E(x["environment_note"])+'</p><div class="environment-grid">'
            for category in x["environment"]:
                env+='<div class="environment-category"><h4>'+E(category["category"])+'</h4><div class="stack">'+''.join('<span class="chip">'+E(t)+'</span>' for t in category["items"])+'</div></div>'
            env+='</div></details>'
            body.append(fragment(env))
    green=soup.select_one("#project-greenops")
    green.extract();green["class"]=["featured-project"];green.attrs.pop("data-category",None)
    for node in green.select(".award-tag"):node.decompose()
    for label in green.select(".label"):
        if label.get_text()=="Team":label.decompose()
    for node in green.select(".compact"):node.decompose()
    achievement=fragment('<section class="section" id="achievement" aria-labelledby="achievement-heading"><div class="section-heading"><h2 id="achievement-heading">Data engineering. Competition impact.</h2><p>A team achievement, with a clearly defined individual role.</p></div><div class="featured-achievement"><aside class="award-panel"><p class="eyebrow">GreenOPS AI / Team award</p><div class="award-rank">2<small>nd</small></div><p class="award-prize">2,000 TND prize</p><p class="award-caption">AI competition / Pharmaceutical sustainability</p></aside></div></section>')
    achievement.select_one(".featured-achievement").append(green)
    soup.select_one("#projects").insert_before(achievement)
    for btn in list(soup.select("[data-filter]")):
        if btn["data-filter"]=="Competition":btn.decompose()
    soup.select_one("#filter-status").string="4 projects shown"
    for x in soup.select(".project"):
        for node in list(x.select(".date")):
            if "unavailable" in node.get_text().lower():node.decompose()
        if not x.select(".contribution"):
            for label in list(x.select(".label")):
                if label.get_text()=="My contribution":label.decompose()
        for a in x.select(".project-links a"):
            a.string="View Repository \u2192" if a.get_text()=="GitHub" else "Contribution evidence \u2192"
    # Keep confirmed competition participation; do not expose incomplete award metadata.
    for item in list(soup.select("#awards .education-item")):
        if item.h3.get_text()!="IEEEXtreme 17.0":item.decompose()
    for idx,h in enumerate(soup.select(".section-heading h2"),1):h["data-number"]=f"{idx:02d} /"
    contact=soup.select_one(".contact-panel")
    wrapper=soup.new_tag("div");nodes=list(contact.contents)
    for node in nodes:
        if getattr(node,"name",None)=="div" and "actions" in node.get("class",[]):continue
        wrapper.append(node.extract())
    contact.insert(0,wrapper)
    for a in contact.select(".actions a"):
        if a.get("href") in [p["linkedin"],p["github"]]:a["class"]=["button","social"]
    footer=soup.select_one("footer")
    footer.clear();footer.append(fragment(f'<div class="footer-inner"><span>{E(p["name"])} &middot; {E(p["objective"])}</span><div><a href="cv.html">Printable CV</a>{external(p["github"],"GitHub")}{external(p["linkedin"],"LinkedIn")}</div></div>'))
    result=str(soup)
    for placeholder in ["TODO","REVIEW:","Date to confirm","requires confirmation"]:
        if placeholder in soup.body.get_text():raise RuntimeError("Public placeholder leaked: "+placeholder)
    return result

def cv(d):
    p=d["personal"]
    def project(id):return next(x for x in d["projects"] if x["id"]==id)
    def contribution(items):return "<ul>"+"".join("<li>"+E(t)+"</li>" for t in items)+"</ul>"
    b='<body><div class="cv-toolbar"><a href="index.html">Portfolio</a><button type="button" onclick="window.print()">Print / Save as PDF</button><a href="assets/cv/CV.pdf" download="Mohamed-Sbissi-CV.pdf">Download CV</a></div><main class="cv-document">'
    b+=f'<header class="cv-header"><a class="qr" href="{E(p["portfolio"])}"><img src="assets/qr/portfolio-qr.png" alt="Portfolio QR code"><span>Portfolio</span></a><h1>{E(p["name"])}</h1><p class="cv-role">{E(p["title"])}</p><p>Data Engineering &middot; Business Intelligence &middot; SAP <strong class="cv-objective">| {E(p["objective"])}</strong></p><p class="cv-contact">{external("mailto:"+p["email"],p["email"])} | {E(p["location"])}</p><p class="cv-links">{external(p["linkedin"],"linkedin.com/in/mohamed-sbissi")} &middot; {external(p["github"],"github.com/MOHAsbissi01")}<br>{external(p["portfolio"],p["portfolio"].replace("https://",""))}</p></header>'
    b+='<section><h2>Professional Summary</h2><p class="summary">'+E(p["cv_summary"])+'</p></section><section><h2>Experience</h2>'
    for id in d["cv"]["experience_ids"]:
        x=next(x for x in d["experience"] if x["id"]==id)
        b+=f'<article class="entry"><div class="entry-heading"><h3>{E(x["company"])} | {E(x["role"])}</h3><span class="date">{E(x["date"])}</span></div>'+contribution(x["cv_contributions"])
        if id=="oddo":
            b+='<p class="tech"><strong>Main implementation:</strong> ' + E(", ".join(x["cv_main_stack"])) + '<br><strong>Environment exposure:</strong> '+E(', '.join(x["cv_exposure"]))+'</p>'
        b+='</article>'
    b+='</section><section><h2>Awards / Competitions</h2>'
    green=project("greenops")
    b+=f'<article class="entry"><h3 class="award-title">GreenOPS AI - {E(green["achievement"])}</h3><p class="role">{E(green["role"])} | AI competition | Pharmaceutical sustainability</p>'+contribution(green["cv_contributions"])+'<p class="tech">Tools withheld under NDA. LLM development delivered by teammates.</p></article></section>'
    b+='<section><h2>Selected Projects</h2>'
    urban=project("urban")
    b+=f'<article class="entry"><div class="entry-heading"><h3>Intelligent Urban Mobility | Data / ML team contributor</h3><span class="date">{E(urban["date"])}</span></div>'+contribution(urban["cv_contributions"])+'<p class="tech">Tech: Python, scikit-learn, FastAPI, n8n &middot; '+external(urban["links"][0]["url"],"GitHub / project evidence")+'</p></article>'
    business,superstore=project("business"),project("superstore")
    b+='<p class="short-project"><strong>Business Performance Prediction / ML Superstore</strong> ('+E(business["date"])+')<br>Applied CRISP-DM; built a Streamlit prediction app with model comparison and business insights. '+external(business["links"][0]["url"],"Analysis repository")+' / '+external(superstore["links"][0]["url"],"Application repository")+'</p></section>'
    b+='<section class="skills"><h2>Technical Skills</h2>'
    groups=[(x["category"],x["items"]) for x in d["cv"]["skills"]]
    for title,items in groups:b+='<p><strong>'+E(title)+':</strong> '+E(' / '.join(items))+'</p>'
    b+='</section><section class="education"><h2>Education</h2>'
    x=d["education"][0]
    b+='<p><strong>'+E(x["school"])+'</strong> | '+E(x["degree"])+'<br>'+E(x["date"])+' | Final-year student; degree in progress.</p></section>'
    b+='<section class="credentials"><h2>Certifications</h2><p>'+E(' | '.join([d["certifications"][i] for i in d["cv"]["certification_indexes"]]))+'</p></section><section class="languages"><h2>Languages</h2><p>'+E(' | '.join(x["name"]+': '+x["level"] for x in d["languages"]))+'</p></section></main></body></html>'
    return page_head(d,p["name"]+" - One-page CV - PFE 2027",["css/cv.css"])+b

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--pdf",action="store_true");args=parser.parse_args()
    d=json.loads((ROOT/"data/profile.json").read_text(encoding="utf-8"))
    import qrcode
    from qrcode.image.svg import SvgPathImage
    q=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=8,border=4);q.add_data(d["personal"]["portfolio"]);q.make(fit=True)
    q.make_image(fill_color="black",back_color="white").save(ROOT/"assets/qr/portfolio-qr.png")
    q.make_image(image_factory=SvgPathImage).save(ROOT/"assets/qr/portfolio-qr.svg")
    (ROOT/"index.html").write_text(portfolio(d),encoding="utf-8");(ROOT/"cv.html").write_text(cv(d),encoding="utf-8")
    facts="# FACTS TO VERIFY\n\n"+"\n".join("- "+x for x in d["facts_to_verify"])+"\n\n## PDF editorial decisions\n\n"+"\n".join("- "+x for x in d["pdf_editorial"])+"\n"
    (ROOT/"FACTS_TO_VERIFY.md").write_text(facts,encoding="utf-8")
    if args.pdf:
        from playwright.sync_api import sync_playwright
        from pypdf import PdfReader
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            try:
                page=browser.new_page();page.goto((ROOT/"cv.html").as_uri(),wait_until="load");page.emulate_media(media="print")
                pdf=page.pdf(format="A4",prefer_css_page_size=True,print_background=True)
                reader=PdfReader(io.BytesIO(pdf))
                if len(reader.pages)!=1:raise RuntimeError(f"PDF has {len(reader.pages)} pages; MUST equal 1.")
                text=reader.pages[0].extract_text()
                for term in ["ODDO BHF","Ooredoo","GreenOPS AI","2nd Place","2,000 TND",d["personal"]["email"],"Seeking PFE 2027","Technical Skills","ESPRIT"]:
                    if term.casefold() not in text.casefold():raise RuntimeError("Missing PDF content: "+term)
                (ROOT/"assets/cv/CV.pdf").write_bytes(pdf);(ROOT/"validation/cv-text.txt").write_text(text,encoding="utf-8")
                print("CV.pdf generated: EXACTLY 1 A4 PAGE. Text extraction passed.")
            finally:browser.close()
    manifest={"profile_sha256":hashlib.sha256((ROOT/"data/profile.json").read_bytes()).hexdigest(),"portfolio_url":d["personal"]["portfolio"],"cv":"assets/cv/CV.pdf","page_requirement":1}
    (ROOT/"data/build-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("Built CvWebsite, printable CV, QR and owner review notes.")

if __name__=="__main__":main()
