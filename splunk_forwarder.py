import requests, os, json
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

url = f'http://{os.getenv("splunk_host")}:{os.getenv("splunk_port")}/services/collector/event'
authHeader = {
    'Authorization': f'Splunk {os.getenv("splunk_token")}',
    'Content-Type': 'application/json'
}

def sendEvent(event, source):
    try:
        jsonDict = {
            "event" : json.dumps(event),
            "source" : f'{source[59:]}'
        }
        r = requests.post(url,headers=authHeader,json=jsonDict, verify=False)
        if r.status_code==200:
            return 1
        else:
            print(f"[*] Error when sending out, statusCode: {r.status_code}")
    except Exception as e:
        print(f"[*] Error when sending out event: {e}")

