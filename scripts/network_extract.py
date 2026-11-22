#!/usr/bin/env python3
"""Research proof: official source extraction, cached in this scratch directory."""
import argparse,concurrent.futures,csv,hashlib,ipaddress,json,pathlib,time,urllib.request,urllib.parse
from datetime import datetime,timezone,timedelta
ROOT=pathlib.Path(__file__).resolve().parents[1]/'.cache'; ROOT.mkdir(exist_ok=True); CACHE=ROOT/'requests';CACHE.mkdir(exist_ok=True)
def iso():return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
def fetch(url):
 p=CACHE/(hashlib.sha256(url.encode()).hexdigest()+'.json')
 if p.exists():return json.loads(p.read_text())
 for attempt in range(3):
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'CoolCode public-data research (https://coolcode.ca/)'})
   with urllib.request.urlopen(req,timeout=30) as r:b=r.read(30_000_001)
   if len(b)>30_000_000:raise ValueError('Response too large')
   d=json.loads(b);p.write_text(json.dumps(d,separators=(',',':')));return d
  except Exception:
   if attempt==2:raise
   time.sleep(1+attempt)
def map4(fn,items):
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:return list(pool.map(fn,items))
def source(url):return {'url':url,'retrieved_at':iso()}
def attempt(url):
 try:return fetch(url),None
 except Exception as e:return None,type(e).__name__
def dns(item):
 rank,domain=item; rec={'rank':int(rank),'domain':domain,'dns':{},'addresses':[]}
 for kind,t in [('A',1),('AAAA',28)]:
  url='https://dns.google/resolve?'+urllib.parse.urlencode({'name':domain,'type':kind,'edns_client_subnet':'0.0.0.0/0'})
  d,error=attempt(url);rec['dns'][kind]={'status':d.get('Status') if d else None,'error':error,'source_url':url}
  if d:
   for a in d.get('Answer',[]):
    if a.get('type')==t:
     try:ip=ipaddress.ip_address(a['data'])
     except ValueError:continue
     if ip.is_global:rec['addresses'].append({'ip':str(ip),'family':ip.version,'ttl':a.get('TTL')})
 rec['observed_at']=iso();return rec
def ipinfo(ip):
 out={'ip':ip,'asns':[],'prefix':None,'countries':[],'geo_date':None,'errors':[]}
 for kind in ['network-info','maxmind-geo-lite']:
  url='https://stat.ripe.net/data/'+kind+'/data.json?'+urllib.parse.urlencode({'resource':ip})
  d,error=attempt(url)
  if error:out['errors'].append(kind+': '+error);continue
  if d.get('status')!='ok':out['errors'].append(kind+': API status not OK');continue
  d=d['data']
  if kind=='network-info':out.update(asns=[int(a) for a in d.get('asns',[])],prefix=d.get('prefix'))
  else:
   out['geo_date']=d.get('result_time');out['countries']=sorted({g['country'] for p in d.get('located_resources',[]) for g in p.get('locations',[]) if g.get('country') and g['country']!='?'})
 return out
def maple():
 meta=fetch('https://tranco-list.eu/api/lists/date/latest')
 # First 100 .ca names are within rank 22,474 in this list; prefix download is equivalent to filtering the full list up to this point.
 url=meta['download'].rsplit('/',1)[0]+'/100000'
 with urllib.request.urlopen(url,timeout=30) as response:lines=response.read(10_000_000).decode().splitlines()
 chosen=[r for r in csv.reader(lines) if len(r)==2 and r[1].lower().endswith('.ca')][:100]
 if len(chosen)!=100:raise ValueError('Top 100k did not contain 100 .ca domains; download full list')
 records=map4(dns,chosen);print('DNS complete',len(records),flush=True)
 ips=sorted({a['ip'] for r in records for a in r['addresses']});networks={r['ip']:r for r in map4(ipinfo,ips)};print('Network lookup complete',len(networks),flush=True)
 asns=sorted({a for n in networks.values() for a in n['asns']})
 def holder(asn):
  d,error=attempt(f'https://stat.ripe.net/data/as-overview/data.json?resource=AS{asn}');return str(asn), d.get('data',{}).get('holder') if d else None
 holders=dict(map4(holder,asns))
 for r in records:
  for a in r['addresses']:a.update(networks[a['ip']])
 data={'schema':1,'captured_at':iso(),'source':{'ranking':meta,'downloaded_prefix':url,'selected':len(chosen),'policy':'First 100 .ca domains by rank; DNS apex A and AAAA from Google DoH with ECS disabled. All returned public IPs enriched. A .ca suffix is not proof of a Canadian operator.'},'holders':holders,'records':records,'method':'RIPE RIS origin ASNs; RIPEstat MaxMind GeoLite estimated countries. Unknown countries remain empty, not Canadian. CDN/anycast can make geography misleading. DNS apex does not establish which host serves the actual website.'}
 (ROOT/'maplehosting-fixture.json').write_text(json.dumps(data,separators=(',',':'))+'\n');print('Saved maplehosting-fixture.json',flush=True)
