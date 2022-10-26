"""
Script to manualy cut the target sample of an image.
You can do it calling extract_sample(img) passing the 
image you want to cut.
"""
from random import sample
import cv2
import numpy as np
import enum
from unwraper import unwrapping

BLUE = [255,0,0]
RED = [0, 0, 255]
GREEN = [0, 255, 0]
LIGHTBLUE = [230, 216, 173]
BLACK = [0, 0, 0]

class ExtractorModeEnum(enum.Enum, str):
    PANORAMIC = "panoramic"
    UNWRAPPER = "unwrapper"


        
class SampleExtractor(object):
    """
    This class is in charge of extracting a sub-image
    from an input image. The sub-image is created using
    an area defined by the user.
    """
    
    def __init__(self, img: cv2.Mat) -> None:
        """
        Class constructor, sets the main attributes of the
        instance acording to the input image.
        """
        self.img = img
        self.img_size = self.img.shape
        self.original_image = self.img.copy()
        
        self.mode = ExtractorModeEnum.UNWRAPPER
        
        self.vertex_data = []
        self.vertex_dirty = []
        
        self.min_radius = 6
        self.radius = 7

        self.reset_vertexes_pos()
        self._draw_circles_and_lines()
    
    def set_unwrapper_mode(self):
        self.mode = ExtractorModeEnum.UNWRAPPER

    def set_panoramic_mode(self):
        self.mode = ExtractorModeEnum.PANORAMIC
    
    def check_circle_movement(self, x: int, y: int) -> None:
    
    def process_movement(self, x, y):
        class_extraction = UnwrapperExtraction if self.mode == ExtractorModeEnum.UNWRAPPER else PanoramicExtraction
        class_extraction.process_movement(self, x, y)

class PanoramicExtraction(object):
    @staticmethod
    def process_movement(sample_extractor: SampleExtractor, x, y):
        v1, v2, v3, v4 = sample_extractor.vertex_data
        cond_list = [
            lambda x, y: x < min(v4[0], v3[0]) and y < min(v2[1], v3[1]),
            lambda x, y: x < min(v4[0], v3[0]) and y > max(v1[1], v4[1]),
            lambda x, y: x > max(v1[0], v2[0]) and y > max(v1[1], v4[1]),
            lambda x, y: x > max(v1[0], v2[0]) and y < min(v2[1], v3[1]),
        ]



        if len(sample_extractor.vertex_dirty) != 0 and cond_list[self.vertex_dirty](x, y) and self._margin_conditions(x, y):
            self.vertex_data[self.vertex_dirty] = np.array((x, y))


class UnwrapperExtraction(object):
    @staticmethod
    def process_movement(sample_extractor: SampleExtractor):
        pass