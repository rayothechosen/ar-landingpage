import cv2
import numpy as np

phone_path = r"C:\Users\Pichau\.gemini\antigravity\brain\e1d1136b-a305-4369-9e32-9f9d2f97ddfa\media__1779282303525.png"
screen_path = r"C:\Users\Pichau\.gemini\antigravity\brain\e1d1136b-a305-4369-9e32-9f9d2f97ddfa\media__1779282245293.png"

phone_img = cv2.imread(phone_path)
screen_img = cv2.imread(screen_path)

# Points we found
pts = np.array([
    [270, 21],
    [524, 57],
    [492, 709],
    [242, 690]
], dtype="float32")

# To prevent subpixel gaps showing the checkerboard, we can slightly expand the polygon
center = np.mean(pts, axis=0)
pts = pts + (pts - center) * 0.01  # Expand by 1%

# Sort points to Top-Left, Top-Right, Bottom-Right, Bottom-Left
rect = np.zeros((4, 2), dtype="float32")
s = pts.sum(axis=1)
rect[0] = pts[np.argmin(s)]
rect[2] = pts[np.argmax(s)]
diff = np.diff(pts, axis=1)
rect[1] = pts[np.argmin(diff)]
rect[3] = pts[np.argmax(diff)]

sh, sw = screen_img.shape[:2]
src_pts = np.array([
    [0, 0],
    [sw - 1, 0],
    [sw - 1, sh - 1],
    [0, sh - 1]
], dtype="float32")

M = cv2.getPerspectiveTransform(src_pts, rect)

# Warp screen
h, w = phone_img.shape[:2]
warped = cv2.warpPerspective(screen_img, M, (w, h), flags=cv2.INTER_LINEAR)

mask = np.zeros((h, w), dtype=np.uint8)
cv2.fillConvexPoly(mask, rect.astype(int), 255)

# Smooth the mask to anti-alias the edges
mask = cv2.GaussianBlur(mask, (3, 3), 0)
mask_float = mask.astype(float) / 255.0
mask_float = np.stack([mask_float]*3, axis=2)

result = phone_img.copy()
# Paste warped image over phone using mask
result = warped * mask_float + phone_img * (1 - mask_float)

out_path = r"c:\Users\Pichau\Desktop\projetos antigravity\projeto_renda_extra\montagem_resultado.jpg"
cv2.imwrite(out_path, result.astype(np.uint8))
print("Saved to montagem_resultado.jpg")
