import os
import cv2
import numpy as np
import albumentations as A
import glob
from tqdm import tqdm
import shutil
import yaml

# -------------------------------------------------------------------
# Helper Functions to Convert Between YOLO Polygons and Pixel Masks
# -------------------------------------------------------------------

def yolo_to_masks(label_path, height, width):
    """Converts a YOLO segmentation label file to a list of binary masks."""
    masks = []
    class_ids = []
    if not os.path.exists(label_path):
        return masks, class_ids
        
    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            class_id = int(parts[0])
            polygon = np.array(parts[1:], dtype=np.float32).reshape(-1, 2)
            
            # Denormalize polygon coordinates
            polygon[:, 0] *= width
            polygon[:, 1] *= height
            
            # Create a binary mask for the current polygon
            mask = np.zeros((height, width), dtype=np.uint8)
            cv2.fillPoly(mask, [polygon.astype(np.int32)], 1)
            masks.append(mask)
            class_ids.append(class_id)
            
    return masks, class_ids

def masks_to_yolo(masks, class_ids, height, width):
    """Converts a list of binary masks back to YOLO segmentation format strings."""
    yolo_lines = []
    for i, mask in enumerate(masks):
        # Find contours from the binary mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) > 0:
            # Use the largest contour
            contour = max(contours, key=cv2.contourArea)
            
            if contour.shape[0] > 2:
                # Normalize coordinates
                contour = contour.astype(np.float32)
                contour[:, 0, 0] /= width
                contour[:, 0, 1] /= height
                
                # Flatten to x1 y1 x2 y2 ... format and create the YOLO string
                polygon_str = ' '.join(map(str, contour.flatten()))
                yolo_lines.append(f"{class_ids[i]} {polygon_str}")
                
    return yolo_lines

# -------------------------------------------------------------------
# Main Augmentation Function
# -------------------------------------------------------------------

def augment_dataset(base_dir, num_augs_per_image):
    """
    Applies augmentations to a YOLOv8 dataset and saves the results
    to a new directory with a new data.yaml file.
    """
    # Define the "crazy" augmentation pipeline
    transform = A.Compose([
        A.Rotate(limit=45, p=0.9, border_mode=cv2.BORDER_CONSTANT),
        A.ColorJitter(brightness=0, contrast=0, saturation=0.09, hue=0.5, p=0.9),
        A.RandomBrightnessContrast(brightness_limit=(-0.08, 0.41), contrast_limit=0, p=0.9),
        A.HorizontalFlip(p=0.5),
    ])

    # Create a new directory for the augmented dataset
    output_dir = f"{base_dir}_augmented"
    if os.path.exists(output_dir):
        print(f"Error: Output directory '{output_dir}' already exists. Please remove it or choose a different name.")
        return
    print(f"Creating new augmented dataset at: {output_dir}\n")

    # Loop through 'train' and 'valid' splits
    for split in ['train', 'valid']:
        print(f"--- Processing '{split}' split ---")
        img_dir = os.path.join(base_dir, split, 'images')
        label_dir = os.path.join(base_dir, split, 'labels')

        # Create corresponding output directories
        out_img_dir = os.path.join(output_dir, split, 'images')
        out_label_dir = os.path.join(output_dir, split, 'labels')
        os.makedirs(out_img_dir, exist_ok=True)
        os.makedirs(out_label_dir, exist_ok=True)
        
        image_files = glob.glob(os.path.join(img_dir, '*.jpg')) + \
                      glob.glob(os.path.join(img_dir, '*.png'))

        if not image_files:
            print(f"Warning: No images found in {img_dir}")
            continue

        # Process each image in the split
        for img_path in tqdm(image_files, desc=f"Augmenting {split} images"):
            filename = os.path.basename(img_path)
            basename, ext = os.path.splitext(filename)
            print("extension:", ext)
            label_path = os.path.join(label_dir, f"{basename}.txt")

            # 1. Copy original files to the new directory
            shutil.copy(img_path, os.path.join(out_img_dir, filename))
            if os.path.exists(label_path):
                shutil.copy(label_path, os.path.join(out_label_dir, f"{basename}.txt"))

            # 2. Start augmentation process
            image = cv2.imread(img_path)
            height, width = image.shape[:2]
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            masks, class_ids = yolo_to_masks(label_path, height, width)
            if not masks:
                continue

            # 3. Generate N augmented versions
            for i in range(num_augs_per_image):
                augmented = transform(image=image, masks=masks)
                aug_image = augmented['image']
                aug_masks = augmented['masks']
                yolo_lines = masks_to_yolo(aug_masks, class_ids, aug_image.shape[0], aug_image.shape[1])

                if yolo_lines:
                    new_filename = f"{basename}_aug_{i}"
                    cv2.imwrite(
                        os.path.join(out_img_dir, f"{new_filename}{ext}"),
                        cv2.cvtColor(aug_image, cv2.COLOR_RGB2BGR)
                    )
                    with open(os.path.join(out_label_dir, f"{new_filename}.txt"), 'w') as f:
                        f.write('\n'.join(yolo_lines))
    
    # 4. Create a new data.yaml for the augmented dataset
    print("\nCreating new data.yaml file...")
    original_yaml_path = os.path.join(base_dir, 'data.yaml')
    new_yaml_path = os.path.join(output_dir, 'data.yaml')
    
    class_names = []
    if os.path.exists(original_yaml_path):
        try:
            with open(original_yaml_path, 'r') as f:
                data_yaml = yaml.safe_load(f)
                class_names = data_yaml.get('names', [])
        except Exception as e:
            print(f"Warning: Could not read class names from original data.yaml. Error: {e}")
    else:
        print("Warning: Original data.yaml not found. The 'names' field in the new yaml will be empty.")
    
    new_yaml_data = {
        'path': os.path.abspath(output_dir),  # Use absolute path for robustness
        'train': 'train/images',
        'val': 'valid/images',
        'names': class_names
    }

    try:
        with open(new_yaml_path, 'w') as f:
            yaml.dump(new_yaml_data, f, sort_keys=False, default_flow_style=False)
        print(f"Successfully created new data.yaml at {new_yaml_path}")
    except Exception as e:
        print(f"Error: Could not write new data.yaml file. Error: {e}")

    print("\nAugmentation complete! 🎉 Your new dataset is ready for training.")

# -------------------------------------------------------------------
# Script Execution
# -------------------------------------------------------------------

if __name__ == "__main__":
    print("--- YOLOv8 Segmentation Augmentation Script ---")
    
    # Get user input for the dataset directory
    while True:
        base_folder = input("Enter the full path to your YOLOv8 dataset folder: ")
        if os.path.isdir(base_folder) and \
           os.path.isdir(os.path.join(base_folder, 'train', 'images')) and \
           os.path.isdir(os.path.join(base_folder, 'valid', 'images')):
            break
        else:
            print("Error: Invalid directory. Please ensure it's a YOLOv8 folder with 'train' and 'valid' subdirectories.")

    # Get user input for the number of augmentations
    while True:
        try:
            num_augs = int(input("Enter the number of augmented versions to create per image: "))
            if num_augs > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")
            
    # Run the main augmentation function
    augment_dataset(base_folder, num_augs)