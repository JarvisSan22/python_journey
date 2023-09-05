import os
import requests
import json
import time
from utils.SD_gen import generator,upscaling,variation
from PIL import Image
import nextcord 
from nextcord import Interaction, SlashOption
from nextcord.ext import commands 
from nextcord.ui import Button, View
from io import BytesIO
import base64
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

channel_model_dic={
    "gal_sd_m1":" ayaka_gal_style, galverse <lora:GalverseV45_Multi_V1:0.75>",
    "gal_sd_m2":" <lora:GalverseMV_V3_ft:0.75>",
    "gal_sd_m3":" <lora:GalverseMV_V4_ft_DST2:0.75>",
}


def combine_images(images):
    for i, image in enumerate(images):
        image = BytesIO(base64.decodebytes(image.encode("utf-8"))) 
        images[i]=Image.open(image)
    # Create a blank canvas for the final grid image
    grid_image = Image.new('RGB', (2 * images[0].width, 2 * images[0].height))

    # Iterate over each image and paste it onto the grid
    for i in range(2):
        for j in range(2):
            # Calculate the coordinates to paste the image
            x = j * images[0].width
            y = i * images[0].height

            # Paste the image onto the grid
            grid_image.paste(images[i*2 + j], (x, y))

    return grid_image

bot =commands.Bot(command_prefix="$", intents=nextcord.Intents.all() )
SD = generator()

@bot.event
async def on_ready():
    print("bot is up and ready")

#Model select 
model_dic={}

def ImgResponseToDiscord(img_responce):
    image = BytesIO(base64.decodebytes(img_responce.encode("utf-8")))
    image=Image.open(image)
    image_bytes = BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes.seek(0)
    file=nextcord.File(image_bytes,"image.png")
    return file

class ImageUPscaleButton(nextcord.ui.Button):
    def __init__(self, image_str: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_str = image_str

    async def callback(self, interaction: nextcord.Interaction):
        # Get the user who clicked the button
        # Create an embed with the image
        print("button click")
        response=upscaling(self.image_str,SD.API_URL)
        file=ImgResponseToDiscord(response["image"])
        await interaction.response.send_message("Upscaled x2", ephemeral=False, file=file)



class ImageVariationButton(nextcord.ui.Button):
    def __init__(self,image_str: str, base_payload: str, *args,**kwargs):
        super().__init__(*args,**kwargs)
        self.image_str = image_str
        self.base_payload = base_payload

    async def callback(self, interaction: nextcord.Interaction):
        #await interaction.response.defer() 
        ETA = int(time.time()+60)
        msg = await interaction.response.send_message(f" Varation ETA: <t:{ETA}:R>")
        reponse=variation(self.image_str,SD.API_URL,self.base_payload)
        images = reponse['images']
        grid=combine_images(images.copy())
        new_image_bytes = BytesIO()
        grid.save(new_image_bytes, format="PNG")
        new_image_bytes.seek(0)
        grid.save("test_grid.png")
        file=nextcord.File(new_image_bytes,"Varation_grid.png")
        print(file)
        view=View()
        for i,image in enumerate(images):
            button_up=ImageUPscaleButton(image_str=image,
                         label=f"U{i+1}", style=nextcord.ButtonStyle.blurple)
            view.add_item(button_up)
        await msg.edit(content="",file=file,view=view)
        

serverid=os.getenv("SERVER_ID")
@bot.slash_command(guild_ids=[serverid],description="Galverse AI gen")
async def generate(interaction:  nextcord.Interaction ,prompt:str ):
    print(prompt)
    ETA = int(time.time()+60)
    msg = await interaction.response.send_message(f" Requests sent <t:{ETA}:R>")
    lora=None
    if interaction.channel.name in list(channel_model_dic.keys()):# add channel model to promt
        lora=channel_model_dic[interaction.channel.name]
    #print(prompt)
    results,payload=SD(prompt,lora=lora)
    if not "images" in results:
        print("Error")
        msg=await interaction.response.send_message(str(results["detail"]["msg"]))
    else:
        images = results['images']
        #view=ImageOptionButton()
        view_up= View(timeout=None)
        view_var=View(timeout=None)
        #def button setup
        for i,image in enumerate(images):
            button_up=ImageUPscaleButton(image_str=image,
                         label=f"U{i+1}", style=nextcord.ButtonStyle.blurple)
            view_up.add_item(button_up)
            button_var=ImageVariationButton(image,payload,
                        label=f"V{i+1}", style=nextcord.ButtonStyle.blurple)
            view_var.add_item(button_var)  
        grid=combine_images(images)
        image_bytes = BytesIO()
        grid.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        await msg.edit(content="",file=nextcord.File(image_bytes,"image.png"))
        await interaction.followup.send("", view=view_var) #response.send_message("",view=view_var)
        #await interaction.response.send_message("",view=view_up)


#Generate
@bot.command()
async def generate(ctx: commands.Context,*, prompt: str):
    ETA = int(time.time()+60)
    msg = await ctx.send(f" ETA: <t:{ETA}:R>")
    print(ctx.channel.name)
    lora=None
    if ctx.channel.name in list(channel_model_dic.keys()):# add channel model to promt
        lora=channel_model_dic[ctx.channel.name]
    #print(prompt)
    results,payload=SD(prompt,lora=lora)
    if not "images" in results:
        print("Error")
        msg=await ctx.send(str(results["detail"]["msg"]))
    else:
        images = results['images']
        #view=ImageOptionButton()
        view_up= View(timeout=None)
        view_var=View(timeout=None)
        #def button setup
        for i,image in enumerate(images):
            button_up=ImageUPscaleButton(image_str=image,
                         label=f"U{i+1}", style=nextcord.ButtonStyle.blurple)
            view_up.add_item(button_up)
            button_var=ImageVariationButton(image,payload,
                        label=f"V{i+1}", style=nextcord.ButtonStyle.blurple)
            view_var.add_item(button_var)  
        grid=combine_images(images)
        image_bytes = BytesIO()
        grid.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        await msg.edit(content="",file=nextcord.File(image_bytes,"image.png"))
        await ctx.send("",view=view_var)
        await ctx.send("",view=view_up)
       
bot.run(os.getenv("DISCORD_TOKEN"))


    
