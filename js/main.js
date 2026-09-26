
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
document.addEventListener("keydown",event=>{if(event.key==="Escape" && toggle.getAttribute("aria-expanded")==="true"){closeMenu();toggle.focus();}});
window.matchMedia("(min-width: 781px)").addEventListener("change",closeMenu);
const filters=document.querySelectorAll("[data-filter]");
filters.forEach(button=>button.addEventListener("click",()=>{
  filters.forEach(item=>item.setAttribute("aria-pressed",String(item===button)));
  let count=0;
  document.querySelectorAll(".project[data-category]").forEach(card=>{
    card.hidden=button.dataset.filter!=="All" && card.dataset.category!==button.dataset.filter;
    if(!card.hidden)count++;
  });
  document.querySelector("#filter-status").textContent=count+" projects shown";
}));
if("IntersectionObserver" in window){
  const observer=new IntersectionObserver(entries=>{
    entries.forEach(entry=>{if(entry.isIntersecting){
      nav.querySelectorAll('a[href^="#"]').forEach(a=>{if(a.getAttribute("href")==="#"+entry.target.id)a.setAttribute("aria-current","location");else a.removeAttribute("aria-current");});
    }});
  },{rootMargin:"-15% 0px -60% 0px",threshold:0});
  document.querySelectorAll("#experience,#projects,#skills,#education").forEach(section=>observer.observe(section));
}
