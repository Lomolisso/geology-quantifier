import cv2
import matplotlib.pyplot as plt
import numpy as np
from pywt import dwt2
from skimage.filters import gabor, gaussian
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

from api_fm import load_image

# ----- Gabor filters params -----
ORIENTATIONS = [(np.pi/6)*i for i in range(0,6)] # {0, 30, 60, 90, 120, 150}
FREQUENCIES = [np.sqrt(2), 1+np.sqrt(2), 2+np.sqrt(2), 2*np.sqrt(2)] # empiric
CLUSTERS = 2

# ----- Utilities -----
def get_energy_density(pixels):
    SCALE_FACTOR = 1 # scaling needed if density is small float
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


# ----- Main script -----

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
    for theta in ORIENTATIONS:
        for freq in FREQUENCIES:
            re_filter, im_filter = gabor(img, frequency=freq, bandwidth=bandwidth, theta=theta)
            magnitude_dict[(theta, freq)] = get_magnitude(re_filter, im_filter)

    # Apply gaussian smoothing to the magnitudes
    gabor_mags = np.array([
        gaussian(gab_filter_mag, sigma=0.5*freq)
        for (_, freq), gab_filter_mag in magnitude_dict.items()
    ])

    for i, mag in enumerate(gabor_mags):
        cv2.imshow(f"Texture {i}", np.uint8(mag))
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Reshape the array before standarizing
    reshaped_gabor_mags = gabor_mags.reshape((-1, rows * cols))

    # Standarize the array before applying PCA
    standardized_data = StandardScaler().fit_transform(reshaped_gabor_mags.T)
    
    # Apply PCA to reduce the components to 1, i.e. from 24 
    # gabor features we reduce them to only one.
    pca = PCA(n_components=1).fit(standardized_data)
    pca_img_arr = pca.transform(standardized_data).astype(np.uint8)

    # Reshape the array to the dimensions of the image
    result = pca_img_arr.reshape((rows, cols))
    plt.imshow(result)
    plt.show()
"""
    # Let N = len(gabor_mags), to segmentate the image we will 
    # apply KMeans in a N-dimension space where each dim. is a 
    # gabor feature.

    # Create the DataFrame
    gabor_feature_bank = gabor_mags.reshape((rows * cols, -1))

    # Standarize the data before applying PCA
    std_gabor = StandardScaler().fit_transform(gabor_feature_bank)
    
    # Apply PCA to avoid the curse of dimensionality
    pca = PCA(n_components=12).fit(std_gabor)
    pca_gabor = np.float32(pca.transform(std_gabor))

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.85)
    _, labels, _ = cv2.kmeans(np.float32(gabor_feature_bank), CLUSTERS, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    x = labels.flatten().reshape(rows, cols)
    
    cv2.imshow(f"Gabor feature bank (PCA)", np.float32(x))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
"""

if __name__ == "__main__":
    main()
