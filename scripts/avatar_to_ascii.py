import requests
from PIL import Image
from io import BytesIO

# Character ramps for ASCII conversion
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

def image_to_color_ascii(image: Image.Image, width: int = 60, aspect_ratio_factor: float = 0.5) -> list[list[tuple[str, str]]]:
    """
    Converts a Pillow image to a 2D grid of (character, hex_color).
    """
    # Handle transparency: paste RGBA images onto a dark background
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        alpha_composite = Image.new("RGBA", image.size, (11, 15, 25, 255)) # Match terminal background color
        alpha_composite.paste(image, mask=image.split()[-1])
        image = alpha_composite.convert("RGB")
    else:
        image = image.convert("RGB")
    
    # Calculate height preserving aspect ratio with character font compensation
    img_width, img_height = image.size
    height = int(width * (img_height / img_width) * aspect_ratio_factor)
    height = max(height, 1)
    
    # Resize image
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    
    # Convert pixels to character and color grid
    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            r, g, b = image.getpixel((x, y))
            # Calculate luminance for character mapping
            gray = int(0.299 * r + 0.587 * g + 0.114 * b)
            char_idx = int(gray * (len(ASCII_RAMP) - 1) / 255)
            char = ASCII_RAMP[char_idx]
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            row.append((char, hex_color))
        grid.append(row)
        
    return grid

if __name__ == "__main__":
    import sys
    username = "Harsh-sh7"
    if len(sys.argv) > 1:
        username = sys.argv[1]
        
    print(f"Testing color ASCII conversion for {username}...")
    img = download_avatar(username)
    grid = image_to_color_ascii(img, width=60)
    print(f"Generated grid of size {len(grid)}x{len(grid[0]) if grid else 0}")
    # Print grayscale version in terminal
    for row in grid:
        print("".join([cell[0] for cell in row]))
