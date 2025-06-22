NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# AdvancedAutostereogramNode
try:
    from .autostereogram_node import NODE_CLASS_MAPPINGS as ADV_AS_CLASS_MAPPINGS
    NODE_CLASS_MAPPINGS.update(ADV_AS_CLASS_MAPPINGS)
    from .autostereogram_node import NODE_DISPLAY_NAME_MAPPINGS as ADV_AS_DISPLAY_MAPPINGS
    NODE_DISPLAY_NAME_MAPPINGS.update(ADV_AS_DISPLAY_MAPPINGS)
except (ImportError, AttributeError) as e:
    print(f"[illusion_node] Avertissement (AdvancedAutostereogramNode): {e}")

# PatternGeneratorNode
try:
    from .PatternGenerator_node import NODE_CLASS_MAPPINGS as PG_CLASS_MAPPINGS
    NODE_CLASS_MAPPINGS.update(PG_CLASS_MAPPINGS)
    from .PatternGenerator_node import NODE_DISPLAY_NAME_MAPPINGS as PG_DISPLAY_MAPPINGS
    NODE_DISPLAY_NAME_MAPPINGS.update(PG_DISPLAY_MAPPINGS)
except (ImportError, AttributeError) as e:
    print(f"[illusion_node] Avertissement (PatternGeneratorNode): {e}")

# TileImageRepeaterNode
try:
    from .TileImageRepeaterNode import NODE_CLASS_MAPPINGS as TIR_CLASS_MAPPINGS
    NODE_CLASS_MAPPINGS.update(TIR_CLASS_MAPPINGS)
    from .TileImageRepeaterNode import NODE_DISPLAY_NAME_MAPPINGS as TIR_DISPLAY_MAPPINGS
    NODE_DISPLAY_NAME_MAPPINGS.update(TIR_DISPLAY_MAPPINGS)
except (ImportError, AttributeError) as e:
    print(f"[illusion_node] Avertissement (TileImageRepeaterNode): {e}")

# OpticalIllusionNode
try:
    from .OpticalIllusionNode import OpticalIllusionNode
    NODE_CLASS_MAPPINGS["OpticalIllusionNode"] = OpticalIllusionNode
    NODE_DISPLAY_NAME_MAPPINGS["OpticalIllusionNode"] = "Optical Illusion Generator"
except (ImportError, AttributeError) as e:
    print(f"[illusion_node] Avertissement (OpticalIllusionNode): {e}")

# OpticalGeometricNodee
try:
    from .OpticalGeometricNode import OpticalGeometricNode
    NODE_CLASS_MAPPINGS["OpticalGeometricNode"] = OpticalGeometricNode
    NODE_DISPLAY_NAME_MAPPINGS["OpticalGeometricNode"] = "Optical Geometric Generator"
except Exception as e:
    print(f"[illusion_node] OpticalGeometricNode import error: {e}")

# CheckerboardNode
try:
    from .CheckerboardNode import CheckerboardNode
    NODE_CLASS_MAPPINGS["CheckerboardNode"] = CheckerboardNode
    NODE_DISPLAY_NAME_MAPPINGS["CheckerboardNode"] = "Checkerboard Composer"
except Exception as e:
    print(f"[illusion_node] CheckerboardNode import error: {e}")

# ColorImageNode
try:
    from .ColorImageNode import ColorImageNode
    NODE_CLASS_MAPPINGS["ColorImageNode"] = ColorImageNode
    NODE_DISPLAY_NAME_MAPPINGS["ColorImageNode"] = "Color/Gradient Image"
except Exception as e:
    print(f"[illusion_node] ColorImageNode import error: {e}")

# TessellationNode
try:
    from .TessellationNode import NODE_CLASS_MAPPINGS as TESS_CLASS_MAPPINGS
    NODE_CLASS_MAPPINGS.update(TESS_CLASS_MAPPINGS)
    from .TessellationNode import NODE_DISPLAY_NAME_MAPPINGS as TESS_DISPLAY_MAPPINGS
    NODE_DISPLAY_NAME_MAPPINGS.update(TESS_DISPLAY_MAPPINGS)
except Exception as e:
    print(f"[illusion_node] TessellationNode import error: {e}")

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

print("--- Chargement du pack de nœuds 'illusion_node' ---")
print(f"  {len(NODE_CLASS_MAPPINGS)} classe(s) de nœud(s) trouvée(s) : {list(NODE_CLASS_MAPPINGS.keys())}")
print("--- Fin du chargement de 'illusion_node' ---")
