// GitHub Pages / HTTPS companion: install prompt and explicit offline image pack.
(()=>{'use strict';
const open=document.getElementById('offlineOpen'),panel=document.getElementById('offlinePanel');
const close=document.getElementById('offlineClose'),status=document.getElementById('offlineStatus');
const download=document.getElementById('offlineCache'),install=document.getElementById('offlineInstall');
if(!open||!panel)return;
let registration=null,installEvent=null,running=false;
function update(s){status.textContent=s}
function hide(){panel.hidden=true;open.focus()}
open.addEventListener('click',()=>{panel.hidden=false;if(registration)requestStatus()});
close.addEventListener('click',hide);
panel.addEventListener('click',e=>{if(e.target===panel)hide()});
document.addEventListener('keydown',e=>{if(!panel.hidden&&e.key==='Escape')hide()});
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();installEvent=e;install.hidden=false});
install.addEventListener('click',async()=>{
 if(!installEvent)return;installEvent.prompt();await installEvent.userChoice;installEvent=null;install.hidden=true;
});
function active(){return navigator.serviceWorker?.controller||registration?.active||registration?.waiting}
function requestStatus(){active()?.postMessage({type:'STATUS'})}
function noWorker(){update('Приложение открыто как локальный файл или браузер не поддерживает офлайн-режим. Для установки откройте версию на GitHub Pages по HTTPS.');download.disabled=true}
if(!('serviceWorker' in navigator)||!['https:','http:'].includes(location.protocol)){noWorker();return}
download.addEventListener('click',()=>{
 const sw=active();if(!sw){update('Офлайн-сервис ещё не готов. Обновите страницу после её первой загрузки.');return}
 running=true;download.disabled=true;update('Начинаю сохранение фотографий…');sw.postMessage({type:'CACHE_PHOTOS'});
});
navigator.serviceWorker.addEventListener('message',e=>{
 const d=e.data;if(!d||d.source!=='crilik-offline')return;
 if(d.type==='STATUS'&&!running)update(`Сохранено фото: ${d.done} из ${d.total}. ${d.done===d.total?'Можно пользоваться офлайн.':'Нажмите кнопку, чтобы загрузить все.'}`);
 if(d.type==='PROGRESS')update(`Сохраняю фотографии: ${d.done} из ${d.total}${d.failed?' · ошибок: '+d.failed:''}`);
 if(d.type==='COMPLETE'){running=false;download.disabled=false;update(`Готово: ${d.stored} из ${d.total} фото в кэше.${d.failed?' Ошибок при загрузке: '+d.failed+'. Повторите загрузку при наличии интернета.':' Теперь фото доступны без интернета.'}`)}
});
window.addEventListener('load',async()=>{
 try{registration=await navigator.serviceWorker.register('./sw.js',{scope:'./'});await navigator.serviceWorker.ready;requestStatus();}
 catch{update('Не удалось включить офлайн-кэш. Сайт продолжает работать онлайн.');download.disabled=true}
});
})();
