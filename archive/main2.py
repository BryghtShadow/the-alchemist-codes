import requests
from datetime import datetime, timedelta, timezone


def local_to_utc(ts):
	dt = datetime.fromisoformat(ts)
	return dt.astimezone(tz=timezone.utc)

GLOBAL = 15372089
BASE_URL = "https://gitlab.com/api/v4"

url = f"{BASE_URL}/projects/{GLOBAL}/repository/files/Data%2FMasterParam?ref=master"
# HEAD request to check commit ID, because GET response is 40MB+
r = requests.head(url)
commit_id = r.headers.get("x-gitlab-commit-id")
last_commit_id = r.headers.get("x-gitlab-last-commit-id")

url = f"{BASE_URL}/projects/{GLOBAL}/repository/commits/{last_commit_id}?ref=master"
r = requests.get(url)

last_commit = r.json()
committed_datetime = local_to_utc(last_commit.get('committed_date'))
authored_datetime = local_to_utc(last_commit.get("authored_date"))
print(r.json())

expires_datetime = committed_datetime + timedelta(weeks=1)
print("STARTS: ", committed_datetime)
print("EXPIRES:", expires_datetime)
