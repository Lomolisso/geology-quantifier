"""
Script to manualy cut the target sample of an image.
You can do it calling extract_sample(img) passing the 
image you want to cut.
"""
import cv2
import numpy as np
import enum
from unwraper import unwrapping

BLUE = (255,0,0)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
LIGHTBLUE = (230, 216, 173)
BLACK = (0, 0, 0)


class ExtractorModeEnum(str, enum.Enum):
    PANORAMIC = "panoramic"
    UNWRAPPER = "unwrapper"

class AbstractExtraction(object):
    def __init__(self, img: cv2.Mat) -> None:
        self.image = img
        self.image_size = self.image.shape
        self.original_image = self.image.copy()
        
        self.min_radius = 6
        self.radius = 7
    
    def _reset_vertex_dirty(self) -> None:
        """
        Resets the dirty vertex class attr. back to None.
        """
        self.vertex_dirty = None

    def _draw_circles_and_lines(self) -> None:
        """
        Draws the current selected area of the image.
        """

        # draws the lines
        for i in range(self.TOTAL_VERTICES):
            v1 = self.vertex_data[i]
            v2 = self.vertex_data[(i+1) % self.TOTAL_VERTICES]
            cv2.line(self.image, v1, v2, BLACK)
        
        # draws big circle
        for i in range(self.TOTAL_VERTICES):
            v = self.vertex_data[i]
            cv2.circle(self.image, v, self.radius, BLACK, -1)
        
        # draws small circle
        for i in range(self.TOTAL_VERTICES):
            v = self.vertex_data[i]
            cv2.circle(self.image, v, self.min_radius, LIGHTBLUE, -1)
    
    def refresh_image(self):
        self.image = self.original_image.copy()
        self._draw_circles_and_lines()
        self._reset_vertex_dirty()
    
    def get_image(self):
        return self.image
    
    def get_vertex_data(self):
        return self.vertex_data

    def check_mov(self, x: int, y: int) -> None:
        """
        Checks if a circle was moved, if it happend, sets the dirty attribute
        of it's vertex to True.
        """
        for k in range(len(self.vertex_data)):
            dist = np.linalg.norm(self.vertex_data[k] - np.array((x, y))) 
            if dist <= self.radius:
                self.vertex_dirty = k
                print(f"vertex-{k}")
                break

    
class PanoramicExtraction(AbstractExtraction):
    def __init__(self, img: cv2.Mat) -> None:
        """
        Class constructor, sets the main attributes of the
        instance acording to the input image.
        """
        self.TOTAL_VERTICES = 4
        super(PanoramicExtraction, self).__init__(img)
        
        self.vertex_data = []
        self.vertex_dirty = None
        
        self.reset_vertices()
        self._draw_circles_and_lines()
    
    def reset_vertices(self) -> None:
        """
        Resets the vertices positions back to default.
        """

        _, image_cols, *_ = self.image_size
        image_cols = image_cols//4
        image_rows = 2*image_cols


        d = np.array((
            self.image_size[1]//2-image_cols//2,
            self.image_size[0]//2-image_rows//2
        ))

        self.vertex_data = [
            np.array((0, 0)) + d,
            np.array((0, image_rows)) + d,
            np.array((image_cols, image_rows)) + d,
            np.array((image_cols, 0)) + d
        ]

    def move_vertex(self, x, y):
        self.image = self.original_image.copy()    
        v1, v2, v3, v4 = self.vertex_data
        cond_list = [
            lambda x, y: x < min(v4[0], v3[0]) and y < min(v2[1], v3[1]),
            lambda x, y: x < min(v4[0], v3[0]) and y > max(v1[1], v4[1]),
            lambda x, y: x > max(v1[0], v2[0]) and y > max(v1[1], v4[1]),   
            lambda x, y: x > max(v1[0], v2[0]) and y < min(v2[1], v3[1]),
        ]
        if self.vertex_dirty is not None and cond_list[self.vertex_dirty](x, y):
            self.vertex_data[self.vertex_dirty] = np.array((x, y))

        self._draw_circles_and_lines()
        

