# Neural Network
![v1](https://img.shields.io/badge/Version-v1-green)
![Static Badge](https://img.shields.io/badge/Made_in-Python-blue)

A neural network library built without any AI libraries, only NumPy.

## How to Use
### Training
You have to set any images you want the model to train off of in the `train/` folder.

Then, run `src/ptl-neural-network/train.py`. It will automatically take all the images and train the A.I. model. This could take a while!
It will store the output as a `model.pkl` file.
### Usage
You can now run `src/ptl-neural-network/run.py`, with the only requirement being the `model.pkl` that you got from training.

It will ask for a `.png` file, and you can provide a relative or absolute path here. It will then find the closest image that matches your PNG.

Note that its output is the name of the image found from training data, so you might have to do some filtering to determine what the PNG is (bus) instead of a image name (bus3)
### Alternative
You can also do `pip install ptl-neural-network` to get the CLI.

The command syntax is `ptl-neural train/run`. The above guide also works with the CLI, except don't run `train.py` or `run.py`.
