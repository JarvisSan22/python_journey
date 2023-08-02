import os
import requests
import json
import time
from utils.promt_setup import promt_gen
from utils.sd_api import SD_APICALL
from utils.SD_gen import generator 
from PIL import Image
import nextcord 
from nextcord.ext import commands 
from nextcord.ui import Button, View
from io import BytesIO
import base64


def combine_images(images):
    # Create a blank canvas for the final grid image
    images=[Image.open(image) for image in images]
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

class ImageGrid_Buttons(View):
    def __init__(self,images,grid):
        super().__init__()
        self.images=images 
        self.grid=grid

        for i in range(0,len(self.images)):
            self.create_button(i+1,self.images[i])
    def create_button(self,option_number,image):
        async def option(self, button: nextcord.Button,interaction=nextcord.Interaction):
            await interaction.response.send_message(content=f"You selected Option {option_number}",file=nextcord.File(image,"genimage.png"))
        
        setattr(self, f"option_{option_number}", nextcord.ui.button(label=f"Option {option_number}", style=nextcord.ButtonStyle.primary)(option))

class ImageOptionButton(View):
    def __init__(self):
        super().__init__()
        self.images=[]
    async def on_button_click(self,button:nextcord.Button,interaction:nextcord.Interaction):
        #async def on_button_click(self, button: nextcord.Button, interaction: nextcord.Interaction):
        button_index = int(button.custom_id.replace("U",""))-1
        print("clicked button", button_index)
        await interaction.response.send_message("Image selected",
                                            file=nextcord.File(self.images[button_index],"image.png"))
class ImageButton(nextcord.ui.Button):
    def __init__(self, image_url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_url = image_url

    async def callback(self, interaction: nextcord.Interaction):
        # Get the user who clicked the button
        user = interaction.user
        # Create an embed with the image
        self.image_url.seek(0)
        file=nextcord.File(self.image_url,"image.png")
        await interaction.response.send_message(f"Upscaled", ephemeral=False, file=file)



#Generate
@bot.command()
async def generate(ctx: commands.Context,*, prompt: str):
    ETA = int(time.time()+60)
    msg = await ctx.send(f" ETA: <t:{ETA}:R>")
    #print(prompt)
    results=SD(prompt)
    if not "images" in results:
        print("Error")
        msg=await ctx.send(str(results["detail"]["msg"]))
    else:
        images = results['images']
        
        #view=ImageOptionButton()
        view= View()
        for i,image in enumerate(images):
            image = BytesIO(base64.decodebytes(image.encode("utf-8"))) 
            button=ImageButton(image_url=image,
                         label=f"U{i+1}", style=nextcord.ButtonStyle.blurple)
            view.add_item(button)
            images[i]=image
        grid=combine_images(images)
        
        image_bytes = BytesIO()
        grid.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        #view= ImageGrid_Buttons(images,image_bytes)
        await msg.edit(content="",file=nextcord.File(image_bytes,"image.png"))
        await ctx.send("---",view=view)
       
bot.run(os.getenv("DISCORD_TOKEN"))


    
