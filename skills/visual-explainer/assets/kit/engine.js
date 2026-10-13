/* Explainer kit · engine.js. Topic-neutral: put no subject matter in this file.
   Defines window.Kit: helpers, the 1600x900 stage, the scene engine (objects + beats),
   the gate protocol, the two timeline builders (video frames, slide deck) and a layout lint. */
(function(){
'use strict';
const NS='http://www.w3.org/2000/svg',W=1600,HT=900,DUR=850;
const C={bg:'#0b0e13',stage:'#07090d',panel:'#12161e',ink:'#eceff4',ink2:'#a9b2c3',dim:'#8d97aa',ink3:'#6c7689',faint:'#39414f',line:'#252c3a',
  blue:'#58c4dd',teal:'#5cd0b3',yellow:'#f7d96b',green:'#83c167',red:'#fc6255',orange:'#ff9f5a'};
const reduce=!!(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches);
const Kit=window.Kit={C,W,H:HT,speed:1,reduce,kinds:{},STORY:null};

/* ---------- helpers ---------- */
function E(tag,attrs,parent,text){const e=document.createElementNS(NS,tag);for(const k in attrs)e.setAttribute(k,attrs[k]);if(text!=null)e.textContent=text;if(parent)parent.appendChild(e);return e;}
function D(tag,cls,parent,html){const e=document.createElement(tag);if(cls)e.className=cls;if(html!=null)e.innerHTML=html;if(parent)parent.appendChild(e);return e;}
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const hex=c=>{const n=parseInt(c.slice(1),16);return [n>>16&255,n>>8&255,n&255];};
function mix(a,b,t){const A=hex(a),B=hex(b);return '#'+[0,1,2].map(i=>Math.round(A[i]+(B[i]-A[i])*t).toString(16).padStart(2,'0')).join('');}
const isCol=v=>typeof v==='string'&&v[0]==='#'&&v.length===7;
const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
const tone=t=>C[t]||t||C.ink;
function rr(w,h,r){const x=-w/2,y=-h/2;r=Math.min(r,w/2,h/2);
  return 'M'+(x+r)+','+y+' H'+(x+w-r)+' A'+r+','+r+' 0 0 1 '+(x+w)+','+(y+r)+' V'+(y+h-r)+' A'+r+','+r+' 0 0 1 '+(x+w-r)+','+(y+h)+' H'+(x+r)+' A'+r+','+r+' 0 0 1 '+x+','+(y+h-r)+' V'+(y+r)+' A'+r+','+r+' 0 0 1 '+(x+r)+','+y+' Z';}
const each=(ids,fn)=>{const o={};ids.forEach((id,i)=>{o[id]=fn(i,id);});return o;};
const hide=ids=>each(ids,()=>({o:0}));
const show=(ids,gap)=>each(ids,i=>({o:1,_d:(gap||0)*i}));
Object.assign(Kit,{E,D,esc,mix,isCol,ease,tone,rr,each,hide,show,NS,DUR});

/* A clock owns the tweens and timers of one mounted segment, so cancelling one never touches another. */
function Clock(){
  let tweens=[],timers=[],raf=0,gen=0;
  function frame(now){raf=0;
    for(let i=tweens.length-1;i>=0;i--){const tw=tweens[i];if(now<tw.t0)continue;
      if(!tw.from){tw.from={};if(tw.fx)tw.base=tw.ob.st.s;else for(const k in tw.to){const v=tw.to[k],a=tw.ob.st[k];if((typeof v==='number'&&typeof a==='number')||(isCol(v)&&isCol(a)))tw.from[k]=a;else tw.ob.st[k]=v;}}
      const u=Math.min(1,(now-tw.t0)/tw.dur),e=ease(u);
      if(tw.fx)tw.ob.st.s=tw.base*(1+.14*Math.sin(Math.PI*u));
      else for(const k in tw.from){const a=tw.from[k],b=tw.to[k];tw.ob.st[k]=typeof b==='number'?a+(b-a)*e:mix(a,b,e);}
      tw.ob.render();
      if(u>=1){if(tw.fx){tw.ob.st.s=tw.base;tw.ob.render();}tweens.splice(i,1);tw.res();}}
    if(tweens.length&&!raf)raf=requestAnimationFrame(frame);}
  return {
    get gen(){return gen;},
    tween(ob,to,dur,delay,fx){return new Promise(res=>{tweens.push({ob,to,fx,dur:Math.max(1,dur/Kit.speed),t0:performance.now()+(delay||0)/Kit.speed,from:null,res});if(!raf)raf=requestAnimationFrame(frame);});},
    later(ms){return new Promise(res=>{const t={res};t.id=setTimeout(()=>{timers=timers.filter(x=>x!==t);res();},ms/Kit.speed);timers.push(t);});},
    cancel(){gen++;const tw=tweens;tweens=[];tw.forEach(t=>t.res());const tm=timers;timers=[];tm.forEach(t=>{clearTimeout(t.id);t.res();});}
  };
}
Kit.Clock=Clock;

/* ---------- object kinds (the vocabulary of a scene) ---------- */
function base(g,s){g.setAttribute('transform','translate('+s.x+' '+s.y+') scale('+s.s+')');g.style.opacity=s.o;g.style.display=s.o<0.004?'none':'';}
function dash(p,s){if(s.draw<=0.001){p.style.visibility='hidden';return;}p.style.visibility='visible';p.style.strokeDasharray=s.draw>=1?'none':(s.draw+' 1');}
Kit.base=base;Kit.dash=dash;
Kit.kind=function(name,def,build){Kit.kinds[name]={def,build};};
const T=(g,a,text)=>E('text',Object.assign({'text-anchor':'middle','dominant-baseline':'central',class:'f-sans'},a),g,text);

Kit.kind('cam',{x:800,y:450,s:1,o:1},(g,s0,ctx)=>s=>{ctx.world.setAttribute('transform','translate(800 450) scale('+s.s+') translate('+(-s.x)+' '+(-s.y)+')');});
Kit.kind('box',{w:200,h:80,r:14,fill:C.panel,stroke:C.faint,sw:2.5,draw:1,label:'',sub:'',tcol:C.ink,fs:26,font:'f-sans',lw:500,subcol:C.dim,subfs:20,subTop:false},function(g){
  const p=E('path',{pathLength:1,'stroke-linejoin':'round'},g),t=T(g,{}),t2=T(g,{});g.setAttribute('data-fit','1');
  return s=>{base(g,s);p.setAttribute('d',rr(s.w,s.h,s.r));p.setAttribute('fill',s.fill);p.setAttribute('stroke',s.stroke);p.setAttribute('stroke-width',s.sw);dash(p,s);
    t.setAttribute('class',s.font);t.setAttribute('font-size',s.fs);t.setAttribute('font-weight',s.lw);t.setAttribute('fill',s.tcol);t.textContent=s.label;t.setAttribute('y',s.sub?(s.subTop?16:-12):0);
    t2.textContent=s.sub;t2.setAttribute('font-size',s.subfs);t2.setAttribute('fill',s.subcol);t2.setAttribute('y',s.subTop?-30:19);};});
Kit.kind('txt',{str:'',fs:30,fill:C.ink,anchor:'middle',font:'f-sans',weight:500,reveal:1},function(g){
  const t=E('text',{'dominant-baseline':'central','xml:space':'preserve'},g),a=E('tspan',{},t),b=E('tspan',{'fill-opacity':0},t);t.style.whiteSpace='pre';
  return s=>{base(g,s);t.setAttribute('class',s.font);t.setAttribute('font-size',s.fs);t.setAttribute('font-weight',s.weight);t.setAttribute('fill',s.fill);t.setAttribute('text-anchor',s.anchor);
    const n=s.reveal>=1?s.str.length:Math.round(s.str.length*Math.max(0,s.reveal));a.textContent=s.str.slice(0,n);b.textContent=s.str.slice(n);};});
Kit.kind('line',{d:'',stroke:C.dim,sw:3,draw:1,dashed:false,flow:false,head:null},function(g,s0){
  const p=E('path',{d:s0.d,fill:'none','stroke-linecap':'round','stroke-linejoin':'round'},g);if(!s0.dashed)p.setAttribute('pathLength',1);if(s0.flow)p.setAttribute('class','kx-flow');
  let hd=null;if(s0.head){hd=E('path',{d:'M-15,-9 L3,0 L-15,9 Z'},g);hd.setAttribute('transform','translate('+s0.head[0]+' '+s0.head[1]+') rotate('+s0.head[2]+')');}
  return s=>{base(g,s);p.setAttribute('stroke',s.stroke);p.setAttribute('stroke-width',s.sw);if(s.dashed)p.style.strokeDasharray='11 12';else dash(p,s);
    if(hd){hd.setAttribute('fill',s.stroke);hd.style.opacity=s.draw>=.96?1:0;}};});
/* a round character with eyes: px/py in -1..1 steer the gaze, think shows a spinning ring */
Kit.kind('actor',{fill:C.blue,px:0,py:0,think:0,lab:1,name:''},function(g,s0){
  const ring=E('circle',{r:94,fill:'none','stroke-width':4,'stroke-dasharray':'9 15','stroke-linecap':'round',class:'kx-ring',stroke:s0.fill},g),body=E('circle',{r:70},g),eyes=E('g',{class:'kx-eyes'},g);
  E('ellipse',{cx:-25,cy:-10,rx:16,ry:20,fill:'#ffffff'},eyes);E('ellipse',{cx:25,cy:-10,rx:16,ry:20,fill:'#ffffff'},eyes);
  const pl=E('circle',{r:8,fill:C.bg},eyes),pr=E('circle',{r:8,fill:C.bg},eyes),lab=T(g,{y:122,'font-size':26,fill:C.dim},s0.name);
  return s=>{base(g,s);ring.style.opacity=s.think;body.setAttribute('fill',s.fill);pl.setAttribute('cx',-25+s.px*6);pr.setAttribute('cx',25+s.px*6);pl.setAttribute('cy',-10+s.py*7);pr.setAttribute('cy',-10+s.py*7);lab.style.opacity=s.lab;};});
Kit.kind('file',{name:'',hl:0},function(g,s0){
  const p=E('path',{d:'M-30,-46 H10 L30,-26 V34 H-30 Z','stroke-width':3,'stroke-linejoin':'round'},g),f=E('path',{d:'M10,-46 V-26 H30',fill:'none','stroke-width':3,'stroke-linejoin':'round'},g),
    l=E('path',{d:'M-18,-8 H16 M-18,6 H16 M-18,20 H4',fill:'none','stroke-width':2.5,'stroke-linecap':'round'},g),t=T(g,{y:60,class:'f-mono','font-size':19},s0.name);
  return s=>{base(g,s);const c=mix(C.dim,C.yellow,s.hl);p.setAttribute('stroke',c);f.setAttribute('stroke',c);l.setAttribute('stroke',mix(C.faint,C.yellow,s.hl));p.setAttribute('fill',mix(C.panel,'#2b2710',s.hl));t.setAttribute('fill',c);};});
Kit.kind('term',{hl:0,name:'terminal'},function(g,s0){
  const p=E('rect',{x:-58,y:-38,width:116,height:76,rx:10,'stroke-width':3},g),t=E('text',{x:-36,y:2,'dominant-baseline':'central',class:'f-mono','font-size':26,'font-weight':600},g,'>_'),n=T(g,{y:62,'font-size':19},s0.name);
  return s=>{base(g,s);const c=mix(C.dim,C.yellow,s.hl);p.setAttribute('stroke',c);p.setAttribute('fill',mix(C.panel,'#2b2710',s.hl));t.setAttribute('fill',c);n.setAttribute('fill',c);};});
Kit.kind('shape',{d:'',fill:C.blue,stroke:'none',sw:0},function(g,s0){const p=E('path',{d:s0.d},g);return s=>{base(g,s);p.setAttribute('fill',s.fill);p.setAttribute('stroke',s.stroke);p.setAttribute('stroke-width',s.sw);};});
Kit.kind('bar',{w:0,h:28,fill:C.green},function(g){const r=E('rect',{rx:7},g);return s=>{base(g,s);r.setAttribute('y',-s.h/2);r.setAttribute('width',Math.max(0,s.w));r.setAttribute('height',s.h);r.setAttribute('fill',s.fill);};});
Kit.kind('brk',{w:200,label:'',stroke:C.green,draw:1},function(g){
  const p=E('path',{fill:'none','stroke-width':3,'stroke-linecap':'round','stroke-linejoin':'round',pathLength:1},g),t=T(g,{y:42,'font-size':20});
  return s=>{base(g,s);p.setAttribute('d','M0,0 V14 H'+s.w+' V0');p.setAttribute('stroke',s.stroke);dash(p,s);t.setAttribute('x',s.w/2);t.setAttribute('fill',s.stroke);t.textContent=s.label;t.style.opacity=s.draw>=.9?1:0;};});
Kit.kind('xmark',{},function(g){E('path',{d:'M-13,-13 L13,13 M13,-13 L-13,13',stroke:C.red,'stroke-width':5,'stroke-linecap':'round',fill:'none'},g);return s=>base(g,s);});
Kit.kind('tick',{},function(g){E('circle',{r:17,fill:C.green},g);E('path',{d:'M-8,0 L-2,7 L9,-7',stroke:'#0b1a08','stroke-width':4.5,'stroke-linecap':'round','stroke-linejoin':'round',fill:'none'},g);return s=>base(g,s);});
Kit.kind('lock',{},function(g){E('path',{d:'M-8,-5 V-12 A8,8 0 0 1 8,-12 V-5',fill:'none',stroke:C.orange,'stroke-width':4,'stroke-linecap':'round'},g);E('rect',{x:-13,y:-5,width:26,height:21,rx:5,fill:C.orange},g);return s=>base(g,s);});
Kit.kind('veil',{fill:C.stage},function(g,s0){E('rect',{x:0,y:0,width:W,height:HT,fill:s0.fill},g);return s=>{g.style.opacity=s.o;g.style.display=s.o<0.004?'none':'';};});
/* a button the viewer (or the ghost cursor) can press: give it gate (control id) and pick (option id); any object kind accepts the same two props */
Kit.kind('btn',{w:240,h:66,label:'',fs:24,sel:0,tone:C.yellow},function(g){
  const p=E('path',{'stroke-width':3},g),t=T(g,{'font-weight':600});g.setAttribute('data-fit','1');
  return s=>{base(g,s);p.setAttribute('d',rr(s.w,s.h,s.h/2));p.setAttribute('stroke',s.tone);p.setAttribute('fill',s.sel?s.tone:C.panel);t.setAttribute('font-size',s.fs);t.setAttribute('fill',s.sel?'#17140a':s.tone);t.textContent=s.label;};});
/* a block of monospace lines: show = how many lines are revealed, hl = the highlighted line (-1 for none) */
Kit.kind('code',{lines:[],w:560,fs:20,lh:30,hl:-1,show:99,title:''},function(g,s0){
  const n=s0.lines.length,h=n*s0.lh+(s0.title?66:36);let y0=-h/2+18;
  E('rect',{x:-s0.w/2,y:-h/2,width:s0.w,height:h,rx:12,fill:'#0e1219',stroke:C.faint,'stroke-width':2},g);
  if(s0.title){E('text',{x:-s0.w/2+20,y:y0+8,'dominant-baseline':'central',class:'f-sans','font-size':17,fill:C.dim},g,s0.title);y0+=30;}
  const hb=E('rect',{x:-s0.w/2+6,width:s0.w-12,height:s0.lh,rx:5,fill:C.yellow,opacity:.16},g);
  const ts=s0.lines.map((ln,i)=>{const t=E('text',{x:-s0.w/2+20,y:y0+s0.lh*i+s0.lh/2,'dominant-baseline':'central',class:'f-mono','font-size':s0.fs,'xml:space':'preserve',fill:C.ink},g,ln);t.style.whiteSpace='pre';return t;});
  return s=>{base(g,s);const h1=Math.round(s.hl);hb.style.display=h1<0?'none':'';hb.setAttribute('y',y0+s0.lh*Math.max(0,h1));ts.forEach((t,i)=>{t.style.opacity=i<s.show?(h1>=0&&h1!==i?.5:1):0;});};});
/* one row of a comparison matrix: marks are 2 (yes), 1 (partly) or 0 (no), placed at xs */
Kit.kind('mrow',{label:'',marks:[],note:'',lx:560,xs:[700,880,1060,1240],nx:1320},function(g,s0){
  E('text',{x:s0.lx,'text-anchor':'end','dominant-baseline':'central',class:'f-sans','font-size':24,'font-weight':600,fill:C.ink},g,s0.label);
  E('path',{d:'M'+(s0.lx+30)+',35 H1580',stroke:C.faint,'stroke-width':1,fill:'none'},g);
  s0.xs.forEach((x,i)=>{const v=s0.marks[i];if(v===2)E('circle',{cx:x,cy:0,r:13,fill:C.teal},g);else if(v===1)E('circle',{cx:x,cy:0,r:11.5,fill:'none',stroke:C.teal,'stroke-width':3.5},g);else E('path',{d:'M'+(x-10)+',0 H'+(x+10),stroke:C.dim,'stroke-width':3.5,'stroke-linecap':'round',fill:'none'},g);});
  E('text',{x:s0.nx,'dominant-baseline':'central',class:'f-sans','font-size':16,fill:C.dim},g,s0.note);
  return s=>base(g,s);});

/* ---------- the gate protocol ----------
   A step may carry gate:{id|ids,type,options,demo,say,answer,need,init}. Controls are any elements with data-g (control id)
   and data-o (option id). Choices live in one plain object ch = {controlId: optionId}; every format draws purely from (path, k, ch). */
const ok=(when,ch)=>{if(!when)return true;for(const k in when){const w=when[k];if(Array.isArray(w)?w.indexOf(ch[k])<0:ch[k]!==w)return false;}return true;};
const gids=g=>g.ids||[g.id];
const gkey=g=>gids(g).join('+');
function capOf(st,ch){const g=st.gate;if(g&&g.say){const s=typeof g.say==='function'?g.say(ch):g.say[ch[g.id]];if(s)return s;}return st.cap||'';}
function demoCases(g){
  const d=g.demo||(g.type==='predict'?(g.options||[]).filter(o=>o!==g.answer).concat(g.answer):(g.options||[]));
  return d.map(x=>{if(typeof x==='string')return {set:{[g.id]:x},cap:''};const set=Object.assign({},x);delete set.cap;return {set,cap:x.cap||''};});}
function settled(g,ch,tries){
  if(g.type==='predict')return ch[g.id]===g.answer;
  if(g.type==='explore'){const need=g.need==='all'?demoCases(g).length:(g.need||1);return (tries[gkey(g)]||[]).length>=need;}
  return ch[g.id]!=null;}
Object.assign(Kit,{ok,gids,gkey,capOf,demoCases,settled});

/* ---------- format A: the scene (narrated animation) ---------- */
function Scene(layer,decl){
  const world=E('g',{},layer.svg),ui=E('g',{},layer.svg),O={},ck=Clock(),ctx={world,ui,svg:layer.svg};
  decl.forEach(d=>{const id=d[0],type=d[1],init=d[2]||{},K=Kit.kinds[type];if(!K)throw new Error('unknown object kind: '+type);
    const g=type==='cam'?world:E('g',{'data-id':id},init.layer==='ui'?ui:world);
    if(init.gate!==undefined){g.setAttribute('data-g',init.gate);g.setAttribute('data-o',init.pick);g.setAttribute('role','button');g.setAttribute('tabindex','0');g.setAttribute('aria-label',init.aria||init.label||init.pick);g.style.cursor='pointer';}
    const st=Object.assign({x:0,y:0,s:1,o:0},K.def,init),r=K.build(g,st,ctx);
    const ob={id,type,st,init:Object.assign({},st),render(){r(ob.st);}};O[id]=ob;ob.render();});
  function apply(ph){for(const id in ph){if(id==='_'||!O[id])continue;const u=ph[id],st=O[id].st;if(u._set)Object.assign(st,u._set);for(const k in u)if(k[0]!=='_')st[k]=u[k];}}
  function run(ph){const ps=[];let wait=0;
    for(const id in ph){if(id==='_'){wait=ph._.wait||0;continue;}const ob=O[id];if(!ob){console.warn('missing object',id);continue;}
      const u=Object.assign({},ph[id]),d=u._d||0,t=u._t||DUR,fx=u._fx,set=u._set;delete u._d;delete u._t;delete u._fx;delete u._set;
      if(set){Object.assign(ob.st,set);ob.render();}
      if(fx)ps.push(ck.tween(ob,{},520,d,true));
      if(Object.keys(u).length)ps.push(ck.tween(ob,u,t,d));}
    return Promise.all(ps).then(()=>wait?ck.later(wait):null);}
  /* the state after step k is a pure function of (path, k, ch): reset, then replay every phase up to k */
  function fold(path,k,ch,skip){
    for(const id in O)O[id].st=Object.assign({},O[id].init);
    for(let j=0;j<=k;j++){const b=path[j];(b.ph||[]).forEach(apply);const g=b.gate;if(g&&b.opt&&j!==skip){const v=ch[g.id];if(v!=null&&b.opt[v])b.opt[v].forEach(apply);}}
    for(const id in O){const st=O[id].st;if(st.gate!==undefined)st.sel=ch[st.gate]===st.pick?1:0;}
    for(const id in O)O[id].render();}
  return {O,ck,fold,run,destroy(){ck.cancel();world.remove();ui.remove();}};
}
Kit.scene=function(def){
  let sc=null,built=null;
  const get=()=>built||(built=def.make?def.make(Kit):{o:def.objects,beats:def.beats});
  return {kind:'scene',title:def.title||'',
    steps(ch){return get().beats.filter(b=>ok(b.when,ch));},
    mount(layer){sc=Scene(layer,get().o);},
    unmount(){if(sc){sc.destroy();sc=null;}},
    async render(path,k,ch,how){
      const s=sc;if(!s)return false;s.ck.cancel();const g=s.ck.gen,b=path[k],live=()=>sc===s&&g===s.ck.gen;
      if(how==='jump'||reduce){s.fold(path,k,ch);return true;}
      if(how==='pick'){s.fold(path,k,ch,k);const v=b.gate?ch[b.gate.id]:null;
        for(const ph of (b.opt&&b.opt[v])||[]){await s.run(ph);if(!live())return false;}return true;}
      s.fold(path,k-1,ch);
      for(const ph of b.ph||[]){await s.run(ph);if(!live())return false;}
      if(b.gate&&b.opt&&ch[b.gate.id]!=null)s.fold(path,k,ch);
      return true;}
  };
};
/* a one-beat title card: Kit.card('Part 2', 'The map', 'one line under it') */
Kit.card=function(kicker,title,sub,cap){
  return Kit.scene({title:title,objects:[['k','txt',{x:800,y:330,str:kicker||'',fs:26,fill:C.yellow,font:'f-mono'}],['t','txt',{x:800,y:420,str:title,fs:76,font:'f-serif',weight:700}],['s','txt',{x:800,y:510,str:sub||'',fs:30,fill:C.dim}]],
    beats:[{cap:cap||sub||title,ph:[{k:{o:1},t:{o:1,_d:120},s:{o:1,_d:320}}]}]});
};

/* ---------- the stage: one 1600x900 canvas that scales as a whole ---------- */
Kit.stage=function(el){
  el.classList.add('kx-stage');
  const cur=D('div','kx-cur',el,'<svg viewBox="0 0 24 24"><path d="M4,2 L4,19 L8.6,14.8 L11.6,21.6 L14.4,20.4 L11.4,13.6 L17.6,13.6 Z" fill="#ffffff" stroke="#0b0e13" stroke-width="1.4" stroke-linejoin="round"/></svg><i></i>');
  cur.hidden=true;
  function fit(){el.style.setProperty('--k',el.clientWidth/W);}
  if(window.ResizeObserver)new ResizeObserver(fit).observe(el);fit();
  const wait=ms=>new Promise(r=>setTimeout(r,ms/Kit.speed));
  return {el,cur,fit,
    open(){const root=D('div','kx-layer');el.insertBefore(root,cur);
      const svg=E('svg',{viewBox:'0 0 '+W+' '+HT,class:'kx-svg'},root),html=D('div','kx-html',root);
      return {root,svg,html,close(){root.remove();}};},
    find(cid,oid){return el.querySelector('[data-g="'+cid+'"][data-o="'+oid+'"]');},
    /* move the ghost cursor onto a control and press it; used by the video version to act out every choice */
    async press(target){if(!target)return;const r=el.getBoundingClientRect(),t=target.getBoundingClientRect();
      if(cur.hidden){cur.hidden=false;cur.style.transitionDuration='0ms';cur.style.transform='translate('+(r.width*.5)+'px,'+(r.height*.86)+'px)';void cur.offsetWidth;}
      cur.style.transitionDuration=(reduce?0:650/Kit.speed)+'ms';cur.style.transform='translate('+(t.left+t.width/2-r.left)+'px,'+(t.top+t.height/2-r.top)+'px)';
      await wait(reduce?60:720);cur.classList.add('click');target.classList.add('kx-press');await wait(260);cur.classList.remove('click');target.classList.remove('kx-press');},
    rest(){cur.hidden=true;}
  };
};

/* ---------- timelines ---------- */
Kit.story=function(def){Kit.STORY=def;return def;};
/* video: every step, every branch and every demo case, flattened into frames that can each be jumped to */
Kit.frames=function(S){
  const F=[];let si=0;
  S.chapters.forEach((c,ci)=>{c.segs.forEach(seg=>{const s=si++,seen={};
    const add=o=>F.push(Object.assign({c:ci,s,seg},o));
    (function walk(ch,from){
      const path=seg.steps(ch);
      for(let k=from;k<path.length;k++){
        const st=path[k],g=st.gate;
        if(!g||seen[gkey(g)]){add({ch,k,cap:capOf(st,ch)});continue;}
        seen[gkey(g)]=1;
        const b0=Object.assign({},ch,g.init||{}),cases=demoCases(g);
        add({ch:b0,k,cap:st.cap||'',gate:g,think:g.type==='predict'});
        if(g.type==='branch'){
          for(let i=0;i<cases.length;i++){
            const c2=Object.assign({},b0,cases[i].set);
            add({ch:c2,k,pick:cases[i].set,cap:cases[i].cap||capOf(st,c2)});
            if(i===cases.length-1){walk(c2,k+1);return;}
            const p2=seg.steps(c2);
            for(let j=k+1;j<p2.length&&p2[j].when&&p2[j].when[g.id]!==undefined;j++)add({ch:c2,k:j,cap:capOf(p2[j],c2)});
            add({ch:b0,k,rewind:1,cap:g.rewind||'Rewind to the same moment. This time, the other choice.'});
          }
        }else{
          let cur=b0;cases.forEach(cs=>{cur=Object.assign({},cur,cs.set);add({ch:cur,k,pick:cs.set,cap:cs.cap||capOf(st,cur)});});
          ch=cur;
        }
      }
    })({},0);
  });});
  return F;
};
/* slides: the path under the viewer's own choices, cut at the first gate they have not settled */
Kit.deck=function(S,ch,tries,all){
  const L=[];let si=0,stop=false;
  S.chapters.forEach((c,ci)=>{c.segs.forEach(seg=>{const s=si++;if(stop)return;
    const path=seg.steps(ch);
    for(let k=0;k<path.length;k++){const g=path[k].gate||null,locked=!!(g&&!settled(g,ch,tries));
      L.push({c:ci,s,seg,k,gate:g,locked});
      if(locked&&!all){stop=true;return;}}
  });});
  return L;
};
/* how long a frame stays up when playing: time to read its line, plus thinking time on a question */
Kit.dwell=f=>Math.min(14000,1150+(f.cap||'').length*52)+(f.think?2600:0);

/* ---------- layout lint: run on a mounted stage, returns a list of problems ---------- */
Kit.lint=function(stageEl){
  const R=stageEl.getBoundingClientRect(),k=R.width/W,out=[],items=[];
  const seen=el=>{let o=1;for(let e=el;e&&e!==stageEl;e=e.parentElement){const cs=getComputedStyle(e);if(cs.display==='none'||cs.visibility==='hidden')return 0;o*=parseFloat(cs.opacity);}return o;};
  stageEl.querySelectorAll('.kx-svg text, .kx-html *').forEach(el=>{
    const svg=el.namespaceURI===NS;
    if(!svg&&![...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))return;
    const txt=el.textContent.trim();if(!txt||seen(el)<.3)return;
    const b=el.getBoundingClientRect();if(b.width<2||b.height<2)return;
    /* text scrolled out of a clipped region (data-clip="x,y,w,h" in stage units) is not on screen */
    const cl=el.closest('[data-clip]');if(cl){const c=cl.getAttribute('data-clip').split(',').map(Number),cy=((b.top+b.bottom)/2-R.top)/k,cx=((b.left+b.right)/2-R.left)/k;if(cx<c[0]||cx>c[0]+c[2]||cy<c[1]||cy>c[1]+c[3])return;}
    /* an SVG label inside a scaled object is as big as it is drawn, not as big as its font-size says */
    const fs=svg?Math.round(b.height/k/1.17):parseFloat(getComputedStyle(el).fontSize);
    items.push({el,svg,txt:txt.slice(0,36),x0:(b.left-R.left)/k,y0:(b.top-R.top)/k,x1:(b.right-R.left)/k,y1:(b.bottom-R.top)/k,fs});});
  items.forEach(a=>{
    if(a.fs<15.5)out.push('small text (about '+a.fs+'px on a 1600px stage): "'+a.txt+'"');
    if(a.x1>0&&a.x0<W&&a.y1>0&&a.y0<HT&&(a.x0<-3||a.y0<-3||a.x1>W+3||a.y1>HT+3))out.push('cut by the stage edge: "'+a.txt+'"');
    if(!a.svg){const p=a.el.closest('.sp');if(p){const pb=p.getBoundingClientRect();if(a.el.getBoundingClientRect().bottom>pb.bottom+1)out.push('overflows its panel: "'+a.txt+'"');}}});
  stageEl.querySelectorAll('.sp').forEach(p=>{if(p.scrollHeight>p.clientHeight+2)out.push('panel too short for its content: "'+p.querySelector('h4').textContent.slice(0,30)+'"');});
  for(let i=0;i<items.length;i++)for(let j=i+1;j<items.length;j++){const a=items[i],b=items[j];if(a.el.contains(b.el)||b.el.contains(a.el))continue;
    const w=Math.min(a.x1,b.x1)-Math.max(a.x0,b.x0),h=Math.min(a.y1,b.y1)-Math.max(a.y0,b.y0);if(w<=2||h<=2)continue;
    const sm=Math.min((a.x1-a.x0)*(a.y1-a.y0),(b.x1-b.x0)*(b.y1-b.y0));if(w*h/sm>.18)out.push('overlap: "'+a.txt+'" × "'+b.txt+'"');}
  stageEl.querySelectorAll('[data-fit]').forEach(g=>{if(seen(g)<.3)return;const sh=g.querySelector('path,rect');if(!sh||sh.getAttribute('fill')==='none')return;const sb=sh.getBoundingClientRect();
    g.querySelectorAll('text').forEach(t=>{if(!t.textContent)return;const tb=t.getBoundingClientRect();if(tb.width>sb.width-6*k)out.push('label wider than its box: "'+t.textContent.slice(0,36)+'"');});});
  return out;
};
})();
