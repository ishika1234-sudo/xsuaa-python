import os
import requests
from requests.auth import HTTPBasicAuth
import json

AUTH_TOKEN_URL = "https://lti.authentication.eu10.hana.ondemand.com/oauth/token"
GET_INFO_URL = "https://lti.authentication.eu10.hana.ondemand.com/userinfo"
VCAP_SERVICES = os.getenv('VCAP_SERVICES')
print('VCAP_SERVICES',VCAP_SERVICES, type(VCAP_SERVICES))
VCAP_SERVICE = json.loads(VCAP_SERVICES)
CREDENTIALS = VCAP_SERVICE['xsuaa'][0]['credentials']
APP_CLIENT_ID = CREDENTIALS["clientid"]
APP_CLIENT_SECRET = CREDENTIALS["clientsecret"]
print('credentials', CREDENTIALS, APP_CLIENT_ID, APP_CLIENT_SECRET)


def request_refresh_and_access_token(authorization_code):
    try:
        payload = {"grant_type": "authorization_code","client_id": APP_CLIENT_ID,
                   "code": authorization_code
                   }

        response = requests.post(AUTH_TOKEN_URL,data=payload,auth=HTTPBasicAuth(APP_CLIENT_ID,
                                                                                APP_CLIENT_SECRET))
        print("acces token request resp code :",response.status_code)
        if response.status_code == 200:
            response_json = json.loads(response.content)
            id_token = response_json["id_token"]
            access_token = response_json["access_token"]
            refresh_token = response_json["refresh_token"]
            print(access_token)
            return {'status': 200,'access_token': access_token,"id_token": id_token}
        else:
            return {'status': response.status_code,'msg': response.content}
    except Exception as e:
        print(e)
        return {'status': 500,'msg': str(e)}


def get_user_info_using_access_token(access_token,id_token):
    try:
        response = requests.get(GET_INFO_URL,headers={"Authorization": "Bearer %s" % access_token})
        if response.status_code == 200:
            # print("User info : ",json.loads(response.content))
            user_info = json.loads(response.content)
            data = {"email": user_info["email"],
                    "first_name": user_info['given_name'],
                    "last_name": user_info['family_name']
                    }
            # print('data', data)
            return {'status': 200,'user_info': data}
        else:
            return {'status': response.status_code,'msg': response.content}
    except Exception as e:
        print(e)
        return {'status': 500,'msg': str(e)}



'''access_and_id_token = request_refresh_and_access_token("2M9IFG4kkQ")
print(access_and_id_token)
get_user_info = get_user_info_using_access_token(access_and_id_token['access_token'], access_and_id_token['id_token'])
print(get_user_info)'''

