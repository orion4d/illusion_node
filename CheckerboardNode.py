from PIL import Image
import numpy as np
import torch

class CheckerboardNode:
    CATEGORY = "illusion"
    FUNCTION = "generate_checkerboard"
    RETURN_TYPES = ("IMAGE",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "img1": ("IMAGE",),   # Première image ou couleur
                "img2": ("IMAGE",),   # Deuxième image ou couleur
                "tiles_x": ("INT", {"default": 8, "min": 1, "max": 128}),  # Cases sur X
                "tiles_y": ("INT", {"default": 8, "min": 1, "max": 128}),  # Cases sur Y
                "tile_width": ("INT", {"default": 128, "min": 8, "max": 1024}),   # Largeur carreau
                "tile_height": ("INT", {"default": 128, "min": 8, "max": 1024}),  # Hauteur carreau
                "tile_mode": (["crop", "resize"], {"default": "resize"}),
            }
        }

    def generate_checkerboard(self, img1, img2, tiles_x, tiles_y, tile_width, tile_height, tile_mode):
        # Conversion de torch.Tensor vers numpy si besoin
        if hasattr(img1, "cpu"):
            img1 = img1.cpu().numpy()
        if hasattr(img2, "cpu"):
            img2 = img2.cpu().numpy()
        if isinstance(img1, list) or img1.ndim == 4:
            img1 = img1[0]
        if isinstance(img2, list) or img2.ndim == 4:
            img2 = img2[0]
        im1 = Image.fromarray(np.clip((img1 * 255), 0, 255).astype(np.uint8))
        im2 = Image.fromarray(np.clip((img2 * 255), 0, 255).astype(np.uint8))

        # Nouvelle taille finale
        final_width = tiles_x * tile_width
        final_height = tiles_y * tile_height

        # Préparer les dalles
        if tile_mode == "resize":
            tile1 = im1.resize((tile_width, tile_height))
            tile2 = im2.resize((tile_width, tile_height))
        else:  # "crop"
            tile1 = im1.crop((0, 0, tile_width, tile_height))
            tile2 = im2.crop((0, 0, tile_width, tile_height))

        result = Image.new("RGB", (final_width, final_height))
        for y in range(tiles_y):
            for x in range(tiles_x):
                tile = tile1 if (x + y) % 2 == 0 else tile2
                px, py = x * tile_width, y * tile_height
                result.paste(tile, (px, py))
        arr = np.array(result).astype(np.float32) / 255.0
        tensor = torch.from_numpy(arr).unsqueeze(0)
        return (tensor,)

NODE_CLASS_MAPPINGS = {
    "CheckerboardNode": CheckerboardNode,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "CheckerboardNode": "Checkerboard Composer",
}
