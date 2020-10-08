import json
from urllib.parse import quote_plus

import requests

project_path = quote_plus('the-alchemist-codes/Global')
resp = requests.get(f'https://gitlab.com/api/v4/projects/{project_path}')
project = json.loads(resp.content.decode('utf-8'))
print(project)

group_id = project['namespace']['id']
file_path = quote_plus('Data/MasterParam')
r = requests.head(f'https://gitlab.com/api/v4/group/{group_id}/repository/files/{file_path}?ref=master')
print(r.headers)
