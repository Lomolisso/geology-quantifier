import cv2
import numpy as np

from shape_detection import ContourData, contour_segmentation


def math_area(array):
    """
    Calculate the area using the determinant of a matrix created using the input array,
    the points must be ordered and the image must not have holes in it.
    """
    left_det = 0
    right_det = 0
    for i in range(len(array)):
        if i == len(array) - 1:
            left_det += array[i][0] * array[0][1]
            right_det += array[i][1] * array[0][0]
        else:
            left_det += array[i][0] * array[i + 1][1]
            right_det += array[i][1] * array[i + 1][0]
    if 1 / 2 * (left_det - right_det) > 0:
        return np.round(1 / 2 * (left_det - right_det), 2)
    else:
        return np.round(-1 / 2 * (left_det - right_det), 2)


def math_aspect_ratio(array):
    """
    Calculate the aspect ratio of the points in the input array.
    it draws the inscrite rectangle of the shapes and perform its aspect ratio.
    """
    maxx = max(fila[0] for fila in array)
    minx = min(fila[0] for fila in array)
    maxy = max(fila[1] for fila in array)
    miny = min(fila[1] for fila in array)
    x = maxx - minx + 1
    y = maxy - miny + 1
    ratio = x / y
    if ratio < 1:
        ratio = 1 / ratio
    return np.round(ratio, 2)


def math_equiv_radio(array):
    """
    Calculate the equivalent radius of the shape using the formula:
    area = pi * radius**2
    """
    return np.sqrt(math_area(array) / np.pi)


def math_equiv_length(array):
    """
    Calculate the equivalent length of the shape using the formula:
    area = (length) * (asp_ratio * length)
    """
    return np.round(np.sqrt(math_area(array) / math_aspect_ratio(array)), 1)


def math_middle_point(array):
    """
    Calculate the middle points of the shape using the minimum and maximum coordinate in the x and y axis of the points.
    """
    maxx = max(fila[0] for fila in array)
    x = min(fila[0] for fila in array)
    maxy = max(fila[1] for fila in array)
    y = min(fila[1] for fila in array)
    h = maxy - y + 1
    w = maxx - x + 1
    return (np.round(x + w / 2, 1), np.round(y + h / 2, 1))


def math_perimeter(array):
    """
    Calculate the perimeter of the shape calculate the euclidean distance between every point in the shape.
    """
    perimeter = 0
    for i in range(len(array)):
        if i == len(array) - 1:
            long = np.sqrt(
                np.square(abs(array[0][0] - array[i][0]))
                + np.square(abs(array[0][1] - array[i][1]))
            )
        else:
            long = np.sqrt(
                np.square(abs(array[i + 1][0] - array[i][0]))
                + np.square(abs(array[i + 1][1] - array[i][1]))
            )
        perimeter += long
    return perimeter


def poli_gen(n, center, radius):
    """
    Generate a random poligon with n vertices. The point is at distance radius of the center, with an angle given by a random number.
    """
    x, y = center
    theta = np.sort(np.random.rand(n))
    theta = 2 * np.pi * theta
    points = [
        [round(x + radius * np.cos(a), 0), round(y + radius * np.sin(a), 0)]
        for a in theta
    ]
    return np.array(points, np.int32)


def poli_gen_radio(n, center, radius, min):
    """
    Generate a random poligon with n vertices. The point is at distance radius (with a difference given by a random number) of the center, with an angle given by a random number.
    """
    x, y = center
    theta = np.sort(np.random.uniform(0, 1, n))
    theta = 2 * np.pi * theta
    ran = radius * np.random.uniform(min, 1, n)
    points = [
        [
            round(x + ran[i] * np.cos(theta[i]), 0),
            round(y + ran[i] * np.sin(theta[i]), 0),
        ]
        for i in range(len(theta))
    ]
    return np.array(points, np.int32)


def assert_error_tuple(estimate_value: tuple, calculated_value: tuple, error: float):
    """
    Compares the estimate_value with the calculate_value and throws an Assertion Error if the difference between both values is greater than error.
    It compares the two values inside the tuple.
    """
    est_x, est_y = estimate_value
    cal_x, cal_y = calculated_value
    error_calculado = (cal_x - est_x) / est_x
    assert error > abs(error_calculado)
    error_calculado = (cal_y - est_y) / est_y
    assert error > abs(error_calculado)


def assert_error_float(
    estimate_value: np.float64, calculated_value: np.float64, error: float
):
    """
    Compares the estimate_value with the calculate_value and throws an Assertion Error if the difference between both values is greater than error.
    """
    calculated_error = (calculated_value - estimate_value) / estimate_value
    assert error > abs(calculated_error)


def assert_error(estimate_value, calculated_value, error: float):
    """
    Dispach the values to the assert_error_tuple or assert_error_float depending on the type of the input values.
    """
    if type(estimate_value) == tuple:
        assert_error_tuple(estimate_value, calculated_value, error)
    else:
        assert_error_float(estimate_value, calculated_value, error)


def testing(program_function, math_function, error):
    """
    Perform the testing of the given program_function againts the ground truth math_function.
    It fails with an AssesionError if the diference between the function is greater than the error value.
    """
    height = 400
    width = 400
    channels = 3

    points = []
    points.append(np.array([[100, 100], [100, 200], [200, 200]]))
    points.append(np.array([[250, 250], [350, 250], [300, 350]]))
    points.append(np.array([[0, 200], [0, 300], [100, 260]]))
    points.append(
        np.array([[100, 100], [100, 200], [200, 200], [150, 150], [200, 100]], np.int32)
    )
    points.append(
        np.array([[250, 250], [300, 300], [350, 250], [320, 200], [280, 200]], np.int32)
    )
    points.append(np.array([[0, 200], [0, 300], [100, 260], [70, 200]], np.int32))

    for pts in points:
        img = np.zeros((height, width, channels), dtype=np.uint8)
        value = math_function(pts)
        pts = pts.reshape((-1, 1, 2))
        img = cv2.fillPoly(img, [pts], (0, 255, 255))
        data = contour_segmentation(img)
        # Check complex diagonals
        try:
            assert_error(value, program_function(data[0]), error)
        except:
            cv2.imshow(f"{program_function}", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    for i in range(10, 100):
        img = np.zeros((height, width, channels), dtype=np.uint8)
        pts = poli_gen(i, (200, 200), 100)
        value = math_function(pts)
        pts = pts.reshape((-1, 1, 2))
        img = cv2.fillPoly(img, [pts], (0, 255, 255))
        data = contour_segmentation(img)
        try:
            assert_error(value, program_function(data[0]), error)
        except:
            cv2.imshow(f"{program_function}", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    for i in range(10, 100):
        img = np.zeros((height, width, channels), dtype=np.uint8)
        pts = poli_gen_radio(i, (200, 200), 100, 0.8)
        value = math_function(pts)
        pts = pts.reshape((-1, 1, 2))
        img = cv2.fillPoly(img, [pts], (0, 255, 255))
        data = contour_segmentation(img)
        try:
            assert_error(value, program_function(data[0]), error)
        except:
            cv2.imshow(f"{program_function}", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()


i = 0
while i <= 30:
    testing(ContourData.get_area, math_area, 0.05)
    testing(ContourData.aspect_ratio, math_aspect_ratio, 0.01)
    testing(ContourData.get_equiv_radius, math_equiv_radio, 0.05)
    testing(ContourData.get_equiv_lenght, math_equiv_length, 0.01)
    testing(ContourData.get_middle_point, math_middle_point, 0.01)
    i += 1
