import requests
from typing import Dict, Optional
import json

class OpenSearchClient:
    def __init__(self, host: str, auth: tuple):
        self.base_url = f"https://{host}"
        self.auth = auth
        self.headers = {'Content-Type': 'application/json'}

    def is_accessible(self) -> bool:
        health_url = f"{self.base_url}/_cluster/health"
        print(f"[DEBUG] Checking OpenSearch health: {health_url}")
        try:
            response = requests.get(
                health_url,
                auth=self.auth,
                headers=self.headers
            )
            print(f"[DEBUG] OpenSearch health response: {response.status_code} {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"[ERROR] Error checking OpenSearch accessibility: {str(e)}")
            return False

    def search_template(self, query: Dict) -> Dict:
        url = f"{self.base_url}/event-data-index_v1/_search/template"
        print(f"[DEBUG] Executing search template: {url}")
        print(f"[DEBUG] Payload: {json.dumps(query, indent=2)}")
        try:
            response = requests.post(url, auth=self.auth, headers=self.headers, data=json.dumps(query))
            print(f"[DEBUG] Search template response status: {response.status_code}")
            if response.status_code != 200:
                print(f"[DEBUG] Search template response text: {response.text}")
            response.raise_for_status()
            data = response.json()
            print(f"[DEBUG] Resposne Json: {data}")
            print(f"[DEBUG] Search template response hits: {len(data.get('hits', {}).get('hits', []))}")
            return data
        except Exception as e:
            print(f"[ERROR] Search template error: {str(e)}")
            return {"hits": {"hits": []}}

    def search(self, query: Dict) -> Dict:
        url = f"{self.base_url}/event-data-index_v1/_search"
        print(f"[DEBUG] Executing search: {url}")
        print(f"[DEBUG] Payload: {json.dumps(query, indent=2)}")
        try:
            response = requests.post(url, auth=self.auth, headers=self.headers, data=json.dumps(query))
            print(f"[DEBUG] Search response status: {response.status_code}")
            if response.status_code != 200:
                print(f"[DEBUG] Search response text: {response.text}")
            response.raise_for_status()
            data = response.json()
            print(f"[DEBUG] Search response hits: {len(data.get('hits', {}).get('hits', []))}")
            return data
        except Exception as e:
            print(f"[ERROR] Search error: {str(e)}")
            return {"hits": {"hits": []}}

    def get_total_count(self) -> int:
        url = f"{self.base_url}/event-data-index_v1/_count"
        query = {"query": {"match_all": {}}}
        print(f"[DEBUG] Executing count: {url}")
        print(f"[DEBUG] Payload: {json.dumps(query, indent=2)}")
        try:
            response = requests.post(url, auth=self.auth, headers=self.headers, data=json.dumps(query))
            print(f"[DEBUG] Count response status: {response.status_code}")
            if response.status_code != 200:
                print(f"[DEBUG] Count response text: {response.text}")
            response.raise_for_status()
            data = response.json()
            print(f"[DEBUG] Count: {data.get('count', 0)}")
            return data.get('count', 0)
        except Exception as e:
            print(f"[ERROR] Count error: {str(e)}")
            return 0

    def get_latest_record(self) -> Optional[Dict]:
        url = f"{self.base_url}/event-data-index_v1/_search"
        query = {
            "sort": [{"Creation_Date": {"order": "desc"}}],
            "size": 1
        }
        print(f"[DEBUG] Getting latest record: {url}")
        print(f"[DEBUG] Payload: {json.dumps(query, indent=2)}")
        try:
            response = requests.post(url, auth=self.auth, headers=self.headers, data=json.dumps(query))
            print(f"[DEBUG] Latest record response status: {response.status_code}")
            if response.status_code != 200:
                print(f"[DEBUG] Latest record response text: {response.text}")
            response.raise_for_status()
            data = response.json()
            hits = data.get('hits', {}).get('hits', [])
            print(f"[DEBUG] Latest record hits: {len(hits)}")
            return hits[0].get('_source', {}) if hits else None
        except Exception as e:
            print(f"[ERROR] Error getting latest record: {str(e)}")
            return None
