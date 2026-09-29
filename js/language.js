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
    ['aria-label','alt','title'].forEach(attribute=>{
      document.querySelectorAll(`[data-i18n-${attribute}]`).forEach(element=>{
        element.setAttribute(attribute,dictionary[element.getAttribute(`data-i18n-${attribute}`)][current]);
      });
    });
    document.querySelector('.locale-toggle').textContent=current.toUpperCase()+' / '+(current==='en'?'FR':'EN');
    // The approved download remains the original English CV in both languages.
    document.querySelectorAll('a[download$=".pdf"]').forEach(a=>{
      a.title=current==='fr'?'CV en anglais — une page':'English CV — one page';
    });
    document.dispatchEvent(new CustomEvent('portfolio:language',{detail:current}));
  }
  function close(language){
    applyLanguage(language);
    try{localStorage.setItem(storageKey,current);}catch(_){/* Browsing works with storage disabled. */}
    dialog.close();document.body.classList.remove('language-open');
    document.querySelector('#main-navigation').classList.remove('is-open');
    document.querySelector('.menu-toggle').setAttribute('aria-expanded','false');
    const focusTarget=returnFocus?.closest('#main-navigation') && window.matchMedia('(max-width: 780px)').matches
      ? document.querySelector('.menu-toggle') : (returnFocus || document.querySelector('.hero .button'));
    focusTarget.focus({preventScroll:true});
  }
  function open(){
    returnFocus=document.activeElement===document.body?null:document.activeElement;
    dialog.showModal();document.body.classList.add('language-open');
  }
  dialog.querySelectorAll('[data-choose-language]').forEach(button=>button.addEventListener('click',()=>close(button.dataset.chooseLanguage)));
  dialog.addEventListener('cancel',event=>{event.preventDefault();close(current);});
  document.querySelector('.locale-toggle').addEventListener('click',open);
  let saved;
  try{saved=localStorage.getItem(storageKey);}catch(_){}
  applyLanguage(saved);
})();
