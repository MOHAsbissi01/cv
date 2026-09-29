"""Portfolio presentation; illustrations describe workflows, not measured outputs."""
from bs4 import BeautifulSoup
from localize import localize
from engagement import engagement

def polish(soup, data):
    def frag(markup): return BeautifulSoup(markup, 'html.parser')
    soup.head.append(frag('<link rel="stylesheet" href="css/premium.css">'))
    soup.head.append(frag('<link rel="icon" href="assets/images/favicon.svg" type="image/svg+xml">'))
    soup.body.insert(0,frag('<div class="reading-progress" aria-hidden="true"></div>'))
    hero=soup.select_one('.hero')
    zone=soup.new_tag('div',attrs={'class':'hero-zone'})
    hero.insert_before(zone);zone.append(hero.extract())
    zone.append(soup.select_one('.quick-facts').extract())
    hero.select_one('.eyebrow').string='FINAL-YEAR COMPUTER ENGINEERING STUDENT · TUNIS, TUNISIA'
    hero.select_one('.visual-note').decompose()
    facts=soup.select_one('.quick-facts');facts.clear()
    for name,role,evidence in [('ODDO BHF','Software Development Factory Intern','12 HR domains · 7 SQL views · 25 DAX measures'),('Ooredoo Tunisie','Software Engineering Intern','B2B platform · Power BI · ETL'),('GreenOPS AI','2nd Place · Team award','2,000 TND Award')]:
        facts.append(frag(f'<div><strong>{name}</strong><span>{role}</span><small>{evidence}</small></div>'))
    oddo=soup.select_one('#experience-oddo .meta')
    oddo.append(frag('<div class="experience-signature"><span>DATA → BI → APPLICATION</span><strong>Banking.<br>Enterprise engineering.</strong></div>'))
    headings={'experience':('Enterprise experience','Banking and telecom work in data, BI and application integration.'),'projects':('Selected projects','Data, machine learning and business applications.'),'skills':('Technical skills','Applied tools and current coursework.'),'education':('Education','Final-year engineering / ERP & Business Intelligence'),'contact':("Let's Connect",'PFE 2027 / Data Engineering, BI & SAP')}
    for id,(title,subtitle) in headings.items():
        section=soup.select_one('#'+id);section.select_one('.section-heading h2').string=title
        section.select_one('.section-heading p').string=subtitle
    for a in soup.select('a[href="assets/cv/CV.pdf"]'):
        a['href']='assets/cv/CV-2.pdf';a['download']='Mohamed_Sbissi_CV.pdf'
    for a in soup.select('a[href="cv.html"]'):a['href']='cv-2.html'
    contact=soup.select_one('.contact-panel .actions')
    contact.insert(0,frag('<a class="button contact-email" href="mailto:sbissi.mohamed@esprit.tn">Get in touch <span aria-hidden="true">↗</span></a>'))
    soup.select_one('#contact .contact-panel p').string="I'm seeking a PFE 2027 opportunity in Data Engineering, Business Intelligence, ERP/SAP or related enterprise technology roles."
    footer=soup.select_one('.footer-inner')
    footer.append(frag('<a class="back-top" href="#main" aria-label="Back to top">↑</a>'))
    personal=data['personal']
    if personal.get('phone'):
        for container in [soup.select_one('.hero-meta'),soup.select_one('.contact-panel a[href^="mailto:"]').parent]:
            container.append(soup.new_tag('br'))
            phone=soup.new_tag('a',attrs={'href':personal['phone_uri']})
            phone.string=personal['phone'];container.append(phone)
    return localize(engagement(soup))
