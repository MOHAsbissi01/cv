"use strict";
(() => {
  const config=window.MS_ANALYTICS || {enabled:false};
  const fr=()=>document.documentElement.lang==='fr';
  const say=(en,french)=>fr()?french:en;
  const dialog=document.querySelector('.share-dialog');
  const shareURL=document.querySelector('link[rel="canonical"]').href;
  const output=document.querySelector('.share-status');
  let shareFocus;
  document.querySelector('.share-button').addEventListener('click',async()=>{
    if(navigator.share){
      try{await navigator.share({title:'Mohamed Sbissi — PFE 2027',url:shareURL});return;}
      catch(error){if(error.name==='AbortError')return;}
    }
    shareFocus=document.activeElement;document.querySelector('#share-url').value=shareURL;
    output.textContent='';dialog.showModal();
  });
  document.querySelector('.copy-link').addEventListener('click',async()=>{
    try{await navigator.clipboard.writeText(shareURL);output.textContent=say('Link copied.','Lien copié.');}
    catch(_){document.querySelector('#share-url').select();output.textContent=say('Select and copy the link.','Sélectionnez et copiez le lien.');}
  });
  document.querySelector('.close-share').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('close',()=>shareFocus?.focus({preventScroll:true}));
  // Telemetry begins only after explicit opt-in. No contact details or URLs are sent.
  const banner=document.querySelector('.analytics-consent');
  const status=document.querySelector('.privacy-status');
  const choiceKey='ms-statistics-choice-v1';
  const sessionKey='ms-statistics-visit-v1';
  const blocked=()=>navigator.globalPrivacyControl===true || navigator.doNotTrack==='1';
  const ready=()=>config.enabled && /^https:\/\//.test(config.endpoint) && !blocked();
  let allowed=false,id=null,timer=null,lastActivity=performance.now(),lastTick=performance.now(),active=0,events=[],sequence=0,visible=document.visibilityState==='visible';
  const endpoint=String(config.endpoint||'').replace(/\/$/,'');
  function load(store,key){try{return JSON.parse(store.getItem(key));}catch(_){return null;}}
  function save(store,key,value){try{store.setItem(key,JSON.stringify(value));}catch(_){}}
  function elapsed(){
    const now=performance.now();
    if(allowed && visible && now-lastActivity<60000)active+=Math.min(5000,now-lastTick);
    lastTick=now;
  }
  async function flush(){
    if(!allowed || !id || !ready())return;
    const sentEvents=events.splice(0,20),sentActive=Math.round(active);active=0;
    const payload={visit:id,seq:++sequence,active_ms:sentActive,events:sentEvents,consent:true};
    try{const response=await fetch(endpoint+'/collect',{method:'POST',mode:'cors',credentials:'omit',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),keepalive:true});
      if(!response.ok)throw new Error('collector unavailable');
    }catch(_){/* Counts may be lost offline. Never retry after withdrawal. */}
  }
  function start(){
    if(!ready())return;
    const prior=load(sessionStorage,sessionKey);
    id=prior?.id || crypto.randomUUID();sequence=prior?.seq || 0;
    save(sessionStorage,sessionKey,{id,seq:sequence});allowed=true;lastTick=performance.now();lastActivity=lastTick;
    events=[{action:'visit_start'}];flush();
    timer=setInterval(()=>{elapsed();if(events.length){flush();save(sessionStorage,sessionKey,{id,seq:sequence});}},5000);
    // Separate heartbeat; hidden tabs and idle periods contribute no active time.
    heartbeat=setInterval(()=>{flush();save(sessionStorage,sessionKey,{id,seq:sequence});},15000);
  }
  let heartbeat;
  function stop(){allowed=false;clearInterval(timer);clearInterval(heartbeat);active=0;events=[];}
  function choose(value){
    stop();save(localStorage,choiceKey,{value,at:Date.now()});banner.hidden=true;
    if(value==='yes')start();
    document.querySelector('.delete-visit').hidden=!load(sessionStorage,sessionKey)?.id;
  }
  banner.querySelectorAll('[data-consent]').forEach(button=>button.addEventListener('click',()=>choose(button.dataset.consent)));
  document.querySelector('.privacy-settings').addEventListener('click',()=>{
    banner.hidden=false;
    document.querySelector('.delete-visit').hidden=!load(sessionStorage,sessionKey)?.id;
    status.textContent=ready()?'':say('Optional statistics are currently disabled.','Les statistiques facultatives sont actuellement désactivées.');
  });
  document.querySelector('.delete-visit').addEventListener('click',async()=>{
    const visit=load(sessionStorage,sessionKey)?.id;stop();save(localStorage,choiceKey,{value:'no',at:Date.now()});
    if(!visit || !config.enabled)return;
    try{const response=await fetch(endpoint+'/erase',{method:'POST',credentials:'omit',headers:{'Content-Type':'application/json'},body:JSON.stringify({visit})});
      if(!response.ok)throw new Error();
      try{sessionStorage.removeItem(sessionKey);}catch(_){}
      id=null;status.textContent=say('This visit’s data was deleted. Statistics are off.','Les données de cette visite ont été supprimées. Les statistiques sont désactivées.');
      document.querySelector('.delete-visit').hidden=true;
    }catch(_){status.textContent=say('Deletion failed. Statistics are off; please retry or contact me.','Échec de la suppression. Les statistiques sont désactivées ; réessayez ou contactez-moi.');}
  });
  ['pointerdown','keydown','scroll'].forEach(event=>window.addEventListener(event,()=>{lastActivity=performance.now();},{passive:true}));
  document.addEventListener('click',event=>{
    if(!allowed)return;
    const target=event.target.closest('[data-action]');
    if(target && events.length<20)events.push({action:target.dataset.action});
  });
  document.addEventListener('visibilitychange',()=>{elapsed();visible=document.visibilityState==='visible';lastTick=performance.now();if(!visible)flush();});
  window.addEventListener('pagehide',()=>{elapsed();save(sessionStorage,sessionKey,{id,seq:sequence+1});flush();});
  const previous=load(localStorage,choiceKey);
  if(ready()){
    if(previous && Date.now()-previous.at<180*86400000){if(previous.value==='yes')start();}
    else banner.hidden=false;
  }
})();
