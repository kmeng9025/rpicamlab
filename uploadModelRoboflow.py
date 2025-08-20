from roboflow import Roboflow

rf = Roboflow(api_key="QAUBBg794t1JwH7hpv7f")
project = rf.workspace("mouse-vadhq").project("mousetest-a5ase")

version = project.version(3)

version.deploy("yolov8", ".", "best.pt")