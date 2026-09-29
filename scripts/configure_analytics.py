"""Enable collection only after deploying the backend; no credentials in public JS."""
import argparse,json
from pathlib import Path
from urllib.parse import urlsplit
parser=argparse.ArgumentParser();parser.add_argument('endpoint');args=parser.parse_args()
url=urlsplit(args.endpoint)
if url.scheme!='https' or not url.hostname or url.username or url.password or url.query or url.fragment or url.path not in ['', '/']:
    parser.error('Use the deployed HTTPS Worker origin, without credentials, query or path.')
root=Path(__file__).resolve().parents[1]
config={'enabled':True,'endpoint':args.endpoint.rstrip('/')}
(root/'js/analytics-config.js').write_text('window.MS_ANALYTICS='+json.dumps(config)+';\n',encoding='utf-8')
print('Configured public collector URL. Publish js/analytics-config.js to GitHub Pages after reviewing the privacy notice.')
