"""Read-only checks of the published host; no credentials or private data."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import urllib.error
import urllib.request

base='https://vamos-api.onrender.com'
out=Path(sys.argv[1])
out.mkdir(parents=True,exist_ok=True)
results=[]
for route in ['/admin/revision-sofia/','/admin/','/api/v1/health']:
    request=urllib.request.Request(base+route,headers={'User-Agent':'Vamos-Sofia-Security-Verification/1.0'})
    try:
        response=urllib.request.urlopen(request,timeout=90)
    except urllib.error.HTTPError as error:response=error
    with response:
        headers=dict(response.headers.items())
        hsts=response.headers.get('Strict-Transport-Security','')
        results.append({'url':base+route,'status':response.code,'headers':headers,'hsts':hsts,'pass':any(part.strip()=='max-age=31536000' for part in hsts.split(';'))})
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None
try:
    response=urllib.request.build_opener(NoRedirect).open('http://vamos-api.onrender.com/admin/revision-sofia/',timeout=30)
except urllib.error.HTTPError as error:response=error
with response:
    location=response.headers.get('Location','')
    redirect={'status':response.code,'location':location,'pass':response.code in [301,302,307,308] and location.startswith(base+'/')}
report={'generatedAtUtc':datetime.now(timezone.utc).isoformat(),'https':results,'httpRedirect':redirect}
(out/'01-hsts-publicado.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'hsts':[{'url':r['url'],'pass':r['pass']} for r in results],'httpRedirect':redirect},ensure_ascii=False,indent=2))
if not all(r['pass'] for r in results) or not redirect['pass']:raise SystemExit('HSTS o redirección HTTPS pendiente en el servidor publicado')
