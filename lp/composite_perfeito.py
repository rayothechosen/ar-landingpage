import cv2
import numpy as np
import os

phone_path = r"C:\Users\Pichau\.gemini\antigravity\brain\e1d1136b-a305-4369-9e32-9f9d2f97ddfa\media__1779282303525.png"
screen_path = r"C:\Users\Pichau\.gemini\antigravity\brain\e1d1136b-a305-4369-9e32-9f9d2f97ddfa\media__1779282245293.png"

phone_img = cv2.imread(phone_path)
screen_img = cv2.imread(screen_path)

# 1. Create a mask of the dark phone frame
gray = cv2.cvtColor(phone_img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (15, 15), 0)
is_dark = blurred < 150

# Find the frame component
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(is_dark.astype(np.uint8)*255, connectivity=8)
max_area = 0
frame_label = -1
for i in range(1, num_labels):
    area = stats[i, cv2.CC_STAT_AREA]
    if area > max_area:
        max_area = area
        frame_label = i

# 2. Extract the screen hole from the frame
mask_frame = (labels == frame_label).astype(np.uint8) * 255

# Floodfill from (0,0) to get the outside background
im_floodfill = mask_frame.copy()
h, w = im_floodfill.shape
mask_ff = np.zeros((h+2, w+2), np.uint8)
cv2.floodFill(im_floodfill, mask_ff, (0,0), 255)

# Invert floodfilled image. This gives us EXACTLY the inner hole!
im_floodfill_inv = cv2.bitwise_not(im_floodfill)

# The inner hole mask (im_floodfill_inv) perfectly captures the screen, 
# including the dynamic island and rounded corners!

# 3. Find 4 corners of this mask for perspective warp
contours, _ = cv2.findContours(im_floodfill_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
c = max(contours, key=cv2.contourArea)
hull = cv2.convexHull(c)

approx = None
for eps_factor in np.linspace(0.01, 0.1, 50):
    epsilon = eps_factor * cv2.arcLength(hull, True)
    approx_test = cv2.approxPolyDP(hull, epsilon, True)
    if len(approx_test) == 4:
        approx = approx_test
        break

if approx is None:
    raise Exception("Could not find 4 corners")

pts = approx.reshape(4, 2).astype("float32")

# Sort points Top-Left, Top-Right, Bottom-Right, Bottom-Left
rect = np.zeros((4, 2), dtype="float32")
s = pts.sum(axis=1)
rect[0] = pts[np.argmin(s)]
rect[2] = pts[np.argmax(s)]
diff = np.diff(pts, axis=1)
rect[1] = pts[np.argmin(diff)]
rect[3] = pts[np.argmax(diff)]

# 4. Warp the screen image
sh, sw = screen_img.shape[:2]
src_pts = np.array([
    [0, 0],
    [sw - 1, 0],
    [sw - 1, sh - 1],
    [0, sh - 1]
], dtype="float32")

M = cv2.getPerspectiveTransform(src_pts, rect)
warped = cv2.warpPerspective(screen_img, M, (w, h), flags=cv2.INTER_LINEAR)

# 5. Composite using the EXACT mask of the hole
# We slightly erode the mask to avoid a 1px gray artifact at the edges,
# but actually, if the hole mask is perfect, we just use it directly.
# Let's smooth the mask to anti-alias the rounded corners and island.
mask_smoothed = cv2.GaussianBlur(im_floodfill_inv, (3, 3), 0)
mask_float = mask_smoothed.astype(float) / 255.0
mask_float = np.stack([mask_float]*3, axis=2)

result = phone_img.copy()
result = warped * mask_float + phone_img * (1 - mask_float)

out_path = r"C:\Users\Pichau\.gemini\antigravity\brain\e1d1136b-a305-4369-9e32-9f9d2f97ddfa\montagem_perfeita.jpg"
cv2.imwrite(out_path, result.astype(np.uint8))
print("Saved to", out_path)
