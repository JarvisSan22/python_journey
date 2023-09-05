# python_journey
midjourny discord bot clone made in python and using StableDiffusion Web UI by automatic 1111

![test image](https://github.com/JarvisSan22/python_journey/blob/main/Example_20230905.png)

# Setup
* (1) First install and setup [automatic1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui), download a model and lora model into the repo. When all downloaded and installed run it with the tag ```--api ``` to activate the api settins
* (2) Set up a virtual python environment for and install the requirments.txt file
* (3) Set up your discord server and retrive the Server, name, ID, secrete keys... and add it all into the .env file (.env_template is provided, please change it I)
* (4) Update the lora setting inside the python_journy_channel.py channel_model_dic. Add the channel names as key and then the lora call commands as items. These will be added to the prompt depending on the channel used to generate imagery
* (5) Run python_journy_channel.py , and do a test generateion. If all work well 4 images with 8 buttons should be sent to the discord when the webui finished generation. 

# How to use 
To run use the slash command generate. The command take input the same way midjourny does. With a text prompt and an option to add imagery by pasting a image discord url into the prompt. There are also several extra setting that can be added to the prompt be using --{setting} at the end of the prompt
## Settings options 
--ar 1:2  , aspect ratio ig. 1:2 changes the imagery aspect size </br>
--img2img-at  : img2img alternative test setting is turned on for img2img generations </br>
--ds 0.9  : denoising strength for img2img generations  </br>


# To Do
[ ] Quality imrpovment </br>
[ ] AR fix for large image size </br>
[ ] Seed options </br>
[ ] negative prompt option</br>
[ ] Image saving by user </br>
[ ] Face detection and high res inpaint option 
[ ] inpaint control net pfp to fullbody option 
[ ] Pixelation option 
