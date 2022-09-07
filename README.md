# Geology Quantifier

## Description
This repository contains the implementation of a basic geological quantifier that uses computer vision techniques to detect minerals in a rock sample and calculate rock statistics.

# Install
You need to install some libraries in order to use this tool. You can use `pip install -r requirements.txt` to install all the required dependencies.

## Usage
All you need to do is run the main.py file. You can use `python main.py`. Whenever the script needs a user input it will be displayed in the terminal, so please check it.

## Segmentation tools
For this iteration only the color segmentation tool is available, which uses k-means to create clusters to group similar colors. You can choose the number of clusters according to the different minerals you want to find. The clusters will then be displayed on the screen.
