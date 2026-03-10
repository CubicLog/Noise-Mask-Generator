# Noise-Mask-Generator
A Python tool used to replace a single color mask in an image with random noise using the desired color shades.


# Example Usage
```
python generate.py -i example.png -o out.png --shades "#1F5F4A, #4C9A73, #B7E4C7" --mask-color ff0000
```

# Arguments

- `--input | -i` `(str)` `REQUIRED`: The path to the input image containing a single-color mask.

- `--output  | -o` `(str)`: The path the output image will save to.

- `--mask-color` `(str)` `REQUIRED`: The hex color code corresponding to the mask that should be replaced.

- `--shades` `(str)` `REQUIRED`: A list of hex color codes delimited by commas corresponding to which colors to replace the mask with.

- `--scale` `(float)`: The scale of the 2D Simplex Noise layer. Higher values result in noisier texture.

- `--seed` `(int)`: The seed to use for the Simplex Noise function. Defaults to a random seed.

- `--tolerance` `(int)`: The tolerance level for the mask color. A higher value will match more similar-color pixels. 
