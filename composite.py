import cv2
import numpy as np

phone_path = r"C:\Users\Pichau\.gemini\antigravity\brain\e1d1136b-a305-4369-9e32-9f9d2f97ddfa\media__1779282303525.png"
screen_path = r"C:\Users\Pichau\.gemini\antigravity\brain\e1d1136b-a305-4369-9e32-9f9d2f97ddfa\media__1779282245293.png"

print("Loading images...")
phone_img = cv2.imread(phone_path, cv2.IMREAD_UNCHANGED)
screen_img = cv2.imread(screen_path, cv2.IMREAD_UNCHANGED)

if phone_img is None or screen_img is None:
    raise Exception("Failed to load images.")

print("Phone shape:", phone_img.shape)
print("Screen shape:", screen_img.shape)

if phone_img.shape[2] != 4:
    raise Exception("Phone image lacks an alpha channel!")

# Threshold alpha channel to find transparent regions
alpha = phone_img[:, :, 3]
_, thresh = cv2.threshold(alpha, 50, 255, cv2.THRESH_BINARY_INV)

# Find contours
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

h_img, w_img = alpha.shape
valid_contours = []
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    # Avoid the contour that represents the transparent background outside the phone
    if x > 2 and y > 2 and (x+w) < w_img-2 and (y+h) < h_img-2:
        valid_contours.append(cnt)

if not valid_contours:
    raise Exception("No screen contour found inside the phone!")

largest_contour = max(valid_contours, key=cv2.contourArea)

# Find 4 corners
hull = cv2.convexHull(largest_contour)
epsilon = 0.05 * cv2.arcLength(hull, True)
approx = cv2.approxPolyDP(hull, epsilon, True)

if len(approx) != 4:
    # Try different epsilon
    for eps_factor in np.linspace(0.01, 0.1, 20):
        epsilon = eps_factor * cv2.arcLength(hull, True)
        approx = cv2.approxPolyDP(hull, epsilon, True)
        if len(approx) == 4:
            break
    
    if len(approx) != 4:
        raise Exception(f"Failed to find exactly 4 corners for the screen. Found {len(approx)}.")

pts = approx.reshape(4, 2)
rect = np.zeros((4, 2), dtype="float32")
s = pts.sum(axis=1)
rect[0] = pts[np.argmin(s)] # Top-Left
rect[2] = pts[np.argmax(s)] # Bottom-Right
diff = np.diff(pts, axis=1)
rect[1] = pts[np.argmin(diff)] # Top-Right
rect[3] = pts[np.argmax(diff)] # Bottom-Left

# To avoid gaps, expand the rect slightly
center = np.mean(rect, axis=0)
rect = rect + (rect - center) * 0.02

if screen_img.shape[2] == 3:
    screen_img = cv2.cvtColor(screen_img, cv2.COLOR_BGR2BGRA)

sh, sw = screen_img.shape[:2]
src_pts = np.array([
    [0, 0],
    [sw - 1, 0],
    [sw - 1, sh - 1],
    [0, sh - 1]
], dtype="float32")

# Warp screen
M = cv2.getPerspectiveTransform(src_pts, rect)
warped = cv2.warpPerspective(screen_img, M, (w_img, h_img))

# Composite phone OVER the warped screen
result = warped.copy()
alpha_phone = phone_img[:, :, 3] / 255.0

for c in range(0, 3):
    result[:, :, c] = (alpha_phone * phone_img[:, :, c] + (1 - alpha_phone) * warped[:, :, c])

alpha_warped = warped[:, :, 3] / 255.0
result_alpha = np.maximum(alpha_phone, alpha_warped) * 255.0
result[:, :, 3] = result_alpha.astype(np.uint8)

out_path = r"c:\Users\Pichau\Desktop\projetos antigravity\projeto_renda_extra\montagem_app.png"
cv2.imwrite(out_path, result)
print("Montagem successfully saved to:", out_path)
