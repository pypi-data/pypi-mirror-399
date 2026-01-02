import json
import os
import uuid
from pathlib import Path

import requests


def save(data, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    json.dump(data, open(path, "w", encoding="utf8"), ensure_ascii=False, indent=4)


def load(path):
    return json.load(open(path, "r", encoding="utf8"))


def submit(path, config, address="localhost:80", is_auto=False, submit_id="", version="", token=""):
    with open(path, "r", encoding="utf-8") as file:
        content = json.load(file)
    # TODO do some content validation before sending

    config["user_guid"] = uuid.uuid4().hex
    config["is_auto"] = is_auto

    with open(path, "rb") as file:
        data = {
            "config": json.dumps(config),
            "submit_id": submit_id,
            "version": version,
            "token": token,
            "filename": os.path.basename(path),
        }
        files = {path: file}
        response = requests.post(
            f"http://{address}/submit/create",
            data=data,
            files=files,
        )

    try:
        res = json.loads(response.content.decode("utf-8"))
    except Exception as e:
        print("Exception occured:", str(e))
        return

    print(f"Done. Your submission id is {res['id']}")
    return res['id']


def fetch_judge_requests(address="localhost:80", token=""):
    """Fetch all submissions with judge_state == 1"""
    data = {
        "token": token
    }
    response = requests.post(
        f"http://{address}/submit/fetch_judge_requests",
        data=data
    )

    try:
        res = json.loads(response.content.decode("utf-8"))
    except Exception as e:
        print("Exception occurred:", str(e))
        return []

    return res.get("items", [])


def download_for_judge(submit_id, version, output_path, address="localhost:80", token=""):
    """Download file for judging"""
    print(f"Downloading judge file for submit {submit_id} version {version}")
    data = {
        "token": token,
        "submit_id": submit_id,
        "version": version
    }
    response = requests.post(
        f"http://{address}/submit/get_gen_output",
        data=data,
        stream=True
    )

    if response.status_code == 200:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"File saved to {output_path}")
    else:
        print(f"Error downloading file: {response.status_code}")
        try:
            print(response.json())
        except Exception:
            print(response.text)


def add_judge_results(submit_id, version, judge_metrics, address="localhost:80", token="", is_auto=False):
    """Add judge results for a submit"""
    data = {
        "token": token,
        "submit_id": submit_id,
        "version": version,
        "judge_results": json.dumps(judge_metrics),
        "is_auto": is_auto
    }
    response = requests.post(
        f"http://{address}/submit/add_judge_results",
        data=data
    )

    if response.status_code == 200:
        print("Judge results added successfully.")
    else:
        print(f"Error adding judge results: {response.status_code}")
        try:
            print(response.json())
        except Exception:
            print(response.text)
