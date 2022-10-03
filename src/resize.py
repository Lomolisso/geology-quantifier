import cv2
def resize_image(img, height, width):
    new_image = []
    # Height is related with img.shape[0]
    if img.shape[0] > img.shape[1]:
        new_image = cv2.resize(img, ((int(img.shape[1] * height / img.shape[0])), height))
    # Width is relates with img.shape[0]
    else:
        new_image = cv2.resize(img, (width, int(img.shape[0] * width / img.shape[1])))
    return new_image