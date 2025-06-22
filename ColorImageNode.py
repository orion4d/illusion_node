from PIL import Image
import numpy as np
import torch

def parse_color(color):
    # Gère hex, noms, tuple/list
    if isinstance(color, str):
        color = color.lstrip("#")
        if len(color) == 6:
            return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        elif len(color) == 3:
            return tuple(int(color[i]*2, 16) for i in range(3))
        else:
            try:
                img = Image.new("RGB", (1, 1), color)
                return img.getpixel((0, 0))
            except:
                return (0, 0, 0)
    elif isinstance(color, (tuple, list)) and len(color) == 3:
        return tuple(int(c) for c in color)
    else:
        return (0, 0, 0)

class ColorImageNode:
    CATEGORY = "illusion"
    FUNCTION = "generate_color"
    RETURN_TYPES = ("IMAGE",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 512, "min": 16, "max": 4096}),
                "height": ("INT", {"default": 512, "min": 16, "max": 4096}),
                "mode": (["solid", "linear", "radial", "angular", "mirror", "diamond"], {"default": "solid"}),
                "color1": ("STRING", {"default": "#ffffff"}),
                "color2": ("STRING", {"default": "#000000"}),
                "angle": ("FLOAT", {"default": 0.0, "min": 0, "max": 360, "step": 0.1}),
            }
        }

    def generate_color(self, width, height, mode, color1, color2, angle):
        rgb1 = parse_color(color1)
        rgb2 = parse_color(color2)
        arr = np.zeros((height, width, 3), dtype=np.uint8)
        cx, cy = width // 2, height // 2
        Y, X = np.ogrid[:height, :width]

        if mode == "solid":
            arr[:, :] = rgb1

        elif mode == "linear":
            x = np.linspace(0, 1, width)
            y = np.linspace(0, 1, height)
            Xg, Yg = np.meshgrid(x, y)
            theta = np.deg2rad(angle)
            t = Xg * np.cos(theta) + Yg * np.sin(theta)
            t = (t - t.min()) / (t.max() - t.min())
            for i in range(3):
                arr[..., i] = (rgb1[i] * (1 - t) + rgb2[i] * t).astype(np.uint8)

        elif mode == "radial":
            dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
            dist = dist / dist.max()
            for i in range(3):
                arr[..., i] = (rgb1[i] * (1 - dist) + rgb2[i] * dist).astype(np.uint8)

        elif mode == "angular":  # Sweep/angle Photoshop
            Xg = X - cx
            Yg = Y - cy
            theta = np.arctan2(Yg, Xg)  # -π à π
            offset = np.deg2rad(angle)
            t = ((theta + np.pi + offset) % (2 * np.pi)) / (2 * np.pi)
            for i in range(3):
                arr[..., i] = (rgb1[i] * (1 - t) + rgb2[i] * t).astype(np.uint8)

        elif mode == "mirror":  # Réfléchi
            x = np.linspace(0, 1, width)
            y = np.linspace(0, 1, height)
            Xg, Yg = np.meshgrid(x, y)
            theta = np.deg2rad(angle)
            t = Xg * np.cos(theta) + Yg * np.sin(theta)
            t = np.abs((t - 0.5) * 2)  # miroir autour du centre
            t = (t - t.min()) / (t.max() - t.min())
            for i in range(3):
                arr[..., i] = (rgb1[i] * (1 - t) + rgb2[i] * t).astype(np.uint8)

        elif mode == "diamond":
            dx = np.abs((X - cx) / (width / 2))
            dy = np.abs((Y - cy) / (height / 2))
            t = (dx + dy) / 2
            t = np.clip(t, 0, 1)
            for i in range(3):
                arr[..., i] = (rgb1[i] * (1 - t) + rgb2[i] * t).astype(np.uint8)

        img = torch.from_numpy(arr.astype(np.float32) / 255.0).unsqueeze(0)
        return (img,)

NODE_CLASS_MAPPINGS = {
    "ColorImageNode": ColorImageNode,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "ColorImageNode": "Color/Gradient Image",
}
