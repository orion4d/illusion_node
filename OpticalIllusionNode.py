from PIL import Image, ImageDraw
import numpy as np
import torch
import math

class OpticalIllusionNode:
    CATEGORY = "illusion"
    FUNCTION = "generate_illusion"
    RETURN_TYPES = ("IMAGE",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "illusion_type": (["checkerboard", "circles", "lines", "spiral"], {"default": "checkerboard"}),
                "size": ("INT", {"default": 512, "min": 128, "max": 2048}),
                "frequency": ("INT", {"default": 10, "min": 2, "max": 100}),
                "line_width": ("INT", {"default": 3, "min": 1, "max": 100}),
                "color1": ("STRING", {"default": "#FFFFFF"}),
                "color2": ("STRING", {"default": "#000000"})
            }
        }

    def generate_illusion(self, illusion_type, size, frequency, line_width, color1, color2):
        img = Image.new('RGB', (size, size), color1)
        draw = ImageDraw.Draw(img)

        if illusion_type == "checkerboard":
            tile = size // frequency
            for y in range(frequency):
                for x in range(frequency):
                    if (x + y) % 2 == 0:
                        draw.rectangle([x*tile, y*tile, (x+1)*tile, (y+1)*tile], fill=color2)

        elif illusion_type == "circles":
            step = size / (frequency * 2)
            for i in range(frequency):
                radius = step * (i + 1)
                bbox = [size//2 - radius, size//2 - radius, size//2 + radius, size//2 + radius]
                draw.ellipse(bbox, outline=color2 if i % 2 == 0 else color1, width=line_width)

        elif illusion_type == "lines":
            spacing = size / frequency
            for i in range(frequency):
                offset = i * spacing
                draw.line([(offset, 0), (offset, size)], fill=color2 if i % 2 == 0 else color1, width=line_width)

        elif illusion_type == "spiral":
            cx, cy = size // 2, size // 2
            max_radius = size * 0.48
            num_turns = frequency
            step_theta = math.pi / 720  # très fin = très lisse
            a = 0
            b = max_radius / (2 * math.pi * num_turns)
            theta = 0
            while theta < 2 * math.pi * num_turns:
                r = a + b * theta
                bbox = [cx - r, cy - r, cx + r, cy + r]
                start = math.degrees(theta)
                end = math.degrees(theta + step_theta)
                draw.arc(bbox, start, end, fill=color2, width=line_width)
                theta += step_theta

        img_array = np.array(img).astype(np.float32) / 255.0
        tensor = torch.from_numpy(img_array).unsqueeze(0)
        return (tensor,)
