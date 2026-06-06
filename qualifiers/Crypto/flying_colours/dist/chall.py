import numpy as np
from PIL import Image
from random import randint

def image_encryption(input_path, output_path, key, noise):
    img = Image.open(input_path).convert('RGBA')
    pixels = np.array(img, dtype=np.int32)
    h, w, _ = pixels.shape
    x = np.random.randint(0, 256, (h, w))
    with open('x.txt', 'w') as f:
        f.write('\n'.join(map(str, x.flatten())) + '\n')
    pixels = (np.dot(pixels, key.T) + x[..., None] * noise) % 257
    for i in range(3):
        mask = (pixels[..., i] == 256)
        pixels[mask, 3] -= (1 << i)
        pixels[mask, i] = 255
            
    Image.fromarray(pixels.astype(np.uint8)).save(output_path)

key = np.eye(4, dtype=int)
while True:
    key[:3, :3] = np.random.randint(0, 256, (3, 3))
    det = round(np.linalg.det(key))
    if det % 2 != 0:
        break

noise = np.array([randint(0, 255), randint(0, 255), randint(0, 255), 0])
image_encryption("input.png", "encrypted.png", key, noise)
