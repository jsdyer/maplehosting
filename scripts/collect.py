from common import ROOT,save,sha
import network_extract as source,maple_source,json,argparse,shutil

def main():
 p=argparse.ArgumentParser();p.add_argument('--seed',action='store_true');a=p.parse_args()
 if not a.seed:
  shutil.rmtree(source.CACHE);source.CACHE.mkdir();maple_source.main()
 d=json.loads((source.ROOT/'maplehosting-final-fixture.json').read_text());rows=[]
 for r in d['records']:
  asns=sorted({asn for ip in r['addresses'] for asn in ip['asns']});countries=sorted({ip['country'] for ip in r['addresses'] if ip.get('country')});networks=[f"AS{asn} · {d['holders'].get(str(asn)) or 'Holder unavailable'}" for asn in asns]
  row={**r,'id':r['domain'],'countries':countries or ['Unknown'],'networks':networks or ['Unknown'],'ipv6':'Yes' if any(ip['family']==6 for ip in r['addresses']) else 'No answer','dns_status':'Resolved' if r['addresses'] else 'No public answer','ranking_date':d['source']['ranking']['configuration']['endDate'],'list_id':d['source']['ranking']['list_id'],'source_url':'https://tranco-list.eu/list/'+d['source']['ranking']['list_id']}
  row['_fingerprint']=sha(json.dumps({'addresses':sorted(ip['ip'] for ip in r['addresses']),'countries':countries,'asns':asns,'rank':r['rank']},sort_keys=True).encode());rows.append(row)
 if len(rows)!=100:raise ValueError('Expected complete defined 100-domain sample')
 save(rows,sources=[{'label':'Dated Tranco ranking','url':d['source']['downloaded_prefix'],'sha256':d['source']['ranking_sha256'],'updated':d['source']['ranking']['configuration']['endDate']},{'label':'Google DNS-over-HTTPS','url':'https://developers.google.com/speed/public-dns/docs/doh'},{'label':'RIPEstat network observations','url':'https://stat.ripe.net/'},{'label':'IP geolocation by DB-IP (CC BY 4.0)','url':'https://db-ip.com','updated':d['geography']['date']}],coverage='First 100 .ca apex domains · Tranco '+d['source']['ranking']['list_id']+' dated '+d['source']['ranking']['configuration']['endDate'],warnings=['Network observations are not evidence of data residency or Canadian ownership. CDN/anycast, redirects and a single DNS resolver vantage affect interpretation.'],extra={'ranking':d['source'],'geography':d['geography']})
if __name__=='__main__':main()
