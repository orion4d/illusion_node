# ComfyUI Illusion & Pattern Nodes

This repository contains a collection of custom nodes for ComfyUI, designed for generating various patterns, optical illusions, and performing related image manipulations. All nodes are categorized under "illusion" in the ComfyUI menu.

## Installation

1.  Navigate to your ComfyUI `custom_nodes` directory:
    ```bash
    cd ComfyUI/custom_nodes/
    ```
2.  Clone this repository:
    ```bash
    git clone https://github.com/orion4d/illusion_node.git
    ```
3.  Restart ComfyUI.

The nodes should now be available in the "illusion" category when you right-click or use the "Add Node" menu.

## Nodes Overview

Below is a summary of each node provided in this pack:

---

### 1. Pattern Generator (`PatternGenerator_node.py`)

*   **Display Name:** `Pattern Generator`
*   **Function:** Generates various 2D procedural patterns.
*   **Key Features:**
    *   **Pattern Types:**
        *   `Stripes`: Creates vertical or horizontal stripes using two colors.
            *   `parameter1`: Stripe width.
        *   `Checkerboard`: Creates a checkerboard pattern.
            *   `parameter1`: Square size.
        *   `Random Dots`: Scatters dots of `color2` over a `color1` background.
            *   `parameter1`: Density percentage (1-100).
            *   `parameter2`: Maximum dot radius.
        *   `Solid Color`: Fills the image with `color1`.
        *   `Gradient`: Creates a linear gradient between `color1` and `color2`.
            *   `parameter1`: Direction (0: L-R, 1: T-B, 2: R-L, 3: B-T).
        *   `Noise`: Generates blocky random noise.
            *   `parameter1`: 0 for Color Noise, 1 for Grayscale Noise.
            *   `parameter2`: Block scale (1 for pixel-level noise).
    *   Customizable `width`, `height`, `color1_hex`, `color2_hex`, and `seed`.

---

### 2. Tessellation Composer (Advanced) (`TessellationNode.py`)

*   **Display Name:** `Tessellation Composer (Advanced)`
*   **Function:** Creates complex tiled patterns from an input image, with various transformations per tile.
*   **Key Features:**
    *   Uses an `input_image` as the base tile.
    *   `tile_width`, `tile_height`: Dimensions of the base tile (input image will be resized).
    *   `tiles_x`, `tiles_y`: Number of tiles in horizontal and vertical directions.
    *   `mode`: Tiling strategy (`repeat`, `mirror`, `diamond`).
    *   `mirror_axis`: Optional mirroring of tiles (`none`, `x`, `y`, `xy`, `random`).
    *   `offset_x`, `offset_y`: Offsets applied to alternating rows/columns.
    *   `rotation_mode`: How rotation is applied (`none`, `by_tile`, `random`).
    *   `rotation_angle`: Base rotation angle.
    *   `scale_mode`: How scaling is applied (`none`, `by_tile`, `random`).
    *   `scale_factor`: Base scale factor.
    *   `opacity`: Opacity of the composited tiles.
    *   `random_seed`: For random operations.

---

### 3. Optical Illusion Generator (`OpticalIllusionNode.py`)

*   **Display Name:** `OpticalIllusionNode` (or similar, based on class name if not explicitly mapped)
*   **Function:** Generates classic optical illusion patterns.
*   **Key Features:**
    *   `illusion_type`:
        *   `checkerboard`: Standard checkerboard.
        *   `circles`: Concentric circles.
        *   `lines`: Parallel lines.
        *   `spiral`: Archimedean spiral.
    *   Customizable `size`, `frequency` (density/count of elements), `line_width`, `color1` (background), and `color2` (foreground/lines).

---

### 4. Optical Geometric Pattern Generator (`OpticalGeometricNode.py`)

*   **Display Name:** `OpticalGeometricNode` (or similar, based on class name if not explicitly mapped)
*   **Function:** Generates various geometric optical art patterns.
*   **Key Features:**
    *   `pattern_type`:
        *   `concentric_squares`
        *   `concentric_triangles`
        *   `wavy_grid`: Grid lines distorted by sine waves.
        *   `starburst`: Lines radiating from the center.
        *   `hexagons`: Honeycomb pattern.
        *   `waves`: Superimposed sinusoidal waves.
    *   Customizable `size`, `frequency`, `line_width`, `color1`, and `color2`.

---

### 5. Color/Gradient Image (`ColorImageNode.py`)

*   **Display Name:** `Color/Gradient Image`
*   **Function:** Creates images with solid colors or various types of gradients.
*   **Key Features:**
    *   `mode`:
        *   `solid`: Fills with `color1`.
        *   `linear`: Linear gradient between `color1` and `color2`, controlled by `angle`.
        *   `radial`: Radial gradient from center (`color1`) to edges (`color2`).
        *   `angular`: Angular (sweep/cone) gradient, rotation controlled by `angle`.
        *   `mirror`: Reflected linear gradient.
        *   `diamond`: Diamond-shaped gradient.
    *   Customizable `width`, `height`, `color1`, `color2`, and `angle`.

---

### 6. Autostereogram Creator (Advanced) (`autostereogram_node.py`)

*   **Display Name:** `Autostereogram Creator (Advanced)`
*   **Function:** Generates Single Image Random Dot Stereograms (SIRDS), also known as "Magic Eye" images.
*   **Key Features:**
    *   Takes a `depth_map` (grayscale image where brightness indicates depth) and a `pattern` image.
    *   `eye_separation_pixels`: Simulates the distance between eyes projected onto the image plane, influencing the pattern period.
    *   `depth_scale_factor`: Controls the intensity of the 3D effect (how much objects "pop out" or recede).

---

### 7. Checkerboard Composer (`CheckerboardNode.py`)

*   **Display Name:** `Checkerboard Composer`
*   **Function:** Creates a checkerboard pattern using two input images as alternating tiles.
*   **Key Features:**
    *   Takes `img1` and `img2` as inputs for the two alternating tiles.
    *   `tiles_x`, `tiles_y`: Number of tiles in the checkerboard.
    *   `tile_width`, `tile_height`: Desired dimensions for each tile.
    *   `tile_mode`:
        *   `resize`: Input images are resized to `tile_width` x `tile_height`.
        *   `crop`: Input images are cropped from the top-left to `tile_width` x `tile_height`.

---

### 8. Tile Image Repeater (Smart Resize) (`TileImageRepeaterNode.py`)

*   **Display Name:** `Tile Image Repeater (Smart Resize)`
*   **Function:** Repeats an input image to create a larger tiled image, with intelligent resizing options for the base tile.
*   **Key Features:**
    *   Takes an `image` as the base tile.
    *   `horizontal_repeats`, `vertical_repeats`: Number of times to repeat the tile.
    *   `resize_mode`: How the base tile is resized before tiling:
        *   `None`: No resizing.
        *   `Width`: Tile is resized to `tile_target_size` width, height adjusted by aspect ratio.
        *   `Height`: Tile is resized to `tile_target_size` height, width adjusted by aspect ratio.
        *   `Shortest Side`: The shorter side of the tile is resized to `tile_target_size`.
        *   `Longest Side`: The longer side of the tile is resized to `tile_target_size`.
    *   `tile_target_size`: The target dimension for resizing (if `resize_mode` is not `None`).
    *   `resampling_filter`: Filter used for resizing (`lanczos`, `bicubic`, `bilinear`, `nearest`).

---

Enjoy creating illusions and patterns!
