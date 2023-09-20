import requests


def auto_start_parser():
    url = "http://127.0.0.1:8000/api/v1/load"
    payload = ""
    headers = {
        'Login': 'Basic password'
    }
    _ = requests.request("POST", url, headers=headers, data=payload)


auto_start_parser()
