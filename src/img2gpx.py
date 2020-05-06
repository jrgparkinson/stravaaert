import numpy as np
# import matplotlib.pyplot as plt
# from skimage.filters import gaussian
from skimage import measure
from skimage import io, feature, exposure
from skimage.color import rgb2gray
import gpxpy
# Construct some test data
# x, y = np.ogrid[-np.pi:np.pi:100j, -np.pi:np.pi:100j]
# r = np.sin(np.exp((np.sin(x)**3 + np.cos(y)**2)))


def metres_to_latlng_conversion(reference_lat):
    reference_lat = reference_lat * (np.pi / 180)  # Convert to radians
    m_per_deg_lat = 111132.92 - 559.822 * np.cos(2 * reference_lat) + 1.175 * np.cos(
        4 * reference_lat) - 0.0023 * np.cos(6 * reference_lat)
    m_per_deg_lon = 111412.84 * np.cos(reference_lat) - 93.5 * np.cos(3 * reference_lat) + 0.118 * np.cos(
        5 * reference_lat)

    return [m_per_deg_lat, m_per_deg_lon]

def img2gpx(img_path,
            top_left = [51.765688, -1.245077], # exeter-hertford
            scale = 1.0):
    r = rgb2gray(io.imread(img_path))

    # Find contours at a constant value of 0.8

    # try filters
    # r = feature.canny(r, sigma=0.1)
    # edges2 = feature.canny(im, sigma=3)

    # Best so far
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
    # ax.plot(longest_contour[:, 1], longest_contour[:, 0], linewidth=2)

    sorted_contours = sorted(contours_paths, key=lambda x:len(x))
    # for c in sorted_contours[-1:]:
    #     ax.plot(c[:, 1], c[:, 0], linewidth=2, linestyle='--')

    # ax.axis('image')
    # ax.set_xticks([])
    # ax.set_yticks([])

    gpx = gpxpy.gpx.GPX()

    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # Create points:



    m_lat, m_lon = metres_to_latlng_conversion(top_left[0])
    print("{}, {}".format(m_lat, m_lon))

    for c in longest_contour:
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(top_left[0] - scale*c[0]/m_lat,
                                                          top_left[1] + scale*c[1]/m_lon,
                                                          elevation=10))

    # with open('out.gpx', 'w') as f:
    #     f.write(gpx.to_xml())
    #     print('Wrote to out.gpx')


    return gpx.to_xml()



