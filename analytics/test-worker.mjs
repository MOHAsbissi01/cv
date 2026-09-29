import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync} from 'node:fs';
import worker,{prune} from './worker.mjs';
const sqlite=new DatabaseSync(':memory:');sqlite.exec(readFileSync(new URL('./schema.sql',import.meta.url),'utf8'));
class Statement{
  constructor(sql,args=[]){this.sql=sql;this.args=args;}
  bind(...args){return new Statement(this.sql,args);}
  async first(){return sqlite.prepare(this.sql).get(...this.args)||null;}
  async all(){return {results:sqlite.prepare(this.sql).all(...this.args)};}
  async run(){return sqlite.prepare(this.sql).run(...this.args);}
}
const db={prepare:sql=>new Statement(sql),async batch(statements){sqlite.exec('BEGIN');try{for(const s of statements)await s.run();sqlite.exec('COMMIT');}catch(e){sqlite.exec('ROLLBACK');throw e;}}};
const env={DB:db,ADMIN_TOKEN:'test-only-token-never-use-in-production-123456',PORTFOLIO_ORIGIN:'https://mohasbissi01.github.io'};
const visit='22222222-2222-4222-8222-222222222222';
async function send(path,body,origin=env.PORTFOLIO_ORIGIN){return worker.fetch(new Request('https://collector.test'+path,{method:'POST',headers:{Origin:origin,'Content-Type':'application/json'},body:JSON.stringify(body)}),env);}
const packet={visit,seq:1,active_ms:0,events:[{action:'visit_start'}],consent:true};
assert.equal((await send('/collect',packet,'https://evil.test')).status,403);
assert.equal((await send('/collect',null)).status,400);
assert.equal((await send('/collect',{...packet,events:[null]})).status,400);
assert.equal((await send('/collect',{...packet,extra:'x'.repeat(9000)})).status,413);
assert.equal((await send('/collect',{...packet,consent:false})).status,400);
assert.equal((await send('/collect',{...packet,email:'someone@example.com'})).status,400);
assert.equal((await send('/collect',{...packet,events:[{action:'https://private.example'}]})).status,400);
assert.equal((await send('/collect',packet)).status,200);
assert.equal((await send('/collect',packet)).status,200);
assert.equal(sqlite.prepare('SELECT COUNT(*) AS n FROM events').get().n,1);
sqlite.prepare('UPDATE visits SET updated=?').run(Date.now()-20000);
assert.equal((await send('/collect',{...packet,seq:2,active_ms:15000,events:[{action:'download_cv'}]})).status,200);
assert.equal(sqlite.prepare('SELECT active_ms FROM visits').get().active_ms,15000);
const unauth=await worker.fetch(new Request('https://collector.test/api/admin/summary'),env);assert.equal(unauth.status,401);
const summary=await worker.fetch(new Request('https://collector.test/api/admin/summary',{headers:{Authorization:'Bearer '+env.ADMIN_TOKEN}}),env);
assert.equal(summary.status,200);const data=await summary.json();assert.equal(data.totals.visits,1);assert.equal(data.events.length,2);
assert(!JSON.stringify(data).includes('email'));assert(!JSON.stringify(data).includes('ip_address'));
assert.equal((await send('/erase',{visit})).status,200);
await send('/collect',{...packet,seq:3});assert.equal(sqlite.prepare('SELECT COUNT(*) AS n FROM visits').get().n,0);
sqlite.prepare('INSERT INTO visits(id,started,updated) VALUES(?,?,?)').run('expired',1,1);
await prune(db);assert.equal(sqlite.prepare('SELECT COUNT(*) AS n FROM visits').get().n,0);
assert.deepEqual(sqlite.prepare('PRAGMA table_info(visits)').all().map(c=>c.name),['id','started','updated','active_ms','seq','consent_version']);
console.log('Worker tests passed: explicit consent, exact CORS, payload allowlist, SQL storage, duplicates, active time, private authorization, erasure tombstone and 30-day expiry.');
sqlite.close();