ISPS={577:'Bell Canada',852:'TELUS',812:'Rogers',5645:'TekSavvy',5769:'Videotron',11260:'Eastlink',21949:'Beanfield'}
def apnic(asn,metric):
 v6=metric=='ipv6'; url=f'https://stats.labs.apnic.net/cgi-bin/json-table{"-v6" if v6 else ""}.pl?x=CA{asn}'
 d,error=attempt(url)
 if not d or not isinstance(d.get('data'),list):return {'metric':metric,'source_url':url,'date':None,'samples':None,'rate':None,'error':error or 'No data','history':[]}
 rows=[]
 for p in d['data']:
  if p.get('cc')!='CA' or str(p.get('as','')).replace('AS','')!=str(asn):continue
  raw=p.get('raw' if v6 else '1_day')
  if not raw or not p.get('date'):continue
  seen=raw.get('seen');yes=raw.get('capable' if v6 else 'validating')
  if not isinstance(seen,(int,float)) or not isinstance(yes,(int,float)) or not 0<=yes<=seen:continue
  rows.append({'date':p['date'],'samples':int(seen),'positive':int(yes),'rate':100*yes/seen if seen else None,'partial_positive':raw.get('partial_validating') if not v6 else None})
 rows.sort(key=lambda p:p['date'])
 if not rows:return {'metric':metric,'source_url':url,'date':None,'samples':None,'rate':None,'error':'No valid rows','history':[]}
 latest=datetime.fromisoformat(rows[-1]['date']);cutoff=(latest-timedelta(days=29)).date().isoformat();window=[p for p in rows if p['date']>=cutoff];samples=sum(p['samples'] for p in window);positive=sum(p['positive'] for p in window)
 return {'metric':metric,'source_url':url,'date':rows[-1]['date'],'window_start':cutoff,'window_days':len(window),'samples':samples,'positive':positive,'rate':100*positive/samples if samples else None,'error':None,'history':rows[-366:]}
def rpki(asn):
 full=ROOT/'rpki-full-fixture.json'
 if full.exists():return next(r for r in json.loads(full.read_text())['records'] if r['asn']==asn)
 url=f'https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS{asn}';d,error=attempt(url)
 if not d or d.get('status')!='ok':return {'sampled':0,'valid':None,'unknown':None,'invalid':None,'error':error or 'API error','source_url':url}
 d=d['data'];latest=d['query_endtime'];eligible=sorted({p['prefix'] for p in d.get('prefixes',[]) if any(t['starttime']<=latest<=t['endtime'] for t in p['timelines'])})
 # Fixed 32-prefix cryptographic-hash sample; label as sampled coverage, never total-AS coverage.
 selected=sorted(eligible,key=lambda p:hashlib.sha256(f'{asn}|{p}'.encode()).hexdigest())[:32]
 def validate(prefix):
  source_url='https://stat.ripe.net/data/rpki-validation/data.json?'+urllib.parse.urlencode({'resource':asn,'prefix':prefix})
  x,err=attempt(source_url);status=x.get('data',{}).get('status') if x else None
  if status not in ['valid','invalid_asn','invalid_length','unknown']:status=None
  return {'prefix':prefix,'status':status,'source_url':source_url,'observed_at':iso(),'error':err}
 checks=map4(validate,selected);valid=sum(p['status']=='valid' for p in checks);unknown=sum(p['status']=='unknown' for p in checks);invalid=sum(p['status'] in ('invalid_asn','invalid_length') for p in checks);complete=valid+unknown+invalid
 return {'source_url':url,'route_date':latest,'observed_at':iso(),'total_announced':len(eligible),'sampled':len(selected),'checked':complete,'valid':valid,'unknown':unknown,'invalid':invalid,'valid_pct':100*valid/complete if complete else None,'authorized_pct':100*(valid+invalid)/complete if complete else None,'policy':'32 announced prefixes selected by SHA256(asn|prefix); unweighted sample; valid = ROA authorizes observed origin and length. Covered = valid or invalid. This does not measure route filtering.','checks':checks}
def isp():
 records=[]
 for asn,name in ISPS.items():
  metrics=map4(lambda metric:apnic(asn,metric),['ipv6','dnssec']);record={'asn':asn,'provider':name,**{m['metric']:m for m in metrics},'rpki':rpki(asn)};records.append(record)
  (ROOT/'ispreportcard-full-fixture.json').write_text(json.dumps({'schema':1,'captured_at':iso(),'records':records,'attribution':'APNIC measurements reused with attribution; RIPE NCC RIS and Routinator validation.'},separators=(',',':'))+'\n')
  print(name,[(m['metric'],m['date'],m['samples'],m['rate']) for m in metrics],'RPKI',record['rpki'].get('checked'),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['maple','isp']);a=p.parse_args();globals()[a.mode]()
