import requests
import time

# Set the base URL as needed
# base_url = "https://litellm-api.onrender.com"
# Uncomment the line below if you want to switch to the local server
base_url = "http://0.0.0.0:8000"

# Step 1 Add a config to the proxy, generate a temp key
config = {
  "model_list": [
  ]
}

response = requests.post(
    url=f"{base_url}/key/generate",
    json={
        "config": config,
        "duration": "30d"  # default to 30d, set it to 30m if you want a temp key
    },
    headers={
        "Authorization": "Bearer sk-1234"
    }
)

print("\nresponse from generating key", response.text)
print("\n json response from gen key", response.json())

generated_key = response.json()["key"]
print("\ngenerated key for proxy", generated_key)

# Step 2: Queue a request to the proxy, using your generated_key
print("Creating a job on the proxy")
job_response = requests.post(
    url=f"{base_url}/queue/request",
    json={
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': f'You are a helpful assistant. What is your name'},
        ],
    },
    headers={
        "Authorization": f"Bearer {generated_key}"
    }
)
print(job_response.status_code)
print(job_response.text)
print("\nResponse from creating job", job_response.text)
job_response = job_response.json()
job_id = job_response["id"]
polling_url = job_response["url"]
polling_url = f"{base_url}{polling_url}"
print("\nCreated Job, Polling Url", polling_url)

# Step 3: Poll the request
while True:
    try:
        print("\nPolling URL", polling_url)
        polling_response = requests.get(
            url=polling_url,
            headers={
                "Authorization": f"Bearer {generated_key}"
            }
        )
        print("\nResponse from polling url", polling_response.text)
        polling_response = polling_response.json()
        status = polling_response.get("status", None)
        if status == "finished":
            llm_response = polling_response["result"]
            print("LLM Response")
            print(llm_response)
            break
        time.sleep(0.5)
    except Exception as e:
        print("got exception in polling", e)
        break
