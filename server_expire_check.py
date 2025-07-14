import datetime
import time
import databasehandler
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def freeze_server(serverid):
    url = f"https://panel.bluedhost.org/api/application/servers/{serverid}"
    headers = {
        "Authorization": f"Bearer, {os.getenv('PANELKEY')}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    json_data = response.json()
    server_uuid = json_data["attributes"]["uuid"]
    server_node = json_data["attributes"]["node"]
    get_node_url = f"https://panel.bluedhost.org/api/application/nodes/{server_node}"
    node_response = requests.get(get_node_url, headers=headers)
    node_response.raise_for_status()
    node_json_data = node_response.json()
    node_fqdn = node_json_data["attributes"]["fqdn"]
    freeze_url = f"http://{node_fqdn}:8888/freeze/{server_uuid}"
    requests.post(freeze_url, headers=headers)

def expire_check():
    while True:
        servers = databasehandler.get_all_server_expiry_times()
        for serverid, last_renew_date in servers:
            if last_renew_date is None:
                continue
            if last_renew_date <= int((datetime.datetime.now(datetime.UTC).timestamp()-604800)//1):
                freeze_server(serverid)
                request = requests.post(f"https://panel.bluedhost.org/api/application/servers/{serverid}/suspend",
                                    headers={"Authorization": f"Bearer {os.getenv('PANELKEY')}",
                                            "Accept": "application/json",
                                            "Content-Type": "application/json"})
                if request.status_code == 204:
                    print(f"Server {serverid} suspended.")

        time.sleep(180)