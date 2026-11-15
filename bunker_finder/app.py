"""Bunker Finder: a Flask site that tracks your location and finds nearby bunkers.

Bunker data comes from OpenStreetMap through the Overpass API.
Run:  pip install -r requirements.txt && python app.py
Open: http://127.0.0.1:5000
Note: browsers only allow geolocation on https or localhost.
"""
import math

import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
RADII_M = [5_000, 25_000, 100_000, 300_000]  # widen the search until something is found
MAX_RESULTS = 25


def haversine_m(lat1, lon1, lat2, lon2):
    r = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def bearing_deg(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def query_overpass(lat, lon, radius):
    q = f"""
    [out:json][timeout:25];
    (
      nwr["military"="bunker"](around:{radius},{lat},{lon});
      nwr["building"="bunker"](around:{radius},{lat},{lon});
      nwr["historic"="bunker"](around:{radius},{lat},{lon});
      nwr["bunker_type"](around:{radius},{lat},{lon});
    );
    out center tags;
    """
    last_err = None
    for url in OVERPASS_URLS:
        try:
            r = requests.post(url, data={"data": q}, timeout=30,
                              headers={"User-Agent": "bunker-finder-demo/1.0"})
            r.raise_for_status()
            return r.json().get("elements", [])
        except (requests.RequestException, ValueError) as e:
            last_err = e
    raise RuntimeError(f"Overpass unavailable: {last_err}")


@app.get("/api/bunkers")
def api_bunkers():
    try:
        lat = float(request.args["lat"])
        lon = float(request.args["lon"])
    except (KeyError, ValueError):
        return jsonify(error="lat and lon are required numbers"), 400
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return jsonify(error="lat/lon out of range"), 400

    try:
        for radius in RADII_M:
            elements = query_overpass(lat, lon, radius)
            if elements:
                break
    except RuntimeError as e:
        return jsonify(error=str(e)), 502

    bunkers = []
    for el in elements:
        blat = el.get("lat") or (el.get("center") or {}).get("lat")
        blon = el.get("lon") or (el.get("center") or {}).get("lon")
        if blat is None or blon is None:
            continue
        tags = el.get("tags", {})
        bunkers.append({
            "id": f"{el['type']}/{el['id']}",
            "name": tags.get("name") or tags.get("bunker_type", "").replace("_", " ").title() or "Unnamed bunker",
            "lat": blat,
            "lon": blon,
            "distance_m": round(haversine_m(lat, lon, blat, blon)),
            "bearing": round(bearing_deg(lat, lon, blat, blon)),
            "tags": tags,
        })
    bunkers.sort(key=lambda b: b["distance_m"])
    return jsonify(bunkers=bunkers[:MAX_RESULTS], total=len(bunkers), radius_m=radius)


@app.get("/")
def index():
    return render_template_string(PAGE)


PAGE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bunker Finder</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root{--bg:#10141a;--panel:#1a212b;--panel2:#232c39;--text:#e6ebf2;--mute:#8d9bb0;--acc:#f5a524;--ok:#3ecf8e}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,Segoe UI,sans-serif;background:var(--bg);color:var(--text);height:100vh;display:flex;flex-direction:column}
header{display:flex;align-items:center;gap:14px;padding:12px 18px;background:var(--panel);border-bottom:1px solid #2b3646}
header h1{font-size:1.15rem;margin:0;flex:1;letter-spacing:.5px}
header h1 span{color:var(--acc)}
button{background:var(--acc);color:#1b1300;border:0;border-radius:8px;padding:10px 18px;font-weight:700;cursor:pointer}
button.stop{background:#e5484d;color:#fff}
button.ghost{background:var(--panel2);color:var(--text)}
button:disabled{opacity:.5;cursor:default}
#status{font-size:.85rem;color:var(--mute)}
main{flex:1;display:grid;grid-template-columns:360px 1fr;min-height:0}
aside{background:var(--panel);overflow-y:auto;border-right:1px solid #2b3646}
#map{height:100%}
.item{padding:12px 16px;border-bottom:1px solid #2b3646;cursor:pointer}
.item:hover,.item.sel{background:var(--panel2)}
.item .n{font-weight:600}
.item .d{color:var(--mute);font-size:.85rem;margin-top:2px}
.badge{display:inline-block;background:var(--ok);color:#06210f;border-radius:99px;font-size:.7rem;padding:1px 8px;margin-left:6px;font-weight:700}
#detail{padding:16px;background:var(--panel2);border-bottom:2px solid var(--acc)}
#detail h2{margin:0 0 4px;font-size:1.1rem}
#detail table{width:100%;font-size:.85rem;border-collapse:collapse;margin:10px 0}
#detail td{padding:4px 0;border-bottom:1px solid #2f3a4b;vertical-align:top;word-break:break-word}
#detail td:first-child{color:var(--mute);width:42%}
.empty{padding:24px 16px;color:var(--mute)}
a.btn{display:inline-block;background:var(--acc);color:#1b1300;padding:8px 14px;border-radius:8px;text-decoration:none;font-weight:700;font-size:.85rem}
@media(max-width:800px){main{grid-template-columns:1fr;grid-template-rows:45% 55%}aside{order:2}}
</style></head><body>
<header>
  <h1>&#9763; <span>Bunker</span> Finder</h1>
  <span id="status">Idle</span>
  <button id="go">Initialize finder</button>
</header>
<main>
  <aside><div id="detail" hidden></div><div id="list"><div class="empty">Press “Initialize finder” and allow location access. The nearest bunkers will appear here.</div></div></aside>
  <div id="map"></div>
</main>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const $ = id => document.getElementById(id);
const map = L.map('map').setView([20,0],2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; OpenStreetMap contributors'}).addTo(map);
let watchId=null, me=null, meCircle=null, markers={}, bunkers=[], selected=null, lastFetch=null, line=null, firstFix=true;

const fmt = m => m<1000 ? m+' m' : (m/1000).toFixed(m<10000?2:1)+' km';
const dirs = ['N','NE','E','SE','S','SW','W','NW'];
const compass = b => dirs[Math.round(b/45)%8];
const el = (tag, text, cls) => { const e=document.createElement(tag); if(text!=null) e.textContent=text; if(cls) e.className=cls; return e; };
const setStatus = t => $('status').textContent = t;

$('go').onclick = () => watchId===null ? start() : stop();

function start(){
  if(!navigator.geolocation){ setStatus('Geolocation not supported'); return; }
  setStatus('Locating…');
  $('go').textContent='Stop tracking'; $('go').className='stop'; firstFix=true;
  watchId = navigator.geolocation.watchPosition(onPos, e=>{ setStatus('Location error: '+e.message); stop(); },
    {enableHighAccuracy:true, maximumAge:5000, timeout:20000});
}
function stop(){
  if(watchId!==null) navigator.geolocation.clearWatch(watchId);
  watchId=null; $('go').textContent='Initialize finder'; $('go').className='';
}

function onPos(p){
  const {latitude:lat, longitude:lon, accuracy} = p.coords;
  me=[lat,lon];
  if(!meCircle){
    meCircle=L.circleMarker(me,{radius:8,color:'#fff',weight:2,fillColor:'#3b82f6',fillOpacity:1}).addTo(map).bindTooltip('You');
  } else meCircle.setLatLng(me);
  setStatus(`Tracking (±${Math.round(accuracy)} m)`);
  // refetch on first fix or after moving >500 m
  if(!lastFetch || distance(lastFetch,me)>500){ lastFetch=me; fetchBunkers(lat,lon); }
  else { updateDistances(); }
}

function distance(a,b){ return map.distance(a,b); }

async function fetchBunkers(lat,lon){
  setStatus('Searching for bunkers…');
  try{
    const r = await fetch(`/api/bunkers?lat=${lat}&lon=${lon}`);
    const j = await r.json();
    if(!r.ok) throw new Error(j.error||r.statusText);
    bunkers=j.bunkers; render(j);
    setStatus(`Tracking · ${j.total} found within ${fmt(j.radius_m)}`);
    if(bunkers.length){ if(firstFix){ select(bunkers[0].id,true); firstFix=false; } }
  }catch(e){ setStatus('Search failed: '+e.message); lastFetch=null; }
}

function updateDistances(){
  bunkers.forEach(b=>b.distance_m=Math.round(distance(me,[b.lat,b.lon])));
  bunkers.sort((a,b)=>a.distance_m-b.distance_m);
  render({total:bunkers.length});
}

function render(){
  const list=$('list'); list.replaceChildren();
  Object.values(markers).forEach(m=>m.remove()); markers={};
  if(!bunkers.length){ list.append(el('div','No bunkers found within 300 km.','empty')); return; }
  bunkers.forEach((b,i)=>{
    const item=el('div',null,'item'+(b.id===selected?' sel':'')); item.dataset.id=b.id;
    const n=el('div',b.name,'n'); if(i===0) n.append(el('span','NEAREST','badge'));
    item.append(n, el('div',`${fmt(b.distance_m)} ${compass(b.bearing)}`,'d'));
    item.onclick=()=>select(b.id,true); list.append(item);
    const m=L.marker([b.lat,b.lon]).addTo(map).bindTooltip(b.name); m.on('click',()=>select(b.id,false)); markers[b.id]=m;
  });
  if(selected) showDetail(selected);
}

function select(id,pan){
  selected=id; showDetail(id);
  document.querySelectorAll('.item').forEach(i=>i.classList.toggle('sel',i.dataset.id===id));
  const b=bunkers.find(x=>x.id===id); if(!b) return;
  if(line) line.remove();
  if(me) line=L.polyline([me,[b.lat,b.lon]],{color:'#f5a524',dashArray:'6 8'}).addTo(map);
  if(pan) map.fitBounds(L.latLngBounds([me||[b.lat,b.lon],[b.lat,b.lon]]).pad(0.3),{maxZoom:16});
}

function showDetail(id){
  const b=bunkers.find(x=>x.id===id), d=$('detail'); if(!b){ d.hidden=true; return; }
  d.hidden=false; d.replaceChildren();
  d.append(el('h2',b.name), el('div',`${fmt(b.distance_m)} to the ${compass(b.bearing)} (${b.bearing}°)`,'d'));
  const t=el('table');
  const rows=[['Coordinates',`${b.lat.toFixed(5)}, ${b.lon.toFixed(5)}`],...Object.entries(b.tags).map(([k,v])=>[k,v])];
  rows.forEach(([k,v])=>{ const tr=el('tr'); tr.append(el('td',k),el('td',v)); t.append(tr); });
  d.append(t);
  const a=el('a','Open directions','btn'); a.target='_blank'; a.rel='noopener';
  a.href=`https://www.openstreetmap.org/directions?from=${me?me.join(','):''}&to=${b.lat},${b.lon}`;
  const o=el('a','View on OSM','btn'); o.target='_blank'; o.rel='noopener'; o.style.marginLeft='8px';
  o.href=`https://www.openstreetmap.org/${b.id}`;
  d.append(a,o);
}
</script></body></html>"""

if __name__ == "__main__":
    app.run(debug=True)
