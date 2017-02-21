import requests
import sys
import time
import json

# https://www.microsoft.com/cognitive-services/en-us/subscriptions
# linkedin account

key = "5b9c6da7511e443d95adf4a7d0554f7c"

headers = {
    # Request headers
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': key,
}

params = {
    # Request parameters
    # 'sensitivityLevel': '{string}',
    # 'frameSamplingValue': '{number}',
    # 'detectionZones': '{string}',
    # 'detectLightChange': '{boolean}',
    # 'mergeTimeThreshold': '{number}',
}


with open(sys.argv[1]) as f:
    data = f.read()


def check1(data):
    r = requests.post("https://api.projectoxford.ai/video/v1.0/detectmotion",
                      params=params, headers=headers, data=data, timeout=120)

    if r.status_code == 202:
        l = r.headers['operation-location']
        while True:
            r = requests.get(l, headers=headers, timeout=15)
            print r.status_code, r.headers, r.content
            j = r.json()
            if 'status' not in j:
                time.sleep(20)
                continue
            if j['status'] == 'Succeeded':
                data = json.loads(j['processingResult'])
                print data
                for f in data['fragments']:
                    if 'events' in f:
                        print "FOUND MOTION"
                break
            elif j['status'] == 'Running':
                pass
            else:
                break
            time.sleep(10)
        return 202
    else:
        print r.status_code, r.content
        return r.status_code

while True:
    r = check1(data)
    if r in [429]:
        time.sleep(20)
        continue
    break
