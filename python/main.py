# -*- coding: utf-8 -*-
import time
import visla_utils
from api_client import APIClient


if __name__ == "__main__":
    client = APIClient()
    # (Optional) My Space is the special private teamspace to hold new video
    user_info = client.get_user_info()
    my_space_uuid = user_info['data']['myTeamspaceUuid']
    print(f'All new videos will be created into this space (My Space): {my_space_uuid}')

    # Step 1: Load request body by parsing script json file
    json_path = "../docs/create_video.json"  # Replace with your .json file path
    json_obj = visla_utils.parse_json_from_file(json_path)
    print(json_obj)

    # Step 2: Invoke create-video-with-script api
    rsp_create_video = client.script_to_video(json_obj)
    print(rsp_create_video)
    new_project_uuid = rsp_create_video['data']['projectUuid']
    print(f'New video project id: {new_project_uuid}')
    project_info = client.get_project_info(new_project_uuid)
    print(project_info)
    # new_project_uuid = '1316073234210238464'

    # 2.1 wait some minutes to make sure creation completed before counting consumed credit
    start_time = time.time()  # Record start time
    client.wait_for_project_completion(new_project_uuid)
    duration = time.time() - start_time  # Calculate duration
    print(f"waited {duration:.2f} seconds on creating video")

    # Step 3: get project consumed credit (wait until project is created and processed)
    consumed_credit = client.get_project_consumed_credit(new_project_uuid)['data']
    print(f'consumed credit: {consumed_credit}')

    # Step 4: Invoke export-video api after project is ready
    rsp_export_video = client.export_video(new_project_uuid)
    print(rsp_export_video)
    new_clip_uuid = rsp_export_video['data']['clipUuid']
    print(f'New video clip id: {new_clip_uuid}')
    # new_clip_uuid = '1316073457099747328'

    # 4.1: wait some minutes to make sure exporting completed before get the download url
    start_time = time.time()
    client.wait_for_clip_completion(new_clip_uuid)
    duration = time.time() - start_time
    print(f"waited {duration:.2f} seconds on exporting video")

    clip_info = client.get_clip_info(new_clip_uuid)
    print(clip_info)

    # Step 5: wait some time to make sure clip download link is ready (a preSigned s3 link, which is valid for 1hour+)
    start_time = time.time()
    download_link = client.wait_for_download_link_ready(new_clip_uuid)
    duration = time.time() - start_time
    print(f"waited {duration:.2f} seconds before download link is available")
    # 5.1 download it
    if download_link is not None:
        start_time = time.time()
        visla_utils.download_video(download_link)
        duration = time.time() - start_time
        print(f"spent {duration:.2f} seconds on downloading")
