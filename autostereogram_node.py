import numpy as np
import torch
from PIL import Image

class AdvancedAutostereogramNode: # Le nom de la classe est AdvancedAutostereogramNode
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "depth_map": ("IMAGE",),
                "pattern": ("IMAGE",),
                "eye_separation_pixels": ("INT", {"default": 100, "min": 30, "max": 400, "step": 1, "tooltip": "Typical eye separation projected onto the image plane in pixels. Influences pattern period and perceived depth."}),
                "depth_scale_factor": ("FLOAT", {"default": 0.5, "min": 0.01, "max": 2.0, "step": 0.01, "tooltip": "Scales the depth effect. Values around 0.3-0.7 are common. Higher values = more 'pop-out'."}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "create_advanced_autostereogram" # La fonction à appeler
    CATEGORY = "illusion"

    def preprocess_image_to_numpy(self, image_tensor_or_pil, target_channels=None, is_depth_map=False):
        # Fonction utilitaire pour convertir l'entrée IMAGE en array NumPy HWC, float32 [0,1]
        if isinstance(image_tensor_or_pil, torch.Tensor):
            img_tensor = image_tensor_or_pil.clone() # Cloner pour éviter de modifier l'original
            if img_tensor.ndim == 4: # B,H,W,C
                img_np = img_tensor[0].cpu().numpy()
            elif img_tensor.ndim == 3: # H,W,C
                img_np = img_tensor.cpu().numpy()
            elif img_tensor.ndim == 2: # H,W (grayscale)
                img_np = img_tensor.cpu().numpy()
            else:
                raise ValueError(f"Unsupported tensor dimensions: {img_tensor.shape}")
        elif isinstance(image_tensor_or_pil, Image.Image):
            # Convertir PIL en NumPy HWC, float32 [0,1]
            if is_depth_map or (target_channels == 1 and image_tensor_or_pil.mode != 'RGB' and image_tensor_or_pil.mode != 'RGBA'):
                img_pil = image_tensor_or_pil.convert("L")
                img_np = np.array(img_pil).astype(np.float32) / 255.0
            else:
                img_pil = image_tensor_or_pil.convert("RGB")
                img_np = np.array(img_pil).astype(np.float32) / 255.0
        else:
            raise TypeError(f"Input must be a torch.Tensor or PIL.Image. Got {type(image_tensor_or_pil)}")

        # S'assurer que les valeurs sont bien entre 0 et 1 si elles ne le sont pas déjà
        if img_np.max() > 1.1 and not (img_np.min() >=0 and img_np.max() <=1.01): # Vérifier si déjà normalisé avant de re-normaliser
             img_np = np.clip(img_np.astype(np.float32) / 255.0, 0.0, 1.0)
        else:
             img_np = np.clip(img_np.astype(np.float32), 0.0, 1.0)


        # Gestion des canaux et de la forme finale
        if is_depth_map: # Pour les cartes de profondeur, on veut (H,W) puis on ajoutera le canal
            if img_np.ndim == 3 and img_np.shape[2] > 1: # Si c'est HWC (ex: RGB), prendre la moyenne pour grayscale
                img_np = np.mean(img_np, axis=2)
            img_np = img_np[..., np.newaxis] # Assurer H, W, 1
        elif target_channels:
            current_channels = img_np.shape[2] if img_np.ndim == 3 else 1 if img_np.ndim == 2 else 0

            if img_np.ndim == 2: # H,W -> H,W,C
                if target_channels == 1:
                    img_np = img_np[..., np.newaxis]
                elif target_channels == 3:
                    img_np = np.stack([img_np]*target_channels, axis=-1)
            elif img_np.ndim == 3: # H,W,Cin -> H,W,Cout
                if current_channels == 1 and target_channels == 3:
                    img_np = np.repeat(img_np, 3, axis=2)
                elif current_channels == 3 and target_channels == 1:
                    img_np = np.mean(img_np, axis=2, keepdims=True)
                elif current_channels == 4 and target_channels == 3: # RGBA -> RGB
                    img_np = img_np[..., :3]
                elif current_channels != target_channels:
                    # Tentative de gestion simple si pas match parfait
                    print(f"Warning: Channel mismatch for pattern. Input {current_channels}, target {target_channels}. Attempting basic conversion.")
                    if target_channels == 3:
                        img_np = np.mean(img_np, axis=2, keepdims=True) # D'abord grayscale
                        img_np = np.repeat(img_np, 3, axis=2)          # Puis RGB
                    elif target_channels == 1:
                         img_np = np.mean(img_np, axis=2, keepdims=True) # Grayscale

        return img_np


    def create_advanced_autostereogram(self, depth_map, pattern, eye_separation_pixels, depth_scale_factor):
        depth_map_np = self.preprocess_image_to_numpy(depth_map, is_depth_map=True) # H, W, 1, float [0,1]
        pattern_np = self.preprocess_image_to_numpy(pattern, target_channels=3)     # PatH, PatW, 3, float [0,1]

        h, w, _ = depth_map_np.shape
        pat_h, pat_w, pat_c = pattern_np.shape

        if pat_w == 0:
            raise ValueError("Pattern width cannot be zero.")
        if eye_separation_pixels <=0:
            raise ValueError("Eye separation in pixels must be positive.")


        stereogram = np.zeros((h, w, pat_c), dtype=np.float32)
        links = np.full(w, -1, dtype=int) # Stores the source pattern column index for each stereogram column

        # Période du motif à utiliser pour les liens. Devrait être eye_separation_pixels.
        # Mais le motif fourni (pattern_np) a sa propre largeur pat_w.
        # On va utiliser eye_separation_pixels comme la "largeur virtuelle" du motif de base pour les calculs de liens,
        # et ensuite on mapperax % eye_separation_pixels à une colonne dans le motif réel (pat_w).
        effective_pattern_period = eye_separation_pixels

        for y in range(h):
            links.fill(-1)
            pattern_row_tile = pattern_np[y % pat_h, :, :] # (pat_w, C)

            for x in range(w):
                # Depth_value: 0.0 (loin, sur le plan de l'écran), 1.0 (proche, sort le plus)
                depth_value = depth_map_np[y, x, 0] 
                
                # Separation: combien de pixels le point correspondant à l'oeil droit est décalé par rapport à l'oeil gauche
                # Si depth_value = 0, separation = 0 (points sur l'écran)
                # Si depth_value = 1, separation = max_separation (points les plus proches)
                # max_separation est une fraction (depth_scale_factor) de eye_separation_pixels.
                # Par exemple, si eye_separation_pixels = 100 et depth_scale_factor = 0.5, max_separation = 50.
                # Cela signifie que pour les objets les plus proches, l'oeil gauche voit le pixel x,
                # et l'oeil droit voit le pixel x + 50. Les deux doivent avoir la même couleur.
                
                separation = int(round(depth_value * depth_scale_factor * effective_pattern_period))

                # Le pixel x de l'autostéréogramme est vu par l'un des yeux (disons l'oeil gauche).
                # Le pixel "frère" correspondant (qui devrait avoir la même couleur de motif) est à:
                # x_linked = x - effective_pattern_period + separation
                # (Formule classique: S(i) = S(i - P + s(D(i))), où P=period, s(D)=separation)
                
                x_linked = x - effective_pattern_period + separation
                
                if 0 <= x_linked < w and links[x_linked] != -1:
                    # Si x_linked est valide et a déjà une source de motif assignée (via links[x_linked]),
                    # alors x doit utiliser la même source de motif.
                    source_col_in_virtual_pattern = links[x_linked]
                    # On mappe cette colonne du "motif virtuel" (de période effective_pattern_period)
                    # à une colonne du motif réel (de largeur pat_w).
                    actual_col_in_real_pattern = source_col_in_virtual_pattern % pat_w
                    
                    stereogram[y, x, :] = pattern_row_tile[actual_col_in_real_pattern, :]
                    links[x] = source_col_in_virtual_pattern # On propage le lien au motif virtuel
                else:
                    # Pas de lien à gauche, ou le pixel lié n'a pas encore de source de motif.
                    # x devient un point d'ancrage. Sa source de motif est déterminée par sa position
                    # dans le "motif virtuel" de période effective_pattern_period.
                    source_col_in_virtual_pattern = x % effective_pattern_period
                    actual_col_in_real_pattern = source_col_in_virtual_pattern % pat_w
                    
                    stereogram[y, x, :] = pattern_row_tile[actual_col_in_real_pattern, :]
                    links[x] = source_col_in_virtual_pattern
            
        output_tensor = torch.from_numpy(stereogram.astype(np.float32)).unsqueeze(0)
        return (output_tensor,)

# --- Mappings pour ComfyUI ---
# Assurez-vous que le nom de la classe ici correspond à celui défini ci-dessus.
NODE_CLASS_MAPPINGS = {
    "AdvancedAutostereogramNode": AdvancedAutostereogramNode
    # Si vous voulez que l'ancien workflow fonctionne sans changer le nom du noeud dans le JSON:
    # "AutostereogramNode": AdvancedAutostereogramNode 
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AdvancedAutostereogramNode": "Autostereogram Creator (Advanced)"
    # Ou pour correspondre à la clé ci-dessus si vous l'avez changée :
    # "AutostereogramNode": "Autostereogram Creator (Adv.)"
}