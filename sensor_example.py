import http.client
import json
import time
import requests

ILISO_HOST = "https://iliso.herokuapp.com/update"


payload = {"all_feeds":[{"feed_name":"motion","samples":[{"value":123,"time":time.time()}]}]}
r = requests.post(ILISO_HOST, json=payload)
print(r)
