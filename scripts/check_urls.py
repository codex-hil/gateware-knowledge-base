#!/usr/bin/env python3
"""Check upstream URLs; distinguish redirects, gone pages, and access failures."""
import argparse
import concurrent.futures
import datetime
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

from kb import ROOT, load, repository_key, walk

def classify(url, final, code):
    if code in (404,410): return 'broken'
    if code in (401,403,429): return 'inaccessible'
    if code >= 400: return 'transient_error'
    if any(x in urlsplit(final).path.lower() for x in ('sign_in','login','signin')):
        return 'inaccessible'
    if repository_key(url) != repository_key(final): return 'moved'
    return 'reachable'

def check(url, timeout=15):
    final=url
    for method in ('HEAD','GET'):
        try:
            req=urllib.request.Request(url,method=method,headers={'User-Agent':'gateware-knowledge-base-link-check/1.0'})
            with urllib.request.urlopen(req,timeout=timeout) as response:
                code=response.status;final=response.url
            if method=='HEAD' and code in (405,501): continue
            return dict(url=url,final_url=final,http_status=code,status=classify(url,final,code))
        except urllib.error.HTTPError as exc:
            if method=='HEAD' and exc.code in (403,404,405,501): continue
            return dict(url=url,final_url=exc.url,http_status=exc.code,status=classify(url,exc.url,exc.code))
        except (urllib.error.URLError,TimeoutError,OSError) as exc:
            return dict(url=url,final_url=final,http_status=None,status='transient_error',error=str(exc))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all-evidence',action='store_true',help='Also check pinned evidence links; default checks repository URLs and aliases.')
    parser.add_argument('--output',default='reports/url-check.json')
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--timeout',type=int,default=15)
    parser.add_argument('--strict',action='store_true',help='Fail on moved/broken URLs; access/transient failures remain inconclusive.')
    args=parser.parse_args()
    urls=set()
    for _,data in load():
        if data['kind']=='project':urls.update([data['repository'],*data['aliases']])
        if args.all_evidence:
            urls.update(v['url'] for v in walk(data) if 'url' in v)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(args.workers,16))) as pool:
        results=list(pool.map(lambda u:check(u,args.timeout),sorted(urls)))
    report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'scope':'all evidence' if args.all_evidence else 'canonical repositories and aliases',
            'note':'HTTP reachability is not evidence of IP quality. Access failures are inconclusive; redirects require review, never automatic rewriting.',
            'results':results}
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2)+'\n')
    counts={s:sum(r['status']==s for r in results) for s in sorted({r['status'] for r in results})}
    print(json.dumps(counts,sort_keys=True))
    return int(args.strict and any(r['status'] in ('broken','moved') for r in results))

if __name__=='__main__':sys.exit(main())
