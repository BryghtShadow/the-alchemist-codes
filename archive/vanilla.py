import base64
import csv
import json
import sqlite3
from collections import OrderedDict
from io import StringIO
from typing import Dict, Any, Optional, Mapping, Callable
from urllib.parse import quote_plus

import requests


class Vanilla:
    cache_name = 'cache.sqlite'
    api_base = 'https://gitlab.com/api/v4'

    def __init__(self):
        self.conn = sqlite3.connect(self.cache_name)
        self.conn.row_factory = sqlite3.Row

    def init_cache(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS namespaces(
                id INT,
                name TEXT,
                path TEXT,
                kind TEXT,
                full_path TEXT,
                PRIMARY KEY(id)
            );''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS projects(
                id INT,
                name TEXT,
                path TEXT,
                namespace_id INT,
                PRIMARY KEY(id)
            );''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS files(
                project_id INT,
                file_path TEXT,
                content_sha256 TEXT,
                last_commit_id TEXT,
                content TEXT,
                PRIMARY KEY(project_id, file_path)
            );''')
        # init namespaces
        group_name = 'the-alchemist-codes'
        ns = self.get_namespace(group_name)
        if not ns:
            self.init_namespace(group_name)

        # init projects
        project_names = ('Global', 'Japan')
        for project_name in project_names:
            p = self.get_project(group_name, project_name)
            if not p:
                self.init_project(group_name, project_name)

    def init_namespace(self, group_name):
        url = f'{self.api_base}/groups/{quote_plus(group_name)}'
        resp = requests.get(url, {'with_projects': False})
        data = resp.json()
        v = {
            'id': data['id'],
            'name': data['name'],
            'path': data['path'],
            'kind': 'group',
            'full_path': data['full_path'],
        }
        conn = sqlite3.connect(self.cache_name)
        with conn:
            conn.execute('''
                INSERT INTO namespaces(id, name, path, kind, full_path)
                VALUES (:id, :name, :path, :kind, :full_path)
            ''', v)
        conn.close()
        return v

    def get_namespace(self, path):
        with self.conn:
            n = self.conn.execute('''
                SELECT n.id AS id,
                       n.name AS name,
                       n.path AS path,
                       n.kind AS kind,
                       n.full_path AS full_path
                  FROM namespaces AS n
                 WHERE n.kind="group"
                   AND n.path=:path;
            ''', {'path': path})
        return n

    def init_project(self, group_name, project_name):
        name = f'{group_name}/{project_name}'
        url = f'{self.api_base}/projects/{quote_plus(name)}'
        resp = requests.get(url)
        data = resp.json()
        p = {
            'id': data['id'],
            'name': data['name'],
            'path': data['path'],
            'group_id': data['namespace']['id'],
        }
        with self.conn:
            self.conn.execute('''
                INSERT INTO projects(id, name, path, namespace_id)
                VALUES(:id, :name, :path, :group_id);
            ''', p)
        return p

    def get_project(self, group_name, project_name):
        conn = sqlite3.connect(self.cache_name)
        with conn:
            p = conn.execute('''
                SELECT p.id AS id,
                       p.name AS name,
                       p.path AS path,
                       p.namespace_id AS group_id
                  FROM projects AS p, namespaces AS n
                 WHERE n.id = p.namespace_id
                   AND n.path = ? COLLATE NOCASE
                   AND p.path = ? COLLATE NOCASE;
            ''', (group_name, project_name,))
        conn.close()
        return p

    def get_file(self, project_name, file_path, force_update=False):
        project = self.conn.execute('''
        SELECT p.id AS id,
               p.name AS name,
               p.path AS path
          FROM projects AS p
         WHERE p.path = :path COLLATE NOCASE;
        ''', {
            'path': project_name,
        }).fetchone()

        p_id = project['id']
        url = f'{self.api_base}/projects/{p_id}/repository/files/{quote_plus(file_path)}'
        resp = requests.head(url, params={'ref': 'master'})
        # header_keys = [
        #     'x-gitlab-blob-id',
        #     'x-gitlab-commit-id',
        #     'x-gitlab-content-sha256',
        #     'x-gitlab-encoding',
        #     'x-gitlab-file-name',
        #     'x-gitlab-file-path',
        #     'x-gitlab-last-commit-id',
        #     'x-gitlab-ref',
        #     'x-gitlab-size',
        # ]

        f = self.conn.execute('''
            SELECT f.project_id AS project_id,
                   f.file_path AS file_path,
                   f.content_sha256 AS content_sha256,
                   f.last_commit_id AS last_commit_id,
                   f.content AS content
              FROM files as f
             WHERE f.project_id = :project_id
               AND f.file_path = :file_path COLLATE NOCASE
               AND f.last_commit_id = :last_commit_id;
        ''', {
            'project_id': p_id,
            'file_path': resp.headers.get('x-gitlab-file-path'),
            'last_commit_id': resp.headers.get('x-gitlab-last-commit-id'),
        }).fetchone()
        if f is None or force_update:
            resp = requests.get(url, {'ref': 'master'})
            data = resp.json()
            content = base64.b64decode(data['content']).decode('utf-8')
            f = {
                'project_id': p_id,
                'file_path': data['file_path'],
                'content_sha256': data['content_sha256'],
                'last_commit_id': data['last_commit_id'],
                'content': content,
            }
            with self.conn:
                self.conn.execute('''
                INSERT INTO files (
                    project_id,
                    file_path,
                    content_sha256,
                    last_commit_id,
                    content
                ) VALUES (
                    :project_id,
                    :file_path,
                    :content_sha256,
                    :last_commit_id,
                    :content
                ) ON CONFLICT (project_id, file_path) DO UPDATE SET
                content_sha256=excluded.content_sha256,
                last_commit_id=excluded.last_commit_id,
                content=excluded.content;''', f)
        return f['content']


def main():
    vanilla = Vanilla()
    vanilla.init_cache()

    languages = (
        'english',
        'french',
        'german',
        'spanish',
    )
    toReturn = {}
    for lang in languages:
        file_path = f'Loc/{lang}/LocalizedMasterParam'
        content = vanilla.get_file('Global', file_path)
        reader = csv.reader(content, delimiter='\t')
    jpConceptCardLoc = vanilla.get_file('Global', 'Loc/japanese/external_conceptcard')

    def parse(remotePath, server):
        content = vanilla.get_file(remotePath, 'Data/MasterParam')
        gObj = json.loads(content)
        return  gObj

    mp = MasterParam()
    wikiFiles = mp.generate({
        server: parse(remotePath, server)
        for server, remotePath in {
            'jp': 'Japan',
            'gl': 'Global',
        }.items()
    })


class GameFile:
    def parse(self, server, remotePath):
        pass


class JsonGameFile(GameFile):
    def __init__(self, endpoint):
        super(JsonGameFile, self).__init__('Data/'+endpoint)

    def _parse(self, s):
        return json.loads(s)

class MasterParam(JsonGameFile):
    def parse(self, server, remotePath):
        result = {
            'data': super(MasterParam, self).parse(server, remotePath),
        }


    def generate(self, data):
        to_return = Dict[str, str]

        # Extract loc
        data = self.subdivide(data, (lambda k, v=None: k))
        loc: Dict[str, Dict[str, str]] = {}
        loc.update(data['loc'].get('gl', {}))
        loc.update(data['loc'].get('jp', {}))
        data = data['data']

        def get_loc_for(key: str, jp_val: Optional[str]) -> Mapping[str, str]:
            m = {
                k: v.pop(key)
                for k, v in loc.items()
                if v.get(key) is not None
            }
            if jp_val is not None:
                m['japanese'] = jp_val
            return m

        # Group by key
        groups = self.subdivide(data, (lambda k, v: k))

        def get_iname(m: Mapping[str, Optional[str]]) -> str:
            return m.get('iname')

        def store_packet(group: str,
                         loc_keys: Dict[str, str],
                         key: str,
                         packet: Dict[str, Optional[dict]]):
            for locN, dataN in loc_keys.items():
                jp_name = (packet.get('jp', {}).get(dataN) or
                           packet.get('gl', {}).get(dataN))

                for _, subpacket in packet:
                    subpacket.pop(dataN)

                packet.setdefault('loc', {})[dataN] = get_loc_for(f'SRPG_{group}Param_{key}_{locN}', jp_name)

            buf = StringIO()
            buf.write('{{#invoke:Data|insert')
            for server in sorted(packet.keys()):
                val = json.dumps(packet[server],
                                 sort_keys=True,
                                 ensure_ascii=False,
                                 separators=(',', ':'))
                buf.write(f'|{server}=<nowiki>{val}</nowiki>')
            buf.write('}}')
            to_return[f'Data:Game/MasterParam/{type_}/{k}'] = buf.getvalue()

        replacements = {
            'Unit': {
                'NAME': 'name',
            },
            'Job': {
                'NAME': 'name',
                'CHARADESC': 'desc_ch',
                'OTHERDESC': 'desc_ot',
            },
            'JobSet': {},
            'JobGroup': {},
            'UnitGroup': {},
            'ConceptCardGroup': {},
            'CustomTarget': {},
            'ConceptCardConditions': {},
            'Ability': {
                'NAME': 'name',
                'EXPR': 'expr',
            },
            'Buff': {},
            'Cond': {},
            'AI': {},
            'Artifact': {
                'NAME': 'name',
                'EXPR': 'expr',
                'SPEC': 'spec',
                'FLAVOR': 'flavor',
            },
            'Item': {
                'NAME': 'name',
                'EXPR': 'expr',
                'FLAVOR': 'flavor',
            },
        }
        for type_, locKeys in replacements.items():
            for k, packet in self.subdivide(groups.pop(type_), get_iname).items():
                store_packet(type_, locKeys, k, packet)

        # ConceptCard
        trust_rewards = self.subdivide(groups.pop('ConceptCardTrustReward'), get_iname)
        for k, packet in self.subdivide(groups.pop('ConceptCard'), get_iname).items():
            for server, p in packet.items():
                if p.get('trust_reward') is None: continue
                trust_reward = trust_rewards.get(p.pop('trust_reward'))
                if trust_reward is None: continue
                rewards_parsed = OrderedDict()
                for reward in trust_reward.get(server, {}).get('rewards', {}):
                    if reward['reward_type'] in (1,2):
                        m = rewards_parsed.setdefault(reward['reward_type'], OrderedDict())
                        m[reward['reward_iname']] = m.get(reward['reward_iname'], 0) + reward['reward_num']
                    else:
                        raise NotImplementedError(f"Encountered unimplemented trust reward type: {json.dumps(reward)}")
                for s, i in {'item': 1, 'artifact': 2}.items():
                    key = f'trust_{s}_names'
                    if key in p:
                        raise ValueError(f'{key} already in {p}')
                    p[key] = list(rewards_parsed.get(i, {}).keys())
                    key = f'trust_{s}_names'
                    if key in p:
                        raise ValueError(f'{key} already in {p}')
                    p[key] = list(rewards_parsed.get(i, {}).values())
            store_packet('ConceptCard', {
                'NAME': 'name',
                'EXPR': 'expr',
                'FLAVOR': 'flavor',
            }, k, packet)

        # Skill





    @staticmethod
    def subdivide(server_map: Mapping[str, Optional[Any]],
                  f: Callable[[Any, Optional[Any]], str]) -> Dict[str, Dict[str, Optional[Any]]]:
        groups = {}
        for server, d in server_map.items():
            for k, v in d.items():
                groups.setdefault(f(k, v), {})[server] = v
        return groups


if __name__ == '__main__':
    main()
    # curs = conn.cursor()
    # curs.execute('''
    #     SELECT f.file_path FROM projects AS p, files AS f
    #     WHERE p.id = f.project_id
    #     AND p.path_with_namespace LIKE ? COLLATE NOCASE
    # ''', ("%/Global",))
    # for row in curs.fetchall():
    #     print(row['file_path'])


#
#
# p = get_project('the-alchemist-codes/Global')
# print(p)
# # project_id = p['id']
#
# project_id = quote_plus('the-alchemist-codes/Global')
#
# file_path = 'Data/MasterParam'
# url = f'https://gitlab.com/api/v4/projects/{project_id}/repository/files/{quote_plus(file_path)}?ref=master'
# r = requests.head(url)
# h = r.headers
# print('blob id', h.get('X-Gitlab-Blob-Id'))
# print('commit id', h.get('X-Gitlab-Commit-Id'))
# print('content sha256', h.get('X-Gitlab-Content-Sha256'))
# print('encoding', h.get('X-Gitlab-Encoding'))
# print('file name', h.get('X-Gitlab-File-Name'))
# print('file path', h.get('X-Gitlab-File-Path'))
# print('last commit id', h.get('X-Gitlab-Last-Commit-Id'))
# print('ref', h.get('X-Gitlab-Ref'))
# print('size', h.get('X-Gitlab-Size'))
#
# #
# # curs = conn.cursor()
# # curs.execute('select project_id, file_path, content_sha256, commit_id, last_commit_id from cache')
# # for i, row in enumerate(curs.fetchall()):
# #     print(i, dict(row))
#
#
# # def get_file(project_name: Union[str, int], file_path: str):
# #     project_path = 'the-alchemist-codes/Global'
# #     resp = requests.get(f'https://gitlab.com/api/v4/projects/{quote_plus(project_path)}')
# #     project = json.loads(resp.content.decode('utf-8'))
# #     print(project)
# #
# # group_id = project['namespace']['id']
# # file_path = 'Data/MasterParam'
# # r = requests.head(f'https://gitlab.com/api/v4/group/{group_id}/repository/files/{quote_plus(file_path)}?ref=master')
# # print(r.headers)
# #
# #     curs = conn.cursor()
# #
