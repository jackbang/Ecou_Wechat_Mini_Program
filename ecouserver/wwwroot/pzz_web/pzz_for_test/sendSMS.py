import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20190711 import sms_client, models

def sendSMS(phoneNumber, validCode):
    try: 
        cred = credential.Credential("", "") 
        httpProfile = HttpProfile()
        httpProfile.endpoint = "sms.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = sms_client.SmsClient(cred, "", clientProfile) 

        req = models.SendSmsRequest()
        params = {
            "PhoneNumberSet": [ phoneNumber ],
            "TemplateID": "",
            "Sign": "",
            "TemplateParamSet": [ str(validCode) ],
            "SessionContext": "",
            "SmsSdkAppid": ""
        }
        req.from_json_string(json.dumps(params))

        resp = client.SendSms(req) 
        return resp.to_json_string()

    except TencentCloudSDKException as err: 
        return str(err)