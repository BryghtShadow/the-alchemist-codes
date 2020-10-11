import sqlite3
from urllib.parse import quote_plus

import requests


class Vanilla:
    cache_name = 'cache.sqlite'
    api_base = 'https://gitlab.com/api/v4'

    def init_cache(self):
        conn = sqlite3.connect(self.cache_name)
        conn.row_factory = sqlite3.Row
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS namespaces(
                id INT,
                name TEXT,
                path TEXT,
                kind TEXT,
                full_path TEXT,
                PRIMARY KEY(id)
            );''')
            conn.execute('''CREATE TABLE IF NOT EXISTS projects(
                id INT,
                name TEXT,
                path TEXT,
                namespace_id INT,
                PRIMARY KEY(id)
            );''')
            conn.execute('''CREATE TABLE IF NOT EXISTS files(
                project_id INT,
                file_path TEXT,
                content_sha256 TEXT,
                commit_id TEXT,
                last_commit_id TEXT,
                content TEXT,
                PRIMARY KEY(project_id, file_path)
            );''')
        conn.close()
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
        conn = sqlite3.connect(self.cache_name)
        with conn:
            n = conn.execute('''
                SELECT n.id AS id,
                       n.name AS name,
                       n.path AS path,
                       n.kind AS kind,
                       n.full_path AS full_path
                  FROM namespaces AS n
                 WHERE n.kind="group"
                   AND n.path=:path;
            ''', {'path': path})
        conn.close()
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
        conn = sqlite3.connect(self.cache_name)
        with conn:
            conn.execute('''
                INSERT INTO projects(id, name, path, namespace_id)
                VALUES(:id, :name, :path, :group_id);
            ''', p)
        conn.close()
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


if __name__ == '__main__':
    vanilla = Vanilla()
    vanilla.init_cache()

    # conn = sqlite3.connect('cache.sqlite')
    # conn.row_factory = sqlite3.Row
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
