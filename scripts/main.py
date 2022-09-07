import cv2

import sampleExtraction
import tube
import contornoMeanshift
import porcentaje

def gen_percent():
	# Get mask using kmeans
	cluster_masks, img = contornoMeanshift.gen_masks(3)

	# Show the masks
	for i in range(len(cluster_masks)):
		cv2.imshow(f"Original", img)
		cv2.imshow(f"Cluster {i}",cluster_masks[i])
		# Calculate and show the area pecent of the cluster in the image
		mask_percent = porcentaje.porcentaje(cluster_masks[i])
		print(f"Cluster {i}, porcentaje :{mask_percent}")
		cv2.waitKey(0)
		cv2.destroyAllWindows()


def gen_texture_tube():
	img = sampleExtraction.extract_sample()
	tube.fill_tube(img)

while True:
	menu = cv2.imread("img/HUD.jpg")
	cv2.imshow("Menu", menu)
	key = cv2.waitKey(0) & 0xFF

	if key == ord("1"):
		cv2.destroyAllWindows()
		gen_percent()
	
	elif key == ord("2"):
		cv2.destroyAllWindows()
		gen_texture_tube()
	
	elif key == ord("q"):
		cv2.destroyAllWindows()
		break