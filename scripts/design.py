"""Portfolio presentation; illustrations describe workflows, not measured outputs."""
from bs4 import BeautifulSoup
from localize import localize

def polish(soup):
    def frag(markup): return BeautifulSoup(markup, 'html.parser')
    soup.head.append(frag('<link rel="stylesheet" href="css/premium.css">'))
    soup.head.append(frag('<link rel="icon" href="assets/images/favicon.svg" type="image/svg+xml">'))
    soup.body.insert(0,frag('<div class="reading-progress" aria-hidden="true"></div>'))
    hero=soup.select_one('.hero')
    zone=soup.new_tag('div',attrs={'class':'hero-zone'})
    hero.insert_before(zone);zone.append(hero.extract())
    zone.append(soup.select_one('.quick-facts').extract())
    hero.select_one('.eyebrow').string='DATA ENGINEERING / BUSINESS INTELLIGENCE'
    hero.select_one('.hero-intro').string='From raw data to decisions that matter. I build reliable pipelines, clear analytics and the applications that connect them.'
    hero.select_one('.hero-visual').append(frag('''<div class="signal-panel" aria-label="My engineering focus"><div class="signal-heading"><span>THE WORKFLOW</span><span>01 — 03</span></div><div class="signal-flow"><span><i aria-hidden="true">01</i>Prepare</span><b aria-hidden="true">→</b><span><i aria-hidden="true">02</i>Connect</span><b aria-hidden="true">→</b><span><i aria-hidden="true">03</i>Explain</span></div></div>'''))
    hero.select_one('.visual-note').decompose()
    hero.select_one('.hero-meta').insert_after(frag('<a class="explore-link" href="#experience">Explore my work <span aria-hidden="true">↓</span></a>'))
    facts=soup.select_one('.quick-facts');facts.clear()
    for number,label,context in [('12','HR data domains','ODDO BHF / PostgreSQL'),('25','DAX measures','ODDO BHF / Power BI'),('10','Analytics endpoints','ODDO BHF / .NET'),('2nd','GreenOPS AI','Team award / 2,000 TND')]:
        facts.append(frag(f'<div><strong>{number}</strong><span>{label}</span><small>{context}</small></div>'))
    oddo=soup.select_one('#experience-oddo .meta')
    oddo.append(frag('<div class="experience-signature"><span>DATA → BI → APPLICATION</span><strong>Banking.<br>Enterprise engineering.</strong></div>'))
    headings={'experience':('Built in the real world.','Banking and telecom experience. Data preparation, analytics and application integration.'),'projects':('Ideas, made tangible.','Selected work in data, machine learning and business applications.'),'skills':('A connected toolkit.','Applied engineering, academic projects and ongoing learning.'),'education':('Learning with intention.','Final-year engineering / ERP & Business Intelligence'),'contact':('Let’s build what’s next.','PFE 2027 / Data Engineering, BI & SAP')}
    for id,(title,subtitle) in headings.items():
        section=soup.select_one('#'+id);section.select_one('.section-heading h2').string=title
        section.select_one('.section-heading p').string=subtitle
    # Decorative, deliberately unnumbered concept diagrams; no fabricated data.
    paths={
        'urban':'<path d="M25 68H122L162 28H238L284 68H355M25 120H116L158 160H239L282 120H355M122 68L158 160M238 28L282 120"/><g><circle cx="25" cy="68" r="5"/><circle cx="122" cy="68" r="7"/><circle cx="162" cy="28" r="5"/><circle cx="238" cy="28" r="5"/><circle cx="284" cy="68" r="7"/><circle cx="355" cy="68" r="5"/><circle cx="25" cy="120" r="5"/><circle cx="116" cy="120" r="5"/><circle cx="158" cy="160" r="7"/><circle cx="239" cy="160" r="5"/><circle cx="282" cy="120" r="7"/><circle cx="355" cy="120" r="5"/></g>',
        'business':'<path d="M30 155H350M30 35V155M42 130L98 111L154 122L210 76L266 87L330 38"/><path class="secondary-line" d="M42 145L98 137L154 103L210 113L266 65L330 61"/><circle cx="210" cy="76" r="6"/><circle cx="330" cy="38" r="6"/>',
        'superstore':'<rect x="30" y="26" width="320" height="145" rx="9"/><path d="M30 55H350M52 40H75M86 40H109M220 78V149M267 98V149M314 68V149"/><path class="secondary-line" d="M51 87H150M51 107H130M51 127H165"/>',
        'edutech':'<path d="M130 45L72 96L130 145M250 45L308 96L250 145M216 31L169 159"/>'}
    labels={'urban':'Mobility / Connected intelligence','business':'Business / Predictive analysis','superstore':'Application / Explainable outputs','edutech':'Development / Platform foundations'}
    for id,paths_markup in paths.items():
        card=soup.select_one('#project-'+id)
        card.insert(0,frag(f'<div class="project-art art-{id}" aria-hidden="true"><span>{labels[id]}</span><svg viewBox="0 0 380 190" fill="none" xmlns="http://www.w3.org/2000/svg">{paths_markup}</svg><small>WORKFLOW CONCEPT</small></div>'))
        if id=='urban':
            inner=soup.new_tag('div',attrs={'class':'project-copy'})
            for node in list(card.contents)[1:]:inner.append(node.extract())
            card.append(inner)
    for a in soup.select('a[href="assets/cv/CV.pdf"]'):
        a['href']='assets/cv/CV-2.pdf';a['download']='Mohamed-Sbissi-CV-2.pdf'
    for a in soup.select('a[href="cv.html"]'):a['href']='cv-2.html'
    contact=soup.select_one('.contact-panel .actions')
    contact.insert(0,frag('<a class="button contact-email" href="mailto:sbissi.mohamed@esprit.tn">Get in touch <span aria-hidden="true">↗</span></a>'))
    footer=soup.select_one('.footer-inner')
    footer.append(frag('<a class="back-top" href="#main" aria-label="Back to top">↑</a>'))
    return localize(soup)
