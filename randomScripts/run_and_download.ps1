modal run .\trainModal.py::train
if ($LASTEXITCODE -ne 0) { throw "Training job failed." }

# ---- 4) Download to your Downloads folder ----
$Downloads = Join-Path $env:USERPROFILE "Downloads"
$Target    = Join-Path $Downloads "yolov8_outputs"  # we'll create/update this folder

Write-Host "Downloading checkpoints to $Target ..."
# This pulls the entire volume contents (e.g., /checkpoints/exp/weights/best.pt)
modal volume get yolov8-checkpoints $Target

Write-Host "Done!"
Write-Host "Model weights path (example): $Target\exp\weights\best.pt"