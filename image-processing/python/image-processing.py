import requests
from io import BytesIO
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageOps
import os

image_url = "https://raw.githubusercontent.com/mikolalysenko/lena/master/lena.png"

def generate_multiple_images(image_url):

    if not image_url:
        print("Image URL is not provided.")
        return
    
    response = requests.get(image_url)

    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
    else:
        print(f"Failed to fetch image: {response.status_code}")
        print(response.text[:500])
        return  # exit if failed to fetch image

    os.makedirs("/data/outputs", exist_ok=True)

    # List of filters & operations
    filters = [
        ("GaussianBlur", img.filter(ImageFilter.GaussianBlur(radius=5))),
        ("Grayscale", img.convert("L")),
        ("UnsharpMask", img.filter(ImageFilter.UnsharpMask(radius=5))),
        ("BoxBlur", img.filter(ImageFilter.BoxBlur(radius=5))),
        ("Contour", img.filter(ImageFilter.CONTOUR)),
        ("Detail", img.filter(ImageFilter.DETAIL)),
        ("EdgeEnhance", img.filter(ImageFilter.EDGE_ENHANCE)),
        ("EdgeEnhanceMore", img.filter(ImageFilter.EDGE_ENHANCE_MORE)),
        ("Emboss", img.filter(ImageFilter.EMBOSS)),
        ("FindEdges", img.filter(ImageFilter.FIND_EDGES)),
        ("Sharpen", img.filter(ImageFilter.SHARPEN)),
        ("Smooth", img.filter(ImageFilter.SMOOTH)),
        ("SmoothMore", img.filter(ImageFilter.SMOOTH_MORE)),
        ("MedianFilter", img.filter(ImageFilter.MedianFilter(size=5))),
        ("MinFilter", img.filter(ImageFilter.MinFilter(size=5))),
        ("MaxFilter", img.filter(ImageFilter.MaxFilter(size=5))),
        ("ModeFilter", img.filter(ImageFilter.ModeFilter(size=5))),
        ("Posterize", ImageOps.posterize(img, bits=4)),
        ("Invert", ImageOps.invert(img.convert("RGB"))),
        ("Solarize",  ImageOps.solarize(img, threshold=128))
    ]

    # Save individual images
    for name, image in filters:
        image.save(f"/data/outputs/{name.lower()}_img.png")

    # --- Now create the final grid image ---

    cols = 4
    padding = 20
    label_height = 30

    # Reload saved images to ensure grayscale modes are handled uniformly
    images = [Image.open(f"/data/outputs/{name.lower()}_img.png").convert("RGB") for name, _ in filters]

    img_width, img_height = images[0].size
    rows = (len(images) + cols - 1) // cols
    grid_width = cols * (img_width + padding) + padding
    grid_height = rows * (img_height + label_height + padding) + padding

    grid_img = Image.new("RGB", (grid_width, grid_height), color="white")

    # Font handling
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(grid_img)

    for idx, (filter_name, _) in enumerate(filters):
        x = padding + (idx % cols) * (img_width + padding)
        y = padding + (idx // cols) * (img_height + label_height + padding)

        grid_img.paste(images[idx], (x, y))

        bbox = draw.textbbox((0, 0), filter_name, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = x + (img_width - text_width) // 2
        text_y = y + img_height
        draw.text((text_x, text_y), filter_name, fill="black", font=font)


    grid_img.save("/data/outputs/filters_grid.png")
    print("Grid image saved at: /data/outputs/filters_grid.png")

if __name__ == "__main__":
    generate_multiple_images(image_url=image_url)
