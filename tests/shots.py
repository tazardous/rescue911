"""Saves screenshots of every screen to the folder given as the first argument."""
import sys, glob
from playwright.sync_api import sync_playwright
CH=(glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome') or [None])[0]
URL='file://'+__file__.rsplit('/tests/',1)[0]+'/index.html'
out=sys.argv[1] if len(sys.argv)>1 else 'shots'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CH,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':960,'height':540})
    pg.goto(URL); pg.wait_for_timeout(800); pg.evaluate("window.__FTmanual=true")
    def snap(name,js='',steps=1):
        pg.evaluate("(()=>{"+js+"; for(let i=0;i<"+str(steps)+";i++) __FT.step(); __FT.draw();})()"); pg.screenshot(path=f'{out}/{name}.png')
    snap('01_title','__FT.state="title"',30)
    snap('02_select','__FT.state="select"',5)
    for L in range(5):
        snap(f'1{L}_level{L+1}_start',f'__FT.setDiff(1); __FT.startLevel({L})',20)
        snap(f'1{L}_level{L+1}_mid',f'__FT.P.x=__FT.LEVELS[{L}].W*16*0.45; __FT.P.y=8*16-22; __FT.down.spray=true',40)
        pg.evaluate("__FT.down.spray=false")
    snap('20_truck','__FT.P.x=(__FT.LV.W-12)*16; __FT.LV.needHelp=true; __FT.LV.got=2',30)
    snap('21_boss','__FT.startLevel(4); __FT.P.x=100*16; __FT.P.y=8*16-22; __FT.down.spray=true',90)
    pg.evaluate("__FT.down.spray=false")
    snap('22_drive','__FT.LV.boss.hp=0; __FT.LV.boss.state="calm"; __FT.LV.got=8; __FT.P.x=(__FT.LV.W-7)*16',60)
    snap('30_levelend','__FT.startLevel(1); __FT.LV.got=6; __FT.finishLevel()',90)
    for e in (60,150,230,320,430):
        snap(f'4{e:03d}_ending',f'__FT.startLevel(4); __FT.finishLevel(); __FT.endT={e}',1)
    snap('50_pause','__FT.startLevel(0); __FT.state="pause"',1)
    b.close()
