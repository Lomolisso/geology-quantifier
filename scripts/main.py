import cv2
import numpy as np
import api_fm
import contornoMeanshift
import panoramica


def algo():
	img = panoramica.function_out()
	img = cv2.resize(img, (int(img.shape[1]*0.2),int(img.shape[0]*0.2)))
	cv2.imshow("image", img)

algo()