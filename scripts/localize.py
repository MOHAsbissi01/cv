"""Annotate translated text without replacing links, icons or semantic structure."""
import json,re
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]

def localize(soup):
    soup.head.append(BeautifulSoup('<link rel="stylesheet" href="css/language.css">','html.parser'))
    translations=json.loads((ROOT/'data/translations-fr.json').read_text(encoding='utf-8'))
    strings={}
    for node in list(soup.body.find_all(string=True)):
        text=str(node).strip()
        if not text or node.parent.name in ['script','style','svg']:continue
        french=translations.get(text)
        if french is None:continue
        key='t'+str(len(strings));strings[key]={'en':text,'fr':french}
        if len(node.parent.contents)==1:
            node.parent['data-i18n']=key
        else:
            span=soup.new_tag('span',attrs={'data-i18n':key});span.string=text
            node.replace_with(span)
    for element in soup.select('[aria-label],img[alt],[title]'):
        for attr in ['aria-label','alt','title']:
            text=element.get(attr)
            if text in translations:
                key='t'+str(len(strings));strings[key]={'en':text,'fr':translations[text]}
                element['data-i18n-'+attr]=key
    popup=BeautifulSoup('''<dialog class="language-dialog" aria-labelledby="language-title" aria-describedby="language-description"><div class="welcome-mark" aria-hidden="true">MS</div><p class="welcome-eyebrow">MOHAMED SBISSI / PORTFOLIO</p><h2 id="language-title">Hello. <span>Bonjour.</span></h2><p id="language-description">Which language would you like to explore?<br><span lang="fr">Dans quelle langue souhaitez-vous découvrir mon portfolio ?</span></p><div class="language-choices"><button type="button" data-choose-language="en" autofocus><span class="language-code" aria-hidden="true">EN</span><strong lang="en">English</strong><span aria-hidden="true">↗</span></button><button type="button" data-choose-language="fr"><span class="language-code" aria-hidden="true">FR</span><strong lang="fr">Français</strong><span aria-hidden="true">↗</span></button></div><p class="language-hint">You can switch anytime. <span lang="fr">Vous pouvez changer à tout moment.</span></p></dialog>''','html.parser')
    soup.body.append(popup)
    button=soup.new_tag('button',attrs={'class':'locale-toggle','type':'button','aria-label':'Choose language / Choisir la langue'})
    button.string='EN / FR';soup.select_one('nav').append(button)
    script=soup.new_tag('script',attrs={'src':'js/language.js','defer':''})
    soup.select_one('script[src="js/main.js"]').insert_before(script)
    payload=soup.new_tag('script',attrs={'type':'application/json','id':'portfolio-translations'})
    payload.string=json.dumps(strings,ensure_ascii=True).replace('</','<\\/')
    script.insert_before(payload)
    return soup
