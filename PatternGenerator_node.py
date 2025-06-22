import numpy as np
import torch
from PIL import Image, ImageDraw, ImageColor
import random

class PatternGeneratorNode:
    PATTERN_TYPES = ["Stripes", "Checkerboard", "Random Dots", "Solid Color", "Gradient", "Noise"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 128, "min": 16, "max": 4096, "step": 8}),
                "height": ("INT", {"default": 128, "min": 16, "max": 4096, "step": 8}),
                "pattern_type": (cls.PATTERN_TYPES, {"default": "Noise"}),
                "color1_hex": ("STRING", {"default": "#000000", "multiline": False}),
                "color2_hex": ("STRING", {"default": "#FFFFFF", "multiline": False}),
                "parameter1": ("INT", {"default": 1, "min": 0, "max": 256, "step": 1, "tooltip":"Stripes:width; Dots:density%; Gradient:direction; Noise:0=Color/1=Grayscale"}), 
                "parameter2": ("INT", {"default": 1, "min": 1, "max": 64, "step": 1, "tooltip":"Dots:max_radius; Noise:block_scale"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFF}), 
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_pattern"
    CATEGORY = "illusion"

    def _hex_to_rgb(self, hex_color_string):
        try:
            return ImageColor.getrgb(hex_color_string)
        except ValueError:
            print(f"PatternGeneratorNode Warning: Invalid color string '{hex_color_string}'. Defaulting to black.")
            return (0, 0, 0)

    def generate_pattern(self, width, height, pattern_type, color1_hex, color2_hex, parameter1, parameter2, seed):
        np.random.seed(seed)
        random.seed(seed)

        c1 = self._hex_to_rgb(color1_hex)
        c2 = self._hex_to_rgb(color2_hex)
        
        image_np = np.zeros((height, width, 3), dtype=np.uint8)

        if pattern_type == "Stripes":
            stripe_width = max(1, parameter1) # Stripe width
            orientation = "Vertical" # Could be an input later
            for y_coord in range(height):
                for x_coord in range(width):
                    if orientation == "Vertical":
                        if (x_coord // stripe_width) % 2 == 0:
                            image_np[y_coord, x_coord] = c1
                        else:
                            image_np[y_coord, x_coord] = c2
                    else: # Horizontal
                        if (y_coord // stripe_width) % 2 == 0:
                            image_np[y_coord, x_coord] = c1
                        else:
                            image_np[y_coord, x_coord] = c2
        
        elif pattern_type == "Checkerboard":
            square_size = max(1, parameter1) # Square size
            for y_coord in range(height):
                for x_coord in range(width):
                    if ((x_coord // square_size) % 2 == (y_coord // square_size) % 2):
                        image_np[y_coord, x_coord] = c1
                    else:
                        image_np[y_coord, x_coord] = c2

        elif pattern_type == "Random Dots":
            density_percent = np.clip(parameter1, 1, 100) # Density percentage
            dot_radius_min = 1
            dot_radius_max = np.clip(parameter2, 1, min(width, height)//4) # Max dot radius
            
            avg_radius = (dot_radius_min + dot_radius_max) / 2.0
            if avg_radius < 1: avg_radius = 1
            num_dots = int((width * height * (density_percent / 100.0)) / (np.pi * avg_radius**2))
            num_dots = max(10, num_dots) 
            num_dots = min(num_dots, width * height // 2) # Prevent extreme overdraw

            pil_image = Image.fromarray(image_np) 
            pil_image = pil_image.convert("RGB") 
            pil_image.paste(c1, (0,0,width,height)) 
            draw = ImageDraw.Draw(pil_image)

            for _ in range(num_dots):
                dot_x = random.randint(0, width - 1)
                dot_y = random.randint(0, height - 1)
                dot_radius = random.randint(dot_radius_min, dot_radius_max)
                color_choice = c2 
                
                bbox = (dot_x - dot_radius, dot_y - dot_radius, 
                        dot_x + dot_radius, dot_y + dot_radius)
                try: # Add try-except for rare issues with ellipse on tiny images/radii
                    draw.ellipse(bbox, fill=color_choice)
                except ValueError:
                    pass # Skip dot if it causes an issue
            image_np = np.array(pil_image)

        elif pattern_type == "Solid Color":
            image_np[:, :] = c1

        elif pattern_type == "Gradient":
            direction = parameter1 % 4 # Gradient direction
            for y_coord in range(height):
                for x_coord in range(width):
                    if direction == 0: # Left to Right
                        ratio = x_coord / (width -1) if width > 1 else 0
                    elif direction == 1: # Top to Bottom
                        ratio = y_coord / (height -1) if height > 1 else 0
                    elif direction == 2: # Right to Left
                        ratio = (width - 1 - x_coord) / (width - 1) if width > 1 else 0
                    else: # Bottom to Top (direction == 3)
                        ratio = (height - 1 - y_coord) / (height - 1) if height > 1 else 0
                    
                    r_val = int(c1[0] * (1 - ratio) + c2[0] * ratio)
                    g_val = int(c1[1] * (1 - ratio) + c2[1] * ratio)
                    b_val = int(c1[2] * (1 - ratio) + c2[2] * ratio)
                    image_np[y_coord, x_coord] = (r_val, g_val, b_val)
        
        elif pattern_type == "Noise":
            is_grayscale_noise = parameter1 == 1 # 0 for color, 1 for grayscale
            block_scale = max(1, parameter2)      # Scale of noise blocks, 1 for pixel noise

            for y_base in range(0, height, block_scale):
                for x_base in range(0, width, block_scale):
                    if is_grayscale_noise:
                        val = random.randint(0, 255)
                        chosen_color = (val, val, val)
                    else:
                        chosen_color = (random.randint(0, 255), 
                                 random.randint(0, 255), 
                                 random.randint(0, 255))
                    
                    for y_offset in range(block_scale):
                        for x_offset in range(block_scale):
                            y = y_base + y_offset
                            x = x_base + x_offset
                            if y < height and x < width:
                                image_np[y, x] = chosen_color
        
        image_tensor = torch.from_numpy(image_np.astype(np.float32) / 255.0).unsqueeze(0)
        return (image_tensor,)

NODE_CLASS_MAPPINGS = {
    "PatternGeneratorNode": PatternGeneratorNode,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "PatternGeneratorNode": "Pattern Generator"
}