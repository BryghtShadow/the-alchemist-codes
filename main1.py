import sqlite3
import json
import requests
import requests_cache
import csv
import io
import os
import base64
import urllib.parse
import re
from enum import Enum

requests_cache.install_cache('tac')

whitelist = {
	'AI',
	'Ability',
	'Artifact',
	'Buff',
	'ConceptCard',
	'ConceptCardConditions',
	'ConceptCardGroup',
	'Conditions',
	'CustomTarget',
	'Item',
	'Job',
	'JobGroup',
	'JobSet',
	'Loc',
	'News',
	'Pages',
	'Recipe',
	'Skill',
	'Unit',
	'UnitGroup',
}

class Project(Enum):
	GLOBAL = 15372089
	JAPAN = 13648989
	def __int__(self):
		return self.value

def getFile(project_id, filename):
	try:
		project_id = int(project_id)
	except ValueError:
		project_id = int(Project[project_id])

	file_path = urllib.parse.quote(filename, safe='')
	url = f"https://gitlab.com/api/v4/projects/{project_id}/repository/files/{file_path}?ref=master"

	cached_header = cache.get(url)
	if not cached_header:
		r = requests.head(url)
		cached_header = {
			'X-Gitlab-Blob-Id': r.headers.get('X-Gitlab-Blob-Id'),
			'X-Gitlab-Commit-Id': r.headers.get('X-Gitlab-Commit-Id'),
			'X-Gitlab-Content-Sha256': r.headers.get('X-Gitlab-Content-Sha256'),
			'X-Gitlab-Encoding': r.headers.get('X-Gitlab-Encoding'),
			'X-Gitlab-File-Name': r.headers.get('X-Gitlab-File-Name'),
			'X-Gitlab-File-Path': r.headers.get('X-Gitlab-File-Path'),
			'X-Gitlab-Last-Commit-Id': r.headers.get('X-Gitlab-Last-Commit-Id'),
			'X-Gitlab-Ref': r.headers.get('X-Gitlab-Ref'),
			'X-Gitlab-Size': r.headers.get('X-Gitlab-Size'),
		}
		cache[url] = cached_header
	else:



	resp = requests.get(url)
	data = resp.json()
	content = base64.b64decode(data['content']).decode('utf-8-sig')
	f = io.StringIO(content)

	is_cached = cached_resp and all([
		cached_resp['size'] == data['size'],
		cached_resp['content_sha256'] == data['content_sha256'],
		cached_resp['blob_id'] == data['blob_id'],
		cached_resp['commit_id'] == data['commit_id'],
		cached_resp['last_commit_id'] == data['last_commit_id'],
	])
	if not is_cached:
		content = data['content']
		del data['content']
		cache[url] = data
		dirname = os.path.dirname(filename)
		os.makedirs(dirname, exist_ok=True)
		with open(filename, 'wb') as fp:
			fp.write(base64.b64decode(content))
	return f

def getMasterParam(project_name):
	f = getFile(Project[project_name].value, 'Data/MasterParam')
	return json.load(f)

def getMasterParams():
	regionProject = {
		'gl': 'GLOBAL',
		'jp': 'JAPAN',
	}
	data = {}
	for region, project_name in regionProject.items():
		mp = getMasterParam(project_name)
		for group, entries in mp.items():
			for entry in entries:
				try:
					iname = entry['iname']
				except KeyError:
					break
				except TypeError:
					break
				data.setdefault(group, {}).setdefault(iname, {})[region] = entry
	return data

def getLoc(lang, filename):
	f = getFile(Project.GLOBAL.value, f'Loc/{lang}/{filename}')
	reader = csv.reader(f, delimiter='\t')
	data = {k:v for k,v in reader}
	return data

def getLocalizedMasterParams():
	params = set()

	langs = ('english', 'french', 'german', 'japanese', 'spanish')
	data = {}
	for lang in langs:
		loc = getLoc(lang, 'LocalizedMasterParam')
		for key, val in loc.items():
			m = re.match(r'SRPG_(\w+)Param_(.+)', key)
			if not m:
				print('Unexpected localization:', (lang, key, val))
				continue
			group, tail = m.groups()
			if group not in whitelist:
				continue
			m = re.match(r'(.+)_(CHARADESC|CONCEPT_TXT|EXPR|FLAVOR|IMAGE_TEXT|MAPEFF|NAME|OTHERDESC|SPEC|TAG)', tail)
			if not m:
				print((lang, key, val))
				continue
			iname, param = m.groups()
			params.add(param)
			data.setdefault(group, {}).setdefault(iname, {}).setdefault(param, {})[lang] = val
	print(sorted(params))
	return data

def main():
	getMasterParams()
	loc = getLocalizedMasterParams()
	print(loc['Skill'].get('SK_GL_MAN_YUJ_PETRIFY_WIDE'))
	pass

if __name__ == '__main__':
	main()