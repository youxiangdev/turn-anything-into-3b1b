/* Explainer kit · formats.js. Topic-neutral. Formats B to E behind the same segment interface as Kit.scene:
   { kind, title, steps(ch), mount(layer), unmount(), render(path, k, ch, how) }, how = 'jump' | 'enter' | 'pick'.
   Every format draws its state purely from (path, k, ch), so any step can be jumped to. */
(function(){
'use strict';
const Kit=window.Kit,E=Kit.E,D=Kit.D,esc=Kit.esc,tone=Kit.tone,mix=Kit.mix,C=Kit.C,ok=Kit.ok,W=Kit.W,HT=Kit.H;
const wait=ms=>new Promise(r=>setTimeout(r,ms/Kit.speed));
const lerp=(a,b,t)=>[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t];

/* ---------- format B: the simulator (state panels, stepped) ----------
   def: { title, panels:[{id,title,x,y,w,h,tone}], init(), steps:[{cap,do(S,ch),hi:[ids],move:[from,to,label,tone],when,gate}], draw(S,P,ch,info) } */
Kit.sim=function(def){
  let layer=null,P={},gen=0;
  function state(path,k,ch){const S=def.init?def.init():{};for(let i=0;i<=k;i++)if(path[i].do)path[i].do(S,ch);return S;}
  function api(id,anim){const p=P[id],body=p.body;const a={
    count(t){p.cnt.textContent=t;return a;},
    text(s,t){const e=D('p','',body,esc(s));if(t)e.style.color=tone(t);return a;},
    status(s,t){D('div','st',body,esc(s)).style.color=tone(t||'ink');return a;},
    list(items,fresh){const ul=D('ul','',body);if(!items.length)D('li','empty',ul,'nothing yet');
      items.forEach((it,i)=>{if(typeof it==='string')it={t:it};const li=D('li',(anim&&fresh!=null&&i>=fresh?'new ':'')+(it.mono?'mono':''),ul,esc(it.t));li.style.setProperty('--t',tone(it.tone||'ink3'));});return a;},
    code(s){D('pre','',body).textContent=s;return a;},
    steps(names,on){const ol=D('ol','stn',body);names.forEach((n,i)=>D('li',i===on?'on':'',ol,esc(n)));return a;},
    tags(items,on,label){const d=D('div','tags',body);if(label)D('span','lb',d,esc(label));items.forEach((t,i)=>D('code',i===on?'on':'',d,esc(t)));return a;},
    kv(pairs){const dl=D('dl','kv',body);pairs.forEach(q=>{D('dt','',dl,esc(q[0]));const dd=D('dd','',dl,esc(q[1]));if(q[2])dd.style.color=tone(q[2]);});return a;},
    buttons(cid,opts,ch,label){const d=D('div','btns',body);if(label)D('span','lb',d,esc(label));const grp=D('span','bg',d);
      opts.forEach(o=>{if(typeof o==='string')o={id:o,label:o};const b=D('button','kx-b',grp,esc(o.label||o.id));b.type='button';b.dataset.g=cid;b.dataset.o=o.id;b.setAttribute('aria-pressed',String(ch[cid]===o.id));});return a;},
    pipeline(stages,result){const d=D('div','pipe',body);
      stages.concat(result?[Object.assign({res:1},result)]:[]).forEach(s=>{
        const g=D('div','pg'+(s.res?' res':'')+(s.off?' off':''),d,'<b>'+esc(s.title||'')+'</b>'+(s.sub?'<small>'+esc(s.sub)+'</small>':'')+'<span>'+esc(s.verdict||(s.off?'not used':'not reached'))+'</span>');
        if(s.verdict&&!s.off){g.dataset.t='1';g.style.setProperty('--t',tone(s.tone||'ink'));}});
      return a;},
    note(s,t){const e=D('p','note',body,esc(s));if(t)e.style.color=tone(t);return a;},
    html(s){D('div','',body,s);return a;}
  };return a;}
  const mid=el=>[el.offsetLeft+el.offsetWidth/2,el.offsetTop+el.offsetHeight/2];
  function fly(m){const a=P[m[0]],b=P[m[1]];if(!a||!b)return Promise.resolve();
    const ca=mid(a.el),cb=mid(b.el),kf=p=>'translate('+p[0].toFixed(1)+'px,'+p[1].toFixed(1)+'px) translate(-50%,-50%)';
    const chip=D('div','fly',layer.html,esc(m[2]||''));chip.style.setProperty('--t',tone(m[3]||'yellow'));
    const an=chip.animate([{transform:kf(ca),opacity:0},{transform:kf(lerp(ca,cb,.14)),opacity:1,offset:.14},{transform:kf(lerp(ca,cb,.86)),opacity:1,offset:.86},{transform:kf(cb),opacity:0}],{duration:780/Kit.speed,easing:'ease-in-out'});
    return an.finished.then(()=>chip.remove(),()=>chip.remove());}
  return {kind:'sim',title:def.title||'',
    steps(ch){return def.steps.filter(s=>ok(s.when,ch));},
    mount(L){layer=L;P={};L.html.classList.add('sim');
      if(def.head)D('div','simh',L.html,esc(def.head));
      (def.panels||[]).forEach(p=>{const el=D('section','sp',L.html);el.style.cssText='left:'+p.x+'px;top:'+p.y+'px;width:'+p.w+'px;height:'+p.h+'px';
        const h=D('h4','',el,'<span>'+esc(p.title||'')+'</span><i></i>');if(p.tone)h.firstChild.style.color=tone(p.tone);
        P[p.id]={el,cnt:h.lastChild,body:D('div','spb',el)};});},
    unmount(){gen++;layer=null;P={};},
    async render(path,k,ch,how){
      if(!layer)return false;const g=++gen,st=path[k],anim=how!=='jump'&&!Kit.reduce;
      layer.html.querySelectorAll('.fly').forEach(e=>e.remove());
      if(anim&&how==='enter'&&st.move){await fly(st.move);if(g!==gen)return false;}
      const S=state(path,k,ch),prev=k>0?state(path,k-1,ch):null,A={};
      for(const id in P){P[id].body.textContent='';P[id].cnt.textContent='';P[id].el.classList.toggle('hi',(st.hi||[]).indexOf(id)>=0);A[id]=api(id,anim&&how==='enter');}
      def.draw(S,A,ch,{prev,step:st,k,how});
      const pg=[].slice.call(layer.html.querySelectorAll('.pipe .pg[data-t]')),pipes=layer.html.querySelectorAll('.pipe');
      if(!anim||!pg.length){pg.forEach(e=>e.classList.add('on'));return true;}
      pipes.forEach(p=>p.classList.add('wait'));
      for(const e of pg){await wait(380);if(g!==gen)return false;e.classList.add('on');}
      pipes.forEach(p=>p.classList.remove('wait'));
      return true;}
  };
};

/* ---------- format C: the sequence diagram ----------
   def: { title, actors:[{id,name,tone}], msgs:[{f,t,l,cap,tone,grp,when}] }  one diagram
     or { title, lanes:[{title,actors}], msgs:[{lane,f,t,l,row,cap,tone}] }   two diagrams side by side, rows aligned */
let uid=0;
Kit.seq=function(def){
  const lanes=def.lanes||[{title:'',actors:def.actors}],two=lanes.length>1,RH=def.row||(two?52:48),TOP=two?176:132,VH=HT-TOP-26;
  const LX=lanes.map((ln,li)=>{const x0=two?(li?826:26):90,x1=two?(li?1574:774):1510,n=ln.actors.length,o={x0,x1};
    ln.actors.forEach((a,i)=>{o[a.id]=n===1?(x0+x1)/2:x0+96+(x1-x0-192)*i/(n-1);});return o;});
  let layer=null,gen=0,body=null,hl=null,frames=null,lifes=[],els=[];
  function place(path){const pos=new Map(),next=lanes.map(()=>0),grp=[];let y=40,pg,H=0;
    path.forEach((m,i)=>{
      if(two){const li=m.lane||0,r=m.row!=null?m.row:next[li];next[li]=r+1;pos.set(m,40+r*RH);}
      else{if(i&&m.grp!==pg)y+=30;if(m.grp&&m.grp!==pg)grp.push({name:m.grp,y0:y});pg=m.grp;pos.set(m,y);if(m.grp)grp[grp.length-1].y1=y;y+=RH;}
      H=Math.max(H,pos.get(m)+RH*.7);});
    return {pos,grp,H};}
  return {kind:'seq',title:def.title||'',
    steps(ch){return def.msgs.filter(m=>ok(m.when,ch));},
    mount(L){layer=L;const svg=L.svg,id='kxc'+(uid++);els=[];lifes=[];
      E('clipPath',{id},E('defs',{},svg)).appendChild(E('rect',{x:0,y:TOP,width:W,height:VH}));
      lanes.forEach((ln,li)=>{const X=LX[li];
        if(two)E('text',{x:(X.x0+X.x1)/2,y:52,class:'sq-lane'},svg,ln.title||'');
        ln.actors.forEach(a=>{E('rect',{x:X[a.id]-88,y:TOP-62,width:176,height:46,rx:9,class:'sq-head',stroke:tone(a.tone||'faint')},svg);E('text',{x:X[a.id],y:TOP-39,class:'sq-ht'},svg,a.name);});});
      if(two)E('line',{x1:800,y1:24,x2:800,y2:HT-20,class:'sq-split'},svg);
      /* the clip is in stage coordinates, so it sits on the outer group and the offset on an inner one */
      body=E('g',{class:'sq-body'},E('g',{transform:'translate(0 '+TOP+')'},E('g',{'clip-path':'url(#'+id+')','data-clip':'0,'+TOP+','+W+','+VH},svg)));
      lanes.forEach((ln,li)=>ln.actors.forEach(a=>lifes.push(E('line',{x1:LX[li][a.id],y1:0,x2:LX[li][a.id],y2:VH,class:'sq-life'},body))));
      frames=E('g',{},body);hl=E('rect',{x:0,y:0,width:10,height:RH-4,rx:7,class:'sq-hl'},body);
      def.msgs.forEach(m=>{const X=LX[m.lane||0],g=E('g',{class:'sq-m'},body),col=tone(m.tone||'ink');g.style.display='none';
        if(m.f===m.t){E('rect',{x:X[m.f]-11,y:-21,width:22,height:26,rx:5,fill:col},g);E('text',{x:X[m.f]+24,y:-7,class:'sq-lab start',fill:col},g,m.l);}
        else{const x1=X[m.f],x2=X[m.t],d=x2>x1?1:-1;
          E('line',{x1:x1+d*4,y1:0,x2:x2-d*14,y2:0,class:'sq-ar',stroke:col,pathLength:1},g);E('path',{d:'M'+(x2-d*3)+',0 l'+(-d*13)+',-7 v14 z',fill:col,class:'sq-hd'},g);E('text',{x:(x1+x2)/2,y:-13,class:'sq-lab',fill:col},g,m.l);}
        els.push(g);});},
    unmount(){gen++;layer=null;},
    async render(path,k,ch,how){
      if(!layer)return false;const g=++gen,anim=how==='enter'&&!Kit.reduce,pl=place(path),cur=path[k],X=LX[cur.lane||0],y=pl.pos.get(cur);
      const on=new Set(path.slice(0,k+1));
      def.msgs.forEach((m,i)=>{const e=els[i];if(on.has(m)){e.style.display='';e.setAttribute('transform','translate(0 '+pl.pos.get(m)+')');e.classList.toggle('cur',m===cur);}else e.style.display='none';});
      frames.textContent='';
      pl.grp.forEach(f=>{const seen=path.filter(m=>m.grp===f.name&&on.has(m));if(!seen.length)return;const y1=pl.pos.get(seen[seen.length-1]);E('rect',{x:LX[0].x0-50,y:f.y0-36,width:LX[0].x1-LX[0].x0+100,height:y1-f.y0+56,rx:12,class:'sq-frm'},frames);E('text',{x:LX[0].x0-34,y:f.y0-18,class:'sq-frt'},frames,f.name);});
      const full=Math.max(pl.H,VH),sc=Math.max(0,Math.min(full-VH,y-VH*.62));
      lifes.forEach(l=>l.setAttribute('y2',full));
      body.style.transform='translateY('+(-sc).toFixed(1)+'px)';
      hl.setAttribute('width',X.x1-X.x0+(two?0:100));hl.style.transform='translate('+(X.x0-(two?0:50))+'px,'+(y-RH*.62).toFixed(1)+'px)';
      if(!anim)return true;
      const e=els[def.msgs.indexOf(cur)],ar=e.querySelector('.sq-ar');
      if(ar)ar.animate([{strokeDashoffset:1},{strokeDashoffset:0}],{duration:520/Kit.speed,easing:'ease-out'});
      e.animate([{opacity:0},{opacity:1}],{duration:260/Kit.speed});
      await wait(640);return g===gen;}
  };
};

/* ---------- format D: the zoomable map (compiles to a scene) ----------
   def: { id, title, regions:[{id,x,y,w,h,label,tone}], nodes:[{id,x,y,w,h,label,sub,tone}], edges:[{id,d,label,lx,ly,la,head,tone}],
          steps:[{cap,show:[ids]|'all',focus:id|[ids],done:[ids],zoom:id|null,scale,pick:id,prompt,say,when}], extra(A) }
   ids must be unique across regions, nodes and edges. pick makes that node a control: pressing it zooms the camera in. */
Kit.map=function(def){
  const N={};def.nodes.forEach(n=>{N[n.id]=n;});
  const gid=i=>(def.id||'map')+'@'+i,picks={};def.steps.forEach((st,i)=>{if(st.pick)picks[st.pick]=gid(i);});
  const base=n=>tone(n.tone||'faint'),zoomTo=(n,st)=>({cam:{x:n.x,y:n.y,s:st.scale||3,_t:1000}});
  return Kit.scene({title:def.title||'',make(){
    const o=[],A=(id,t,i)=>o.push([id,t,i||{}]);A('cam','cam');
    (def.regions||[]).forEach(r=>{A('r_'+r.id,'box',{x:r.x+r.w/2,y:r.y+r.h/2,w:r.w,h:r.h,r:24,fill:'none',stroke:tone(r.tone||'teal'),sw:3.5,draw:0,o:1});
      A('rt_'+r.id,'txt',{x:r.x+26,y:r.y+36,str:r.label||'',fs:26,anchor:'start',font:'f-math',fill:tone(r.tone||'teal')});});
    (def.edges||[]).forEach(e=>{A('e_'+e.id,'line',{d:e.d,stroke:tone(e.tone||'dim'),sw:3,draw:0,o:1,head:e.head||null});
      if(e.label)A('et_'+e.id,'txt',{x:e.lx,y:e.ly,str:e.label,fs:20,fill:tone(e.tone||'dim'),anchor:e.la||'middle'});});
    def.nodes.forEach(n=>{const w=n.w||200,h=n.h||88,init={x:n.x,y:n.y,w,h,label:n.label,sub:n.sub||'',fs:n.fs||26,subfs:n.subfs||18,stroke:base(n),tcol:tone(n.tcol||'ink'),fill:n.fill||C.panel,s:.9};
      if(picks[n.id]){init.gate=picks[n.id];init.pick=n.id;}
      A('n_'+n.id,'box',init);A('k_'+n.id,'tick',{x:n.x+w/2-4,y:n.y-h/2+4,s:.85});});
    if(def.extra)def.extra(A);
    const isR=id=>(def.regions||[]).some(r=>r.id===id),edge=id=>(def.edges||[]).find(e=>e.id===id);
    const all=def.nodes.map(n=>n.id).concat((def.edges||[]).map(e=>e.id),(def.regions||[]).map(r=>r.id));
    const beats=def.steps.map((st,i)=>{
      const p={},sh=st.show==='all'?all:(st.show||[]),foc=[].concat(st.focus||[]);let d=0;
      sh.forEach(id=>{if(isR(id)){p['r_'+id]={draw:1,_t:1100};p['rt_'+id]={o:1,_d:450};}});
      sh.forEach(id=>{if(N[id]){p['n_'+id]={o:1,s:1,_d:d};d+=90;}});
      sh.forEach(id=>{const e=edge(id);if(e){p['e_'+id]={draw:1,_d:d,_t:700};if(e.label)p['et_'+id]={o:1,_d:d+350};d+=110;}});
      def.nodes.forEach(n=>{const q=p['n_'+n.id]||(p['n_'+n.id]={}),on=foc.indexOf(n.id)>=0;q.stroke=on?C.yellow:base(n);q.sw=on?5:2.5;});
      (st.done||[]).forEach(id=>{p['k_'+id]={o:1};});
      const ph=[p];if(st.also)ph.push(st.also);
      if(st.zoom!==undefined)ph.push(N[st.zoom]?zoomTo(N[st.zoom],st):{cam:{x:800,y:450,s:1,_t:900}});
      const b={cap:st.cap,ph,when:st.when};
      if(st.pick){const n=N[st.pick];b.gate={id:gid(i),type:'branch',options:[st.pick],prompt:st.prompt||('Click “'+n.label+'” to zoom in.'),say:st.say?{[st.pick]:st.say}:null};b.opt={[st.pick]:[zoomTo(n,st)]};}
      return b;});
    return {o,beats};
  }});
};
/* a small inset of a map def, with one node lit: the "you are here" corner of a zoomed-in chapter */
Kit.kind('mini',{map:null,cur:'',k:.13,note:'you are here'},function(g,s0){
  const m=s0.map,k=s0.k,n=m.nodes.find(x=>x.id===s0.cur);
  E('rect',{x:0,y:0,width:W*k+8,height:HT*k+8,rx:10,fill:C.panel,stroke:C.faint,'stroke-width':2},g);
  (m.regions||[]).forEach(r=>E('rect',{x:4+r.x*k,y:4+r.y*k,width:r.w*k,height:r.h*k,rx:5,fill:'none',stroke:tone(r.tone||'teal'),'stroke-width':1.5},g));
  m.nodes.forEach(x=>{const on=x.id===s0.cur,w=(x.w||200)*k,h=(x.h||88)*k;E('rect',{x:4+x.x*k-w/2,y:4+x.y*k-h/2,width:w,height:h,rx:3,fill:on?C.yellow:C.faint},g);});
  E('text',{x:W*k+26,y:42,'dominant-baseline':'central',class:'f-sans','font-size':17,fill:C.dim},g,s0.note);
  E('text',{x:W*k+26,y:74,'dominant-baseline':'central',class:'f-serif','font-size':30,'font-weight':700,fill:C.yellow},g,n?n.label:'');
  return s=>Kit.base(g,s);});

/* ---------- format E: the tiny world (isometric, one courier) ----------
   def: { title, origin:[x,y], unit, floor:[{from:[x,y],to:[x,y],col}], cargo:{name:tone},
          props:[{id,kind:'block'|'orb'|'gate'|'stack'|'person',at:[x,y],size:[w,d,h],span,col,label,state:{}}],
          stops:{name:[x,y]}, courier:{home:'name',col},
          steps:[{cap,pre:{prop:{..}},legs:[{to:'name',carry:'cargo',set:{prop:{..}}}],carry,set:{prop:{..}},when}] }
   prop state: gate {open,sign}, stack {push:'tone'}, orb {glow}, person {say}, block {flash}. */
Kit.world=function(def){
  const U=def.unit||62,OX=(def.origin||[800,150])[0],OY=(def.origin||[800,150])[1];
  const Pt=(x,y,z)=>[OX+(x-y)*U,OY+(x+y)*U/2-(z||0)*U],Q=(x,y,z)=>[(x-y)*U,(x+y)*U/2-(z||0)*U];
  const pts=a=>a.map(p=>p[0].toFixed(1)+','+p[1].toFixed(1)).join(' ');
  function prism(par,f,x,y,z,w,d,h,col){const g=E('g',{},par);
    E('polygon',{points:pts([f(x,y+d,z+h),f(x+w,y+d,z+h),f(x+w,y+d,z),f(x,y+d,z)]),fill:mix(col,'#000000',.3)},g);
    E('polygon',{points:pts([f(x+w,y,z+h),f(x+w,y+d,z+h),f(x+w,y+d,z),f(x+w,y,z)]),fill:mix(col,'#000000',.5)},g);
    E('polygon',{points:pts([f(x,y,z+h),f(x+w,y,z+h),f(x+w,y+d,z+h),f(x,y+d,z+h)]),fill:col},g);return g;}
  const stop=n=>Array.isArray(n)?n:def.stops[n];
  let layer=null,gen=0,raf=0,objs=null,cg=null,card=null,crect=null,ctext=null,props=[];
  const KIND={
    block(g,p){const s=p.size||[1,1,1],pr=prism(g,Pt,p.at[0],p.at[1],0,s[0],s[1],s[2],tone(p.col||'#3a4459'));const c=Pt(p.at[0]+s[0]/2,p.at[1]+s[1]/2,s[2]);
      return {key:p.at[0]+p.at[1]+(s[0]+s[1])/2,lab:[c[0],c[1]-(s[0]+s[1])*U/4-18],up(st){pr.classList.toggle('kx-flash',!!st.flash);}};},
    orb(g,p){const c=Pt(p.at[0]+.5,p.at[1]+.5,.25),col=tone(p.col||'blue');prism(g,Pt,p.at[0],p.at[1],0,1,1,.25,mix(col,'#000000',.62));
      const ring=E('circle',{cx:c[0],cy:c[1]-38,r:50,fill:'none',stroke:col,'stroke-width':3.5,'stroke-dasharray':'8 13','stroke-linecap':'round',class:'kx-ring2'},g);E('circle',{cx:c[0],cy:c[1]-38,r:35,fill:col},g);
      if(p.eyes!==false)[-12,12].forEach(dx=>{E('ellipse',{cx:c[0]+dx,cy:c[1]-42,rx:7.5,ry:9.5,fill:'#ffffff'},g);E('circle',{cx:c[0]+dx-2,cy:c[1]-40,r:3.8,fill:C.bg},g);});
      return {key:p.at[0]+p.at[1]+1,lab:[c[0],c[1]-108],up(st){ring.style.opacity=st.glow?1:0;}};},
    gate(g,p){const x=p.at[0],y=p.at[1],n=p.span||1;prism(g,Pt,x-.05,y-.05,0,.1,.1,.8,'#4a5366');prism(g,Pt,x-.05,y+n-.05,0,.1,.1,.8,'#4a5366');
      const a=Pt(x,y+.04,.7),b=Pt(x,y+n-.04,.7),bar=E('line',{x1:a[0],y1:a[1],x2:b[0],y2:b[1],class:'kx-bar'},g),c=Pt(x,y+n/2,1.55),f=Pt(x,y+n+.45);
      return {key:x+y+n/2,lab:[f[0]-10,f[1]+18],sign:[c[0],c[1]],up(st){bar.classList.toggle('open',!!st.open);}};},
    stack(g,p){const hold=E('g',{},g),c=Pt(p.at[0]+.5,p.at[1]+1.2);let shown=null;prism(g,Pt,p.at[0],p.at[1],0,1,1,.04,'#1a2130');g.appendChild(hold);
      return {key:p.at[0]+p.at[1]+1,lab:[c[0]-20,c[1]+44],up(st){const it=st.items||[],key=it.join();if(key===shown)return;shown=key;hold.textContent='';it.forEach((t,i)=>prism(hold,Pt,p.at[0]+.1,p.at[1]+.1,.04+i*.3,.8,.8,.26,tone(t)));}};},
    person(g,p){const c=Pt(p.at[0],p.at[1]),col=tone(p.col||'ink');E('circle',{cx:c[0],cy:c[1]-36,r:13,fill:col},g);E('path',{d:'M'+(c[0]-16)+','+c[1]+' q16,-36 32,0 z',fill:col},g);
      return {key:p.at[0]+p.at[1],lab:[c[0],c[1]+26],sign:[c[0],c[1]-66],up(){}};}
  };
  function fold(path,k){const S={pos:stop(def.courier.home).slice(),carry:'',props:{}};
    def.props.forEach(p=>{S.props[p.id]=Object.assign({},p.state||{});});
    const set=o=>{for(const id in o||{}){const t=S.props[id]||(S.props[id]={}),v=o[id];for(const q in v){if(q==='push')t.items=(t.items||[]).concat(v.push);else t[q]=v[q];}}};
    for(let i=0;i<=k;i++){const st=path[i];set(st.pre);(st.legs||[]).forEach(l=>{S.pos=stop(l.to).slice();if(l.carry!==undefined)S.carry=l.carry;set(l.set);});if(st.carry!==undefined)S.carry=st.carry;set(st.set);}
    return {S,set};}
  function paint(S){const p=Pt(S.pos[0],S.pos[1]);cg.setAttribute('transform','translate('+p[0].toFixed(1)+' '+p[1].toFixed(1)+')');
    card.style.display=S.carry?'':'none';
    if(S.carry){const w=Math.max(54,S.carry.length*11+26);crect.setAttribute('x',-w/2);crect.setAttribute('width',w);crect.setAttribute('fill',tone((def.cargo||{})[S.carry]||'yellow'));ctext.textContent=S.carry;}
    props.forEach(q=>{const st=S.props[q.p.id]||{};q.v.up(st);if(q.sign)q.sign.textContent=st.sign||st.say||'';});
    const key=S.pos[0]+S.pos[1],nx=props.find(q=>q.v.key>key);objs.insertBefore(cg,nx?nx.g:null);}
  function move(S,to,g){return new Promise(res=>{const a=S.pos.slice(),dist=Math.hypot(to[0]-a[0],to[1]-a[1]),dur=Math.max(180,dist*240)/Kit.speed;let t0=null;
    (function fr(t){if(g!==gen){res();return;}if(t0===null)t0=t;const u=Math.min(1,(t-t0)/dur),e=u<.5?2*u*u:1-Math.pow(-2*u+2,2)/2;S.pos=lerp(a,to,e);paint(S);if(u<1)raf=requestAnimationFrame(fr);else res();})(performance.now());});}
  return {kind:'world',title:def.title||'',
    steps(ch){return def.steps.filter(s=>ok(s.when,ch));},
    mount(L){layer=L;const svg=L.svg;props=[];
      (def.floor||[]).forEach(f=>{for(let x=Math.min(f.from[0],f.to[0]);x<=Math.max(f.from[0],f.to[0]);x++)for(let y=Math.min(f.from[1],f.to[1]);y<=Math.max(f.from[1],f.to[1]);y++)
        E('polygon',{points:pts([Pt(x,y),Pt(x+1,y),Pt(x+1,y+1),Pt(x,y+1)]),fill:tone(f.col||'#1a2130'),stroke:C.stage,'stroke-width':1.5},svg);});
      objs=E('g',{},svg);const labs=E('g',{},svg);
      def.props.forEach(p=>{const g=E('g',{},null),v=KIND[p.kind](g,p),q={p,g,v};
        if(p.label)E('text',{x:v.lab[0]+(p.dx||0),y:v.lab[1]+(p.dy||0),class:'kx-lab',fill:tone(p.ltone||'dim')},labs,p.label);
        if(v.sign)q.sign=E('text',{x:v.sign[0],y:v.sign[1],class:'kx-sign'},labs,'');
        props.push(q);});
      props.sort((a,b)=>a.v.key-b.v.key).forEach(q=>objs.appendChild(q.g));
      cg=E('g',{},objs);prism(cg,Q,-.26,-.26,0,.52,.52,.44,tone(def.courier.col||'teal'));
      card=E('g',{},cg);crect=E('rect',{y:-74,height:30,rx:6},card);ctext=E('text',{x:0,y:-58,class:'kx-card'},card,'');},
    unmount(){gen++;cancelAnimationFrame(raf);layer=null;},
    async render(path,k,ch,how){
      if(!layer)return false;const g=++gen;cancelAnimationFrame(raf);
      if(how!=='enter'||Kit.reduce){paint(fold(path,k).S);return true;}
      const f=fold(path,k-1),S=f.S,st=path[k];f.set(st.pre);paint(S);
      for(const l of st.legs||[]){if(l.carry!==undefined)S.carry=l.carry;paint(S);await move(S,stop(l.to),g);if(g!==gen)return false;f.set(l.set);paint(S);}
      paint(fold(path,k).S);await wait(260);return g===gen;}
  };
};
})();
