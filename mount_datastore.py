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
from vars import api_token, endPoint, junctionPath, storageEndpoint, org_id, cluster_id

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # 1. Get access token
        
        url = "https://console.cloud.vmware.com/csp/gateway/am/api/auth/api-tokens/authorize"
        headers = {"accept": "application/json","Content-Type": "application/x-www-form-urlencoded"}
        data = {"api_token": api_token}
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        access_token = response.json().get('access_token')
        logger.info(f'Access Token API: ${response.json()}')


        # 2. Get orgs
        # url = "https://vmc.vmware.com/vmc/api/orgs"
        # headers = {"accept": "application/json","csp-auth-token": access_token}
        # response = requests.get(url, headers=headers)
        # response.raise_for_status()
        # orgs = response.json()
        # logger.info(f'VMC Orgs API: ${orgs}')

        # Iterate over all orgs
        # for org in orgs:
        #     org_id = org.get('id')

        #     # 3. Get sddc
        #     url = f"https://vmc.vmware.com/vmc/api/orgs/{org_id}/sddcs"
        #     headers = {"csp-auth-token": access_token}
        #     response = requests.get(url, headers=headers)
        #     # response.raise_for_status()
        #     sddcs = response.json()
        #     logger.info(f'SDDC Orgs API: ${sddcs}')

        #     # Find the SDDC with the matching vc_url
        #     for sddc in sddcs:
        #         if sddc['resource_config']['vc_url'] == endPoint or sddc['resource_config']['vc_public_ip'] == endPoint:
        #             sddc_id = sddc.get('id')
        #             logger.info(f'SDDC ID Match Found: SDDC: ${sddc_id}, Org: ${org_id}')
        #             break

        #     # If a matching SDDC was found, break the loop
        #     if 'sddc_id' in locals():
        #         break

        # # If no matching SDDC was found, return an error
        # if 'sddc_id' not in locals():
        #     logger.info(f'SDDC ID Match NOT found')
        #     return {
        #         'statusCode': 404,
        #         'body': 'No matching SDDC found'
        #     }

        # 4. Get cluster id
        # url = f"https://vmc.vmware.com/vmc/api/orgs/{org_id}/sddcs/{sddc_id}/primarycluster"
        # headers = {'accept': 'application/json',"csp-auth-token": access_token}
        # response = requests.get(url, headers=headers)
        # response.raise_for_status()
        # cluster_id = response.json().get('cluster_id')  # Assuming the first cluster is the one we want
        # logger.info(f'VMC Primary Cluster API: ${response.json()}')

        # 5. Mount datastore
        url = f"https://vmc.vmware.com/api/inventory/{org_id}/vmc-aws/clusters/{cluster_id}:mount-datastores"
        headers = {"Content-Type": "application/json","csp-auth-token": access_token}
        data = {
            "mount_info": [{
                "storage_endpoint": storageEndpoint, 
                "volume_path": junctionPath,
                "storage_vendor": 'AWS_FSxN',
                "datastore_name": "NetAppDSAutomation"
            }]
        }
        logger.info(f'Mount DataStore API Body: ${data}')
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logger.info(f'VMC Mount Datastore API: ${response.json()}')

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