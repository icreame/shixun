import requests
import json

# 百度云的模型
def get_access_key():
    url = "https://aip.baidubce.com/oauth/2.0/token?client_id=jVPCk0VAZMoXzB6FkGcE9uu4&client_secret=Bv1iSAmyytZstILdyXDeHRzFQUaeLWc3&grant_type=client_credentials"

    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


if __name__ == '__main__':
    get_access_key()
