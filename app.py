import gc
import torch
import base64
import pathlib
from modelscope.pipelines import pipeline
from modelscope.outputs import OutputKeys
from huggingface_hub import snapshot_download
import ffmpeg

# Init is ran on server startup
# Load your model to GPU as a global variable here using the variable name "model"
def init():
    global model
    model_dir = pathlib.Path('weights')
    snapshot_download('damo-vilab/modelscope-damo-text-to-video-synthesis', repo_type='model', local_dir=model_dir)
    model = pipeline('text-to-video-synthesis', model_dir.as_posix())

# Inference is ran for every server call
# Reference your preloaded global model variable here.
def inference(model_inputs:dict) -> dict:
    global model

    # Parse out your arguments
    prompt = model_inputs.get('prompt', None)
    if prompt == None:
        return {'message': "No prompt provided"}
    
    # Run the model
    input_text = {
        'text': prompt,
    }
    result_path = model(input_text,)[OutputKeys.OUTPUT_VIDEO]

    maxWidth = 512
    maxHeight = 512
    threads=8

    inp = ffmpeg.input(result_path)
    out = ffmpeg.output(inp.video,f"{result_path}.gif",vf=f"scale=if(gte(iw\,ih)\,min({maxWidth}\,iw)\,-2):if(lt(iw\,ih)\,min({maxHeight}\,ih)\,-2),split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",threads=threads)
    ffmpeg.run(out,cmd='ffmpeg',overwrite_output=True)

    # read the gif file as bytes
    with open(f"{result_path}.gif", 'rb') as file:
        gif_bytes = file.read()

    # encode the gif file as base64
    base64_bytes = base64.b64encode(gif_bytes)
    base64_string = base64_bytes.decode('utf-8')
    
    # create a response object with the base64-encoded gif file as the content
    response = {'gif_bytes': base64_string}

    return response
