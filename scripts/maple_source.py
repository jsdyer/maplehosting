#!/usr/bin/env python3
"""Reproducible Maple fixture, DB-IP geography (CCBY4.0), RIPE RIS origin networks."""
import bisect,csv,gzip,hashlib,ipaddress,json,urllib.request,urllib.parse
from network_extract import ROOT,fetch,attempt,map4,dns,iso
from datetime import datetime,timezone
GEO_MONTH=datetime.now(timezone.utc).strftime('%Y-%m')
GEO_URL=f'https://download.db-ip.com/free/dbip-country-lite-{GEO_MONTH}.csv.gz'
def geo_for(ips,path):
 targets={4:[],6:[]}
 for ip in ips:
  a=ipaddress.ip_address(ip);targets[a.version].append((int(a),ip))
 for family in targets:targets[family].sort()
 numbers={f:[p[0] for p in v] for f,v in targets.items()};result={}
 with gzip.open(path,'rt') as f:
  for row in csv.reader(f):
   start=ipaddress.ip_address(row[0]);end=ipaddress.ip_address(row[1]);family=start.version
   if family!=end.version:raise ValueError('Mixed-family range')
   i=bisect.bisect_left(numbers[family],int(start))
   while i<len(numbers[family]) and numbers[family][i]<=int(end):
    result[targets[family][i][1]]=row[2] if row[2]!='ZZ' else None;i+=1
 return result

def network(ip):
 url='https://stat.ripe.net/data/network-info/data.json?'+urllib.parse.urlencode({'resource':ip});d,error=attempt(url)
 data=d.get('data',{}) if d else {};return {'ip':ip,'asns':[int(a) for a in data.get('asns',[])],'prefix':data.get('prefix'),'network_source':url,'network_time':d.get('time') if d else None,'error':error}
def main():
 meta=fetch('https://tranco-list.eu/api/lists/date/latest');url=meta['download'].rsplit('/',1)[0]+'/100000'
 # Previously downloaded ranking is immutable by ID. A fresh run downloads this source.
 if meta['list_id']=='46YLX' and (ROOT/'tranco-top100k.csv').exists():raw=(ROOT/'tranco-top100k.csv').read_bytes()
 else:
  with urllib.request.urlopen(url,timeout=45) as f:raw=f.read(10000000)
 chosen=[r for r in csv.reader(raw.decode().splitlines()) if len(r)==2 and r[1].lower().endswith('.ca')][:100]
 if len(chosen)!=100:raise ValueError('Download full Tranco1m when fewer than100 .ca names are found')
 records=map4(dns,chosen);ips=sorted({a['ip'] for r in records for a in r['addresses']});print('DNS done',len(records),len(ips),flush=True)
 networks={r['ip']:r for r in map4(network,ips)};print('Networks done',len(networks),flush=True)
 path=ROOT/f'dbip-country-lite-{GEO_MONTH}.csv.gz'
 if not path.exists():
  req=urllib.request.Request(GEO_URL,headers={'User-Agent':'CoolCode public-data research (https://coolcode.ca/)','Accept':'application/gzip,application/octet-stream,*/*'})
  with urllib.request.urlopen(req,timeout=45) as f:path.write_bytes(f.read(15000000))
 countries=geo_for(ips,path)
 asns=sorted({a for n in networks.values() for a in n['asns']})
 def holder(asn):
  d,error=attempt(f'https://stat.ripe.net/data/as-overview/data.json?resource=AS{asn}');return str(asn), d.get('data',{}).get('holder') if d else None
 holders=dict(map4(holder,asns))
 for r in records:
  for a in r['addresses']:a.update(networks[a['ip']],country=countries.get(a['ip']),geo_date=GEO_MONTH,geo_source=GEO_URL)
  cs={a['country'] for a in r['addresses'] if a['country']};unknown=any(a['country'] is None for a in r['addresses'])
  r['country_group']='Unknown or incomplete' if not cs or unknown else 'Canada only' if cs=={'CA'} else 'Outside Canada only' if 'CA' not in cs else 'Canada and abroad'
 data={'schema':1,'captured_at':iso(),'source':{'ranking':meta,'downloaded_prefix':url,'ranking_sha256':hashlib.sha256(raw).hexdigest(),'selected':len(chosen),'policy':'First 100 .ca domains in the dated ranking, selected from its first 100,000 entries; collection fails if that prefix is insufficient. DNS apex A and AAAA from Google DoH with ECS disabled. All returned public IPs enriched. A .ca suffix is not proof of a Canadian operator.'},'geography':{'provider':'DB-IP Country Lite','date':GEO_MONTH,'source_url':GEO_URL,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'attribution_url':'https://db-ip.com','license':'CC BY4.0'},'holders':holders,'records':records,'method':'RIPE RIS origin ASNs and DB-IP Country Lite estimated countries. Unknown stays null. CDN and anycast geography is misleading; this is not data residency. DNS apex does not establish which host serves the actual website. DNS uses one Google resolver vantage with ECS disabled.'}
 (ROOT/'maplehosting-final-fixture.json').write_text(json.dumps(data,separators=(',',':'))+'\n');print('Saved maplehosting-final-fixture.json',len(records),flush=True)
if __name__=='__main__':main()
