# VMC Details
apiToken = "your_api_token_here" # VMC API Token
orgId = ""
clusterId = ""

# FSx Details
createVolume = False # change to True if you want to create a new FSx for ONTAP volume

# if createVolume == True
fsxId = "fsx_filesystem_id"
volSize = "volume_size_in_megabytes"

# Datastore Details
storageEndpoint = ["10.10.10.10"] # SVM NFS IP address
junctionPath = "/vol1" # volume junction path (enter the new path if createVolume == True)