class UnwrapperExtraction(AbstractExtraction):
    def __init__(self, img: cv2.Mat) -> None: 
        """
        Class constructor, sets the main attributes of the
        instance acording to the input image.
        """
        self.TOTAL_VERTICES = 6
        super(UnwrapperExtraction, self).__init__(img)
        
        self.vertex_data = []
        self.vertex_dirty = None
        
        self.reset_vertices()
        self._draw_circles_and_lines()
    
        
    def reset_vertices(self) -> None:
        """
        Resets the vertices positions back to default.
        """
        _, image_cols, *_ = self.image_size
        image_cols = image_cols//4
        image_rows = 2*image_cols


        d = np.array((
            self.image_size[1]//2-image_cols//2,
            self.image_size[0]//2-image_rows//2
        ))

        self.vertex_data = [
            np.array((0, 0))+d,
            np.array((0, image_rows))+d,
            np.array((image_cols//2, image_rows))+d,
            np.array((image_cols, image_rows))+d,
            np.array((image_cols, 0))+d,
            np.array((image_cols//2, 0))+d,
        ]
    
    def _mov_vertex_0(self, x, y):
        """
        Handles the scaled movement of each vertex
        when the clicked is vertex_0
        """
        
        v0, v1, v2, _, v4, v5 = self.vertex_data
        vect = np.array([x, y])
        dx, dy = vect - v0
        m = (vect[0] + v4[0])//2
        
        v0 += np.array([dx, dy])
        v1 += np.array([dx, 0])
        v4 += np.array([0, dy])
        v2 += np.array([m-v2[0], 0])  
        v5 += np.array([m-v5[0], dy])         

        
    def _mov_vertex_1(self, x, y):
        """
        Handles the scaled movement of each vertex
        when the clicked is vertex_1
        """
        v0, v1, v2, v3, v4, v5 = self.vertex_data
        vect = np.array([x, y])
        dx, dy = vect - v1
        m = (vect[0] + v4[0])//2

        v0 += np.array([dx, 0])
        v1 += np.array([dx, dy])
        v2 += np.array([m-v2[0], dy])
        v3 += np.array([0, dy])
        v5 += np.array([m-v5[0], 0])        

    def _mov_vertex_2(self, x, y):
        _, _, v2, _, _, v5 = self.vertex_data
        vect = np.array([x, y])
        dx, dy = vect - v2
        v2 += np.array([dx, dy])
        v5 += np.array([dx, 0])

    def _mov_vertex_3(self, x, y):
        """
        Handles the scaled movement of each vertex
        when the clicked is vertex_3
        """
        _, v1, v2, v3, v4, v5 = self.vertex_data
        vect = np.array([x, y])
        dx, dy = vect - v3
        m = (vect[0] + v1[0])//2

        v1 += np.array([0, dy])
        v2 += np.array([m-v2[0], dy])
        v3 += np.array([dx, dy])
        v4 += np.array([dx, 0])
        v5 += np.array([m-v5[0], 0])
        
    def _mov_vertex_4(self, x, y):
        """
        Handles the scaled movement of each vertex
        when the clicked is vertex_4
        """
        v0, _, v2, v3, v4, v5 = self.vertex_data
        vect = np.array([x, y])
        dx, dy = vect - v4
        m = (vect[0] + v0[0])//2

        v0 += np.array([0, dy])
        v2 += np.array([m-v2[0], 0])
        v3 += np.array([dx, 0])
        v4 += np.array([dx, dy])
        v5 += np.array([m-v5[0], dy])

    def _mov_vertex_5(self, x, y):
        _, _, v2, _, _, v5 = self.vertex_data
        vect = np.array([x, y])
        dx, dy = vect - v5
        v2 += np.array([dx, 0])
        v5 += np.array([dx, dy])
        
    def _process_scale_mov(self, x, y):
        mov_dict = {
            0 : self._mov_vertex_0,
            1 : self._mov_vertex_1,
            2 : self._mov_vertex_2,
            3 : self._mov_vertex_3,
            4 : self._mov_vertex_4,
            5 : self._mov_vertex_5
        }
        if self.vertex_dirty is not None:
            mov_dict[self.vertex_dirty](x, y)
        
        
    def move_vertex(self, x, y):
        self.image = self.original_image.copy()
        is_free_vertex = lambda v: v == 6
        
        if is_free_vertex(self.vertex_dirty):
            self.vertex_data[self.vertex_dirty] = np.array((x, y))

        else:
            self._process_scale_mov(x, y)
        
        self._draw_circles_and_lines()
        

class SampleExtractor(object):
    def __init__(self,img: cv2.Mat, mode: ExtractorModeEnum) -> None:
        self.img = img
        if mode == ExtractorModeEnum.PANORAMIC:
            self.to_panoramic()
        else:
            self.to_unwrapper()

    # --- Switch between states ---
    def to_panoramic(self):
        self.mode = ExtractorModeEnum.PANORAMIC
        self.ext = PanoramicExtraction(img=self.img)
    
    def to_unwrapper(self):
        self.mode = ExtractorModeEnum.UNWRAPPER
        self.ext = UnwrapperExtraction(img=self.img)
    
    # --- Public extraction methods ---
        
    def get_image(self):
        return self.ext.get_image()
    
    def refresh_image(self):
        self.ext.refresh_image()
    
    def get_vertex_data(self):
        return self.ext.vertex_data
    
    def check_mov(self, x, y):
        self.ext.check_mov(x, y)
    
    def move_vertex(self, x, y):
        self.ext.move_vertex(x, y)

def resize_unwrapping(img, sample_extractor):
    """
    Cut the same part of imagen of the sample extractor,
    but in a different version of the image.
    """

    copy_img = np.copy(img)

    v1, v6, v5, v4, v3, v2 = sample_extractor.get_vertex_data()

    points = v1, v2, v3, v4, v5, v6

    # distance = v5[0]-v1[0]

    # proportion = 0.1

    # correction = distance*proportion//2

    # v1[0] = v1[0] - correction
    # v2[0] = v2[0] - correction
    # v4[0] = v4[0] + correction
    # v5[0] = v5[0] + correction

    
    resize_image = sample_extractor.get_image()
    rs_shape = resize_image.shape
    org_shape = img.shape
    ratio = org_shape[0]/rs_shape[0]
    vertex = []
    
    for value in points:
        vertex.append(value*ratio)
    
    vertex_1, vertex_2, vertex_3, vertex_4, vertex_5, vertex_6 = [v for v in vertex]
    points = vertex_1, vertex_2, vertex_3, vertex_4, vertex_5, vertex_6
    
    return unwrapping(copy_img, "awa.jpg", points)

def cut_image_from_vertex(img, sample_extractor):
    """
    Cut the same part of imagen of the sample extractor,
    but in a different version of the image.
    """
    vertex_data = sample_extractor.get_vertex_data()
    resize_image = sample_extractor.get_image()
    rs_shape = resize_image.shape
    org_shape = img.shape
    ratio = org_shape[0]/rs_shape[0]
    vertex = []
    for value in vertex_data:
        vertex.append(value*ratio)
    vertex_1, vertex_2, vertex_3, vertex_4 = [v for v in vertex]

    width_1 = np.linalg.norm(vertex_1 - vertex_4)
    width_2 = np.linalg.norm(vertex_2 - vertex_3)
    max_width = max(int(width_1), int(width_2))

    height_1 = np.linalg.norm(vertex_1 - vertex_2)
    height_2 = np.linalg.norm(vertex_3 - vertex_4)
    max_height = max(int(height_1), int(height_2))

    output_points = np.array([
            [0, 0],
            [0, max_height - 1],
            [max_width - 1, max_height - 1],
            [max_width - 1, 0]
        ], 
        dtype=np.float32
    )
    input_points = np.array(vertex, dtype=np.float32)    
    M = cv2.getPerspectiveTransform(input_points, output_points)
    out = cv2.warpPerspective(img, M,(max_width, max_height), flags=cv2.INTER_LINEAR)

    return out