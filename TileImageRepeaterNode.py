import numpy as np
import torch
from PIL import Image

class TileImageRepeaterNode:
    RESIZE_MODES = ["None", "Width", "Height", "Shortest Side", "Longest Side"] # Ajout de None, et de Shortest/Longest Side
    RESAMPLING_FILTERS = ["lanczos", "bicubic", "bilinear", "nearest"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "horizontal_repeats": ("INT", {"default": 3, "min": 1, "max": 32, "step": 1}),
                "vertical_repeats": ("INT", {"default": 3, "min": 1, "max": 32, "step": 1}),
                "resize_mode": (cls.RESIZE_MODES, {"default": "None"}),
                "tile_target_size": ("INT", {"default": 256, "min": 0, "max": 8192, "step": 8, "tooltip": "Target size for the chosen dimension (Width, Height, Shortest/Longest Side). 0 or 'None' mode to disable resize."}),
                "resampling_filter": (cls.RESAMPLING_FILTERS, {"default": "lanczos"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "repeat_image_as_tiles"
    CATEGORY = "illusion"

    def repeat_image_as_tiles(self, image, horizontal_repeats, vertical_repeats, resize_mode, tile_target_size, resampling_filter):
        if not isinstance(image, torch.Tensor):
            if isinstance(image, list) and len(image) > 0 and isinstance(image[0], torch.Tensor):
                image_tensor = image[0]
            else:
                raise TypeError(f"Input image must be a torch.Tensor or a list containing one, got {type(image)}")
        else:
            image_tensor = image
        
        if image_tensor.ndim == 3:
            image_bchw_float = image_tensor.unsqueeze(0) 
        elif image_tensor.ndim == 4:
             image_bchw_float = image_tensor
        else:
             raise ValueError(f"Input image tensor must be 3D (H,W,C) or 4D (B,H,W,C), got {image_tensor.ndim}D shape: {image_tensor.shape}")

        single_image_hwc_float = image_bchw_float[0].cpu().numpy()
        
        pil_image_mode = 'RGB'
        if single_image_hwc_float.ndim == 3 and single_image_hwc_float.shape[2] == 1:
            pil_image_mode = 'L'
        elif single_image_hwc_float.ndim == 2: # Si c'est déjà 2D (grayscale)
            pil_image_mode = 'L'
            
        pil_image = Image.fromarray((single_image_hwc_float * 255).squeeze().astype(np.uint8), mode=pil_image_mode)
        
        original_width, original_height = pil_image.size
        resized_image_hwc_float = single_image_hwc_float # Par défaut, pas de redimensionnement

        if resize_mode != "None" and tile_target_size > 0:
            target_w = original_width
            target_h = original_height
            aspect_ratio = original_width / original_height if original_height != 0 else 1

            if resize_mode == "Width":
                target_w = tile_target_size
                target_h = int(target_w / aspect_ratio) if aspect_ratio != 0 else original_height
            elif resize_mode == "Height":
                target_h = tile_target_size
                target_w = int(target_h * aspect_ratio)
            elif resize_mode == "Shortest Side":
                if original_width < original_height: # Width is shortest
                    target_w = tile_target_size
                    target_h = int(target_w / aspect_ratio) if aspect_ratio != 0 else original_height
                else: # Height is shortest (or square)
                    target_h = tile_target_size
                    target_w = int(target_h * aspect_ratio)
            elif resize_mode == "Longest Side":
                if original_width > original_height: # Width is longest
                    target_w = tile_target_size
                    target_h = int(target_w / aspect_ratio) if aspect_ratio != 0 else original_height
                else: # Height is longest (or square)
                    target_h = tile_target_size
                    target_w = int(target_h * aspect_ratio)

            # S'assurer que les dimensions cibles ne sont pas nulles
            target_w = max(1, target_w)
            target_h = max(1, target_h)

            if (target_w != original_width or target_h != original_height):
                resampling_map = {
                    "lanczos": Image.Resampling.LANCZOS, "bicubic": Image.Resampling.BICUBIC,
                    "bilinear": Image.Resampling.BILINEAR, "nearest": Image.Resampling.NEAREST
                }
                resample_pil = resampling_map.get(resampling_filter, Image.Resampling.LANCZOS)
                
                print(f"TileImageRepeaterNode: Resizing tile from {original_width}x{original_height} to {target_w}x{target_h} using {resampling_filter}")
                pil_image_resized = pil_image.resize((target_w, target_h), resample=resample_pil)
                
                # Reconvertir en NumPy array et s'assurer qu'il a 3 canaux si l'original en avait 3
                resized_np = np.array(pil_image_resized).astype(np.float32) / 255.0
                if resized_np.ndim == 2: # Si PIL retourne une image en niveaux de gris (L mode)
                    resized_image_hwc_float = np.stack((resized_np,) * 3, axis=-1) if single_image_hwc_float.shape[2] == 3 else resized_np[:,:,np.newaxis]
                else: # Déjà RGB
                    resized_image_hwc_float = resized_np
            else:
                 resized_image_hwc_float = single_image_hwc_float # Aucune redimension effective
        else: # resize_mode == "None" or tile_target_size == 0
            resized_image_hwc_float = single_image_hwc_float


        # S'assurer que le nombre de canaux est correct après toutes les opérations
        # Surtout si l'entrée était grayscale
        if single_image_hwc_float.shape[2] == 1 and resized_image_hwc_float.ndim == 3 and resized_image_hwc_float.shape[2] == 3:
            # Si l'entrée était grayscale mais que le redimensionnement a produit RGB (ex: mode 'L' vers 'RGB'), prendre la moyenne
            resized_image_hwc_float = np.mean(resized_image_hwc_float, axis=2, keepdims=True)
        elif single_image_hwc_float.shape[2] == 3 and resized_image_hwc_float.ndim == 2:
            # Si l'entrée était RGB mais que le redimensionnement a produit Grayscale, répéter le canal
            resized_image_hwc_float = np.stack((resized_image_hwc_float,) * 3, axis=-1)
        elif single_image_hwc_float.shape[2] == 3 and resized_image_hwc_float.ndim == 3 and resized_image_hwc_float.shape[2] == 1:
             resized_image_hwc_float = np.repeat(resized_image_hwc_float, 3, axis=2)


        tiled_image_np_float = np.tile(resized_image_hwc_float, 
                                       (vertical_repeats, horizontal_repeats, 1))
        
        output_tensor_bhwc = torch.from_numpy(tiled_image_np_float).unsqueeze(0)
        
        return (output_tensor_bhwc,)

NODE_CLASS_MAPPINGS = {
    "TileImageRepeaterNode": TileImageRepeaterNode
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "TileImageRepeaterNode": "Tile Image Repeater (Smart Resize)"
}