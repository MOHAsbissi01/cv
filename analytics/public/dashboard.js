"use strict";
let token='',snapshot=null,poll=null,busy=false,demo=false;
const el=id=>document.getElementById(id);
const names={visit_start:'Visit started',download_cv:'CV link',save_contact:'Contact card',call:'Call',email:'Email',linkedin:'LinkedIn',share_open:'Share requested',project_urban:'Mobility repository',project_business:'Business ML repository',project_superstore:'Streamlit repository',filter_all:'All projects',filter_data:'Data projects',filter_development:'Development projects'};
const time=ms=>{const s=Math.round(ms/1000);return s>=60?Math.floor(s/60)+'m '+s%60+'s':s+'s';};
const date=value=>new Date(value).toLocaleString();
function text(tag,value){const e=document.createElement(tag);e.textContent=value;return e;}
function render(data){
  snapshot=data;el('visits').textContent=data.totals.visits;el('active').textContent=time(data.totals.active_ms);
  el('average').textContent=time(data.totals.visits?data.totals.active_ms/data.totals.visits:0);
  el('downloads').textContent=data.buttons.find(b=>b.action==='download_cv')?.count||0;
  el('updated').textContent='Updated '+date(data.as_of)+' · Refreshes every 10s while visible';
  el('buttons').replaceChildren();
  const max=Math.max(1,...data.buttons.filter(b=>b.action!=='visit_start').map(b=>b.count));
  data.buttons.filter(b=>b.action!=='visit_start').forEach(item=>{
    const row=text('div','');row.className='signal';const line=text('div','');line.append(text('span',names[item.action]||item.action),text('strong',item.count));
    const bar=text('div','');bar.className='bar';bar.style.width=(item.count/max*100)+'%';row.append(line,bar);el('buttons').append(row);
  });
  if(!el('buttons').children.length)el('buttons').append(text('p','No interaction events yet.'));
  el('events').replaceChildren();
  data.events.slice(0,40).forEach(event=>{const row=text('div',names[event.action]||event.action);row.className='event';row.append(text('small',event.visit.slice(0,8)+' · '+date(event.at)));el('events').append(row);});
  el('sessions').replaceChildren();
  data.visits.forEach(visit=>{
    const row=document.createElement('tr'),cell=document.createElement('td'),button=text('button',visit.id.slice(0,8));
    button.addEventListener('click',()=>{
      el('timeline').replaceChildren(text('h2','Visit '+visit.id.slice(0,8)));
      const events=data.events.filter(e=>e.visit===visit.id).reverse();
      events.forEach(e=>el('timeline').append(text('p',date(e.at)+' — '+(names[e.action]||e.action))));
      if(!events.length)el('timeline').append(text('p','No events in the latest 500-event window.'));
    });cell.append(button);row.append(cell,text('td',date(visit.started)),text('td',time(visit.active_ms)),text('td',date(visit.updated)));el('sessions').append(row);
  });
}
async function refresh(){
  if(!token || busy || document.hidden)return;busy=true;const key=token;
  try{const response=await fetch('/api/admin/summary',{headers:{Authorization:'Bearer '+key},cache:'no-store'});
    if(!response.ok)throw new Error(response.status===401?'Invalid private token.':'Dashboard unavailable.');
    const data=await response.json();if(token!==key)return;
    demo=false;el('demo-notice').hidden=true;el('logout').textContent='Log out';
    render(data);el('dashboard').hidden=false;el('login').hidden=true;el('status').textContent='';el('connection').textContent='Private / connected';
  }catch(error){if(token===key)el('status').textContent=error.message;}finally{busy=false;}
}
el('login').addEventListener('submit',event=>{event.preventDefault();token=el('token').value.trim();el('token').value='';refresh();clearInterval(poll);poll=setInterval(refresh,10000);});
el('refresh').addEventListener('click',()=>demo?showPrototype():refresh());
el('logout').addEventListener('click',()=>{token='';snapshot=null;demo=false;clearInterval(poll);el('dashboard').hidden=true;el('demo-notice').hidden=true;el('login').hidden=false;el('status').textContent='';el('connection').textContent='Locked';['sessions','events','buttons','timeline'].forEach(id=>el(id).replaceChildren());});
el('export').addEventListener('click',()=>{if(!snapshot)return;const blob=new Blob([JSON.stringify(snapshot,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=demo?'prototype-sample-data.json':'portfolio-statistics.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh();});

function showPrototype(){
  token='';demo=true;clearInterval(poll);
  const now=Date.now();
  const visits=[
    {id:'example1-visit',started:now-600000,updated:now-300000,active_ms:185000},
    {id:'example2-visit',started:now-240000,updated:now-90000,active_ms:97000},
    {id:'example3-visit',started:now-120000,updated:now-30000,active_ms:45000}
  ];
  const actions=[['visit_start','download_cv','save_contact','project_urban'],['visit_start','share_open','download_cv'],['visit_start','linkedin']];
  const events=visits.flatMap((visit,index)=>actions[index].map((action,n)=>({visit:visit.id,at:visit.started+n*15000,action}))).sort((a,b)=>b.at-a.at);
  const counts={};events.forEach(event=>counts[event.action]=(counts[event.action]||0)+1);
  render({sample_data:true,totals:{visits:3,active_ms:327000},visits,events,buttons:Object.entries(counts).map(([action,count])=>({action,count})),as_of:now});
  el('dashboard').hidden=false;el('login').hidden=true;el('demo-notice').hidden=false;el('status').textContent='';
  el('connection').textContent='Prototype / sample data';el('updated').textContent='Example data only — no backend connection or visitor tracking';el('logout').textContent='Exit prototype';
}
el('view-prototype').addEventListener('click',showPrototype);
