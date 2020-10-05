import json
import requests
import mwparserfromhell as parser
import mwclient
from urllib.parse import quote_plus
import datetime as dt


utcnow = int(dt.datetime.utcnow().strftime('%Y%m%d%H%M%S'))

###############################################################################
# Fetch the latest commit ID
###############################################################################

# id = 15372089
# file_path = quote_plus('Data/MasterParam')
# r = requests.head(f'https://gitlab.com/api/v4/projects/{id}/repository/files/{file_path}?ref=master')
# commit_id = r.headers.get("x-gitlab-commit-id")
# last_commit_id = r.headers.get("x-gitlab-last-commit-id")

# # print(r.headers)
# print(commit_id)
# print(last_commit_id)

# Check fetched ID with cache
# import sqlite3
# conn = sqlite3.connect(':memory:')
# conn.execute('''CREATE TABLE files(
# 	project_id INT,
# 	file_path TEXT,
	
# )''')



###############################################################################
# Get list of pages where commit_id does not match.
###############################################################################

# resp = requests.get('https://thealchemistcode.gamepedia.com/api.php', params={
# 	'action': 'cargoquery',
# 	'tables': '_pageData=PAGEDATA',
# 	'fields': '_pageTitle=PAGENAME,_pageName=FULLPAGENAME,FLOOR(_modificationDate)=REVISIONTIMESTAMP',
# 	'where': '_pageNamespace=10000',
# 	'limit': 5,
# 	'offset': 0,
# 	'format': 'json',
# })
# data = resp.json()

# data = {'cargoquery': [{'title': {'PAGENAME': 'Game/MasterParam/Ability/AB 01 DESERT BALT 01', 'FULLPAGENAME': 'Data:Game/MasterParam/Ability/AB 01 DESERT BALT 01', 'REVISIONTIMESTAMP': '20200227094604'}}, {'title': {'PAGENAME': 'Game/MasterParam/Ability/AB 01 DESERT RYLE 01', 'FULLPAGENAME': 'Data:Game/MasterParam/Ability/AB 01 DESERT RYLE 01', 'REVISIONTIMESTAMP': '20191219084732'}}, {'title': {'PAGENAME': 'Game/MasterParam/Ability/AB 01 ENVYRIA CANON 01', 'FULLPAGENAME': 'Data:Game/MasterParam/Ability/AB 01 ENVYRIA CANON 01', 'REVISIONTIMESTAMP': '20191219091959'}}, {'title': {'PAGENAME': 'Game/MasterParam/Ability/AB 01 ENVYRIA CLOE 01', 'FULLPAGENAME': 'Data:Game/MasterParam/Ability/AB 01 ENVYRIA CLOE 01', 'REVISIONTIMESTAMP': '20200319182646'}}, {'title': {'PAGENAME': 'Game/MasterParam/Ability/AB 01 ENVYRIA VETTEL 01', 'FULLPAGENAME': 'Data:Game/MasterParam/Ability/AB 01 ENVYRIA VETTEL 01', 'REVISIONTIMESTAMP': '20200319182642'}}]}
# rows = data['cargoquery']
# for row in rows:
# 	page = row['title']
# 	REVISIONTIMESTAMP = page['REVISIONTIMESTAMP']
# 	last_modified = dt.datetime.strptime(REVISIONTIMESTAMP, '%Y%m%d%H%M%S')
# 	print((page['PAGENAME'], last_modified, REVISIONTIMESTAMP))



# # site = mwclient.Site('wikisandbox-ucp.gamepedia.com', path='/')
# # site.login(username='BryghtShadow@Manjaro', password="ciqdln5a62ruoodogff7ainsk098i3rt")

# # page = site.pages['User:BryghtShadow/manjaro']
# # print(page.exists)
# # text = page.text()
# commit_id = '6475087fd59139551839cc08a4797981f583ed1c'


# x = parser.parse('{{#invoke:Data|insert|gl = foo|jp = bar|commit_id = '+commit_id+'}}')
# templates = x.filter_templates()

# for t in templates:
# 	print(t.name)
# 	for p in t.params:
# 		print(repr(p.name.strip()), repr(p.value.strip()))

# # page.edit('Hello', "this is a test")


