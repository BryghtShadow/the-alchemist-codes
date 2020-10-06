import base64
import sqlite3
from typing import Union

import gitlab
import mwclient


group_name = 'the-alchemist-codes'

conn = sqlite3.connect('cache.sqlite')
conn.row_factory = sqlite3.Row
conn.execute("""DROP TABLE IF EXISTS cache;""")
conn.execute("""CREATE TABLE IF NOT EXISTS cache(
    project_id INT,
    file_path TEXT,
    content_sha256 TEXT,
    commit_id TEXT,
    last_commit_id TEXT,
    content TEXT,
    PRIMARY KEY(project_id, file_path)
);""")
conn.commit()

gl = gitlab.Gitlab('https://gitlab.com')

class GameFile:


def get_file(project_name: Union[str, int], file_path: str):
    curs = conn.cursor()
    p = gl.projects.get(project_name)
    assert(p.namespace['full_path'] == group_name)
    commits = p.commits.list(ref_name='master', per_page=1)
    c = commits[0]
    print("Commit id:", c.id)

    curs.execute("""SELECT content, commit_id FROM cache
        WHERE project_id=:project_id
        AND file_path=:file_path
    """, {
        'project_id': p.id,
        'file_path': file_path,
    })
    row = curs.fetchone()
    if row and row['last_commit_id'] == c.id:
        print("File is cached and is not stale! ^_^")
        return row['content']

    if not row:
        print("File is not cached... ;_;")
    elif row['last_commit_id'] != c.id:
        print("File is stale... ;_;")

    print("Fetching fresh file from server")
    f = p.files.get(file_path, ref='master')
    content = base64.b64decode(f.content).decode('utf-8-sig')
    obj = {
        'project_id': p.id,
        'file_path': f.file_path,
        'content_sha256': f.content_sha256,
        'commit_id': f.commit_id,
        'last_commit_id': f.last_commit_id,
        'content': content,
    }
    f.content = None
    print(f)

    print("Saving file to cache...")
    conn.execute("""
    INSERT INTO cache (project_id, file_path, content_sha256, commit_id, last_commit_id, content)
        VALUES (:project_id, :file_path, :content_sha256, :last_commit_id, :content)
        ON CONFLICT (project_id, file_path) DO UPDATE SET
            content=excluded.content_sha256,
            last_commit_id=excluded.last_commit_id,
            content=excluded.content
        WHERE content_sha256<>excluded.content_sha256
        OR last_commit_id<>excluded.last_commit_id;
    """, obj)
    conn.commit()
    print("Here you go~")
    return content


def main():
    projects = {
        'gl': 'Global',
        'jp': 'Japan',
    }

    for server, project_name in projects.items():
        f = get_file(f'{group_name}/{project_name}', 'Data/MasterParam')
        # print(repr(f[:100]))

    languages = ('english', 'spanish', 'german', 'french')
    for lang in languages:
        f = get_file(f'{group_name}/Global', f'Loc/{lang}/LocalizedMasterParam')
        # print(repr(f[:100]))



if __name__ == '__main__':
    main()
