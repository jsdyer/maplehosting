#!/usr/bin/env python3
"""Research: validate every currently visible ISP announcement against one dated VRP export."""
import hashlib,ipaddress,json
from network_extract import ROOT,ISPS,fetch,map4,iso
SOURCE='https://rpki-validator.ripe.net/api/export.json'
def ancestors(network):
 n=int(network.network_address);bits=network.max_prefixlen
 for length in range(network.prefixlen+1):
  yield (network.version,n>>(bits-length),length)
def routes(asn):
 url=f'https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS{asn}'
 d=fetch(url)['data'];latest=d['query_endtime'];p=sorted({q['prefix'] for q in d['prefixes'] if any(t['starttime']<=latest<=t['endtime'] for t in q['timelines'])});return asn,{'source_url':url,'date':latest,'prefixes':p}
def main():
 allroutes=dict(map4(routes,ISPS));needed=set()
 for r in allroutes.values():
  for p in r['prefixes']:needed.update(ancestors(ipaddress.ip_network(p)))
 raw=(ROOT/'rpki-validator.json').read_bytes();full=json.loads(raw);sh=hashlib.sha256(raw).hexdigest();index={}
 for roa in full['roas']:
  net=ipaddress.ip_network(roa['prefix']);key=(net.version,int(net.network_address)>>(net.max_prefixlen-net.prefixlen),net.prefixlen)
  if key in needed:index.setdefault(key,[]).append({'asn':int(str(roa['asn']).replace('AS','')),'prefix':roa['prefix'],'max_length':int(roa['maxLength'])})
 records=[]
 for asn,info in allroutes.items():
  checks=[]
  for prefix in info['prefixes']:
   net=ipaddress.ip_network(prefix);cover=[r for key in ancestors(net) for r in index.get(key,[])];matching=[r for r in cover if r['asn']==asn]
   status='valid' if any(net.prefixlen<=r['max_length'] for r in matching) else 'invalid_length' if matching else 'invalid_asn' if cover else 'unknown'
   checks.append({'prefix':prefix,'family':net.version,'status':status,'covering_roas':cover})
  count=len(checks);valid=sum(p['status']=='valid' for p in checks);unknown=sum(p['status']=='unknown' for p in checks);invalid=count-valid-unknown
  records.append({'asn':asn,'provider':ISPS[asn],'source_url':info['source_url'],'route_date':info['date'],'vrp_source_url':SOURCE,'vrp_date':full['metadata']['generatedTime'],'vrp_sha256':sh,'sampled':count,'checked':count,'total_announced':count,'valid':valid,'unknown':unknown,'invalid':invalid,'valid_pct':100*valid/count if count else None,'covered_pct':100*(valid+invalid)/count if count else None,'policy':'All prefixes visible at RIPE RIS latest query time; unweighted prefix-origin pairs. Valid means an origin/length-authorizing VRP exists; covered includes invalid announcements. Does not measure ISP route filtering.','checks':checks})
  print(asn,count,valid,unknown,invalid,flush=True)
 (ROOT/'rpki-full-fixture.json').write_text(json.dumps({'captured_at':iso(),'records':records},separators=(',',':'))+'\n')
if __name__=='__main__':main()
