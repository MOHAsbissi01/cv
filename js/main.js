
"use strict";
document.documentElement.classList.add("js-ready");
const toggle = document.querySelector(".menu-toggle");
const nav = document.querySelector("#main-navigation");
function closeMenu(){nav.classList.remove("is-open");toggle.setAttribute("aria-expanded","false");}
toggle.addEventListener("click",()=>{
  const open = toggle.getAttribute("aria-expanded") !== "true";
  toggle.setAttribute("aria-expanded",String(open)); nav.classList.toggle("is-open",open);
});
nav.addEventListener("click",event=>{if(event.target.closest("a"))closeMenu();});
document.addEventListener("keydown",event=>{if(event.key==="Escape" && !document.querySelector('dialog[open]') && toggle.getAttribute("aria-expanded")==="true"){closeMenu();toggle.focus();}});
window.matchMedia("(min-width: 781px)").addEventListener("change",closeMenu);
if("IntersectionObserver" in window){
  const observer=new IntersectionObserver(entries=>{
    entries.forEach(entry=>{if(entry.isIntersecting){
      nav.querySelectorAll('a[href^="#"]').forEach(a=>{if(a.getAttribute("href")==="#"+entry.target.id)a.setAttribute("aria-current","location");else a.removeAttribute("aria-current");});
    }});
  },{rootMargin:"-15% 0px -60% 0px",threshold:0});
  document.querySelectorAll("#about,#experience,#projects,#skills,#contact").forEach(section=>observer.observe(section));
}

// Motion enhances the page; content stays available without JavaScript.
const motionPreference = window.matchMedia("(prefers-reduced-motion: reduce)");
const revealItems = document.querySelectorAll(".section-heading,.experience,.project,.skill-group,.featured-achievement,.contact-panel");
let revealObserver;
function configureMotion(){
  if(revealObserver) revealObserver.disconnect();
  document.documentElement.classList.toggle("motion-ready",!motionPreference.matches && "IntersectionObserver" in window);
  if(motionPreference.matches || !("IntersectionObserver" in window)){
    revealItems.forEach(item=>item.classList.add("is-visible"));
    return;
  }
  revealObserver=new IntersectionObserver(entries=>entries.forEach(entry=>{
    if(entry.isIntersecting){entry.target.classList.add("is-visible");revealObserver.unobserve(entry.target);}
  }),{threshold:0.05,rootMargin:"0px 0px 25px 0px"});
  revealItems.forEach(item=>{item.classList.add("reveal");revealObserver.observe(item);});
}
configureMotion();
motionPreference.addEventListener("change",configureMotion);
window.addEventListener("beforeprint",()=>revealItems.forEach(item=>item.classList.add("is-visible")));
const progress=document.querySelector(".reading-progress");
let scrollPending=false;
function updateProgress(){
  const range=document.documentElement.scrollHeight-window.innerHeight;
  if(progress)progress.style.transform=`scaleX(${range>0?Math.min(1,Math.max(0,window.scrollY/range)):0})`;
  document.querySelector(".site-header").classList.toggle("scrolled",window.scrollY>20);
  scrollPending=false;
}
window.addEventListener("scroll",()=>{if(!scrollPending){scrollPending=true;requestAnimationFrame(updateProgress);}},{passive:true});
window.addEventListener("resize",updateProgress);
updateProgress();
