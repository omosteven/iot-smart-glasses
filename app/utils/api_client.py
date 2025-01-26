import requests
import urllib3

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def send_image_to_api(image_path):
    url = "https://18.198.217.46/api/v1/image-to-text"
    try:
        with open(image_path, 'rb') as img_file:
            # Match the form-data key and include the correct MIME type
            files = {"file": (image_path, img_file, "image/png")}
            headers = {
                "Accept": "application/json"
            }

            # Send the POST request
            response = requests.post(url, files=files, headers=headers, timeout=10, verify=False)
        # Check for HTTP errors
        response.raise_for_status()
        return response.json()  # Parse JSON response
    except requests.exceptions.HTTPError as http_err:
        return {"message": "HTTP Error", "data": str(http_err)}
    except requests.RequestException as req_err:
        return {"message": "Request Error", "data": str(req_err)}
    except Exception as e:
        return {"message": "Unexpected Error", "data": str(e)}
