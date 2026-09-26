# -*- coding: utf-8 -*-
"""Generate the interactive viewer page with the real GLB embedded."""
import base64, json, pathlib
import geometry_master as G, furniture as F, heights as H

glb = base64.b64encode(open('out/model_3d.glb','rb').read()).decode()
prov = json.dumps(H.PROVISIONAL, ensure_ascii=False)

HTML = r'''<title>SOHO 1415 Coordinate Model</title>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
:root{
  --paper:#E8EBEC; --panel:#FDFDFD; --panel2:#F2F4F5; --ink:#0F161C; --muted:#5D6B75;
  --rule:#CBD3D8; --rule2:#DDE3E7; --accent:#0E6B55; --accent-soft:#D6E8E2; --mark:#A34A20;
  --shadow:0 1px 2px rgba(15,22,28,.06),0 8px 24px rgba(15,22,28,.06);
}
@media (prefers-color-scheme:dark){ :root:not([data-theme="light"]){
  --paper:#0C1218; --panel:#141C23; --panel2:#19222A; --ink:#E4E9EC; --muted:#8E9BA5;
  --rule:#27323B; --rule2:#1F2932; --accent:#3FBD98; --accent-soft:#12302A; --mark:#DF8248;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 28px rgba(0,0,0,.35);
}}
:root[data-theme="dark"]{
  --paper:#0C1218; --panel:#141C23; --panel2:#19222A; --ink:#E4E9EC; --muted:#8E9BA5;
  --rule:#27323B; --rule2:#1F2932; --accent:#3FBD98; --accent-soft:#12302A; --mark:#DF8248;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 28px rgba(0,0,0,.35);
}
*{box-sizing:border-box}
body{background:var(--paper);color:var(--ink);
  font-family:"IBM Plex Sans",system-ui,-apple-system,"Hiragino Kaku Gothic ProN","Noto Sans JP",sans-serif;
  font-size:14px;line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding-inline:16px;padding-block:28px 56px}
.mono{font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;font-variant-numeric:tabular-nums}

header.head{display:flex;flex-wrap:wrap;gap:12px 20px;align-items:baseline;
  border-bottom:1px solid var(--rule);padding-bottom:16px;margin-bottom:22px}
h1{font-size:clamp(20px,3.2vw,27px);font-weight:700;letter-spacing:-.018em;margin:0;text-wrap:balance}
.sub{color:var(--muted);font-size:13px;margin:0}
.tag{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.09em;text-transform:uppercase;
  color:var(--accent);background:var(--accent-soft);border-radius:2px;padding:3px 8px;white-space:nowrap}

.stage{display:grid;grid-template-columns:minmax(0,1fr) 258px;gap:14px;align-items:start}
@media(max-width:860px){.stage{grid-template-columns:minmax(0,1fr)}}

.viewport{position:relative;background:var(--panel);border:1px solid var(--rule);
  border-radius:3px;overflow:hidden;box-shadow:var(--shadow)}
#cv{display:block;width:100%;height:clamp(340px,58vh,620px);touch-action:none}
.hud{position:absolute;left:10px;bottom:10px;background:var(--panel);
  background:color-mix(in srgb,var(--panel) 88%,transparent);
  border:1px solid var(--rule2);border-radius:2px;padding:7px 10px;pointer-events:none;
  font-family:"IBM Plex Mono",monospace;font-size:11px;line-height:1.5;max-width:min(88%,380px)}
.hud b{font-weight:600;color:var(--accent)}
.hud span{color:var(--muted)}
.compass{position:absolute;right:10px;top:10px;width:46px;height:46px;pointer-events:none;opacity:.85}
.loading{position:absolute;inset:0;display:grid;place-items:center;font-family:"IBM Plex Mono",monospace;
  font-size:12px;color:var(--muted);background:var(--panel)}

.rail{display:flex;flex-direction:column;gap:12px}
.card{background:var(--panel);border:1px solid var(--rule);border-radius:3px;padding:12px}
.card h2{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);
  font-family:"IBM Plex Mono",monospace;font-weight:500;margin:0 0 9px}
.views{display:grid;grid-template-columns:repeat(3,1fr);gap:5px}
button.v{font-family:"IBM Plex Mono",monospace;font-size:11px;padding:6px 0;background:var(--panel2);
  color:var(--ink);border:1px solid var(--rule2);border-radius:2px;cursor:pointer}
button.v:hover{border-color:var(--accent);color:var(--accent)}
button.v:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.slider{display:flex;align-items:center;gap:9px}
input[type=range]{flex:1;accent-color:var(--accent);min-width:0}
.val{font-family:"IBM Plex Mono",monospace;font-size:12px;width:58px;text-align:right;color:var(--muted)}
.layers{display:flex;flex-direction:column;gap:2px}
.layers label{display:flex;align-items:center;gap:8px;font-size:12.5px;cursor:pointer;padding:2px 0}
.layers input{accent-color:var(--accent);flex:none}
.sw{width:9px;height:9px;border-radius:1px;flex:none;border:1px solid rgba(0,0,0,.18)}

.notes{margin-top:26px;display:grid;grid-template-columns:repeat(auto-fit,minmax(248px,1fr));gap:14px}
.note{background:var(--panel);border:1px solid var(--rule);border-radius:3px;padding:14px 15px}
.note h3{margin:0 0 8px;font-size:13px;font-weight:600;letter-spacing:-.005em}
.note p{margin:0 0 8px;font-size:12.5px;color:var(--muted)}
.note p:last-child{margin-bottom:0}
dl.kv{display:grid;grid-template-columns:auto 1fr;gap:3px 12px;margin:0;font-size:12px}
dl.kv dt{color:var(--muted);font-family:"IBM Plex Mono",monospace}
dl.kv dd{margin:0;font-family:"IBM Plex Mono",monospace;text-align:right}
.flag{border-left:2px solid var(--mark);padding-left:10px}
.flag h3{color:var(--mark)}
footer{margin-top:26px;padding-top:14px;border-top:1px solid var(--rule);
  color:var(--muted);font-size:11.5px;font-family:"IBM Plex Mono",monospace}
</style>

<div class="wrap">
<header class="head">
  <div style="flex:1 1 320px;min-width:0">
    <h1>OIMACHI TRACKS RESIDENCE 1415</h1>
    <p class="sub">元図面の 2D MASTER 座標をそのまま押し出した 3D ジオメトリに、天井・照明・家具・デコレーションまで載せた最終モデルです。画像生成は使っていません。バルコニーは<b>北向き</b>です。</p>
  </div>
  <span class="tag">Phase 10 · final coordinate model</span>
</header>

<div class="stage">
  <div class="viewport">
    <canvas id="cv"></canvas>
    <div class="loading" id="load">loading mesh…</div>
    <svg class="compass" viewBox="0 0 48 48" aria-hidden="true">
      <circle cx="24" cy="24" r="17" fill="none" stroke="currentColor" stroke-opacity=".28"/>
      <g id="needle"><path d="M24 7 L28 25 L24 22 L20 25 Z" fill="currentColor"/>
      <text x="24" y="43" text-anchor="middle" font-size="9"
        font-family="IBM Plex Mono, monospace" fill="currentColor">N</text></g>
    </svg>
    <div class="hud" id="hud"><b>ドラッグ</b><span>で回転 ／ </span><b>ホイール</b><span>で拡大 ／ </span><b>右ドラッグ</b><span>で平行移動</span></div>
  </div>

  <div class="rail">
    <div class="card">
      <h2>view</h2>
      <div class="views">
        <button class="v" data-b="315" data-el="28">NW</button>
        <button class="v" data-b="0"   data-el="28">N</button>
        <button class="v" data-b="45"  data-el="28">NE</button>
        <button class="v" data-b="270" data-el="28">W</button>
        <button class="v" data-b="180" data-el="89.5">TOP</button>
        <button class="v" data-b="90"  data-el="28">E</button>
        <button class="v" data-b="225" data-el="28">SW</button>
        <button class="v" data-b="180" data-el="28">S</button>
        <button class="v" data-b="135" data-el="28">SE</button>
      </div>
      <p class="mono" style="margin:9px 0 0;font-size:10.5px;color:var(--muted)">
        カメラのいる方位 · TOP は北が上<br>orthographic only — perspective = 0</p>
    </div>

    <div class="card">
      <h2>cut plane</h2>
      <div class="slider">
        <input id="cut" type="range" min="200" max="2500" step="25" value="1250" aria-label="cut height">
        <span class="val mono" id="cutv">1250</span>
      </div>
      <p class="mono" style="margin:8px 0 0;font-size:10.5px;color:var(--muted)">
        mm from FL · 2500 = 切断なし</p>
    </div>

    <div class="card">
      <h2>layers</h2>
      <div class="layers" id="layers"></div>
    </div>
  </div>
</div>

<div class="notes">
  <div class="note">
    <h3>方位</h3>
    <dl class="kv">
      <dt>バルコニー</dt><dd>北向き</dd>
      <dt>玄関・廊下</dt><dd>南</dd>
      <dt>Book Shelf 側</dt><dd>東壁</dd>
      <dt>モニター側</dt><dd>西壁</dd>
      <dt>サッシ</dt><dd>2枚・西広/東狭</dd>
      <dt>手すり</dt><dd>ガラス＋笠木</dd>
      <dt>単位</dt><dd>1 px = 13.2 mm</dd>
      <dt>外形</dt><dd>4818 × 8870 mm</dd>
    </dl>
    <p style="margin:8px 0 0;font-size:11.5px">方位記号の N は針の<b>下端</b>に付いており、図面上は北が下です。</p>
  </div>
  <div class="note">
    <h3>XY 一致検証</h3>
    <dl class="kv">
      <dt>比較群</dt><dd>24</dd>
      <dt>完全一致</dt><dd>22 群 / 0.00 px</dd>
      <dt>椅子</dt><dd>1.00 px 内側</dd>
      <dt>TOP 線検証</dt><dd>61 要素 / 0.61 px</dd>
      <dt>未説明残差</dt><dd>0 点</dd>
    </dl>
  </div>
  <div class="note">
    <h3>収納壁</h3>
    <p>OPEN / PARKED 固定。南北ラン 3 枚は南端の戸袋、東西ラン 2 枚は東端の戸袋に格納。レールは全長保持、開口は常時クリア。</p>
    <p class="mono" style="font-size:11px">緑 = 格納パネル / 戸袋 / レール</p>
  </div>
  <div class="note flag">
    <h3>高さは全て仮設定</h3>
    <p>元図面に断面がないため、Z は全て仮変数です。実測値ではありません。どの Z を変えても X・Y は動きません。</p>
    <p class="mono" style="font-size:11px" id="provlist"></p>
  </div>
</div>

<footer>build_3d.py → model_3d.glb · 40 objects · orthographic viewer, three.js r128</footer>
</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
const GLB_B64="__GLB__";
const PROV=__PROV__;
const MM=13.2;

const COLORS={
 Exterior_Walls:0xDFE3E6, Interior_Walls:0xD3D9DD, Columns:0xC3BFC9, PS:0xC8CCCE,
 Entrance:0x7C9CBE, Shower:0xCBD8DE, WD:0xD6D9DA, Powder_Room_Fixtures:0xE1E4E6,
 Toilet:0xE4E7E8, Kitchen:0x9FB6C6, Refrigerator:0xCBD0D3, Closets:0x8FAFC8,
 Book_Shelf:0x6E9BBE, Book_Shelf_Back:0x4E7B9E, Storage_Wall_Pocket:0x4FA07F, Storage_Wall_Parked_Panels:0x2FBE85,
 Storage_Wall_Rail:0x2E6D55, Windows:0x3A3F45, Window_Glass:0x9FC4D6,
 Balcony_Floor:0xC2C7CB, Balcony_Railing:0x3A3F45, Balcony_Glass:0xAFCEDD,
 Balcony_Partitions:0x7A3040, Downpipe:0xD8D4CC, Work_Desks:0x5E8FC0, Work_Chairs:0x4A5158,
 Printer_Unit:0x9AA0A6, Meeting_Table:0x6A4C38, Table_Frame:0xBCBEC1,
 Table_Wirebox:0x3A3A3C, Work_Chair_Bases:0xB0B2B5, Meeting_Chair_Bases:0xB0B2B5, Meeting_Chairs:0x525960,
 Monitor_55:0x23282E, Floor_Slab:0xD9D6D2, Floor_Carpet:0xCED0D2, Floor_Tile:0xB6B2AC,
 Ceiling_Slab:0xE6E4E1, Ceiling_Coffer:0xDCD9D5, Downlights:0xF2E6C8,
 Laptops:0xA8AAAD, Laptop_Screens:0x222226, Desk_Kit:0xDEDDDA, Paper:0xF8F6F0,
 Books:0xB0A08C, Plant_Pots:0xD6D0C6, Plant_Foliage:0x586A4A
};
const GROUPS=[
 ["躯体・仕上げ",["Exterior_Walls","Interior_Walls","Columns","PS","Floor_Slab","Floor_Carpet","Floor_Tile"],0xD3D9DD],
 ["建具・開口",["Windows","Window_Glass","Entrance"],0x7C9CBE],
 ["収納壁 (OPEN)",["Storage_Wall_Pocket","Storage_Wall_Parked_Panels","Storage_Wall_Rail"],0x2FBE85],
 ["設備・造作",["Shower","WD","Powder_Room_Fixtures","Toilet","Kitchen","Refrigerator","Closets","Book_Shelf","Book_Shelf_Back"],0x9FB6C6],
 ["家具",["Work_Desks","Work_Chairs","Work_Chair_Bases","Printer_Unit",
         "Meeting_Table","Table_Frame","Table_Wirebox",
         "Meeting_Chairs","Meeting_Chair_Bases","Monitor_55"],0x6A4C38],
 ["バルコニー",["Balcony_Floor","Balcony_Railing","Balcony_Glass",
                "Balcony_Partitions","Downpipe"],0xADB4B9],
 ["天井・照明",["Ceiling_Slab","Ceiling_Coffer","Downlights"],0xDCD9D5],
 ["デコレーション",["Laptops","Laptop_Screens","Desk_Kit","Paper","Books",
                "Plant_Pots","Plant_Foliage"],0x586A4A]
];
const JP={Exterior_Walls:"外壁",Interior_Walls:"内壁",Columns:"柱",PS:"PS",Entrance:"玄関",
 Shower:"シャワー",WD:"洗濯機置場",Powder_Room_Fixtures:"洗面",Toilet:"トイレ",Kitchen:"キッチン",
 Refrigerator:"冷蔵庫置場",Closets:"クローゼット",Book_Shelf:"Book Shelf",Book_Shelf_Back:"Book Shelf 背板",
 Storage_Wall_Pocket:"戸袋",Storage_Wall_Parked_Panels:"格納パネル",Storage_Wall_Rail:"レール",
 Windows:"サッシ枠",Window_Glass:"ガラス",
 Balcony_Glass:"手すりガラス",Balcony_Partitions:"隔て板",Downpipe:"縦樋",Balcony_Floor:"バルコニー床",Balcony_Railing:"手すり",
 Work_Desks:"執務デスク",Work_Chairs:"アーロンチェア",Work_Chair_Bases:"アーロン脚",
 Printer_Unit:"プリンター",
 Meeting_Table:"E-CAD-2190KW 天板",Table_Frame:"E-CAD 脚（ポリッシュ）",
 Table_Wirebox:"配線ボックス",
 Meeting_Chairs:"セトゥーチェア",Meeting_Chair_Bases:"セトゥー脚",Monitor_55:"55型モニター",
 Floor_Slab:"フローリング",Floor_Carpet:"カーペット（LD）",Floor_Tile:"石目調タイル（廊下・水回り）",
 Ceiling_Slab:"天井スラブ",Ceiling_Coffer:"折上げ天井",Downlights:"ダウンライト",
 Laptops:"ノートPC",Laptop_Screens:"PC画面",Desk_Kit:"キーボード・マウス",
 Paper:"ノート・書類",Books:"書籍",Plant_Pots:"鉢",Plant_Foliage:"植栽"};

document.getElementById('provlist').textContent =
  ["WALL_HEIGHT","DOOR_HEIGHT","WINDOW_HEAD","BOOKSHELF_HEIGHT","PARTITION_PANEL_HEIGHT"]
  .map(k=>k+" "+PROV[k]).join("  ·  ");

if(typeof THREE==='undefined'){
  document.getElementById('load').textContent=
    '3D ライブラリを読み込めませんでした。再読み込みしてください。';
  throw new Error('three.js unavailable');
}
const REDUCED=matchMedia('(prefers-reduced-motion: reduce)').matches;
const cv=document.getElementById('cv');
const renderer=new THREE.WebGLRenderer({canvas:cv,antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.localClippingEnabled=true;
const scene=new THREE.Scene();
const root=new THREE.Group(); root.scale.x=-1; scene.add(root);
const inner=new THREE.Group(); inner.rotation.x=-Math.PI/2; root.add(inner);
// MASTER (x right, y down, z up) -> world (EAST, UP, SOUTH), right-handed.
// north = MASTER +y (plan down), east = -MASTER x.  The MASTER tuple is
// left-handed, so the conversion is a reflection: scale.x = -1 after the
// -90 deg X rotation gives world = (-x, z, -y).  See orientation.py.
const camera=new THREE.OrthographicCamera(-1,1,1,-1,-6000,6000);
const controls=new THREE.OrbitControls(camera,cv);
controls.enableDamping=!REDUCED; controls.dampingFactor=.09; controls.enablePan=true;
scene.add(new THREE.HemisphereLight(0xffffff,0x9aa4ac,.85));
const key=new THREE.DirectionalLight(0xffffff,.62); key.position.set(-420,760,520); scene.add(key);
const fill=new THREE.DirectionalLight(0xffffff,.22); fill.position.set(520,420,-380); scene.add(fill);
const clip=new THREE.Plane(new THREE.Vector3(0,-1,0),0);
renderer.clippingPlanes=[clip];

function themeColor(){
  const c=getComputedStyle(document.body).backgroundColor;
  const m=c.match(/\d+/g); return m?new THREE.Color(m[0]/255,m[1]/255,m[2]/255):new THREE.Color(0xffffff);
}
function paint(){ renderer.setClearColor(themeColor(),1); }

const bytes=Uint8Array.from(atob(GLB_B64),c=>c.charCodeAt(0));
let RADIUS=600, CENTER=new THREE.Vector3(), objs=[];
new THREE.GLTFLoader().parse(bytes.buffer,"",gltf=>{
  const box=new THREE.Box3();
  gltf.scene.traverse(o=>{ if(o.isMesh){
    const name=(o.name||"").replace(/[.\-]\d+$/,"");
    o.userData.key=name;
    o.geometry.computeBoundingBox();
    const b=o.geometry.boundingBox;
    o.userData.bounds=[b.min.x,b.min.y,b.max.x,b.max.y,b.min.z,b.max.z];
    o.material=new THREE.MeshLambertMaterial({
      color:COLORS[name]!==undefined?COLORS[name]:0xB9BEC2, side:THREE.DoubleSide});
    const eg=new THREE.LineSegments(
      new THREE.EdgesGeometry(o.geometry,28),
      new THREE.LineBasicMaterial({color:0x000000,transparent:true,opacity:.24}));
    o.add(eg);
    objs.push(o); box.expandByObject(o);
  }});
  gltf.scene.updateMatrixWorld(true);
  box.getCenter(CENTER); RADIUS=box.getSize(new THREE.Vector3()).length()/2;
  gltf.scene.position.set(-CENTER.x,-CENTER.y,-CENTER.z);   // centre in MASTER space
  inner.add(gltf.scene);
  buildLayers(); setView(45,28); onCut();
  document.getElementById('load').remove();
});

function buildLayers(){
  const host=document.getElementById('layers');
  GROUPS.forEach(([label,keys,col],i)=>{
    const id='lay'+i;
    const l=document.createElement('label');
    l.innerHTML='<input type="checkbox" id="'+id+'" checked>'+
      '<span class="sw" style="background:#'+col.toString(16).padStart(6,'0')+'"></span>'+label;
    l.querySelector('input').addEventListener('change',e=>{
      objs.forEach(o=>{ if(keys.indexOf(o.userData.key)>=0) o.visible=e.target.checked; });
    });
    host.appendChild(l);
  });
}

function setView(bearing,el){            // bearing = compass position of the CAMERA
  const b=bearing*Math.PI/180, e=el*Math.PI/180, d=RADIUS*2.4;
  camera.position.set(d*Math.cos(e)*Math.sin(b), d*Math.sin(e), -d*Math.cos(e)*Math.cos(b));
  controls.target.set(0,0,0); camera.up.set(0,1,0); controls.update(); resize();
}
document.querySelectorAll('button.v').forEach(b=>
  b.addEventListener('click',()=>setView(+b.dataset.b,+b.dataset.el)));

const cutEl=document.getElementById('cut'), cutV=document.getElementById('cutv');
function onCut(){
  const mm=+cutEl.value; cutV.textContent=mm>=2500?'off':mm;
  clip.constant = (mm>=2500?1e6:(mm/MM - CENTER.z));
}
cutEl.addEventListener('input',onCut);

const ray=new THREE.Raycaster(), ptr=new THREE.Vector2(), hud=document.getElementById('hud');
const DEF=hud.innerHTML;
cv.addEventListener('pointermove',ev=>{
  const r=cv.getBoundingClientRect();
  ptr.x=((ev.clientX-r.left)/r.width)*2-1; ptr.y=-((ev.clientY-r.top)/r.height)*2+1;
  ray.setFromCamera(ptr,camera);
  const hit=ray.intersectObjects(objs.filter(o=>o.visible),false)[0];
  if(!hit){ hud.innerHTML=DEF; return; }
  const k=hit.object.userData.key, b=hit.object.userData.bounds;
  const f=(v)=>Math.round(v), g=(v)=>Math.round(v*MM);
  hud.innerHTML='<b>'+(JP[k]||k)+'</b> <span>'+k+'</span><br>'+
    '<span>X</span> '+f(b[0])+'–'+f(b[2])+' px <span>/</span> '+g(b[0])+'–'+g(b[2])+' mm<br>'+
    '<span>Y</span> '+f(b[1])+'–'+f(b[3])+' px <span>/</span> '+g(b[1])+'–'+g(b[3])+' mm<br>'+
    '<span>Z</span> '+g(b[4])+'–'+g(b[5])+' mm <span>(仮設定)</span>';
});
cv.addEventListener('pointerleave',()=>hud.innerHTML=DEF);

const needle=document.getElementById('needle');
function resize(){
  const w=cv.clientWidth,h=cv.clientHeight;
  renderer.setSize(w,h,false);
  const a=w/h, s=RADIUS*1.18;
  camera.left=-s*a; camera.right=s*a; camera.top=s; camera.bottom=-s;
  camera.updateProjectionMatrix();
}
addEventListener('resize',resize);
matchMedia('(prefers-color-scheme:dark)').addEventListener('change',paint);
new MutationObserver(paint).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});

paint(); resize();
(function loop(){
  requestAnimationFrame(loop); controls.update();
  const nv=new THREE.Vector3(0,0,-1).applyQuaternion(camera.quaternion.clone().invert());
  needle.setAttribute('transform','rotate('+(Math.atan2(nv.x,nv.y)*180/Math.PI).toFixed(1)+' 24 24)');
  renderer.render(scene,camera);
})();
</script>
'''
HTML = HTML.replace('__GLB__', glb).replace('__PROV__', prov)
pathlib.Path('viewer/index.html').write_text(HTML, encoding='utf-8')
print('written', len(HTML), 'bytes')
