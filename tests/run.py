"""Play-test bot for Rescue 911: Fire Truck Dino Rescue.

1. Reachability: every egg and bone in every level can be collected with the
   game's own physics on HARD (single jump, no stepping stones, no float).
2. Plays every level on EASY, MEDIUM and HARD with a bot that walks right,
   jumps pits, fires and dinos, sprays its hose, and fights Big Grumpasaur.
3. Falling in a pit respawns; the finale plays through to the title screen.
4. A short real-time session with the keyboard.
"""
import sys, glob
from playwright.sync_api import sync_playwright
CH = (glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome') or [None])[0]
URL = 'file://' + __file__.rsplit('/tests/', 1)[0] + '/index.html'

JS = r"""
window.resetP=function(x,y){ const P=__FT.P; Object.assign(P,{x,y,vx:0,vy:0,ground:true,wasGround:true,coyote:7,jbuf:0,inv:0,dbl:false,sx:1,sy:1}); };
window.reach=function(lv,diff){
  const F=__FT; F.setDiff(diff); F.startLevel(lv); const LV=F.LV, P=F.P, T=16;
  LV.crits.length=0; LV.fires.length=0; LV.truckX=-99999; if(LV.boss) LV.boss.state='calm';
  const starts=[];
  for(let tx=0;tx<LV.W;tx++) for(let ty=1;ty<LV.H;ty++){ const c=LV.t[ty][tx], up=LV.t[ty-1][tx]; if((c==='#'||c==='=')&&up===' ') starts.push([tx*T+3,ty*T-P.h]); }
  const items=LV.eggs.map((e,i)=>['egg',i,e]).concat(LV.bones.map((b,i)=>['bone',i,b]));
  const out=[];
  for(const [kind,i,it] of items){
    let ok=false;
    const near=starts.filter(([sx])=>Math.abs(sx-it.x)<7*T);
    outer: for(const [sx,sy] of near) for(const dir of [1,-1,0]) for(const delay of [0,4,8,14,20,30]){
      it.got=false; resetP(sx,sy); for(const k in F.down) F.down[k]=false; F.state='play';
      for(let f=0;f<110;f++){
        F.down.right=dir>0; F.down.left=dir<0;
        if(f===delay){ F.hit.add('jump'); }
        F.step(); if(it.got){ ok=true; break outer; } if(F.state!=='play') break;
      }
    }
    out.push({kind,i,x:Math.floor(it.x/T),ok});
  }
  for(const k in F.down) F.down[k]=false;
  return out;
};
window.bot=function(maxFrames){
  const F=__FT,P=F.P,T=16; let frames=0,falls=0,lastX=-1,stuck=0,gave=0,natural=0,bossFrames=0;
  const solid=c=>c==='#'||c==='G';
  while(frames<maxFrames&&F.state!=='levelEnd'&&F.state!=='ending'){
    frames++;
    if(F.state==='drive'){ F.step(); continue; }
    if(F.state!=='play') return {fail:'bad state '+F.state,frames};
    const LV=F.LV, tile=(tx,ty)=>(tx<0||tx>=LV.W)?'#':(ty<0||ty>=LV.H)?' ':LV.t[ty][tx];
    const px=P.x+P.w, feetRow=Math.floor((P.y+P.h-1)/T);
    let right=true, jump=false;
    const aheadTx=Math.floor((px+4)/T);
    for(let r=feetRow-1;r<=feetRow;r++) if(solid(tile(aheadTx,r))) jump=true;
    const gTx=Math.floor((px+6)/T); let ground=false; for(let r=LV.top;r<LV.H;r++) if(solid(tile(gTx,r))) ground=true;
    if(!ground) jump=true;
    for(const c of LV.crits) if(c.alive&&c.st==='walk'&&c.x>P.x-4&&c.x-P.x<30&&Math.abs(c.y-P.y)<26) jump=true;
    for(const f of LV.fires) if(!f.out&&f.x>P.x&&f.x-P.x<22) jump=true;
    const B=LV.boss;
    if(B&&B.state!=='sleep'&&B.state!=='calm'){ bossFrames++; const d=B.x-px; right=d>70||P.face<0; if(d<30&&P.ground) jump=true; }
    // at the truck without enough eggs: hand over the missing ones (counted separately)
    if(P.x>LV.truckX-20&&LV.got<LV.need){ for(const e of LV.eggs) if(!e.got&&LV.got<LV.need){ e.got=true; LV.got++; gave++; } }
    F.down.right=right; F.down.spray=true;
    if(jump&&P.ground) F.hit.add('jump');
    F.step();
    if(P.inv===90) falls++;
    if(Math.abs(P.x-lastX)<0.01&&!(B&&B.state!=='sleep'&&B.state!=='calm')){ stuck++; } else stuck=0; lastX=P.x;
    if(stuck>400) return {fail:'stuck at tile '+Math.floor(P.x/T),frames};
  }
  for(const k in F.down) F.down[k]=false;
  const r=F.lastResult;
  return {ok:F.state==='levelEnd'||F.state==='ending',state:F.state,frames,falls,eggsGivenByTest:gave,result:r,bossFrames};
};
"""
fails = 0
def check(ok, name, info=''):
    global fails
    print(('PASS ' if ok else 'FAIL ') + name, info)
    if not ok: fails += 1

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CH, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 800, 'height': 400})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and 'Failed to load resource' not in m.text and 'ERR_' not in m.text else None)
    pg.goto(URL); pg.wait_for_timeout(600)
    pg.evaluate("window.__FTmanual=true"); pg.evaluate(JS + ";0")
    check(pg.evaluate("__FT.diff") == 0, 'opens on EASY')
    for L in range(5):
        r = pg.evaluate(f"reach({L},2)")
        bad = [x for x in r if not x['ok']]
        check(not bad, f'level {L+1}: all {len(r)} eggs and bones reachable on HARD', bad)
    for diff in (0, 1, 2):
        for L in range(5):
            pg.evaluate(f"__FT.setDiff({diff}); __FT.startLevel({L}); for(const k in __FT.down) __FT.down[k]=false;")
            r = pg.evaluate("bot(16000)")
            check(bool(r.get('ok')), f'diff={diff} level={L+1}', r)
    # pit: drop into the first pit and come back
    pg.evaluate("__FT.setDiff(2); __FT.startLevel(0)")
    r = pg.evaluate("""(()=>{const F=__FT,P=F.P; P.x=24*16+4; P.y=8*16+4; P.vy=1; P.ground=false; let f=0; while(f<200){F.step(); f++; if(P.inv===90) break;}
      const ok=P.inv>0&&P.y<8*16&&F.state==='play'; F.down.right=true; const x0=P.x; for(let i=0;i<60;i++) F.step(); F.down.right=false; return {ok,moved:P.x-x0,hp:P.hp}})()""")
    check(r['ok'] and r['moved'] > 20 and r['hp'] == 2, 'fall into pit respawns (HARD costs one heart)', r)
    # easy: bumping a dino never costs anything
    pg.evaluate("__FT.setDiff(0); __FT.startLevel(0)")
    r = pg.evaluate("""(()=>{const F=__FT,P=F.P,c=F.LV.crits[0]; P.x=c.x-4; P.y=c.y-6; P.vy=0; F.step(); return {inv:P.inv,state:F.state}})()""")
    check(r['inv'] > 0 and r['state'] == 'play', 'easy bump just pushes back', r)
    # finale plays to the end and returns to the title
    pg.evaluate("__FT.setDiff(0); __FT.startLevel(4); __FT.finishLevel();")
    r = pg.evaluate("""(()=>{const F=__FT; for(let i=0;i<460;i++){ F.step(); if(i%40===0) F.draw(); } F.hit.add('start'); F.step(); return F.state})()""")
    check(r == 'title', 'finale returns to title', r)
    # draw every screen once to catch drawing errors
    pg.evaluate("""(()=>{const F=__FT; for(const s of ['title','select']){ F.state=s; F.draw(); } F.startLevel(2); F.draw(); F.state='pause'; F.draw(); F.state='play'; F.finishLevel(); F.draw(); })()""")
    # real time with the keyboard
    pg.evaluate("window.__FTmanual=false; __FT.setDiff(0); __FT.startLevel(0); for(const k in __FT.down) __FT.down[k]=false")
    pg.keyboard.down('ArrowRight'); pg.wait_for_timeout(1200)
    pg.keyboard.press('Space'); pg.wait_for_timeout(300); pg.keyboard.down('x'); pg.wait_for_timeout(600); pg.keyboard.up('x')
    pg.keyboard.up('ArrowRight'); pg.wait_for_timeout(300)
    r = pg.evaluate("({state:__FT.state,x:__FT.P.x})")
    check(r['state'] == 'play' and r['x'] > 60, 'real-time keyboard play', r)
    check(not errs, 'no page errors', errs[:5])
    b.close()
print('FAILURES:', fails)
sys.exit(1 if fails else 0)
