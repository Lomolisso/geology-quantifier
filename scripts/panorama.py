import stitching
import sample_extraction
import sample_extraction
import cv2
import image_managers

# panorama = stitcher.stitch(["/img/raw/diorote/DIO 6N 0°.JPG", "/img/raw/diorote/DIO 6N 90°.JPG", "/img/raw/diorote/DIO 6N 180°.JPG"])
raw_img1 = image_managers.load_image_from_window()
# img = cv2.resize(raw_img1, (int(raw_img1.shape[1]*0.2),int(raw_img1.shape[0]*0.2)))
img1 = sample_extraction.extract_sample(raw_img1)

raw_img2 = image_managers.load_image_from_window()
# img = cv2.resize(raw_img1, (int(raw_img2.shape[1]*0.2),int(raw_img2.shape[0]*0.2)))
img2 = sample_extraction.extract_sample(raw_img2)

raw_img3 = image_managers.load_image_from_window()
# img = cv2.resize(raw_img1, (int(raw_img3.shape[1]*0.2),int(raw_img3.shape[0]*0.2)))
img3 = sample_extraction.extract_sample(raw_img3)

raw_img4 = image_managers.load_image_from_window()
# img = cv2.resize(raw_img1, (int(raw_img4.shape[1]*0.2),int(raw_img4.shape[0]*0.2)))
img4 = sample_extraction.extract_sample(raw_img4)

stitcher = stitching.Stitcher()
panorama = stitcher.stitch([img1, img2, img3, img4])

cv2.namedWindow('Sample Area')
cv2.imshow('Sample Area', panorama)

