from bs4 import BeautifulSoup
def engagement(soup):
    def frag(s):return BeautifulSoup(s,'html.parser')
    soup.head.append(frag('<link rel="stylesheet" href="css/engagement.css">'))
    for phone in soup.select('a[href="tel:+21629785051"]'):
        phone['href']='assets/contact/Mohamed-Sbissi.vcf';phone['type']='text/vcard';phone['data-action']='save_contact'
        phone['title']='Save contact'
        phone.insert_after(frag('<span class="phone-call"> · <a href="tel:+21629785051" data-action="call">Call</a></span>'))
    soup.select_one('.contact-panel>div').append(frag('<div class="engagement-actions"><a href="assets/contact/Mohamed-Sbissi.vcf" type="text/vcard" data-action="save_contact">Save contact <span aria-hidden="true">＋</span></a><button type="button" class="share-button" data-action="share_open">Share portfolio <span aria-hidden="true">↗</span></button></div>'))
    for a in soup.select('a[href="assets/cv/CV-2.pdf"]'):a['data-action']='download_cv'
    for a in soup.select('a[href^="mailto:"]'):a['data-action']='email'
    for a in soup.select('a[href*="linkedin.com"]'):a['data-action']='linkedin'
    for a in soup.select('.project-links a'):a['data-action']='project_'+a.find_parent('article')['id'].replace('project-','')
    soup.select_one('.footer-inner>div').append(frag('<a href="privacy.html">Privacy</a><button class="privacy-settings" type="button">Privacy choices</button>'))
    soup.body.append(frag('''<dialog class="share-dialog" aria-labelledby="share-title"><h2 id="share-title">Share this portfolio</h2><p>Send this link to your team.</p><label for="share-url">Portfolio link</label><input id="share-url" type="url" readonly><div class="dialog-actions"><button class="copy-link" type="button">Copy link</button><button class="close-share" type="button">Close</button></div><p class="share-status" role="status"></p></dialog><aside class="analytics-consent" hidden aria-labelledby="consent-title"><h3 id="consent-title">Optional visit statistics</h3><p>May I measure button interactions and active viewing time using a random visit code? No name, email or fingerprint is collected. Data is kept for 30 days. Your choice does not affect access.</p><a href="privacy.html">Privacy details</a><div class="consent-actions"><button type="button" data-consent="yes">Allow statistics</button><button type="button" data-consent="no">No thanks</button></div><button class="delete-visit" type="button" hidden>Delete this visit’s data</button><p class="privacy-status" role="status"></p></aside>'''))
    for src in ['js/analytics-config.js','js/engagement.js']:
        soup.body.append(frag(f'<script src="{src}" defer></script>'))
    return soup
