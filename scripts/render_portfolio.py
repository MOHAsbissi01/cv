"""Generate static portfolio, ATS CV, QR asset, and review notes from one JSON source."""
from pathlib import Path
import argparse, base64, hashlib, html, json, re, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".build-tools"))
E = html.escape

def link(url, label):
    if not url.startswith(("https://", "mailto:")):
        raise ValueError("Unsafe external URL: " + url)
    return f'<a href="{E(url, quote=True)}">{E(label)}</a>'

def bullets(items):
    return "<ul class='contribution'>" + "".join(f"<li>{E(x)}</li>" for x in items) + "</ul>"

def chips(items):
    return "<div class='stack'>" + "".join(f"<span class='chip'>{E(x)}</span>" for x in items) + "</div>"

def heading(id, title, subtitle=""):
    return f'<section class="section" id="{id}" aria-labelledby="{id}-heading"><div class="section-heading"><h2 id="{id}-heading">{title}</h2><p>{E(subtitle)}</p></div>'

def shell(title, css, body, script=""):
    return f'<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{E(title)}</title><meta name="description" content="Mohamed Sbissi - final-year ERP/BI engineering student at ESPRIT seeking PFE 2027 in Data Engineering, BI, SAP and Data &amp; AI."><link rel="stylesheet" href="{css}"></head><body>{body}{script}</body></html>\n'

