from PIL import Image

def pixelify_image(im: Image, new_width):
    w_ratio = new_width / im.width

    resized_img = im.resize((new_width, round(im.height*w_ratio)), Image.Resampling.LANCZOS)
    return resized_img
