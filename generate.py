from PIL import Image, UnidentifiedImageError
import numpy as np
from opensimplex import OpenSimplex
import sys, getopt
from pathlib import Path

def generate_simplex_noise(width: int, height: int, scale: float = 0.03, seed: int = 0) -> np.ndarray:
    """
    Generates a 2D simplex noise field with values from 0 to 1
    """
    simplex = OpenSimplex(seed=seed)
    noise = np.zeros((height, width), dtype=np.float32)

    for y in range(height):
        for x in range(width):
            v = simplex.noise2(x * scale, y * scale)
            noise[y, x] = v
    
    # normalize
    noise_min = noise.min()
    noise_max = noise.max()
    if noise_max > noise_min:
        noise = (noise - noise_min) / (noise_max - noise_min)
    else:
        noise.fill(0.0)
    
    return noise

def map_noise_to_shades(noise: np.ndarray, shades: list[tuple[int, int, int]]) -> np.ndarray:
    """
    Map noise to a list of RGB colors
    """
    shades_arr = np.array(shades, dtype=np.uint8)

    indices = np.clip((noise * len(shades)).astype(np.int32), 0, len(shades) - 1)

    rgb = shades_arr[indices]
    return rgb

def replace_image_mask_with_noise(
    image: Image,
    mask_color: tuple[int, int, int],
    shades: list[tuple[int, int, int]],
    tolerance: int = 0,
    scale: float = 0.03,
    seed: int = 0,
) -> Image:
    image = np.array(image.convert("RGBA"))
    h, w = image.shape[:2]

    mask_color_arr = np.array(mask_color, dtype=np.int16)
    rgb = image[:, :, :3].astype(np.int16)

    if tolerance == 0:
        mask = np.all(rgb == mask_color_arr, axis=-1)
    else:
        mask = np.all(np.abs(rgb - mask_color_arr) <= tolerance, axis=-1)

    noise = generate_simplex_noise(w, h, scale=scale, seed=seed)
    noise_rgb = map_noise_to_shades(noise, shades)

    image[mask, :3] = noise_rgb[mask]

    return Image.fromarray(image, "RGBA")

def parse_color(s: str) -> tuple[int, int, int]:
    s = s.strip()

    # hex
    if s.startswith("#"):
        s = s[1:]
    if len(s) == 6:
        try:
            r = int(s[0:2], 16)
            g = int(s[2:4], 16)
            b = int(s[4:6], 16)
            return (r, g, b)
        except ValueError:
            pass
    
    raise ValueError

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python generate.py -i <input_path> -o <output_path> --mask-color "#ff0000" --shades "#1e1e28,#465a8c,#78aac8"')
        sys.exit(1)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:", ["input=", "output=", "mask-color=", "shades=", "scale=", "seed=", "tolerance="])
    except getopt.GetoptError as e:
        print(f"Error: {e}")
        sys.exit(1)

    input_path = None
    output_path = None
    mask_color = None
    shades = None
    tolerance = 5
    scale = 0.50
    seed = int(np.random.default_rng().integers(0, 2**32))
    
    # parse args
    for opt, arg in opts:
        try:
            if opt in {"-i", "--input"}:
                input_path = Path(arg)
                if not input_path.is_file():
                    print(f"Err: File not found: '{arg}'")
                    sys.exit(1)
            elif opt in {"-o", "--output"}:
                output_path = Path(arg)
            elif opt == "--mask-color":
                mask_color = parse_color(arg)
            elif opt == "--shades":
                shades = [parse_color(c) for c in arg.split(",")]
                if len(shades) == 0:
                    print("Err: At least 1 color for --shades must be provided")
                    sys.exit(1)
            elif opt == "--scale":
                try:
                    scale = float(arg)
                except ValueError:
                    print("Err: --scale must be a float")
                    sys.exit(1)
            elif opt == "--seed":
                try:
                    seed = int(arg)
                except ValueError:
                    print("Err: --seed must be an integer")
                    sys.exit(1)
            elif opt == "--tolerance":
                try:
                    tolerance = int(arg)
                except ValueError:
                    print("Err: --tolerance must be an integer")
                    sys.exit(1)
        except ValueError:
            print(f"Invalid color: '{arg}'")
            print("Valid formats: #ff00ff | ff00ff")
            sys.exit(1)
    
    # validate args
    if input_path is None:
        print("Err: -i required")
        sys.exit(1)
    if output_path is None:
        # default to output.png in the same dir
        output_path = Path.joinpath(input_path.parent / "output.png")
    if mask_color is None:
        print("Err: --mask-color required")
        sys.exit(1)
    if shades is None:
        print("Err: --shades required")
        sys.exit(1)

    try:
        image = Image.open(input_path)
    except UnidentifiedImageError:
        print(f"Err: Invalid image: '{input_path}'")
        sys.exit(1)

    output_image = replace_image_mask_with_noise(
        image=image,
        mask_color=mask_color,
        shades=shades,
        tolerance=tolerance,
        scale=scale,
        seed=seed,
    )

    output_image.save(output_path)
    
    print(output_path.absolute())
    sys.exit(0)