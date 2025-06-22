from PIL import Image, ImageEnhance
import numpy as np
import torch
import random

class TessellationNode:
    CATEGORY = "illusion"
    FUNCTION = "tessellate"
    RETURN_TYPES = ("IMAGE",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_image": ("IMAGE",),
                "tile_width": ("INT", {"default": 128, "min": 8, "max": 2048}),
                "tile_height": ("INT", {"default": 128, "min": 8, "max": 2048}),
                "tiles_x": ("INT", {"default": 4, "min": 1, "max": 32}),
                "tiles_y": ("INT", {"default": 4, "min": 1, "max": 32}),
                "mode": (["repeat", "mirror", "diamond"], {"default": "repeat"}),
                "mirror_axis": (["none", "x", "y", "xy", "random"], {"default": "none"}),
                "offset_x": ("INT", {"default": 0, "min": -2048, "max": 2048}),
                "offset_y": ("INT", {"default": 0, "min": -2048, "max": 2048}),
                "rotation_mode": (["none", "by_tile", "random"], {"default": "none"}),
                "rotation_angle": ("FLOAT", {"default": 0, "min": 0, "max": 360}),
                "scale_mode": (["none", "by_tile", "random"], {"default": "none"}),
                "scale_factor": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 4.0}),
                "opacity": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 1.0}),
                "random_seed": ("INT", {"default": 0, "min": 0, "max": 999999}),
            }
        }

    def tensor_to_pil(self, img_tensor):
        arr = img_tensor[0] if isinstance(img_tensor, list) or len(img_tensor.shape) == 4 else img_tensor
        arr = arr.cpu().numpy() if hasattr(arr, 'cpu') else arr
        arr = np.clip(arr, 0, 1)
        arr = (arr * 255).astype(np.uint8)
        if arr.shape[-1] == 1:
            arr = np.repeat(arr, 3, axis=-1)
        return Image.fromarray(arr)

    def tessellate(
        self,
        input_image,
        tile_width,
        tile_height,
        tiles_x,
        tiles_y,
        mode,
        mirror_axis,
        offset_x,
        offset_y,
        rotation_mode,
        rotation_angle,
        scale_mode,
        scale_factor,
        opacity,
        random_seed
    ):
        random.seed(random_seed)
        base_tile = self.tensor_to_pil(input_image).convert("RGBA")
        if base_tile.size != (tile_width, tile_height):
            base_tile = base_tile.resize((tile_width, tile_height), resample=Image.LANCZOS)

        # Canvas size for diamond mode
        if mode == "diamond":
            result_w = int(tile_width * (tiles_x + tiles_y/2))
            result_h = int(tile_height * (tiles_y/2 + 0.5))
        else:
            result_w = tile_width * tiles_x
            result_h = tile_height * tiles_y

        result = Image.new("RGBA", (result_w, result_h), (0, 0, 0, 0))

        for iy in range(tiles_y):
            for ix in range(tiles_x):
                tile = base_tile.copy()

                # SCALE
                if scale_mode == "by_tile":
                    fac = scale_factor * (1 + 0.05 * ((ix + iy) % 3))
                    tw, th = max(8, int(tile_width * fac)), max(8, int(tile_height * fac))
                    tile = tile.resize((tw, th), resample=Image.LANCZOS)
                elif scale_mode == "random":
                    fac = scale_factor * random.uniform(0.85, 1.15)
                    tw, th = max(8, int(tile_width * fac)), max(8, int(tile_height * fac))
                    tile = tile.resize((tw, th), resample=Image.LANCZOS)
                else:
                    tw, th = tile_width, tile_height

                # ROTATION
                angle = 0
                if rotation_mode == "by_tile":
                    angle = rotation_angle * ((ix + iy) % 4)
                elif rotation_mode == "random":
                    angle = random.uniform(0, rotation_angle)
                if angle != 0:
                    tile = tile.rotate(angle, expand=True, fillcolor=(0,0,0,0))

                # MIRROR
                if mirror_axis == "x" and (ix % 2 == 1):
                    tile = tile.transpose(Image.FLIP_LEFT_RIGHT)
                if mirror_axis == "y" and (iy % 2 == 1):
                    tile = tile.transpose(Image.FLIP_TOP_BOTTOM)
                if mirror_axis == "xy" and ((ix + iy) % 2 == 1):
                    tile = tile.transpose(Image.ROTATE_180)
                if mirror_axis == "random" and random.random() < 0.5:
                    tile = tile.transpose(random.choice([
                        Image.FLIP_LEFT_RIGHT,
                        Image.FLIP_TOP_BOTTOM,
                        Image.ROTATE_180
                    ]))

                # OPACITY
                if opacity < 1.0:
                    if tile.mode != "RGBA":
                        tile = tile.convert("RGBA")
                    alpha = tile.split()[-1]
                    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
                    tile.putalpha(alpha)

                # OFFSETS (classique ou diamant)
                if mode == "diamond":
                    px = int(ix * tile_width + iy * tile_width / 2 + (offset_x if (iy % 2 == 1) else 0))
                    py = int(iy * tile_height / 2 + (offset_y if (ix % 2 == 1) else 0))
                else:
                    px = ix * tile_width + (offset_x if (iy % 2 == 1) else 0)
                    py = iy * tile_height + (offset_y if (ix % 2 == 1) else 0)

                result.alpha_composite(tile, (int(px), int(py)))

        arr_out = np.array(result.convert("RGB")).astype(np.float32) / 255.0
        tensor = torch.from_numpy(arr_out).unsqueeze(0)
        return (tensor,)

NODE_CLASS_MAPPINGS = {
    "TessellationNode": TessellationNode,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "TessellationNode": "Tessellation Composer (Advanced)",
}
