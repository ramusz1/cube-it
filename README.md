# About

<p align="center" width="100%">

 <img width="30%" src="cubeit.svg">
  
</p>
 
# Info

Currently, this repository contains only the bare minimum code to run our demosaicing model.

# Installation
The following line installs the cubeit package
```bash
pip install .
```

## Requirements:
```bash
pip install torch numpy opencv-python
```

Additionally, to run the demo:
```bash
pip install matplotlib
```

## Run the demo
```
python demo.py
```

Function im2cube takes in an additional argument: guided_adjust. When set to True, this flag applies additional postprocessing on the predicted cube and reduces the reprojection error. This step significantly increases the demosaicing time.
