def resize(image,W_TARGET=512,H_TARGET=512):
    width, height = image.size
    if width < height:
        new_width = W_TARGET
        new_height = int(new_width / width * height)
    else:
        new_height = H_TARGET
        new_width = int(new_height / height * width)

    return image.resize((new_width, new_height))