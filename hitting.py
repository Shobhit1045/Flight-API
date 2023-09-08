import requests
from requests.structures import CaseInsensitiveDict

# url = "http://127.0.0.1:5000"
url = "https://api-flight-46lp.onrender.com"

headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/json"
def hit(prompt,greet,conv1,conv2,last2):
    json1={
        "prompt":prompt,
        "greet":greet,
        "conv1":conv1,
        "conv2":conv2,
        "last2":last2
    }

    resp = requests.post(url, headers=headers,json=json1)
    return(resp.text)
