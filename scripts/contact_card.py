"""Generate a portable vCard 3.0 with an embedded, resized contact photo."""
import base64,io
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def generate(data):
    p=data['personal']
    image=Image.open(ROOT/'assets/images/portrait.jpg').convert('RGB')
    image.thumbnail((320,320));photo=io.BytesIO();image.save(photo,format='JPEG',quality=82)
    def escape(s):return s.replace('\\','\\\\').replace('\n','\\n').replace(';','\\;').replace(',','\\,')
    first,last=p['name'].split(' ',1)
    lines=['BEGIN:VCARD','VERSION:3.0',f'N:{escape(last)};{escape(first)};;;','FN:'+escape(p['name']),
           'TITLE:'+escape(p['title']),'TEL;TYPE=CELL:'+p['phone_uri'][4:],
           'EMAIL;TYPE=INTERNET,WORK:'+escape(p['email']),'URL:'+p['portfolio'],
           'NOTE:'+escape(p['objective']+' | ERP / Business Intelligence | ESPRIT'),
           'PHOTO;ENCODING=b;TYPE=JPEG:'+base64.b64encode(photo.getvalue()).decode(),'END:VCARD']
    # Fold ASCII lines at 75 octets; continuation whitespace is part of vCard syntax.
    folded=[]
    for line in lines:
        raw=line.encode('utf-8')
        while len(raw)>75:
            folded.append(raw[:75]);raw=b' '+raw[75:]
        folded.append(raw)
    directory=ROOT/'assets/contact';directory.mkdir(exist_ok=True)
    (directory/'Mohamed-Sbissi.vcf').write_bytes(b'\r\n'.join(folded)+b'\r\n')
