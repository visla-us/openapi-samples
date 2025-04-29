# -*- coding: utf-8 -*-
import uuid
import requests
import hashlib
import hmac
import time
import config


class APIClient:
    def __init__(self):
        self.base_url = config.BASE_URL
        self.api_key = config.API_KEY
        self.api_secret = config.API_SECRET

    # Sign the request and set headers always
    def sign_request(self, method, url):
        sign_str_pattern = "{method}|{url}|{ts}|{nonce}"
        ts = int(time.time() * 1000)
        nonce = uuid.uuid4()
        sign_str = sign_str_pattern.format(method=method.upper(), url=url, ts=ts, nonce=nonce);
        signature = hmac.new(
            self.api_secret.encode(), sign_str.encode(), hashlib.sha256
        ).hexdigest()

        api_headers = {"Content-Type": "application/json; charset=utf-8", "key":  self.api_key, "ts": f'{ts}', "nonce": str(nonce), "sign": f'{signature}'}
        return api_headers
    
    # Common GET APIs
    def get(self, endpoint, params=None):
        api_url = f"{self.base_url}{endpoint}"
        # Sign the request and set headers always
        api_headers = self.sign_request("Get", api_url)
        params = params or {}
        response = requests.get(api_url, params=params, headers=api_headers)
        return response.json()

    # Common POST APIs
    def post(self, endpoint, json=None):
        api_url = f"{self.base_url}{endpoint}"
        # Sign the request and set headers always
        api_headers = self.sign_request("Post", api_url)
        json = json or {}
        response = requests.post(api_url, json=json, headers=api_headers)
        return response.json()

    # api to get clip upload url
    def get_upload_url(self):
        return self.get("/clip/get-upload-url", {"fileSuffix": "mp4"})
    
    # api to retrieve user info
    def get_user_info(self):
        return self.get("/user/info")

    # api to retrieve project info
    def get_project_info(self, project_uuid):
        return self.get(f"/project/{project_uuid}/info")

    # api to retrieve clip info
    def get_clip_info(self, clip_uuid):
        return self.get(f"/clip/{clip_uuid}/info")

    # api to get project consumed credit
    def get_project_consumed_credit(self, project_uuid):
        return self.get(f"/project/{project_uuid}/get-consumed-credit")

    # api to create video from script
    def script_to_video(self, create_video_json):
        return self.post("/project/script-to-video", create_video_json)

    # api to export project to video
    def export_video(self, project_uuid):
        return self.post(f"/project/{project_uuid}/export-video")

    # api to get clip download link
    def get_clip_download_link(self, clip_uuid):
        return self.get(f"/clip/{clip_uuid}/get-download-link")

    def wait_for_project_completion(self, project_uuid, interval=10, max_attempts=50):
        """
        loop retrieving project status to make sure creation completed before counting consumed credit
        """
        attempts = 0
        while attempts < max_attempts:
            project_info = self.get_project_info(project_uuid)
            status = project_info['data']['progressStatus']
            # print(f"current project creation progress: {status}")

            if status == "editing":
                print("project creation completed")
                return
            elif status == "preparation":
                print(f"project creation is still on-going，wait {interval} seconds then retrieve again...")
            else:
                print(f"wait {interval} seconds then retrieve again...")

            attempts += 1
            time.sleep(interval)

        print("quit after reached max attempts on wait_for_project_completion")

    def wait_for_clip_completion(self, clip_uuid, interval=10, max_attempts=100):
        """
        loop retrieving clip status to make sure exporting completed before download link is available
        """
        attempts = 0
        while attempts < max_attempts:
            clip_info = self.get_clip_info(clip_uuid)
            status = clip_info['data']['clipStatus']
            # print(f"current clip exporting status: {status}")

            if status == "completed":
                print("clip exporting completed")
                return
            elif status == "publishing":
                print(f"clip exporting is still on-going，wait {interval} seconds then retrieve again...")
            else:
                print(f"wait {interval} seconds then retrieve again...")

            attempts += 1
            time.sleep(interval)

        print("quit after reached max attempts on wait_for_clip_completion")

    def wait_for_download_link_ready(self, clip_uuid, interval=10, max_attempts=100):
        """
        loop retrieving download link until it is available
        """
        attempts = 0
        while attempts < max_attempts:
            rsp_get_download_link = self.get_clip_download_link(clip_uuid)
            print(f"response of get-download-link: {rsp_get_download_link}")

            data_node = rsp_get_download_link.get("data")
            if data_node and data_node is not None and "downloadLink" in data_node:
                return data_node['downloadLink']
            else:
                print(f"wait {interval} seconds then retrieve again...")

            attempts += 1
            time.sleep(interval)

        print("quit after reached max attempts on wait_for_download_link_ready")
