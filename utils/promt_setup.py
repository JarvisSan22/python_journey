import base64
import requests
from PIL import Image, PngImagePlugin, ImageDraw
from io import BytesIO
from .def_prompts import *
from .img_tools import resize

def promt_pram(args,type="txt2img"):
    prams={}
    if type.lower()=="img2img":
         print("img2img")
         prams=def_img2img
    else:
         prams=def_text2img
    #Arg i@date 
    for key,val in args.items():
         if key=="ng":
              key="negative_prompt"
         elif key=="ds":
              key="denoising_strength"
         
         prams[key]=val
    print(prams)
    return prams

def promt_gen(
        prompt,
        ng="NSFW, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry",
        seed=-1,
        steps=30,
        cfg=7.5,
        sampler ="Euler",
        NSFW_filter= False,
        w=512,
        h=512,
    ):
    #prompt checker 
    arg_dict={
         "ng":ng,
         "seed":seed,
         "steps":steps,
         "cfg":cfg,
         "sampler":sampler,
         "NSFW_filter":NSFW_filter
    }
    if "--" in prompt:
        args=prompt.split("--")[1:] #assumes prompt is the first part 
        prompt=prompt[:prompt.find("--")]
        #print(args)

        for arg in args:
            arg_type=arg.split(" ")[0]
            arg_dict[arg_type]=arg.replace(arg_type,"")
    #print(prompt)
    if "https://" in prompt: #img2img
        #non img prompt 
        type="img2img"
        img_s=prompt.find("https") #start
        img_url=prompt[img_s:]
        if " " in img_url: #ie image is not at end of prompt but and start
             img_url=img_url.split(" ")[0]
        #img_e=prompt.find("")+3 #Img file + 3 i.e png
    
        #img_url=prompt[img_s:img_e]
        print("image_url",img_url)
        #turn img into img string 
        image = Image.open(requests.get(img_url, stream=True).raw)
        print(image.size)
        #image resize 
        image=resize(image,W_TARGET=w,H_TARGET=h)
        buffered=BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        #mask
        mask = Image.new("L", (w,h), color=0)
        draw = ImageDraw.Draw(mask)
        draw.rectangle([(0, 0), (w,h)], fill=255)
        #buffered = BytesIO()
        #mask.save(buffered)
        #mask_str = base64.b64encode(buffered.getvalue()).decode()


        #img prompt
        print(prompt)
        prompt=prompt.replace(img_url,"") #Cut img url
        print(prompt)
        arg_dict["prompt"]=prompt
        
       
        img2img_prams={
             "init_images":[img_str],
             "mask":img_str,
             "width": image.width,
             "height": image.height,
        }
        del image
        arg_dict.update(img2img_prams)
        return promt_pram(arg_dict,type="img2img"),"img2img"
    
    else: #text2img 
           arg_dict["prompt"]=prompt
           
           #arg_dict["orig_height"]=h
           #arg_dict["orig_width"]=w
           return promt_pram(arg_dict,type="text2img"),"text2img"
                                 #ng,seed, steps,ds,cfg,sampler, NSFW_filter)

    