# Copyright NetApp 2023. Developed by NetApp Solutions Engineering Team
#
# Description:  This Lambda function can be used to automate the mount process for FSx Datastore on AWS VMware Cloud. 
# Pre-requisites for running this template
#   - Create lambda in a private subnet with nat gateway for internal access
#   - Update all values in vars.py with the required inputs.
#   - Ensure that Lambda function has connectivity to FSX by attaching FSxN VPC and subnets to lambda with appropriate security group.
#   - Increase the default timeout for Lambda function from 3 secs. to 5 mins.
#   - Create a new requests Layer for this lambda function with python 3.9. (Use the zip files to create the layers)


import json
import logging
import requests
# requests.packages.urllib3.disable_warnings() 
from vars import apiToken, orgId, clusterId

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # 1. Get access token
        print("Getting Access Token")
        url = "https://console.cloud.vmware.com/csp/gateway/am/api/auth/api-tokens/authorize"
        headers = {"accept": "application/json","Content-Type": "application/x-www-form-urlencoded"}
        payload = f'apiToken={apiToken}'
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        access_token = response.json().get('access_token')
        logger.info(f'Access Token API: {response.json()}')

        # 5. Mount datastore
        print("Mounting Datastore")
        url = f"https://vmc.vmware.com/api/inventory/{orgId}/vmc-aws/clusters/{clusterId}:unmount-datastores"
        headers = {"Content-Type": "application/json","csp-auth-token": access_token}
        data = {
            "datastore_name": ["NetAppDSAutomation"]
        }
        logger.info(f'Mount DataStore API Body: {data}')
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logger.info(f'VMC Mount Datastore API: {response.json()}')

        return {
            'statusCode': 200,
            'body': response.json()
        }

    except requests.exceptions.HTTPError as errh:
        logger.info("Http Error:",errh)
        print("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        logger.info("Error Connecting:",errc)
        print("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        logger.info("Timeout Error:",errt)
        print("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        logger.info("Something went wrong with the request:",err)
        print ("Something went wrong with the request:",err)