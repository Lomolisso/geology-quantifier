import stitching
import sample_extraction
import sample_extraction
import cv2
import image_managers
import os

c = 0
path = './img/panoramic/samples_by_degree/diorite/'

stitcher = stitching.Stitcher()
raw_img1 = image_managers.load_image_from_window()
# img = cv2.resize(raw_img1, (int(raw_img1.shape[1]*0.2),int(raw_img1.shape[0]*0.2)))
img1 = sample_extraction.extract_sample(raw_img1)
os.chdir(path)
cv2.imwrite('image ' + str(c) + '.jpg', img1)

raw_img2 = image_managers.load_image_from_window()
# img = cv2.resize(raw_img1, (int(raw_img2.shape[1]*0.2),int(raw_img2.shape[0]*0.2)))
img2 = sample_extraction.extract_sample(raw_img2)

raw_img3 = image_managers.load_image_from_window()
# img = cv2.resize(raw_img1, (int(raw_img3.shape[1]*0.2),int(raw_img3.shape[0]*0.2)))
img3 = sample_extraction.extract_sample(raw_img3)

raw_img4 = image_managers.load_image_from_window()
# img = cv2.resize(raw_img1, (int(raw_img4.shape[1]*0.2),int(raw_img4.shape[0]*0.2)))
img4 = sample_extraction.extract_sample(raw_img4)

img1 = cv2.resize(img1, (200, 200))
img2 = cv2.resize(img2, (200, 200))
img3 = cv2.resize(img3, (200, 200))
img4 = cv2.resize(img4, (200, 200))



p_img1 = path + "dio_6n_0.jpg"
p_img2 = path + 'dio_6n_90.jpg'
p_img3 = path + 'dio_6n_180.jpg'
p_img4 = path + 'dio_6n_270.jpg'

panorama = stitcher.stitch([p_img1, p_img2])
cv2.namedWindow('Sample Area')
cv2.imshow('Sample Area', panorama)
cv2.waitKey(0)