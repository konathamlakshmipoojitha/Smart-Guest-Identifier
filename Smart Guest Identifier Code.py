import time
import sys
import ibmiotf.application
import ibmiotf.device
import random



import cv2
import numpy as np
import datetime

#ObjectStorage
import ibm_boto3
from ibm_botocore.client import Config, ClientError



#CloudantDB
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
import requests

import json
from watson_developer_cloud import VisualRecognitionV3

face_classifier=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
eye_classifier=cv2.CascadeClassifier("haarcascade_eye.xml")



#Provide CloudantDB credentials such as username,password and url

client = Cloudant("e1437d2d-1d2d-4c02-87a6-2c979d96197e-bluemix", "03a21003379ae3c42a6bcdf53de6b73af12c4d9082f9e35f53287e9a7038d495", url="https://e1437d2d-1d2d-4c02-87a6-2c979d96197e-bluemix:03a21003379ae3c42a6bcdf53de6b73af12c4d9082f9e35f53287e9a7038d495@e1437d2d-1d2d-4c02-87a6-2c979d96197e-bluemix.cloudantnosqldb.appdomain.cloud")
client.connect()

#Provide your database name
database_name = "sample1"
my_database = client.create_database(database_name)

if my_database.exists():
   print(f"'{database_name}' successfully created.")
  

img=cv2.VideoCapture(0)

while True:
       ret,frame=img.read()
       
       global imgname

       cv2.imshow("face",frame)
       imgname=datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")
       cv2.imwrite(imgname+".jpg",frame)
       k=cv2.waitKey(1)
       #waitKey(1)- for every 1 millisecond new frame will be captured
       if k==ord('q'):
        #release the camera
                img.release()
        #destroy all windows
                cv2.destroyAllWindows()
                break
# Constants for IBM COS values
COS_ENDPOINT = "https://s3.jp-tok.cloud-object-storage.appdomain.cloud" # Current list avaiable at https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints
COS_API_KEY_ID = "5xOFhgtbOeSNOnAzeZIOdnvDtc-0myLHgaWa2k1Lz9Da" # eg "W00YiRnLW4a3fTjMB-odB-2ySfTrFBIQQWanc--P3byk"
COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
COS_RESOURCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/d03d8edd8b6049d2817db9754f28605d:0ad8004b-2343-455f-aef2-3b42d11da5f4::" # eg "crn:v1:bluemix:public:cloud-object-storage:global:a/3bf0d9003abfb5d29761c3e97696b71c:d6f04d83-6c4f-4a62-a165-696756d63903::"


# Create resource
cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_RESOURCE_CRN,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)
def create_bucket(bucket_name):
    print("Creating new bucket: {0}".format(bucket_name))
    try:
        cos.Bucket(bucket_name).create(
            CreateBucketConfiguration={
                "LocationConstraint":"jp-tok-standard"
            }
        )
        print("Bucket: {0} created!".format(bucket_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to create bucket: {0}".format(e))

create_bucket("kolli")

def multi_part_upload(bucket_name, item_name, file_path):
        try:
            print("Starting file transfer for {0} to bucket: {1}\n".format(item_name, bucket_name))

            # set 5 MB chunks
            part_size = 1024 * 1024 * 5

            # set threadhold to 15 MB
            file_threshold = 1024 * 1024 * 15

            # set the transfer threshold and chunk size
            transfer_config = ibm_boto3.s3.transfer.TransferConfig(
                multipart_threshold=file_threshold,
                multipart_chunksize=part_size
            )
            # the upload_fileobj method will automatically execute a multi-part upload
            # in 5 MB chunks for all files over 15 MB
            with open(file_path, "rb") as file_data:
                cos.Object(bucket_name, item_name).upload_fileobj(
                    Fileobj=file_data,
                    Config=transfer_config
                )

            print("Transfer for {0} Complete!\n".format(item_name))
        except ClientError as be:
            print("CLIENT ERROR: {0}\n".format(be))
        except Exception as e:
            print("Unable to complete multi-part upload: {0}".format(e))
multi_part_upload("kolli", "image.jpg", imgname+".jpg")
json_document={"link":COS_ENDPOINT+"/"+"kolli"+"/"+"image.jpg"}
new_document = my_database.create_document(json_document)

#Provide your IBM Watson Device Credentials
organization = "e8u3us"
deviceType = "raspberrypi"
deviceId = "123456"
authMethod = "token"
authToken = "12345678"



def myCommandCallback(cmd):
        print("Command received: %s" % cmd.data)#Commands
        
        

try:
	deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
	deviceCli = ibmiotf.device.Client(deviceOptions)
	#..............................................
	
except Exception as e:
	print("Caught exception connecting device: %s" % str(e))
	sys.exit()

# Connect and send a datapoint "hello" with value "world" into the cloud as an event of type "greeting" 10 times
deviceCli.connect()

while True:
        
        #hum=random.randint(10, 40)
        #print(hum)
        #temp =random.randint(30, 80)
        #Send Temperature & Humidity to IBM Watson
        #data = { 'Temperature' : temp, 'Humidity': hum }
        #print (data)
        def myOnPublishCallback():
           # print ("Published Temperature = %s C" % temp, "Humidity = %s %%" % hum, "to IBM Watson")

            success = deviceCli.publishEvent("Weather", "json", data, qos=0, on_publish=myOnPublishCallback)
            if not success:
                print("Not connected to IoTF")
                time.sleep(2)
        
        deviceCli.commandCallback = myCommandCallback

# Disconnect the device and application from the cloud
deviceCli.disconnect()
