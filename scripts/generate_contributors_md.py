"""
Example JSON object:
{
    "login": "danixeee",
    "id": 16227576,
    "node_id": "MDQ6VXNlcjE2MjI3NTc2",
    "avatar_url": "https://avatars.githubusercontent.com/u/16227576?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/danixeee",
    "html_url": "https://github.com/danixeee",
    "followers_url": "https://api.github.com/users/danixeee/followers",
    "following_url": "https://api.github.com/users/danixeee/following{/other_user}",
    "gists_url": "https://api.github.com/users/danixeee/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/danixeee/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/danixeee/subscriptions",
    "organizations_url": "https://api.github.com/users/danixeee/orgs",
    "repos_url": "https://api.github.com/users/danixeee/repos",
    "events_url": "https://api.github.com/users/danixeee/events{/privacy}",
    "received_events_url": "https://api.github.com/users/danixeee/received_events",
    "type": "User",
    "site_admin": false,
    "contributions": 321
}
"""

import requests

PYGLS_CONTRIBUTORS_JSON_URL = (
    "https://api.github.com/repos/openlawlibrary/pygls/contributors"
)
CONTRIBUTORS_FILE = "CONTRIBUTORS.md"

response = requests.get(PYGLS_CONTRIBUTORS_JSON_URL)
contributors = sorted(response.json(), key=lambda d: d["login"].lower())

contents = "# Contributors (contributions)\n"

for contributor in contributors:
    name = contributor["login"]
    contributions = contributor["contributions"]
    url = contributor["html_url"]
    contents += f"* [{name}]({url}) ({contributions})\n"

file = open(CONTRIBUTORS_FILE, "w")
n = file.write(contents)
file.close()

print("✅ CONTRIBUTORS.md updated")
