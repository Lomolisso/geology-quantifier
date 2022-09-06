import cv2
import numpy as np
from pywt import dwt2
from skimage.filters import gabor, gaussian
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from api_fm import load_image


# ----- Utilities -----
def get_energy_density(pixels):
    SCALE_FACTOR = 100 # scaling needed if density is small float
    _, (cH, cV, cD) = dwt2(pixels.T, 'db1')
    energy = (cH ** 2 + cV ** 2 + cD ** 2).sum() / pixels.size
    energy_density = energy / (pixels.shape[0]*pixels.shape[1])
    
    return round(SCALE_FACTOR * energy_density, 5)

def get_magnitude(re_filter, im_filter):
    magnitude = lambda vector: np.linalg.norm(vector)
    assert re_filter.shape == im_filter.shape
    rows, cols = re_filter.shape

    magnitude = np.zeros((rows, cols))
    for i in range(rows):
        for j in range(cols):
            z = [re_filter[i,j], im_filter[i,j]] # complex number
            magnitude[i,j] = np.linalg.norm(z)

    return magnitude

def apply_pca(array):
    """
    :param array: array of shape pXd
    :return: reduced and transformed array of shape dX1
    """
    # apply dimensionality reduction to the input array
    standardized_data = StandardScaler().fit_transform(array)
    pca = PCA(n_components=1)
    pca.fit(standardized_data)
    transformed_data = pca.transform(standardized_data)
    return transformed_data


def main():
    img = load_image()
    
    # Pre processing the img
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rows, cols = img.shape
    img = cv2.equalizeHist(img)

    # Calculating the gabor filter parameters
    energy_density = get_energy_density(img)
    bandwidth = abs(0.4 * energy_density - 0.5)

    # Apply the filters to the img
    magnitude_dict = {}
    for theta in np.arange(0, np.pi, np.pi / 6):
        for freq in np.array([1.4142135623730951, 2.414213562373095, 2.8284271247461903, 3.414213562373095]): 
            re_filter, im_filter = gabor(img, frequency=freq, bandwidth=bandwidth, theta=theta)
            magnitude_dict[(theta, freq)] = get_magnitude(re_filter, im_filter)
            #img_gab = cv2.getGaborKernel()
            #magnitude_dict[(theta, freq)] = img_gab

    # Apply gaussian smoothing to the magnitudes
    gabor_mag = np.array([
        gaussian(gab_filter_mag, sigma=0.5*freq)
        for (_, freq), gab_filter_mag in magnitude_dict.items()
    ])

    # Reshape so that we can apply PCA
    value = gabor_mag.reshape((-1, rows * cols))

    # Get dimensionally reduced image
    pca_img_arr = apply_pca(value.T).astype(np.uint8)
    result = pca_img_arr.reshape((rows, cols))

    cv2.imshow(f"Image segmented by textures", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()




    