def portfolio(d):
    p = d["personal"]
    b = '<a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="#main">MS<span>.</span></a><nav aria-label="Main navigation"><a href="#experience">Experience</a><a href="#projects">Projects</a><a href="#skills">Skills</a><a href="#contact">Contact</a><a href="CV.pdf" download>CV PDF</a></nav></div></header><main id="main" class="wrap">'
    b += f'<section class="hero" aria-labelledby="name"><div><span class="availability">{E(p["objective"])}</span><p class="eyebrow">ESPRIT / FINAL YEAR</p><h1 id="name">{E(p["name"])}</h1><p class="hero-role">{E(p["title"])}</p><p class="hero-focus">{E(p["focus"])}</p><p class="hero-intro">Turning business data into reliable analytics, reporting, and useful applications. Internship experience in banking and telecom; academic projects in data and machine learning.</p><div class="actions"><a class="button" href="CV.pdf" download>Download CV</a><a class="button secondary" href="#projects">View projects</a>{link(p["linkedin"],"LinkedIn")}{link(p["github"],"GitHub")}</div><p class="hero-meta">{E(p["location"])} &middot; {link("mailto:"+p["email"],p["email"])}</p></div><img class="portrait" src="assets/portrait.jpg" width="230" height="280" alt="Portrait of Mohamed Sbissi"></section>'
    b += '<div class="quick-facts" aria-label="Selected achievements"><div><strong>ODDO BHF</strong><span>HR data &amp; analytics internship</span></div><div><strong>Power BI + SQL</strong><span>4 report pages / 7 reporting views</span></div><div><strong>GreenOPS AI</strong><span>2nd place / Data Engineer</span></div></div>'
    b += heading("about","Professional summary","Data Engineering / BI / SAP") + f'<p class="summary-text">{E(p["summary"])}</p></section>'
    b += heading("experience","Experience","Personal deliverables, with tools and context") + '<div class="timeline">'
    for x in d["experience"]:
        b += f'<article class="experience"><div class="meta"><p class="company">{E(x["company"])}</p><p class="date">{E(x["date"])}</p><p class="location">{E(x["location"])}</p></div><div><h3>{E(x["role"])}</h3><p class="context">{E(x["context"])}</p><p class="label">My contribution</p>'
        b += bullets(x["contributions"]) if x["contributions"] else f'<p class="review">{E(x["review"])}</p>'
        if x["stack"]: b += '<p class="label">Technologies used</p>' + chips(x["stack"])
        b += '</div></article>'
    b += '</div></section>' + heading("projects","Selected projects","What the team built. What I contributed.")
    b += '<div class="filter-bar" role="group" aria-label="Filter projects">'
    for category in ["All","Data & ML","Competition","Development"]:
        b += f'<button type="button" data-filter="{E(category)}" aria-pressed="{str(category=="All").lower()}">{E(category)}</button>'
    b += '</div><p class="sr-only" id="filter-status" aria-live="polite">5 projects shown</p><div class="projects">'
    for x in d["projects"]:
        extra = " featured" if x["id"] == "urban" else " early" if x["id"] == "edutech" else ""
        b += f'<article class="project{extra}" data-category="{E(x["category"])}" id="project-{x["id"]}"><p class="eyebrow">{E(x["organization"])}</p><h3>{E(x["name"])}</h3><p class="date">{E(x["date"])}</p>'
        if x.get("achievement"): b += f'<p class="award-tag">{E(x["achievement"])}</p>'
        b += f'<p class="label">Team solution / problem</p><p class="context">{E(x["context"])}</p><p class="label">My role</p><p class="role">{E(x["role"])}</p><p class="label">My contribution</p>'
        b += bullets(x["contributions"]) if x["contributions"] else f'<p class="review">{E(x["review"])}</p>'
        if x["stack"]: b += '<p class="label">Tools in my contribution</p>' + chips(x["stack"])
        if x.get("project_stack"): b += '<p class="label">Project stack (team scope)</p>' + chips(x["project_stack"])
        if x.get("confidentiality"): b += f'<p class="date">{E(x["confidentiality"])}</p>'
        if x.get("team"): b += '<p class="label">Team</p><p class="compact">' + E(", ".join(x["team"])) + '</p>'
        if x.get("review") and x["contributions"]: b += f'<details class="review-details"><summary>Contribution evidence &amp; review note</summary><p>{E(x["review"])}</p></details>'
        if x.get("unavailable_url"): b += '<p class="date">Repository access requires confirmation; public link currently unavailable.</p>'
        if x["links"]: b += '<div class="project-links">' + "".join(link(t["url"],t["label"]) for t in x["links"]) + '</div>'
        b += '</article>'
    b += '</div></section>' + heading("skills","Technical skills","Applied tools are separated from coursework") + '<div class="skills">'
    for x in d["skills"]:
        b += f'<article class="skill-group"><h3>{E(x["category"])}</h3><p class="level">{E(x["level"])}</p>{chips(x["items"])}</article>'
    b += '</div></section>' + heading("education","Education")
    for x in d["education"]:
        b += f'<article class="education-item"><h3>{E(x["school"])}</h3><p>{E(x["degree"])}</p><p class="date">{E(x["date"])}</p><p>{E(x["note"])}</p></article>'
    b += '</section><div class="two-up">' + heading("certifications","Certifications") + bullets(d["certifications"]) + '</section>' + heading("awards","Awards &amp; competitions")
    for x in d["awards"]:
        b += f'<article class="education-item"><h3>{E(x["name"])}</h3><p>{E(x["result"])}</p>'
        if x["role"]: b += f'<p class="role">{E(x["role"])}</p>'
        b += f'<p class="date">{E(x["date"])}</p></article>'
    b += '</section></div>' + heading("languages","Languages") + '<p>' + E(" | ".join(x["name"]+" - "+x["level"] for x in d["languages"])) + '</p></section>'
    b += heading("contact","Let us discuss your PFE opportunity")
    b += f'<div class="contact-panel"><h3>{E(p["objective"])}</h3><p>Interested in Data Engineering, Business Intelligence, SAP / ERP, and Data &amp; AI internship opportunities.</p><p>{link("mailto:"+p["email"],p["email"])}<br>{E(p["location"])}</p><div class="actions"><a class="button" href="CV.pdf" download>Download CV</a>{link(p["linkedin"],"LinkedIn")}{link(p["github"],"GitHub")}</div></div><p class="review-links"><a href="cv.html">View printable CV</a> &middot; <a href="FACTS_TO_VERIFY.md">Facts to verify</a></p></section>'
    b += '<section class="section"><details class="review-details"><summary>Additional credentials to review</summary><p>' + E("; ".join(d["legacy_certifications"])) + '</p><p>Certification issuers, dates, and links require confirmation. No unverified credential has been promoted into the CV.</p></details></section>'
    b += '</main><footer class="wrap">Mohamed Sbissi / PFE 2027 &middot; Built from one shared profile source.</footer>'
    return shell(p["name"]+" | Data Engineering, BI & SAP | PFE 2027","assets/styles.css",b,'<script src="assets/portfolio.js" defer></script>')

