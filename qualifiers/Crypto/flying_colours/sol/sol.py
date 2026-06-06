import numpy as np
from PIL import Image
from sympy import *

def get_params():
    F = GF(257)
    out_img = Image.open('output.png').convert('RGBA')
    out_pixels = np.array(out_img)
    in_img = Image.open('input.png').convert('RGBA')
    in_pixels = np.array(in_img)
    
    with open('x.txt', 'r') as f:
        x_vals = [int(line.strip()) for line in f if line.strip()]
        x_matrix = np.array(x_vals).reshape((in_img.height, in_img.width))

    indices = []
    for r in range(in_pixels.shape[0]):
        for c in range(in_pixels.shape[1]):
            if not np.array_equal(in_pixels[r, c], [0, 0, 0, 255]):
                indices.append((r, c))

    rows = []
    y_r, y_g, y_b = [], [], []

    for r, c in indices:
        p = in_pixels[r, c]
        y_obs = out_pixels[r, c]
        x = x_matrix[r, c]
        
        diff = int(p[3]) - int(y_obs[3])
        
        rows.append([p[0], p[1], p[2], x])
        y_r.append(256 if (diff & 1) else y_obs[0])
        y_g.append(256 if (diff & 2) else y_obs[1])
        y_b.append(256 if (diff & 4) else y_obs[2])

    A = matrix(F, rows)
    sr = A.solve_right(vector(F, y_r))
    sg = A.solve_right(vector(F, y_g))
    sb = A.solve_right(vector(F, y_b))

    key = Matrix([
        [int(sr[0]), int(sr[1]), int(sr[2]), 0],
        [int(sg[0]), int(sg[1]), int(sg[2]), 0],
        [int(sb[0]), int(sb[1]), int(sb[2]), 0],
        [0, 0, 0, 1]
    ])
    noise = [int(sr[3]), int(sg[3]), int(sb[3]), 0]
    return key, noise

def decrypt(key, noise):
    img = Image.open('output.png').convert('RGBA')
    pixels = np.array(img, dtype=np.int32)
    h, w, _ = pixels.shape
    
    with open('x.txt', 'r') as f:
        x_vals = np.array([int(line.strip()) for line in f if line.strip()], dtype=np.int32).reshape((h, w))

    key_inv_t = np.array(Matrix(key).T.inv_mod(257)).astype(np.int32)
    noise = np.array(noise, dtype=np.int32)
    
    recovered = np.zeros_like(pixels, dtype=np.uint8)

    for r in range(h):
        for c in range(w):
            y_obs = pixels[r, c]
            x = x_vals[r, c]
            
            for mask in range(8):
                y_guess = y_obs.copy()
                if mask & 1: y_guess[0] = 256
                if mask & 2: y_guess[1] = 256
                if mask & 4: y_guess[2] = 256
                
                p_guess = (np.dot(y_guess - x * noise, key_inv_t)) % 257
                
                if np.all(p_guess <= 255):
                    if (p_guess[3] - y_obs[3]) == mask:
                        recovered[r, c] = p_guess.astype(np.uint8)
                        break
                        
    Image.fromarray(recovered).save('recovered.png')

key, noise = get_params()
decrypt(key, noise)
