#!/usr/bin/env python3
from __future__ import annotations
import json,re,socket,threading,time
from collections import deque
from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from socketserver import TCPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parent; CONFIG_PATH=ROOT/'config.json'; PREFIX_PATH=ROOT/'data'/'prefixes.json'
SPOT_RE=re.compile(r'DX de\s+([A-Z0-9/]+)[-:# ]+\s*([0-9.]+)\s+([A-Z0-9/]+)\s*(.*?)\s+(\d{4})Z',re.I)
BANDS=[(1800,2000,'160m'),(3500,4000,'80m'),(5000,5500,'60m'),(7000,7300,'40m'),(10100,10150,'30m'),(14000,14350,'20m'),(18068,18168,'17m'),(21000,21450,'15m'),(24890,24990,'12m'),(28000,29700,'10m'),(50000,54000,'6m')]
@dataclass
class Spot:
 id:str;timestamp:str;reporter:str;dx:str;frequency_khz:float;band:str;comment:str;source_lat:float;source_lon:float;source_name:str;target_lat:float;target_lon:float;target_name:str
class PrefixLookup:
 def __init__(self,path):
  self.items=[]
  for e in json.loads(path.read_text()):
   for p in e['prefixes']:self.items.append((p.upper(),e))
  self.items.sort(key=lambda x:len(x[0]),reverse=True)
 def locate(self,call):
  call=call.upper().split('/')[-1]
  for p,e in self.items:
   if call.startswith(p):return float(e['lat']),float(e['lon']),e['name']
def band_for(k):return next((n for lo,hi,n in BANDS if lo<=k<=hi),'other')
def maidenhead(loc):
 loc=loc.strip().upper()
 if not re.fullmatch(r'[A-R]{2}[0-9]{2}([A-X]{2})?',loc):return None
 lon=(ord(loc[0])-65)*20-180+int(loc[2])*2;lat=(ord(loc[1])-65)*10-90+int(loc[3])
 if len(loc)==6:return lat+(ord(loc[5])-65)/24+1/48,lon+(ord(loc[4])-65)/12+1/24
 return lat+.5,lon+1
class Store:
 def __init__(self,cfg,lookup):self.cfg=cfg;self.lookup=lookup;self.lock=threading.Lock();self.spots=deque(maxlen=cfg['display'].get('maximum_spots',500));self.cluster_status='disabled';self.last_cluster_line='';self.demo=False
 def station(self):
  s=self.cfg['station']
  if s.get('latitude') is not None and s.get('longitude') is not None:return float(s['latitude']),float(s['longitude']),s.get('callsign') or 'My station'
  m=maidenhead(s.get('locator',''))
  return (m[0],m[1],s.get('callsign') or s.get('locator')) if m else None
 def add(self,reporter,dx,freq,comment='',timestamp=None):
  try:f=float(freq)
  except:return False
  if f<1000:f*=1000
  src=self.lookup.locate(reporter) or self.station();dst=self.lookup.locate(dx)
  if not src or not dst:return False
  ts=timestamp or datetime.now(timezone.utc).isoformat();s=Spot(f'{reporter}-{dx}-{time.time_ns()}',ts,reporter.upper(),dx.upper(),round(f,3),band_for(f),str(comment)[:100],src[0],src[1],src[2],dst[0],dst[1],dst[2])
  with self.lock:self.spots.appendleft(s)
  return True
 def load_demo(self):
  if self.demo:return
  for i,(a,b,f,c) in enumerate([('ZL4AAA','JA1ABC',14074,'FT8'),('VK3DX','DL1XYZ',21074,'FT8'),('K6TEST','ZL1ABC',28400,'SSB'),('G4AAA','PY2DX',18100,'CW'),('OH2AAA','VK6DX',10136,'FT8'),('W1AW','ZS6ABC',14200,'SSB'),('JA3AAA','LU5DX',7005,'CW'),('ZL2TEST','VK2ABC',50110,'6m')]):self.add(a,b,f,c,datetime.fromtimestamp(time.time()-i*95,tz=timezone.utc).isoformat())
  self.demo=True
 def payload(self):
  cutoff=time.time()-self.cfg['display'].get('spot_max_age_minutes',30)*60
  with self.lock:items=[asdict(s) for s in self.spots if datetime.fromisoformat(s.timestamp).timestamp()>=cutoff]
  if not items and self.cfg['display'].get('demo_when_empty',True):self.load_demo();items=[asdict(s) for s in self.spots]
  counts={}
  for s in items:counts[s['band']]=counts.get(s['band'],0)+1
  return {'updated':datetime.now(timezone.utc).isoformat(),'mode':'live' if self.cfg['cluster'].get('enabled') else 'local/demo','cluster_status':self.cluster_status,'spots':items,'counts':counts}
