# This file is used to verify your http server acts as expected
# Run it with `python3 test.py`
import base64
import requests

model_inputs = {'prompt': 'A panda eating bamboo on a rock.'}

res = requests.post('http://localhost:8000/', json = model_inputs)

video_byte_string = res.json()["mp4_bytes"]
video_encoded = video_byte_string.encode('utf-8')
video_bytes = base64.b64decode(video_encoded)

# save the video bytes to a file
with open('output.mp4', 'wb') as f:
    f.write(video_bytes)