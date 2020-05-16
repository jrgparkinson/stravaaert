import numpy as np
from skimage import measure
from skimage import io, feature, exposure
from skimage.color import rgb2gray
import gpxpy
from typing import List

def metres_to_latlng_conversion(reference_lat : float) -> List[float]:
    print(reference_lat)
    reference_lat = reference_lat * (np.pi / 180)  # Convert to radians
    m_per_deg_lat = 111132.92 - 559.822 * np.cos(2 * reference_lat) + 1.175 * np.cos(
        4 * reference_lat) - 0.0023 * np.cos(6 * reference_lat)
    m_per_deg_lon = 111412.84 * np.cos(reference_lat) - 93.5 * np.cos(3 * reference_lat) + 0.118 * np.cos(
        5 * reference_lat)

    return [m_per_deg_lat, m_per_deg_lon]

def img2gpx(img_path : str,
            center_position = (51.765688, -1.245077), # exeter-hertford
            scale = 1.0,
            extra_args = None) -> str:
    """
    img_pat: file path to image to process
    center_position: (lat, lng)
    scale: metres/pixel

    returns string containing xml 
    """

    print("Convert {} with center {} and scale {}".format(img_path, center_position, scale))
    
    r = rgb2gray(io.imread(img_path))

    # Find contours at a constant value of 0.8

    # try filters
    # r = feature.canny(r, sigma=0.1)
    # edges2 = feature.canny(im, sigma=3)

    # Best method so far
    r = exposure.adjust_gamma(r, 0.5)
    contours = measure.find_contours(r, 0.9)

    # r = feature.canny(r, sigma=0.1)
    # r = gaussian(r, sigma=1.0)
    # r = exposure.adjust_gamma(r, 5.0)
    # from skimage.segmentation import (morphological_chan_vese,
    #                                   morphological_geodesic_active_contour,
    #                                   inverse_gaussian_gradient,
    #                                   checkerboard_level_set)

    # from skimage.filters import threshold_otsu
    # thresh = threshold_otsu(r)
    # r = r > thresh
    # r = gaussian(r, sigma=1.4)

    # contours = measure.find_contours(r, 0.7)

    # Display the image and plot all contours found
    # fig, ax = plt.subplots()
    # ax.imshow(r, cmap=plt.cm.gray)

    # get longest contour:
    contours_paths = [c for n, c in enumerate(contours)]
    longest_contour = max(contours_paths, key=len)


    gpx = gpxpy.gpx.GPX()

    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # Create points:
    
    m_lat, m_lon = metres_to_latlng_conversion(center_position[0])
    print("{}, {}".format(m_lat, m_lon))

    # top left is actually the center
    # center the contours:
    x_vals = [c[0] for c in longest_contour]
    y_vals = [c[1] for c in longest_contour]

    x_center = (max(x_vals) - min(x_vals))/2.0
    y_center = (max(y_vals) - min(y_vals))/2.0

    for c in longest_contour:
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(center_position[0] - scale*(c[0]-x_center)/m_lat,
                                                          center_position[1] + scale*(c[1]-y_center)/m_lon,
                                                          elevation=10))


    return gpx.to_xml()



