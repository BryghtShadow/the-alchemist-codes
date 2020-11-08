# coding=utf8
import hashlib
import base64
import json
import csv
import io
import re
import datetime
from urllib.parse import quote_plus

import requests
import requests_cache
# https://github.com/shoeffner/requests-url-cache
from requests_url_cache import PerURLCacheSession, register_url

requests_cache.install_cache('update', backend='sqlite', session_factory=PerURLCacheSession)

def getfile(project_name, file_path):
    fmt = "%a, %d %b %Y %H:%M:%S %Z"
    api_base = 'https://gitlab.com/api/v4'
    pid = quote_plus(project_name)
    fid = quote_plus(file_path)
    url = f'{api_base}/projects/{pid}/repository/files/{fid}?ref=master'
    resp = requests.get(url)
    data = resp.json()
    cached_last_commit_id = data['last_commit_id']
    print(','.join([project_name.split('/')[-1], file_path, cached_last_commit_id[:8]]))
    if resp.from_cache:
        old_date = datetime.datetime.strptime(resp.headers.get('Date'), fmt)
        resp = requests.head(url)
        head = resp.headers
        server_last_commit_id = head.get('x-gitlab-last-commit-id')
        new_date = datetime.datetime.strptime(head.get('Date'), fmt)
        delta = new_date - old_date
        if cached_last_commit_id != server_last_commit_id:
            print(f"Response was cached on {old_date}")
            print(f"Last Commit ID differs between cache ({cached_last_commit_id[:8]}) and server ({server_last_commit_id[:8]}).")
            register_url(url, 0) # Mark as "expired".
            requests_cache.remove_expired_responses()
            resp = requests.get(url, expire_after='default')
            data = resp.json()
    return data

def main(iname):
    obj = {}
    hashes = {}

    groups = {
        'AF': 'Artifact',
        'IT': 'Item',
    }

    group_key = iname.split('_')[0]
    group_name = groups.get(group_key)
    if not group_name:
        return

    for server, project in {
        'gl': 'Global',
        'jp': 'Japan',
    }.items():
        data = getfile(f'the-alchemist-codes/{project}', 'Data/MasterParam')
        base64_content = data['content']
        content = base64.b64decode(base64_content).decode('utf-8-sig')
        mp = json.loads(content)
        for af in mp[group_name]:
            if af['iname'] == iname:
                name = af.pop('name', None)
                spec = af.pop('spec', None)
                # tag = af.pop('tag', None)
                txt = json.dumps(af, sort_keys=True, ensure_ascii=False, separators=(',',':'))
                obj[server] = txt
    languages = [
        'english',
        'japanese',
    ]
    for lang in languages:
        data = getfile('the-alchemist-codes/Global', f'Loc/{lang}/LocalizedMasterParam')
        base64_content = data['content']
        content = base64.b64decode(base64_content).decode('utf-8-sig')
        loc = io.StringIO(content)
        reader = csv.reader(loc, delimiter="\t")
        for [key, val] in reader:
            m = re.match(f"SRPG_{group_name}Param_{iname}_(.+)", key)
            if not m:
                continue
            param = m.group(1).lower()
            obj.setdefault('loc', {}).setdefault(param, {})[lang] = val
    txt = json.dumps(obj['loc'], sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    obj['loc'] = txt

    # TODO: Directly update wiki instead of dumping output to terminal.
    print("{{#invoke:Data|insert")
    for k, v in obj.items():
        print(f"| {k} = <nowiki>{v}</nowiki>")
    for k, v in obj.items():
        m = hashlib.sha256()
        m.update(v.encode('utf-8'))
        print(f"| {k}_sha256 = {m.hexdigest()}")
    print("}}")

if __name__ == '__main__':
    iname = input("enter iname: ")
    main(iname)
