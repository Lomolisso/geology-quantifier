import color_segmentation
import numpy as np
import cv2

def clustering(image, N):
    return color_segmentation.generate_clusters(image, N)

def substract(image_1, image_2):
    return cv2.subtract(image_1, image_2)

def add(image_1, image_2):
    return cv2.add(image_1, image_2)
    
class ImageNode(object):
    def __init__(self, parent, image) -> None:
        self.parent = parent
        self.image = image
        self.childs = []

    def __propagate_delete(self, deleted_component):
        self.image = substract(self.image, deleted_component)
        if self.parent != None:
            self.parent.__propagate_delete(deleted_component)

    def __collapse_image_nodes(self, indices):
        acc = np.zeros(self.image.shape, dtype='uint8')
        for i in indices:
            child_img = self.childs[i].image
            acc = add(acc, child_img)
            self.childs[i] = None
        self.childs = [child for child in self.childs if child is not None]
        return acc
        
    def delete(self, indices: list[int]) -> None:
        acc = self.__collapse_image_nodes(indices)
        self.__propagate_delete(acc)
    
    def merge(self, indices: list[int]) -> None:
        acc = self.__collapse_image_nodes(indices)
        self.childs.append(ImageNode(self, acc))
        
    def split(self, n_childs: int) -> None:
        self.childs = [ImageNode(self, c_image) for c_image in clustering(self.image, n_childs)]


