import http.client
import json
import time
import requests

ILISO_HOST = "127.0.0.0.1:1111"


payload = {"all_feeds":[{"feed_name":"motion","samples":[{"value":123,"time":time.time()}]}]}
r = requests.post("http://127.0.0.1:1111/update", json=payload)
