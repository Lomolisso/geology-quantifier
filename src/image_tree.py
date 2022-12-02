from typing import List

import cv2
import numpy as np

import color_segmentation


def clustering(image, N):
    """
    Dispatchs the clustering task.
    """
    return color_segmentation.generate_clusters(image, N)


def substract(image_1, image_2):
    """
    Dispatchs the substraction of two images.
    """
    return cv2.subtract(image_1, image_2)


def add(image_1, image_2):
    """
    Dispatchs the addition of two images.
    """
    return cv2.add(image_1, image_2)


class ImageNode(object):
    """
    Data structure in charge of managing the current
    status of the GUI. The combination of ImageNodes
    forms an Image Tree which contains the complete
    history of the interaction between the user and
    the GUI's images.

    First, the tree contains only one ImageNode without
    childs (empty list). Once the user applies clustering
    to the image, the node acquires num_clusters
    childs (list of nodes with image but no childs).

    If a user selects a cluster image as the "current"
    image of the GUI and calls the clustering algorithm
    on it, it's corresponding image at the childs field
    of his father is replaced with an ImageNode. This
    node has childs as well, indeed, the childs field
    contains the images returned by the clustering algorithm.

    This data structure allows the user to travel the each
    status of the gui without lossing information.
    """

    def __init__(self, parent, image, name) -> None:
        """
        Class constructor, instantiates key parameters.
        Note that each node has edges to it's father and
        childs.
        """
        self.parent = parent
        self.image = image
        self.name = name
        self.childs = []

    def _propagate_delete(self, deleted_component):
        """
        Private method, once a cluster image is deleted from
        a childs list of a given node. The deletion should
        propagate all over the tree because basically we are
        deleting pixels of the image.
        """
        self.image = substract(self.image, deleted_component)
        if self.parent != None:
            self.parent._propagate_delete(deleted_component)

    def _collapse_image_nodes(self, indices):
        """
        Combines a list of ImageNodes, the resulting image
        is the addition of the images of the input list.
        """
        acc = np.zeros(self.image.shape, dtype="uint8")
        for i in indices:
            child_img = self.childs[i].image
            acc = add(acc, child_img)
            self.childs[i] = None
        self.childs = [child for child in self.childs if child is not None]
        return acc

    def delete(self, indices: List[int]) -> None:
        """
        Deletes one or more ImageNodes and propagates
        the deletion to the ancestors nodes.
        """
        acc = self._collapse_image_nodes(indices)
        self._propagate_delete(acc)

    def merge(self, indices: List[int]) -> None:
        """
        Merges a list of ImageNodes into one, note that
        they must be brothers, i.e., have the same father.
        """
        acc = self._collapse_image_nodes(indices)
        self.childs.append(ImageNode(self, acc, f"{self.name} cluster {indices[0]}"))

    def split(self, n_childs: int) -> None:
        """
        Takes an ImageNode without childs and sets it's
        parameter to the result of calling the clustering
        algorithm on it's image.
        """
        self.childs = []
        cluster_images = clustering(self.image, n_childs)
        for i in range(len(cluster_images)):
            self.childs.append(
                ImageNode(self, cluster_images[i], f"{self.name} cluster {i}")
            )
