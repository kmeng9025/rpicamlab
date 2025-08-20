# yolov8_seg_modal.py
# - Downloads a Roboflow YOLOv8 (Segmentation) dataset at runtime
# - Trains on an NVIDIA A10
# - Saves all outputs to a Modal Volume so you can download them after the run

import os
import modal

# ---------- Config ----------
MODEL_WEIGHTS = "yolov8n-seg.pt" # yolov8n-seg.pt / yolov8s-seg.pt / etc.
EPOCHS = 200
IMGSZ = 1536  # good starting point for 3280x2460 images
# BATCH = 16             # optional: set a number like "8"; default uses auto-batch

# You created this earlier: holds ROBOFLOW_API_KEY, ROBOFLOW_WORKSPACE, ROBOFLOW_PROJECT, ROBOFLOW_VERSION
ROBOFLOW_SECRET_NAME = "roboflow"

# Volume name to persist outputs/checkpoints
CKPT_VOLUME_NAME = "yolov8-checkpoints"

# ---------- Modal setup ----------
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        "torch==2.3.0",
        "torchvision==0.18.0",
        "torchaudio==2.3.0",
        index_url="https://download.pytorch.org/whl/cu121",   # CUDA 12.1 wheels
    )
    .pip_install(
        "ultralytics==8.0.196",
        # extra_options="--no-deps",   # don't let ultralytics pull/override torch
    )
    .pip_install(
        "roboflow"
    )
)

#TODO: CHANGE THIS
#TODO: CHANGE THIS
#TODO: CHANGE THIS
app = modal.App("yolov8-seg-roboflow-L40S", image=image)

roboflow_secret = modal.Secret.from_name(ROBOFLOW_SECRET_NAME)
ckpt_vol = modal.Volume.from_name(CKPT_VOLUME_NAME, create_if_missing=True)

#TODO: CHANGE THIS
#TODO: CHANGE THIS
#TODO: CHANGE THIS
@app.function(
    gpu="L40S",
    timeout=60 * 60 * 12,
    secrets=[roboflow_secret],
    volumes={"/checkpoints": ckpt_vol},
)
def train():
    # 1) Download dataset from Roboflow (Segmentation) in YOLOv8 format
    from roboflow import Roboflow
    from ultralytics import YOLO
    import yaml, os

    api_key   = os.environ["ROBOFLOW_API_KEY"]
    workspace = "mouse-vadhq"
    project   = "mousetest-a5ase"


    #TODO: CHANGE THIS
    #TODO: CHANGE THIS
    #TODO: CHANGE THIS
    #TODO: CHANGE THIS
    version   = 3

    print("Downloading Roboflow dataset…")
    rf = Roboflow(api_key=api_key)
    ds = rf.workspace(workspace).project(project).version(version).download("yolov8")
    data_yaml = os.path.join(ds.location, "data.yaml")

    with open(data_yaml) as f:
        cfg = yaml.safe_load(f)
    print("Classes:", cfg.get("names"))

    # 2) Train YOLOv8 segmentation on the A10
    print("Starting training…")



    #TODO: CHANGE THIS
    #TODO: CHANGE THIS
    #TODO: CHANGE THIS
    #TODO: CHANGE THIS
    #TODO: CHANGE THIS
    model = YOLO("/checkpoints/exp4/weights/best.pt")

    # Build train kwargs
    # train_kwargs = dict(
    #                  # run folder: /checkpoints/exp
    # )

#TODO: CHANGE THIS
#TODO: CHANGE THIS
#TODO: CHANGE THIS CHANGE BATCH
    results = model.train(
        data=data_yaml,
        epochs=EPOCHS,
        imgsz=IMGSZ,
        # rect=True,          # rectangular batches = less padding for 4:3 images
        cache=True,
        batch=22,
        workers=4,
        patience=30,
        amp=False,
        device=0,
        project="/checkpoints",  # <-- save directly to the Volume
        name="exp"
    )

    # 3) Persist the Volume so it's ready to download
    ckpt_vol = modal.Volume.from_name("yolov8-checkpoints")
    ckpt_vol.commit()

    save_dir = getattr(results, "save_dir", "/checkpoints/exp")
    print("Training complete. Artifacts saved to Volume at:", save_dir)


if __name__ == "__main__":
    # This lets you run with plain Python instead of the Modal CLI.
    # It starts the Modal app, then invokes the remote function.
    with app.run():
        train.remote()