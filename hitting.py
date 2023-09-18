import requests
from requests.structures import CaseInsensitiveDict

url = "http://127.0.0.1:5000"
# url = "https://api-flight-46lp.onrender.com"

headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/json"
def hit(prompt,session_id):
    json1={
        "prompt":prompt,
        "session_id":session_id,
    }

    resp = requests.post(url, headers=headers,json=json1,allow_redirects=False)
    return(resp.text)
