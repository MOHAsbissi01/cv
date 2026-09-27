"use strict";
(() => {
  const dialog=document.querySelector('.language-dialog');
  const dictionary=JSON.parse(document.querySelector('#portfolio-translations').textContent);
  const storageKey='ms-portfolio-language';
  let current='en';
  let returnFocus;
  function applyLanguage(language){
    current=language==='fr'?'fr':'en';
    document.documentElement.lang=current;
    document.querySelectorAll('[data-i18n]').forEach(element=>{
      element.textContent=dictionary[element.dataset.i18n][current];
    });
    ['aria-label','alt'].forEach(attribute=>{
      document.querySelectorAll(`[data-i18n-${attribute}]`).forEach(element=>{
        element.setAttribute(attribute,dictionary[element.getAttribute(`data-i18n-${attribute}`)][current]);
      });
    });
    document.querySelector('.locale-toggle').textContent=current.toUpperCase()+' / '+(current==='en'?'FR':'EN');
    // The approved download remains the original English CV in both languages.
    document.querySelectorAll('a[download]').forEach(a=>{
      a.title=current==='fr'?'CV en anglais — une page':'English CV — one page';
    });
    updateFilterStatus();
    document.dispatchEvent(new CustomEvent('portfolio:language',{detail:current}));
  }
  function updateFilterStatus(){
    const count=document.querySelectorAll('.project:not([hidden])').length;
    document.querySelector('#filter-status').textContent=count+(current==='fr'?' projets affichés':' projects shown');
  }
  function close(language){
    applyLanguage(language);
    try{localStorage.setItem(storageKey,current);}catch(_){/* Browsing works with storage disabled. */}
    dialog.close();document.body.classList.remove('language-open');
    (returnFocus || document.querySelector('.hero .button')).focus({preventScroll:true});
  }
  function open(){
    returnFocus=document.activeElement===document.body?null:document.activeElement;
    dialog.showModal();document.body.classList.add('language-open');
  }
  dialog.querySelectorAll('[data-choose-language]').forEach(button=>button.addEventListener('click',()=>close(button.dataset.chooseLanguage)));
  dialog.addEventListener('cancel',event=>{event.preventDefault();close(current);});
  document.querySelector('.locale-toggle').addEventListener('click',open);
  document.querySelector('.filter-bar').addEventListener('click',()=>queueMicrotask(updateFilterStatus));
  let saved;
  try{saved=localStorage.getItem(storageKey);}catch(_){}
  applyLanguage(saved);
  if(saved!=='en' && saved!=='fr')open();
})();
