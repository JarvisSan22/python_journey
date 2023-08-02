import json
import requests
import io,os
import base64
from PIL import Image, PngImagePlugin
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())



def SD_APICALL(payload : dict,url: str,type: str):
  print("API Call")
  if type=="text2img":
    print(url)
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
  else:
    response = requests.post(url=f'{url}/sdapi/v1/img2img', json=payload)
  print("Recived")
  r = response.json()
  return r