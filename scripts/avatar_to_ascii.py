import requests
from PIL import Image
from io import BytesIO

# Character ramps for ASCII conversion
# For dark backgrounds: darker pixels are mapped to spaces/dots, lighter to denser chars.
ASCII_RAMP = " .:-=+*#%@"

def download_avatar(username: str) -> Image.Image:
    """
    Downloads the GitHub avatar for the given username.
    Falls back to a default placeholder if download fails.
    """
    url = f"https://github.com/{username}.png"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Error downloading avatar: {e}. Falling back to default placeholder.")
        # Create a 100x100 grayscale placeholder image with a circle inside
        img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.ellipse([10, 10, 90, 90], fill=(200, 200, 200, 255))
        return img

def image_to_ascii(image: Image.Image, width: int = 38, aspect_ratio_factor: float = 0.55) -> list[str]:
    """
    Converts a Pillow image to a list of ASCII strings.
    """
    # Handle transparency: paste RGBA images onto a black background
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        alpha_composite = Image.new("RGBA", image.size, (11, 15, 25, 255)) # Match terminal background color
        alpha_composite.paste(image, mask=image.split()[-1])
        image = alpha_composite.convert("RGB")
    else:
        image = image.convert("RGB")
    
    # Calculate height preserving aspect ratio with character font compensation
    img_width, img_height = image.size
    height = int(width * (img_height / img_width) * aspect_ratio_factor)
    
    # Ensure minimum height
    height = max(height, 1)
    
    # Resize image
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    
    # Convert to grayscale
    gray_image = image.convert("L")
    pixels = list(gray_image.tobytes())
    
    # Map pixels to characters
    ascii_chars = []
    ramp_len = len(ASCII_RAMP)
    
    for i, pixel in enumerate(pixels):
        if i % width == 0:
            if i > 0:
                ascii_chars.append("\n")
        
        # Scale to match character ramp index
        char_idx = int(pixel * (ramp_len - 1) / 255)
        ascii_chars.append(ASCII_RAMP[char_idx])
        
    ascii_str = "".join(ascii_chars)
    return ascii_str.split("\n")

if __name__ == "__main__":
    import sys
    username = "Harsh-sh7"
    if len(sys.argv) > 1:
        username = sys.argv[1]
        
    print(f"Testing avatar download and ASCII conversion for {username}...")
    img = download_avatar(username)
    ascii_lines = image_to_ascii(img, width=38)
    for line in ascii_lines:
        print(line)
