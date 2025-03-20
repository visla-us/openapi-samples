# -*- coding: utf-8 -*-
import os
import requests
import json
from datetime import datetime


def parse_json_from_file(file_path):
    """
    Reads a .json file and returns its content as a JSON object.

    :param file_path: Path to the .json file
    :return: JSON object representation of the file content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)  # Parse the JSON file
        # return json.dumps(data, indent=4)  # Convert to JSON string with pretty formatting
        return data  # Return JSON object
    except FileNotFoundError:
        return "Error: File not found."
    except json.JSONDecodeError:
        return "Error: Invalid JSON format."


def put_to_s3(self, file_path, presigned_put_url):
    OBJECT_NAME_TO_UPLOAD = os.path.expanduser(file_path)

    with open(OBJECT_NAME_TO_UPLOAD, 'rb') as data:
        r = requests.put(presigned_put_url, data=data)
    return r


def query_string_remove(url):
    return url[:url.find('?')]


def download_video(download_url):
    datetime_str = datetime.now().strftime("%Y%m%d%H%M")  # Format as yyyyMMddHHmm
    file_name = f"{datetime_str}.mp4"
    response = requests.get(download_url, stream=True)
    response.raise_for_status()  # Raise an error for HTTP errors
    with open(file_name, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # Filter out keep-alive chunks
                file.write(chunk)
    print(f"Video saved as {file_name}")
