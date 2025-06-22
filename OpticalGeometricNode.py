from PIL import Image, ImageDraw
import numpy as np
import torch
import math

class OpticalGeometricNode:
    CATEGORY = "illusion"
    FUNCTION = "generate_geometric"
    RETURN_TYPES = ("IMAGE",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "pattern_type": (
                    ["concentric_squares", "concentric_triangles", "wavy_grid", "starburst", "hexagons", "waves"],
                    {"default": "concentric_squares"}
                ),
                "size": ("INT", {"default": 512, "min": 128, "max": 2048}),
                "frequency": ("INT", {"default": 10, "min": 2, "max": 100}),
                "line_width": ("INT", {"default": 3, "min": 1, "max": 50}),
                "color1": ("STRING", {"default": "#FFFFFF"}),
                "color2": ("STRING", {"default": "#000000"})
            }
        }

    def generate_geometric(self, pattern_type, size, frequency, line_width, color1, color2):
        img = Image.new('RGB', (size, size), color1)
        draw = ImageDraw.Draw(img)
        cx, cy = size // 2, size // 2

        if pattern_type == "concentric_squares":
            step = size // (2 * frequency)
            for i in range(frequency):
                offset = step * i
                draw.rectangle(
                    [offset, offset, size - offset, size - offset],
                    outline=color2 if i % 2 == 0 else color1, width=line_width
                )

        elif pattern_type == "concentric_triangles":
            for i in range(frequency):
                r = (size // 2) * (i + 1) / frequency
                points = [
                    (cx, cy - r),
                    (cx - r * math.sin(math.pi / 3), cy + r * 0.5),
                    (cx + r * math.sin(math.pi / 3), cy + r * 0.5)
                ]
                draw.polygon(points, outline=color2 if i % 2 == 0 else color1, width=line_width)

        elif pattern_type == "wavy_grid":
            waves = frequency
            amp = size / 30
            for y in range(0, size, size // waves):
                points = [
                    (x, int(y + amp * math.sin(2 * math.pi * x / size * waves)))
                    for x in range(size)
                ]
                draw.line(points, fill=color2, width=line_width)
            for x in range(0, size, size // waves):
                points = [
                    (int(x + amp * math.sin(2 * math.pi * y / size * waves)), y)
                    for y in range(size)
                ]
                draw.line(points, fill=color2, width=line_width)

        elif pattern_type == "starburst":
            rays = frequency * 2
            for i in range(rays):
                angle = 2 * math.pi * i / rays
                x = cx + (size // 2) * math.cos(angle)
                y = cy + (size // 2) * math.sin(angle)
                draw.line([(cx, cy), (x, y)], fill=color2 if i % 2 == 0 else color1, width=line_width)

        elif pattern_type == "hexagons":
            # motif nid d’abeille
            hex_r = size // (2 * frequency)
            for y in range(-hex_r, size + hex_r, int(hex_r * 1.5)):
                for x in range(-hex_r, size + hex_r, int(hex_r * math.sqrt(3))):
                    x_shift = x + (hex_r * math.sqrt(3)/2 if (y // (hex_r * 1.5)) % 2 else 0)
                    points = [
                        (x_shift + hex_r * math.cos(a), y + hex_r * math.sin(a))
                        for a in [math.radians(60 * k) for k in range(6)]
                    ]
                    draw.polygon(points, outline=color2, width=line_width)

        elif pattern_type == "waves":
            # Superposition de vagues sinusoïdales (motif Op Art simple)
            for i in range(frequency):
                amp = size / (30 + i * 5)
                y_offset = i * size // (frequency + 1)
                points = [
                    (x, int(y_offset + amp * math.sin(2 * math.pi * x / size * (i+1))))
                    for x in range(size)
                ]
                draw.line(points, fill=color2 if i % 2 == 0 else color1, width=line_width)

        img_array = np.array(img).astype(np.float32) / 255.0
        tensor = torch.from_numpy(img_array).unsqueeze(0)
        return (tensor,)
