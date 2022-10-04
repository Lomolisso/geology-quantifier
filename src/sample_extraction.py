"""
Script to manualy cut the target sample of an image.
You can do it calling extract_sample(img) passing the 
image you want to cut.
"""
import cv2
import numpy as np
import math

IMG_RESIZE_SCALE = 0.2
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
    
    def __init__(self, img) -> None:
        """
        Class constructor, sets the main attributes of the
        instance acording to the input image.
        """
        img_rows, img_cols, *_ = img.shape
        self.bg = cv2.resize(img, 
            (
                int(img_cols * IMG_RESIZE_SCALE),
                int(img_rows * IMG_RESIZE_SCALE)
            )
        )
        self.bg_size = self.bg.shape
        self.original_image = self.bg.copy()
        self.vertex_data = {}
        self.vertex_dirty = None
        self.__reset_vertexes_pos()   
        self.min_radius = 6
        self.radius = 7

    def __draw_circles_and_lines(self):
        """
        Draws the current selected area of the image.
        """
        point_1, point_2, point_3, point_4 = [self.vertex_data[v] for v in self.vertex_data]
        cv2.line(self.bg, point_1, point_2, BLACK)
        cv2.line(self.bg, point_2, point_3, BLACK)
        cv2.line(self.bg, point_4, point_3, BLACK)
        cv2.line(self.bg, point_4, point_1, BLACK) 
        cv2.circle(self.bg, point_1, self.radius, BLACK, -1) 
        cv2.circle(self.bg, point_2, self.radius, BLACK, -1) 
        cv2.circle(self.bg, point_4, self.radius, BLACK, -1) 
        cv2.circle(self.bg, point_3, self.radius, BLACK, -1)
        cv2.circle(self.bg, point_1, self.min_radius, LIGHTBLUE, -1) 
        cv2.circle(self.bg, point_2, self.min_radius, LIGHTBLUE, -1) 
        cv2.circle(self.bg, point_4, self.min_radius, LIGHTBLUE, -1) 
        cv2.circle(self.bg, point_3, self.min_radius, LIGHTBLUE, -1)

    def __reset_vertexes_pos(self):
        """
        Resets the vertexes positions back to default.
        """
        bg_rows, bg_cols, *_ = self.bg_size
        self.vertex_data["vertex_1"] = np.array((bg_cols//4, bg_rows//4))
        self.vertex_data["vertex_2"] = np.array((bg_cols//4, bg_rows*3//4))
        self.vertex_data["vertex_3"] = np.array((bg_cols*3//4, bg_rows*3//4))
        self.vertex_data["vertex_4"] = np.array((bg_cols*3//4, bg_rows//4))
    
    def __reset_vertex_dirty(self):
        """
        Resets the dirty vertex class attr. back to None.
        """
        self.vertex_dirty = None

    def __check_circle_movement(self, x, y):
        """
        Checks if a circle was moved, if it happend, sets the dirty attribute
        of it's vertex to True.
        """
        for v in self.vertex_data:
            dist = np.linalg.norm(self.vertex_data[v] - np.array((x, y))) 
            if dist <= self.radius:
                self.vertex_dirty = v
                break

    def __check_mouse_pos(self, x, y):
        """
        Checks if the mouse position is contained in the image.
        """
        return x <= self.bg_size[1] and y <= self.bg_size[0] and x >= 0 and y>=0

    def __handle_mouse(self, event, x, y, *args):
        """
        Handles the events related to the mouse, such as when a vertex of the 
        selection area is moved.
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            self.__check_circle_movement(x, y)

        elif event == cv2.EVENT_MOUSEMOVE and self.__check_mouse_pos(x, y):
            self.bg = self.original_image.copy()
            v1, v2, v3, v4 = [self.vertex_data[v] for v in self.vertex_data]
            cond_dict = {
                "vertex_1": lambda x, y: x < min(v4[0], v3[0]) and y < min(v2[1], v3[1]),
                "vertex_2": lambda x, y: x < min(v4[0], v3[0]) and y > max(v1[1], v4[1]),
                "vertex_3": lambda x, y: x > max(v1[0], v2[0]) and y > max(v1[1], v4[1]),   
                "vertex_4": lambda x, y: x > max(v1[0], v2[0]) and y < min(v2[1], v3[1]),
            }

            if self.vertex_dirty is not None:
                cond = cond_dict[self.vertex_dirty](x, y)
                if cond:
                    self.vertex_data[self.vertex_dirty] = np.array((x, y))

            self.__draw_circles_and_lines()
        
        elif event == cv2.EVENT_LBUTTONUP:
            self.bg = self.original_image.copy()
            self.__draw_circles_and_lines()
            self.__reset_vertex_dirty()

    def extract_sample(self):
        """
        Only public method of the class, in charge of conducting 
        the extraction of the sample.
        """

        self.__draw_circles_and_lines()    
        cv2.namedWindow('Sample Area')
        cv2.setMouseCallback('Sample Area', self.__handle_mouse)
        instr = cv2.imread("./img/GUI/keyboard.png")
        
        while True:
            cv2.imshow('Sample Area', self.bg)
            cv2.imshow('instructions', instr)
            k = cv2.waitKey(1)

            # if 'Esc' is pressed, the cuting stops.
            if k == 27 & 0xFF:
                cv2.destroyAllWindows()
                return

            # if 's' is pressed, the img was cut in the rectangle area.
            elif k == ord("s"):
                point_1, point_2, point_3, point_4 = [self.vertex_data[v] for v in self.vertex_data]

                width_1 = np.linalg.norm(point_1 - point_4)
                width_2 = np.linalg.norm(point_2 - point_3)
                max_width = max(int(width_1), int(width_2))

                height_1 = np.linalg.norm(point_1 - point_2)
                height_2 = np.linalg.norm(point_3 - point_4)
                max_height = max(int(height_1), int(height_2))

                input_points = np.array([point_1, point_2, point_3, point_4], dtype=np.float32)
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

            # if 'r' is pressed, the rectangle return to the original position.
            elif k == ord('r'):
                self.__reset_vertexes_pos()