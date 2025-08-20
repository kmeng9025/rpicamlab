from roboflow import Roboflow

rf = Roboflow(api_key="QAUBBg794t1JwH7hpv7f")
project = rf.workspace("mouse-vadhq").project("mousetest-a5ase")

#can specify weights_filename, default is "weights/best.pt"
version = project.version(2)

version.deploy(
    model_type="yolov8",  # Type of the model
    model_path=".\\trainingCheckpoints\\testmouseblobs\\check1",  # Path to model directory
    filename="weights/best.pt"  # Path to weights file (default)
)