class Cluster(threading.Thread):
 daemon=True
 def __init__(self,store):super().__init__();self.s=store
 def run(self):
  c=self.s.cfg['cluster']
  if not c.get('enabled'):return
  while True:
   try:
    self.s.cluster_status='connecting'
    with socket.create_connection((c['host'],int(c.get('port',7300))),timeout=20) as sk:
     sk.sendall(((c.get('login_callsign') or self.s.cfg['station'].get('callsign') or 'NOCALL')+'\n').encode());sk.settimeout(60);self.s.cluster_status='connected';buf=''
     while True:
      raw=sk.recv(4096)
      if not raw:raise ConnectionError('cluster closed')
      buf+=raw.decode(errors='ignore');parts=buf.split('\n');buf=parts.pop()
      for line in parts:
       self.s.last_cluster_line=line[-180:];m=SPOT_RE.search(line)
       if m:self.s.add(m.group(1),m.group(3),m.group(2),m.group(4))
   except Exception as e:self.s.cluster_status=f'error: {e}';time.sleep(c.get('reconnect_seconds',30))
class LocalHTTPServer(ThreadingHTTPServer):
 def server_bind(self):
  TCPServer.server_bind(self);self.server_name=str(self.server_address[0]);self.server_port=int(self.server_address[1])
class Handler(SimpleHTTPRequestHandler):
 store=None
 def translate_path(self,path):
  p=path.split('?',1)[0]
  if p=='/':p='/static/index.html'
  return str(ROOT/p.lstrip('/'))
 def js(self,obj,status=200):
  d=json.dumps(obj,separators=(',',':')).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(d)));self.end_headers();self.wfile.write(d)
 def do_GET(self):
  if self.path.startswith('/api/propagation'):return self.js(self.store.payload())
  if self.path.startswith('/api/status'):return self.js({'cluster_status':self.store.cluster_status,'last_cluster_line':self.store.last_cluster_line})
  return super().do_GET()
 def do_POST(self):
  if self.path.split('?',1)[0]!='/api/spots':return self.js({'error':'not found'},404)
  try:
   body=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}');rows=body if isinstance(body,list) else [body];ok=0
   for r in rows:ok+=bool(self.store.add(r.get('reporter',''),r.get('dx',''),r.get('frequency_khz',r.get('frequency','')),r.get('comment',''),r.get('timestamp')))
   self.js({'accepted':ok,'received':len(rows)})
  except Exception as e:self.js({'error':str(e)},400)
 def log_message(self,fmt,*args):print('[HTTP]',fmt%args)
def main():
 cfg=json.loads(CONFIG_PATH.read_text());store=Store(cfg,PrefixLookup(PREFIX_PATH));Handler.store=store;Cluster(store).start();host=cfg['server'].get('host','127.0.0.1');port=int(cfg['server'].get('port',8765));print(f'HRPU Propagation: http://{host}:{port}');LocalHTTPServer((host,port),Handler).serve_forever()
if __name__=='__main__':main()
