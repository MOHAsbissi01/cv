const actions=new Set(['visit_start','download_cv','save_contact','call','email','linkedin','share_open','project_urban','project_business','project_superstore','filter_all','filter_data','filter_development']);
const uuid=/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const days30=30*86400000;
function response(data,status=200,origin=null){
  const headers={'Content-Type':'application/json','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Vary':'Origin'};
  if(origin)headers['Access-Control-Allow-Origin']=origin;
  return new Response(JSON.stringify(data),{status,headers});
}
async function authorized(request,env){
  if(!env.ADMIN_TOKEN || env.ADMIN_TOKEN.length<32)return false;
  const token=request.headers.get('Authorization')||'';
  const a=new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(token)));
  const b=new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode('Bearer '+env.ADMIN_TOKEN)));
  let diff=0;for(let i=0;i<a.length;i++)diff|=a[i]^b[i];return diff===0;
}
export async function prune(db,now=Date.now()){
  await db.batch([db.prepare('DELETE FROM events WHERE at < ?').bind(now-days30),db.prepare('DELETE FROM visits WHERE updated < ?').bind(now-days30),db.prepare('DELETE FROM erased WHERE until < ?').bind(now)]);
}
export default {
  async scheduled(_event,env){await prune(env.DB);},
  async fetch(request,env){
    const url=new URL(request.url),origin=request.headers.get('Origin');
    const allowed=origin===env.PORTFOLIO_ORIGIN || origin===url.origin;
    const cors=allowed?origin:null;
    if(url.pathname.startsWith('/api/admin')){
      if(!await authorized(request,env))return response({error:'Unauthorized'},401);
      if(url.pathname!='/api/admin/summary' || request.method!=='GET')return response({error:'Not found'},404);
      await prune(env.DB);
      const totals=await env.DB.prepare('SELECT COUNT(*) AS visits, COALESCE(SUM(active_ms),0) AS active_ms FROM visits').first();
      const visits=await env.DB.prepare('SELECT * FROM visits ORDER BY updated DESC LIMIT 200').all();
      const events=await env.DB.prepare('SELECT visit, at, action FROM events ORDER BY id DESC LIMIT 500').all();
      const buttons=await env.DB.prepare('SELECT action, COUNT(*) AS count FROM events GROUP BY action ORDER BY count DESC').all();
      return response({totals,visits:visits.results,events:events.results,buttons:buttons.results,as_of:Date.now(),retention_days:30});
    }
    if(url.pathname==='/collect' || url.pathname==='/erase'){
      if(!allowed)return response({error:'Origin denied'},403);
      if(request.method==='OPTIONS')return new Response(null,{status:204,headers:{'Access-Control-Allow-Origin':origin,'Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type','Access-Control-Max-Age':'600','Vary':'Origin'}});
      if(request.method!=='POST')return response({error:'Method denied'},405,cors);
      if(!request.headers.get('Content-Type')?.startsWith('application/json'))return response({error:'JSON required'},415,cors);
      if(Number(request.headers.get('Content-Length'))>8192)return response({error:'Too large'},413,cors);
      const reader=request.body?.getReader(),chunks=[];let size=0;
      if(reader){while(true){const {done,value}=await reader.read();if(done)break;size+=value.byteLength;if(size>8192){await reader.cancel();return response({error:'Too large'},413,cors);}chunks.push(value);}}
      const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}
      const raw=new TextDecoder().decode(bytes);
      let data;try{data=JSON.parse(raw);}catch(_){return response({error:'Invalid JSON'},400,cors);}
      if(!data || typeof data!=='object' || Array.isArray(data))return response({error:'Invalid object'},400,cors);
      if(!uuid.test(data.visit||''))return response({error:'Invalid visit'},400,cors);
      const now=Date.now();
      if(url.pathname==='/erase'){
        await env.DB.batch([env.DB.prepare('DELETE FROM events WHERE visit=?').bind(data.visit),env.DB.prepare('DELETE FROM visits WHERE id=?').bind(data.visit),env.DB.prepare('INSERT OR REPLACE INTO erased(id,until) VALUES(?,?)').bind(data.visit,now+days30)]);
        return response({deleted:true},200,cors);
      }
      if(data.consent!==true || !Number.isSafeInteger(data.seq) || data.seq<1 || data.seq>100000 || !Number.isFinite(data.active_ms) || data.active_ms<0 || !Array.isArray(data.events) || data.events.length>20 || data.events.some(e=>!e || typeof e!=='object' || !actions.has(e.action) || Object.keys(e).some(k=>k!=='action')) || Object.keys(data).some(k=>!['visit','seq','active_ms','events','consent'].includes(k)))return response({error:'Invalid event'},400,cors);
      if(await env.DB.prepare('SELECT id FROM erased WHERE id=? AND until>?').bind(data.visit,now).first())return response({ignored:true},200,cors);
      const old=await env.DB.prepare('SELECT * FROM visits WHERE id=?').bind(data.visit).first();
      if(old && data.seq<=old.seq)return response({duplicate:true},200,cors);
      const increment=old?Math.max(0,Math.min(Math.round(data.active_ms),30000,now-old.updated+1000)):0;
      const statements=[env.DB.prepare('INSERT INTO visits(id,started,updated,active_ms,seq) SELECT ?,?,?,?,? WHERE NOT EXISTS(SELECT 1 FROM erased WHERE id=? AND until>?) ON CONFLICT(id) DO UPDATE SET updated=excluded.updated,active_ms=visits.active_ms+excluded.active_ms,seq=excluded.seq WHERE excluded.seq>visits.seq').bind(data.visit,now,now,increment,data.seq,data.visit,now)];
      data.events.forEach((event,position)=>statements.push(env.DB.prepare('INSERT OR IGNORE INTO events(visit,at,action,seq,position) SELECT ?,?,?,?,? WHERE EXISTS(SELECT 1 FROM visits WHERE id=? AND seq=?)').bind(data.visit,now,event.action,data.seq,position,data.visit,data.seq)));
      await env.DB.batch(statements);
      return response({ok:true},200,cors);
    }
    if(!env.ASSETS)return response({error:'Not found'},404);
    const asset=await env.ASSETS.fetch(request);
    const headers=new Headers(asset.headers);
    headers.set('X-Content-Type-Options','nosniff');headers.set('Referrer-Policy','no-referrer');
    headers.set('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'");
    headers.set('Cache-Control','no-store');
    return new Response(asset.body,{status:asset.status,headers});
  }
};
