import cv2
import sample_extraction2
import image_managers
img = image_managers.load_image_from_window()
img = cv2.resize(img, (img.shape[0] * 0.2, img.shape[1] * 0.2))
sample_extraction2.SampleExtractor(img)
