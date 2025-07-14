import requests
from flask import Flask, jsonify, request
import os
import subprocess
import tempfile
import threading

app = Flask(__name__)


def freeze(server_uuid):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            tarball_path = os.path.join(tempdir, f"{server_uuid}.tar.gz")

            tar_command = ["tar", "-zcvf", tarball_path, "-C", "/var/lib/pelican/volume", server_uuid]
            subprocess.run(tar_command, check=True)
            rclone_command = [
                "rclone", "move", tarball_path, "storage:/mnt/serverdata/pelican-wings", "--progress"
            ]
            subprocess.run(rclone_command, check=True)
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error during backup: {e}")
        return False


def unfreeze(server_uuid):
    try:
        tarball_path = f"/tmp/{server_uuid}.tar.gz"
        rclone_command = [
            "rclone", "copy", f"storage:/mnt/serverdata/pelican-wings/{server_uuid}.tar.gz", tarball_path, "--progress"
        ]
        subprocess.run(rclone_command, check=True)

        restore_directory = f"/var/lib/pelican/volume/{server_uuid}"
        tar_command = ["tar", "-zxvf", tarball_path, "-C", restore_directory]
        subprocess.run(tar_command, check=True)

        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during restore: {e}")
        return False


@app.route('/freeze/<server_uuid>', methods=['POST'])
def freeze_server(server_uuid):
    api_key = request.headers.get('Authorization')
    if not api_key or api_key != "Bearer peli_8QKbIvpLIEixZJ2deVVZI0fZYWokX9bSgCumA9WhMDb":
        return jsonify({"error": "Unauthorized"}), 401
    try:
        def freeze_thread():
            freeze(server_uuid)

        threading.Thread(target=freeze_thread).start()
        return jsonify({"message": "Server frozen and backed up successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/unfreeze/<server_id>', methods=['POST'])
def unfreeze_server_route(server_id):
    api_key = request.headers.get('Authorization')
    if not api_key or api_key != "Bearer peli_8QKbIvpLIEixZJ2deVVZI0fZYWokX9bSgCumA9WhMDb":
        return jsonify({"error": "Unauthorized"}), 401

    try:
        def unfreeze_thread():
            getuuid = f"https://panel.bluedhost.org/api/application/servers/{server_id}"
            headers = {
                "Authorization": f"Bearer peli_8QKbIvpLIEixZJ2deVVZI0fZYWokX9bSgCumA9WhMDb",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            response = requests.get(getuuid, headers=headers)
            response_json = response.json()
            server_uuid = response_json["attributes"]["uuid"]
            unfreeze(server_uuid)
            unsuspend_url = f"https://panel.bluedhost.org/api/application/servers/{server_id}/unsuspend"
            requests.post(unsuspend_url, headers=headers)
        threading.Thread(target=unfreeze_thread).start()
        return jsonify({"message": "Server unsuspended successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888)
