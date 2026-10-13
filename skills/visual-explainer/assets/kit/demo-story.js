/* Demo story for the explainer kit: "How a library lends a book".
   A deliberately small, neutral subject that uses every format and every kind of gate once.
   Copy this file as the starting point of a real story, then replace all of it. */
(function(){
'use strict';
const C=Kit.C,BOOK='A Field Guide to Moss';

/* ---- Part 1 · narrated animation, with a predict gate ---- */
const why=Kit.scene({title:'Why a record exists',make(){
  const o=[],A=(id,t,i)=>o.push([id,t,i||{}]),BK=[C.blue,C.teal,C.yellow,C.orange,C.green],books=BK.map((c,i)=>'b'+i);
  A('cam','cam');
  A('ttl','txt',{x:800,y:390,str:'How a library lends a book',fs:68,font:'f-serif',weight:700});
  A('sub','txt',{x:800,y:470,str:'one small story, told in five formats',fs:28,fill:C.dim});
  BK.forEach((c,i)=>A('b'+i,'box',{x:560+120*i,y:300,w:86,h:210,r:8,fill:Kit.mix(c,'#000000',.6),stroke:c,sw:3}));
  A('plank','line',{d:'M470,412 H1130',stroke:C.dim,sw:6,draw:0,o:1});
  A('r1','actor',{x:190,y:570,s:.62,fill:C.teal,lab:0});A('n1','txt',{x:190,y:640,str:'Ada',fs:22,fill:C.dim});
  A('r2','actor',{x:1410,y:570,s:.62,fill:C.orange,lab:0});A('n2','txt',{x:1410,y:640,str:'Ben',fs:22,fill:C.dim});
  A('w1','line',{d:'M245,548 L770,422',stroke:C.teal,draw:0,o:1,head:[770,422,-13.5]});
  A('w2','line',{d:'M1355,548 L830,422',stroke:C.orange,draw:0,o:1,head:[830,422,193.5]});
  A('q','txt',{x:800,y:540,str:'Who has it now?   When is it due back?',fs:34,font:'f-serif'});
  A('bA','btn',{x:520,y:740,w:440,label:'Trust the librarian’s memory',gate:'track',pick:'mem',fs:23});
  A('bB','btn',{x:1080,y:740,w:440,label:'Write every loan down',gate:'track',pick:'write',fs:23});
  A('xA','xmark',{x:520,y:668});A('yA','txt',{x:520,y:812,str:'the shift ends, and the memory goes home',fs:21,fill:C.red});
  A('kB','tick',{x:1080,y:668});
  A('rec','code',{x:800,y:300,w:640,title:'one record in the catalogue',lines:['book      '+BOOK,'status    on loan','borrower  card #1042','due       2 Nov'],fs:22,lh:34});
  A('recN','txt',{x:800,y:660,str:'Lending a book means changing this record.',fs:32,font:'f-serif'});
  const beats=[
   {cap:'A library owns one copy of most books, and many people who want to read it.',ph:[{ttl:{o:1},sub:{o:1,_d:250}}]},
   {cap:'Here is a shelf. Every book on it exists exactly once.',ph:[{ttl:{o:0},sub:{o:0},plank:{draw:1}},Kit.show(books,90)]},
   {cap:'Two readers want the same book in the same week. Only one of them can take it home.',ph:[{r1:{o:1},n1:{o:1},r2:{o:1,_d:150},n2:{o:1,_d:150}},{w1:{draw:1},w2:{draw:1,_d:200},b2:{sw:6,_d:500}}]},
   {cap:'So at any moment the library must be able to answer two questions: who has this book, and when is it due back. How should it keep track?',
    ph:[{q:{o:1}},{bA:{o:1},bB:{o:1,_d:150}}],
    gate:{id:'track',type:'predict',options:['mem','write'],answer:'write',prompt:'Your turn: pick how the library should keep track.',
     say:{mem:'Memory works until the shift changes. Then the one person who knew has gone home, and the book is simply missing.',
          write:'Writing it down works whoever is at the desk. That written line is called a record, and everything else in a library is built around it.'}},
    opt:{mem:[{xA:{o:1},yA:{o:1,_d:200}},{xA:{_fx:1}}],
         write:[{kB:{o:1}},Object.assign(Kit.each(books,()=>({o:.1})),{plank:{o:.1},w1:{o:0},w2:{o:0},rec:{o:1,_d:200}})]}},
   {cap:'Every loan is one record: which book, which card, due when. The rest of this story is about who is allowed to change it, and in what order.',
    ph:[Object.assign(Kit.hide(books.concat(['plank','q','bA','bB','kB','r1','r2','n1','n2'])),{rec:{y:380,s:1.2}}),{rec:{hl:1},recN:{o:1}}]}
  ];
  return {o,beats};
}});

/* ---- Part 2 · zoomable map, with a click-to-zoom gate ---- */
const MAP={id:'lib',title:'The map',
  regions:[{id:'lib',x:470,y:130,w:870,h:680,label:'library'}],
  nodes:[{id:'you',x:170,y:450,label:'You',tone:'dim'},{id:'desk',x:640,y:450,w:290,label:'Desk',sub:'the only place you talk to'},
         {id:'cat',x:1080,y:290,w:240,label:'Catalogue',sub:'one record per book'},{id:'shelf',x:1080,y:630,w:240,label:'Shelf',sub:'the books themselves'}],
  edges:[{id:'in',d:'M270,432 H492',head:[492,432,0],label:'card + request',lx:372,ly:408},{id:'out',d:'M495,470 H274',head:[274,470,180],label:'book + due date',lx:374,ly:496},
         {id:'look',d:'M785,425 C870,400 910,330 958,302',head:[958,302,-28],label:'look up, update',lx:862,ly:338,la:'end'},{id:'fetch',d:'M785,475 C870,500 910,570 958,606',head:[958,606,34],label:'fetch',lx:862,ly:570,la:'end'}],
  steps:[
   {cap:'The whole library fits in one picture. You stand outside it, and you talk to exactly one place: the desk.',show:['lib','you','desk','in']},
   {cap:'Behind the desk are two things. The shelf holds the books. The catalogue holds the records, one for every book.',show:['cat','shelf','look','fetch']},
   {cap:'A loan ends with a book and a due date coming back out to you. Everything that decides it happens at the desk.',show:['out'],focus:'desk'},
   {cap:'So that is where we look next.',focus:'desk',pick:'desk',prompt:'Your turn: click the desk to zoom in.',say:'Inside the desk: one loan, one step at a time.'}
  ]};

/* ---- Part 3 · simulator, with a branch gate ---- */
const STN=['Scan the card','Look up the book','Decide','Fetch the book','Update the record'];
const loan=Kit.sim({title:'One loan, step by step',head:'One loan, step by step',
  panels:[{id:'you',title:'You',x:40,y:110,w:330,h:640},{id:'desk',title:'Desk',x:400,y:110,w:430,h:640,tone:'teal'},{id:'cat',title:'Catalogue',x:860,y:110,w:400,h:640},{id:'shelf',title:'Shelf',x:1290,y:110,w:270,h:640}],
  init:()=>({have:[],stn:-1,card:'',seen:0,ask:0,held:0,rec:{status:'on the shelf',who:'nobody',due:'none'},books:[BOOK,'Tides','Knots']}),
  steps:[
   {cap:'You walk in with two things: a library card, and the name of a book.',hi:['you'],do(S){S.have=[{t:'library card #1042'},{t:'request: '+BOOK,tone:'yellow'}];}},
   {cap:'The desk scans the card and asks the catalogue one question: may this card borrow?',move:['you','desk','card #1042','ink'],hi:['desk','cat'],do(S){S.stn=0;S.card='valid · 2 of 5 books out';}},
   {cap:'Then it looks up the book. The record says where the book is right now.',move:['desk','cat','where is it?'],hi:['cat'],do(S){S.stn=1;S.seen=1;}},
   {cap:'It is on the shelf, so the desk can offer it. Now the choice is yours.',hi:['desk'],do(S){S.stn=2;S.ask=1;},
    gate:{id:'how',type:'branch',options:['here','home'],prompt:'Your turn: read it here, or take it home?',
     say:{here:'You read it here. Watch what the desk does differently.',home:'You take it home. Watch the order of the next two steps.'}}},
   {when:{how:'here'},cap:'The desk fetches the book and hands it over. Nothing leaves the building, so nobody needs a due date.',move:['shelf','you','the book','orange'],hi:['shelf','you'],
    do(S){S.stn=3;S.books=S.books.slice(1);S.have.push({t:BOOK+' (to read here)',tone:'orange'});}},
   {when:{how:'here'},cap:'The record still changes, in one small way. The book is marked as in use, so nobody goes looking for it on the shelf.',move:['desk','cat','in the reading room'],hi:['cat'],
    do(S){S.stn=4;S.rec={status:'in the reading room',who:'card #1042',due:'today'};}},
   {when:{how:'home'},cap:'The desk fetches the book, and holds on to it for a moment.',move:['shelf','desk','the book','orange'],hi:['shelf','desk'],do(S){S.stn=3;S.books=S.books.slice(1);S.held=1;}},
   {when:{how:'home'},cap:'Before handing it over, the desk writes the loan down: who has the book, and when it is due. Record first, book second. If the two ever disagree, the record is what people will believe.',
    move:['desk','cat','on loan · #1042 · 2 Nov'],hi:['cat'],do(S){S.stn=4;S.rec={status:'on loan',who:'card #1042',due:'2 Nov'};}},
   {when:{how:'home'},cap:'Only then does the book cross the desk. For three weeks, anyone who asks the catalogue gets the same answer.',move:['desk','you','book + due date','orange'],hi:['you'],
    do(S){S.stn=5;S.held=0;S.have.push({t:BOOK+' · due 2 Nov',tone:'orange'});}}
  ],
  draw(S,P,ch,info){
    P.you.list(S.have,info.prev?info.prev.have.length:0);
    P.desk.steps(STN,S.stn);
    if(S.held)P.desk.note('holding: the book','orange');
    if(S.ask)P.desk.buttons('how',[{id:'here',label:'Read it here'},{id:'home',label:'Take it home'}],ch,'your choice');
    P.cat.count('1 of 3 records');
    if(S.seen)P.cat.kv([['book',BOOK],['status',S.rec.status,S.rec.status==='on the shelf'?'green':'yellow'],['with',S.rec.who],['due',S.rec.due]]);else P.cat.text('not looked up yet');
    if(S.card)P.cat.note('card #1042: '+S.card,'green');
    P.shelf.list(S.books);
  }});

/* ---- Part 4 · simulator used as an explore panel: several controls, one pipeline ---- */
function check(v){
  const st=[{title:'1 · Card',sub:'is it valid?'},{title:'2 · Limit',sub:'fewer than 5 books out?'},{title:'3 · Book',sub:'is it on the shelf?'}],R=(verdict,tone,note)=>({st,res:{title:'Result',verdict,tone},note});
  if(v.card==='expired'){Object.assign(st[0],{verdict:'expired',tone:'red'});return R('Refused','red','The first check failed, so the other two never ran.');}
  Object.assign(st[0],{verdict:'valid',tone:'green'});
  if(v.out==='5'){Object.assign(st[1],{verdict:'limit reached',tone:'red'});return R('Refused','red','The card is fine, but five books are already out. The book itself was never looked up.');}
  Object.assign(st[1],{verdict:'room for 3 more',tone:'green'});
  if(v.book==='loan'){Object.assign(st[2],{verdict:'on loan until 26 Oct',tone:'orange'});return R('Offer to reserve it','orange','Both checks about you pass. The book is the problem, so the desk offers a place in the queue.');}
  Object.assign(st[2],{verdict:'on the shelf',tone:'green'});return R('Lend it','green','All three checks pass, in order. Only now does anyone walk to the shelf.');}
const checks=Kit.sim({title:'Three checks',head:'Can this loan go ahead?',
  panels:[{id:'x',title:'Change a setting, watch which check decides',x:70,y:200,w:1460,h:440}],
  steps:[{cap:'Before the desk fetches anything, three checks run in a fixed order. The first one that fails ends the loan.',
    gate:{ids:['card','out','book'],type:'explore',init:{card:'ok',out:'2',book:'shelf'},need:2,prompt:'Your turn: change a setting. Try two different ones.',
     demo:[{card:'expired'},{card:'ok',out:'5'},{out:'2',book:'loan'},{book:'shelf'}],say:ch=>check(ch).note}}],
  draw(S,P,ch){const r=check(ch);
    P.x.buttons('card',[{id:'ok',label:'Valid'},{id:'expired',label:'Expired'}],ch,'Card')
       .buttons('out',[{id:'2',label:'2 of 5'},{id:'5',label:'5 of 5'}],ch,'Books out')
       .buttons('book',[{id:'shelf',label:'On the shelf'},{id:'loan',label:'On loan'}],ch,'This book')
       .pipeline(r.st,r.res).note(r.note);}});

/* ---- Part 5 · sequence diagram ---- */
const log=Kit.seq({title:'The call log',
  actors:[{id:'y',name:'You'},{id:'d',name:'Desk',tone:'teal'},{id:'c',name:'Catalogue'},{id:'s',name:'Shelf'}],
  msgs:[
   {f:'y',t:'d',l:'card + request',grp:'CHECK',cap:'The same loan again, as a list of messages. Time runs downward. You hand over a card and a request.'},
   {f:'d',t:'c',l:'is card #1042 valid?',tone:'yellow',grp:'CHECK',cap:'Every arrow that leaves the desk is a question or an instruction. The first question is about you.'},
   {f:'c',t:'d',l:'valid, 2 of 5 out',tone:'green',grp:'CHECK',cap:'Every arrow that comes back is an answer.'},
   {f:'d',t:'c',l:'where is the book?',tone:'yellow',grp:'CHECK',cap:'The second question is about the book.'},
   {f:'c',t:'d',l:'on the shelf',tone:'green',grp:'CHECK',cap:'Both answers are good, so the checking is over. Notice that the shelf has not been involved yet.'},
   {f:'d',t:'s',l:'fetch',tone:'yellow',grp:'LEND',cap:'Only now does the desk send anyone to the shelf.'},
   {f:'s',t:'d',l:'the book',tone:'orange',grp:'LEND',cap:'The book arrives at the desk.'},
   {f:'d',t:'c',l:'mark on loan, due 2 Nov',tone:'yellow',grp:'LEND',cap:'The desk talks to the catalogue a third time, and this time it changes something.'},
   {f:'d',t:'d',l:'stamp the due date',tone:'teal',grp:'LEND',cap:'A box on a line is work that one actor does alone.'},
   {f:'d',t:'y',l:'book + due date',tone:'orange',grp:'LEND',cap:'The last arrow returns to where the first one started. Ten messages, and you only ever saw two of them.'}
  ]});

/* ---- Part 6 · tiny world ---- */
const world=Kit.world({title:'One picture',origin:[640,120],unit:80,
  floor:[{from:[0,3],to:[10,3]},{from:[5,0],to:[5,2]}],
  cargo:{card:'ink',question:'yellow',answer:'green',book:'orange','book + date':'orange',record:'yellow'},
  props:[{id:'cat',kind:'stack',at:[5,-1],label:'catalogue',state:{items:['ink3','ink3','ink3']}},
         {id:'you',kind:'person',at:[.6,4.4],label:'you'},
         {id:'desk',kind:'block',at:[4.5,4.15],size:[1.1,.45,.5],col:'#1f5a4e',label:'desk',dy:137,ltone:'teal'},
         {id:'gate',kind:'gate',at:[7.5,3],label:'three checks'},
         {id:'shelf',kind:'block',at:[11,2.6],size:[1.1,1.8,1.7],col:'#3a4459',label:'shelf'}],
  stops:{home:[5.5,3.5],you:[1.2,3.5],cat:[5.5,.7],gate:[7.1,3.5],shelf:[10.6,3.5]},
  courier:{home:'home',col:'teal'},
  steps:[
   {cap:'One last view. The small block is the desk clerk, and the whole job is carrying things between four places.'},
   {cap:'A card and a request arrive.',legs:[{to:'you'},{to:'home',carry:'card'}]},
   {cap:'First trip to the catalogue: two questions go up, two answers come back.',legs:[{to:'cat',carry:'question'},{to:'home',carry:'answer'}],set:{gate:{open:1,sign:'all pass'}}},
   {cap:'The checks pass, so the way to the shelf opens.',legs:[{to:'gate',carry:''},{to:'shelf'},{to:'gate',carry:'book'},{to:'home',set:{gate:{open:0,sign:''}}}]},
   {cap:'Second trip to the catalogue: the loan is written down before the book leaves.',legs:[{to:'cat',carry:'record',set:{cat:{push:'yellow'}}},{to:'home',carry:'book + date'}]},
   {cap:'Then the book goes to you. Four places, three trips, one record changed.',legs:[{to:'you'},{to:'home',carry:'',set:{you:{say:'due 2 Nov'}}}]}
  ]});

Kit.story({title:'How a Library Lends a Book',
  credits:'A neutral demo that ships with the explainer kit. Every fact in it is invented for the demo.',
  chapters:[
   {kicker:'Part 1',title:'Why a record exists',segs:[why]},
   {kicker:'Part 2',title:'The map',segs:[Kit.map(MAP)]},
   {kicker:'Part 3',title:'One loan, step by step',segs:[loan]},
   {kicker:'Part 4',title:'Three checks',segs:[checks]},
   {kicker:'Part 5',title:'The call log',segs:[log]},
   {kicker:'Part 6',title:'One picture',segs:[world]}]});
})();
