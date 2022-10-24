# Geology Quantifier

## Description
This repository contains the implementation of a basic geological quantifier that uses computer vision techniques to detect minerals in a rock sample and calculate rock statistics.

# Install
You need to install some libraries in order to use this tool. You can use `pip install -r requirements.txt` to install all the required dependencies.

## Usage
All you need to do is run the gui.py file. You can use `python src/gui.py`.

## Segmentation tools
We have 2 segmentation tools:
- The color segmentation tool, which uses k-means to create clusters to group similar colors. You can choose the number of clusters based on the different minerals you want to find. The clusters will then be displayed on the screen.
- The shape segmentation tool, which uses the aspect ratio of all image contours to segment them. On the screen you will see the original image and another image, with a colored rectangle surrounding each shape, the color of the rectangle determines the mineral.
