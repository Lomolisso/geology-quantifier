"""
Script to manualy cut the target sample of an image.
You can do it calling extract_sample(img) passing the 
image you want to cut.
"""
import cv2
import numpy as np
from unwraper import unwrapping

BLUE = [255,0,0]
RED = [0, 0, 255]
GREEN = [0, 255, 0]
LIGHTBLUE = [230, 216, 173]
BLACK = [0, 0, 0]

class SampleExtractor(object):
    """
    This class is in charge of extracting a sub-image
    from an input image. The sub-image is created using
    an area defined by the user.
    """
    
    def __init__(self, img: cv2.Mat, total_vertices: int = 4) -> None:
        """
        Class constructor, sets the main attributes of the
        instance acording to the input image.
        """
        self.bg = img
        self.total_vertices = total_vertices
        self.bg_size = self.bg.shape
        self.original_image = self.bg.copy()
        self.vertex_data = {}
        self.vertex_dirty = None
        self.min_radius = 6
        self.radius = 7

        self.reset_vertices()
        self._draw_circles_and_lines()
    
    def get_image(self):
        return self.bg
    
    def refresh_image(self):
        self.bg = self.original_image.copy()
        self._draw_circles_and_lines()
        self._reset_vertex_dirty()
    
    def get_vertex_data(self):
        """
        Get vertex
        """
        return self.vertex_data

    def move_vertex(self, x, y):
        self.bg = self.original_image.copy()    
        if self.total_vertices == 4:
            v1, v2, v3, v4 = [self.vertex_data[v] for v in self.vertex_data]
            cond_dict = {
                "vertex_1": lambda x, y: x < min(v4[0], v3[0]) and y < min(v2[1], v3[1]),
                "vertex_2": lambda x, y: x < min(v4[0], v3[0]) and y > max(v1[1], v4[1]),
                "vertex_3": lambda x, y: x > max(v1[0], v2[0]) and y > max(v1[1], v4[1]),   
                "vertex_4": lambda x, y: x > max(v1[0], v2[0]) and y < min(v2[1], v3[1]),
            }
            if self.vertex_dirty is not None and cond_dict[self.vertex_dirty](x, y) and self._margin_conditions(x, y):
                self.vertex_data[self.vertex_dirty] = np.array((x, y))
        else:
            v1, v2, v3, v4, v5, v6 = [self.vertex_data[v] for v in self.vertex_data]
            cond_dict = {
                "vertex_1": lambda x, y: True,
                "vertex_2": lambda x, y: True,
                "vertex_3": lambda x, y: True,
                "vertex_4": lambda x, y: True,
                "vertex_5": lambda x, y: True,
                "vertex_6": lambda x, y: True,
            }
            if self.vertex_dirty is not None and cond_dict[self.vertex_dirty](x, y) and self._margin_conditions(x, y):
                self.vertex_data[self.vertex_dirty] = np.array((x, y))



        self._draw_circles_and_lines()

    def _margin_conditions(self, x, y):
        min_margins = x > 0 and y > 0
        max_margins = x < self.bg_size[1] and y < self.bg_size[0]
        return min_margins and max_margins 

    def _draw_circles_and_lines(self) -> None:
        """
        Draws the current selected area of the image.
        """

        # draws the lines
        for i in range(self.total_vertices):
            v1 = self.vertex_data[f"vertex_{i + 1}"]
            v2 = self.vertex_data[f"vertex_{((i+1) % self.total_vertices) + 1}"]
            cv2.line(self.bg, v1, v2, BLACK)
        
        # draws big circle
        for i in range(1, self.total_vertices + 1):
            v = self.vertex_data[f"vertex_{i}"]
            cv2.circle(self.bg, v, self.radius, BLACK, -1)
        
        # draws small circle
        for i in range(1, self.total_vertices + 1):
            v = self.vertex_data[f"vertex_{i}"]
            cv2.circle(self.bg, v, self.min_radius, LIGHTBLUE, -1)
        

    def reset_vertices(self) -> None:
        """
        Resets the vertices positions back to default.
        """
        bg_rows, bg_cols, *_ = self.bg_size
        step = 0 if self.total_vertices == 4 else 1

        self.vertex_data["vertex_1"] = np.array((bg_cols//4, bg_rows//4))
        self.vertex_data["vertex_2"] = np.array((bg_cols//4, bg_rows*3//4))
        self.vertex_data[f"vertex_{3 + step}"] = np.array((bg_cols*3//4, bg_rows*3//4))
        self.vertex_data[f"vertex_{4 + step}"] = np.array((bg_cols*3//4, bg_rows//4))

        if self.total_vertices == 6:
            self.vertex_data["vertex_3"] = np.array((bg_cols//2, bg_rows*3//4))
            self.vertex_data["vertex_6"] = np.array((bg_cols//2, bg_rows//4))
    
    def _reset_vertex_dirty(self) -> None:
        """
        Resets the dirty vertex class attr. back to None.
        """
        self.vertex_dirty = None

    def check_mov(self, x: int, y: int) -> None:
        """
        Checks if a circle was moved, if it happend, sets the dirty attribute
        of it's vertex to True.
        """
        for v in self.vertex_data:
            dist = np.linalg.norm(self.vertex_data[v] - np.array((x, y))) 
            if dist <= self.radius:
                self.vertex_dirty = v
                break

    def cut(self):
        vertex_1, vertex_2, vertex_3, vertex_4 = [self.vertex_data[v] for v in self.vertex_data]

        width_1 = np.linalg.norm(vertex_1 - vertex_4)
        width_2 = np.linalg.norm(vertex_2 - vertex_3)
        max_width = max(int(width_1), int(width_2))

        height_1 = np.linalg.norm(vertex_1 - vertex_2)
        height_2 = np.linalg.norm(vertex_3 - vertex_4)
        max_height = max(int(height_1), int(height_2))

        input_points = np.array([vertex_1, vertex_2, vertex_3, vertex_4], dtype=np.float32)
        output_points = np.array([
                [0, 0],
                [0, max_height - 1],
                [max_width - 1, max_height - 1],
                [max_width - 1, 0]
            ], 
            dtype=np.float32
        )
        
        # The perspective is built and cut on a clone of the original image.
        M = cv2.getPerspectiveTransform(input_points, output_points)
        out = cv2.warpPerspective(self.original_image, M,(max_width, max_height), flags=cv2.INTER_LINEAR)
        cv2.destroyAllWindows()
        return out
    
    def unwrap(self):
        points = self.vertex_data['vertex_1'], self.vertex_data['vertex_6'], self.vertex_data['vertex_5'], self.vertex_data['vertex_4'], self.vertex_data['vertex_3'], self.vertex_data['vertex_2']
        return unwrapping(self.original_image, "awa.jpg", points)


def resize_unwrapping(img, sample_extractor):
    """
    Cut the same part of imagen of the sample extractor,
    but in a different version of the image.
    """
    points = sample_extractor.vertex_data['vertex_1'], sample_extractor.vertex_data['vertex_6'], sample_extractor.vertex_data['vertex_5'], sample_extractor.vertex_data['vertex_4'], sample_extractor.vertex_data['vertex_3'], sample_extractor.vertex_data['vertex_2']
    vertex_data = sample_extractor.get_vertex_data()
    resize_image = sample_extractor.get_image()
    rs_shape = resize_image.shape
    org_shape = img.shape
    ratio = org_shape[0]/rs_shape[0]
    vertex = []
    for value in points:
        vertex.append(value*ratio)
    vertex_1, vertex_2, vertex_3, vertex_4, vertex_5, vertex_6 = [v for v in vertex]
    points = vertex_1, vertex_2, vertex_3, vertex_4, vertex_5, vertex_6
    return unwrapping(img, "awa.jpg", points)

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
    for value in vertex_data.values():
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