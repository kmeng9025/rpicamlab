# import cv2
# import os
# import numpy as np

# # === Configuration ===
# video_path = "FVB_non acc_LH2.mp4"            # <-- change this to your video filename
# output_dir = "cropped_frames/video3"
# num_frames_to_extract = 1000

# # Crop coordinates
# # [60:720, 285:690]
# x, y = 200, 0
# w, h = 600, 768

# # === Create output folder ===
# os.makedirs(output_dir, exist_ok=True)

# # === Open video ===
# cap = cv2.VideoCapture(video_path)
# total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# if not cap.isOpened():
#     print("❌ Failed to open video.")
#     exit()

# # === Determine which frames to extract ===
# frame_indices = np.linspace(0, total_frames - 1, num_frames_to_extract, dtype=int)

# print(f"Total frames: {total_frames}")
# print(f"Extracting {len(frame_indices)} cropped frames...")

# count = 0
# for idx in frame_indices:
#     cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
#     ret, frame = cap.read()
#     if not ret:
#         print(f"⚠️ Could not read frame {idx}")
#         continue

#     # Crop frame
#     cropped = frame[y:y+h, x:x+w]

#     # Save frame
#     output_path = os.path.join(output_dir, f"frame_{idx:05d}.png")
#     cv2.imwrite(output_path, cropped)
#     count += 1

# print(f"✅ Done. Saved {count} cropped frames to '{output_dir}'.")

# cap.release()
import cv2
import os
import numpy as np

# === Configuration ===
video_path = "G33B_6-10 24hrA 31hr 48min fast LH cage2v2 3fans 2021-03-03_16.20.41.mp4"            # <-- change this to your video filename
output_dir = "cropped_frames/video1"
num_frames_to_extract = 1000

# Crop coordinates
# [60:720, 285:690]
x, y = 200, 0
w, h = 600, 768

# === Create output folder ===
os.makedirs(output_dir, exist_ok=True)

# === Open video ===
cap = cv2.VideoCapture(video_path)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

if not cap.isOpened():
    print("❌ Failed to open video.")
    exit()

# === Determine which frames to extract ===
frame_indices = np.linspace(0, total_frames - 1, num_frames_to_extract, dtype=int)

print(f"Total frames: {total_frames}")
print(f"Extracting {len(frame_indices)} cropped frames...")

count = 0
for idx in frame_indices:
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ret, frame = cap.read()
    if not ret:
        print(f"⚠️ Could not read frame {idx}")
        continue

    # Crop frame
    cropped = frame[y:y+h, x:x+w]

    timestamp_roi = cropped  # y1:y2, x1:x2

    # Convert to grayscale
    gray = cv2.cvtColor(timestamp_roi, cv2.COLOR_BGR2GRAY)

    # Threshold to detect bright text (tweak threshold if needed)
    _, thresh = cv2.threshold(gray[20:50, 165:455], 10, 10, cv2.THRESH_BINARY)

    # Optionally: dilate to make text blobs more connected
    # kernel = np.ones((2, 2), np.uint8)
    # dilated = cv2.dilate(thresh, kernel, iterations=1)

    # Create a full-size mask and paste the text mask into position
    mask = np.zeros(gray.shape, dtype=np.uint8)
    mask[20:50, 165:455] = thresh
    # mask = dilated.copy()

    # Inpaint only where text was detected
    inpainted = cv2.inpaint(cropped, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

    # Save frame
    output_path = os.path.join(output_dir, f"frame_{idx:05d}.png")
    cv2.imwrite(output_path, inpainted)
    count += 1

print(f"✅ Done. Saved {count} cropped frames to '{output_dir}'.")

cap.release()
