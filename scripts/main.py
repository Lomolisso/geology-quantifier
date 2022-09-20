import cv2

import image_managers
import sample_extraction
import contorno_meanshift
import percent
import tube

TOKEN = "[MAIN_APP]"

def gen_percent():
	# Load image using OS file window
	raw_img = image_managers.load_image_from_window()

	# Cut the img to analize an specific part of it.
	img = sample_extraction.extract_sample(raw_img)

	try:
		assert img.all() != None
	except:
		# If 'Esc' was pressed, restart the program
		return
	
	# Ask user for the number of clusters to use
	cluster_num = int(input(f"{TOKEN} Enter the number of clusters to use: "))

	# Get mask using kmeans
	cluster_masks = contorno_meanshift.gen_masks(img, cluster_num)

	# Show the masks
	for i in range(len(cluster_masks)):
		cv2.imshow(f"Original", img)
		cv2.imshow(f"Cluster {i}",cluster_masks[i])
		# Calculate and show the area pecent of the cluster in the image
		mask_percent = percent.percent(cluster_masks[i])
		print(f"{TOKEN} Cluster {i}, area percent :{mask_percent}")
	cv2.waitKey(0)
	cv2.destroyAllWindows()


def gen_texture_tube():
	# Load image using OS file window
	raw_img = image_managers.load_image_from_window()

	# Cut the img to analize an specific part of it.
	img = sample_extraction.extract_sample(raw_img)

	# Use the loaded img to fill a 3D tube surface.
	tube.fill_tube(img)

while True:
	menu = image_managers.load_image_from_path("img/HUD.jpg")
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