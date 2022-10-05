from xml.dom import NotFoundErr
import requests
import json
from slack import WebClient


def gcpDiffVersionCheck():
    return {
        "Alchemy Service": "alchemy-rtr.stage.gcp.rtr.cloud",
        "Auth": "auth.stage.gcp.rtr.cloud",
        "Autumn": "autumn.stage.gcp.rtr.cloud",
        "Bag": "bag.stage.gcp.rtr.cloud",
        "Baywatch": "baywatch.stage.gcp.rtr.cloud",
        "CMS Service": "cms.stage.gcp.rtr.cloud",
        "Commerce": "commerce.stage.gcp.rtr.cloud",
        "CX Admin": "cx-admin.stage.gcp.rtr.cloud",
        "DFS": "dfs.stage.gcp.rtr.cloud",
        "ERP": "erp.stage.gcp.rtr.cloud",
        "Epic": "epic.stage.gcp.rtr.cloud",
        "Fulfillment": "fulfillment-dw.stage.gcp.rtr.cloud/fulfillment",
        "Godfather": "godfather.stage.gcp.rtr.cloud",
        "Godmother": "godmother.stage.gcp.rtr.cloud",
        "Inventory": "inventory.stage.gcp.rtr.cloud",
        "Image": "image.stage.gcp.rtr.cloud",
        "Inbound-processing": "inbound-processing.stage.gcp.rtr.cloud",
        "Inventory-reader": "inventory-reader.stage.gcp.rtr.cloud",
        "Knapp-diverter": "knapp-diverter.stage.gcp.rtr.cloud",
        "Knapp-telegraph": "knapp-telegraph.stage.gcp.rtr.cloud",
        "Knapp-mock-plc": "knapp-mock-plc.stage.gcp.rtr.cloud",
        "Notification Service": "notification.stage.gcp.rtr.cloud",
        "Panda": "panda.stage.gcp.rtr.cloud",
        "Pixel": "pixel.stage.aws.rtr.cloud",
        "Pricing Service": "pricing.stage.gcp.rtr.cloud",
        "Products Service": "products.stage.gcp.rtr.cloud",
        "Quality-control": "quality-control.stage.gcp.rtr.cloud",
        "Queue": "queue.stage.gcp.rtr.cloud",
        "Referral Service": "referral.stage.gcp.rtr.cloud",
        "Relevance Engine": "relevance-engine.stage.gcp.rtr.cloud",
        "Rescache Service": "rescache.stage.gcp.rtr.cloud",
        "Reviews": "reviews.stage.gcp.rtr.cloud",
        "Retail Central": "retail-central.stage.gcp.rtr.cloud",
        "Retail Web": "retail-web.stage.gcp.rtr.cloud",
        "Royalties": "royalties.stage.gcp.rtr.cloud",
        "RTR Admin": "rtr-admin.stage.gcp.rtr.cloud",
        "Storefront": "storefront.stage.gcp.rtr.cloud",
        "User Collections": "user-collections.stage.gcp.rtr.cloud",
        "Users": "users.stage.gcp.rtr.cloud",
        "Shipmunk": "shipmunk.stage.gcp.rtr.cloud",
        "Shipmunk-rate": "shipmunk-rate.stage.gcp.rtr.cloud",
        "Shipping-address": "shipping-address.stage.gcp.rtr.cloud",
        "Simulation": "simulation.stage.gcp.rtr.cloud",
        "Warehouse-containers": "warehouse-containers.stage.gcp.rtr.cloud",
        "Whallocator": "whallocator.stage.gcp.rtr.cloud",
        "WMS Mobile": "wms-mobile.stage.gcp.rtr.cloud",
        "YAMS": "yams.stage.gcp.rtr.cloud"
    }


def versionCheck():
    dicts = {}
    try:
        for service, url in gcpDiffVersionCheck().items():
            dicts[service] = str(requests.get(
                "http://" + url + "/version").content).replace('b', '')

    except requests.exceptions.ConnectionError as errh:
        print('HTTP Error : ' + errh)
    except requests.exceptions.Timeout as errt:
        print('Timeout Error : ' + errt)
    except requests.exceptions.HTTPError as errc:
        print('Error in Connection : ' + errc)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)

    return dicts


def writeToFile(myVersionDict):
    try:
        with open('recentGCPVersions.json', 'w') as f:
            json.dump(myVersionDict, f, indent=2)
    except FileNotFoundError:
        print("Version Change File Not Found")


def checkDiffVersion():
    new_service_versions = versionCheck()
    old_versions_stored = {}
    with open('recentGCPVersions.json', 'r') as f:
        old_versions_stored = json.load(f)

    diff_in_versions = {k: [old_versions_stored[k], new_service_versions[k]]
                        for k in old_versions_stored if k in new_service_versions and old_versions_stored[k] != new_service_versions[k]}

    writeToFile(new_service_versions)

    if len(diff_in_versions) == 0:
        return "No Version Changes"
    else:
        return diff_in_versions

def sendVersionDiffsToSlack(slack_bot_token, channel, thread_id=None):
    diffDict = checkDiffVersion()
    result = ""

    if(isinstance(diffDict, str)):
        result = "`" + diffDict + "` :white_check_mark:"
    elif (isinstance(diffDict, dict)):
        for key in diffDict:
            result += f"`{key}: {diffDict[key][0]} --> {diffDict[key][1]}`\n"
    else:
        result = "Could not fetch Version information. (From versionDiff.py)"

    client = WebClient(token=slack_bot_token)
    
    if thread_id is not None:
        client.api_call(
            api_method='chat.postMessage',
            json={
            'channel': channel,
            'text': result,
            'thread_ts': thread_id
            }
        )
    else:
        client.api_call(
            api_method='chat.postMessage',
            json={
            'channel': channel,
            'text': result,
            }
        )
