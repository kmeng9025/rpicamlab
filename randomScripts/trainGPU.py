def main():    
    from ultralytics import YOLO
    import yaml, os

    SAVE_DIR = "C:\\Users\\kmeng\\Documents\\rpicamlab\\trainingCheckpoints\\final\\check1"
    MODEL_WEIGHTS = "C:\\Users\\kmeng\\Documents\\rpicamlab\\weights\\last.pt"
    EPOCHS = 200
    IMGSZ = 1944
    RESUME = True

    data_yaml = "C:\\Users\\kmeng\\Documents\\rpicamlab\\augmentDataCached\\data.yaml"

    with open(data_yaml) as f:
        cfg = yaml.safe_load(f)
    print("Classes:", cfg.get("names"))

    print("Starting training…")



    model = YOLO(MODEL_WEIGHTS)

    if RESUME:
        model.train(
            data=data_yaml,
            # epochs=EPOCHS,
            # imgsz=IMGSZ,
            resume=True,
            # rect=True,          # rectangular batches = less padding for 4:3 images
            cache="disk",
            batch=-1,
            # workers=16,
            # patience=30,
            # amp=True,
            # device=0,
            # device="cpu",
            project=SAVE_DIR,  # <-- save directly to the Volume
            # name="exp"
        )

    else:
        model.train(
            data=data_yaml,
            epochs=EPOCHS,
            imgsz=IMGSZ,
            # rect=True,          # rectangular batches = less padding for 4:3 images
            cache="disk",
            batch=-1,
            workers=16,
            patience=30,
            amp=True,
            device=0,
            # device="cpu",
            project=SAVE_DIR,  # <-- save directly to the Volume
            name="check"
        )

if (__name__ == "__main__"):
    main()