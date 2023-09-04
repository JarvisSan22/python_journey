import base64
import requests
from PIL import Image, PngImagePlugin, ImageDraw
from io import BytesIO
from .def_prompts import *
from .img_tools import resize
import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())



def upscaling(img_str,url,resize=2,model="R-ESRGAN 4x+ Anime6B"):
        arg_dict={
        "upscaling_resize": resize,
        "upscaler_1":model ,
        "image":img_str
        }
        response = requests.post(url=f'{url}/sdapi/v1/extra-single-image', json=arg_dict)
        return response.json()

def variation(img_str,url,payload,denosing=0.55,seed_varation=1):
    payload["init_images"]=[img_str]
    payload["denoising_strength"]=denosing
    payload["subseed"]=-1
    payload["subseed_strength"]=0.5
    response = requests.post(url=f'{url}/sdapi/v1/img2img', json=payload)
    return response.json()

def arToSize(aspect_ratio,width,height,fix="height"):
    w_ar,h_ar = aspect_ratio.split(':')
    ar=float(w_ar)/float(h_ar)
    ratio=width/height
    if fix=="height":
        new_height=height
        new_width=int(ar*width)
    elif fix=="width":
        new_width=width
        new_height=int(width*ar)
    print(new_height,new_width)
    return new_width,new_height


class generator():
    def __init__(self,file_loc=os.getenv("DEF_LOC"),API_URL=os.getenv("SD_URL")):
        self.file_loc=file_loc
        self.model_loc=os.path.join(self.file_loc,"models","Stable-diffusion")
        self.lora_models=os.path.join(self.file_loc,"models","lora")
        self.API_URL=API_URL
        self.steps=30
        self.cfg=8
        self.sampler="DDIM"
        self.ng="NSFW, large_hips,naked, large_breast, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry",
        super().__init__()

    def __model_dic(self):
        model_list=os.listdir(model_list)
        model_dic={}    
        for i, model in enumerate(model_list):
            model_dic[i]={"name":os.path.basename(model).split(".")[0],"path":os.path.join(self.model_loc,model)}
        return model_dic    
    def __promt_setup(self,text,type="text2img"):
        arg_dict={
         
         "seed":8888,
         "steps":self.steps,
         "width":820,
         "batch_size":1,
         "n_iter":4,
         "height":820,
         "cfg":self.cfg,
         "sampler":self.sampler,
         "NSFW_filter":False,
        }
        #Settings 
        #


        options=["ar","img2img-at","ds","upsacling"]
        if "--" in text:
            args=text.split("--")[1:] #assumes prompt is the first part 
            text=text[:text.find("--")]
            #print(args)
            for arg in args:
                arg_type=arg.split(" ")[0]
                if arg_type in options:
                    if arg_type=="img2img-at": #im2img alterative text 
                        arg_dict["script_name"]="img2img alternative test"
                        arg_dict["script_args"]=["",True,False,"","",False,50,False,1,0,True]
                    if arg_type=="ds":
                        value=arg.split(" ")[1]
                        arg_dict["denoising_strength"]=float(value)
                    if arg_type=="ar":
                        value=arg.split(" ")[1]
                        nw,nh=arToSize(value,arg_dict["width"],arg_dict["height"])
                        arg_dict["width"]=nw
                        arg_dict["height"]=nh
                    #arg_dict[arg_type]=arg.replace(arg_type,"")
                    
        

        print(text)
        if "https://" in text: #img2img
            #non img prompt 
            type="img2img"
            img_s=text.find("https") #start
            img_url=text[img_s:]
            if " " in img_url: #ie image is not at end of prompt but and start
                img_url=img_url.split(" ")[0]
            text=text.replace(img_url,"")
            img_str=self.__imgbuffer(img_url) 
            arg_dict["init_images"]=[img_str]
            if not arg_dict["denoising_strength"]:
                arg_dict["denoising_strength"]=0.75


        arg_dict["prompt"]=text +",(retro_anime_artstyle), ayaka_gal_style, galverse <lora:GalverseV45_Multi_V1:0.75>"
        #arg_dict["negative_prompt"]=self.ng
        self.payload=arg_dict
        self.type=type
        #return type
    def upscaling(self,img_str,resize=2,model="R-ESRGAN 4x+Anime6B"):
        arg_dict={
        "upscaling_resize": resize,
        "upscaler_1":model ,
        "image":img_str
        }
        response = requests.post(url=f'{self.API_URL}/sdapi/v1/extra-single-image', json=arg_dict)
        return response.json()


    def __imgbuffer(self,url:str):
        image = Image.open(requests.get(url, stream=True).raw)
        print(image.size)
        #image resize 
        #image=resize(image,W_TARGET=self.W,H_TARGET=self.H)
        buffered=BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        del image
        return img_str
    

    def __call__(self,text):
        self.__promt_setup(text)
        print("API Call")
        if self.type=="text2img":
            response = requests.post(url=f'{self.API_URL}/sdapi/v1/txt2img', json=self.payload)
        elif self.type=="upscale":
            response = requests.post(url=f'{self.API_URL}/sdapi/v1/extra-single-image', json=self.payload)
        else:
            response = requests.post(url=f'{self.API_URL}/sdapi/v1/img2img', json=self.payload)
        print("Recived")
        r = response.json()
        return r,self.payload

