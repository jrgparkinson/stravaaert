import numpy as np
from skimage import measure
from skimage import io, feature, exposure
from skimage.color import rgb2gray
import gpxpy
from typing import List
from datetime import datetime, timedelta

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
            scale = 100.0,
            extra_args = None) -> str:
    """
    img_pat: file path to image to process
    center_position: center of track (lat, lng)
    scale: image width in metres

    extra_args: dict containing "speed" and "smoothing" options

    returns string containing xml 
    """

    print("Convert {} with center {} and scale {}".format(img_path, center_position, scale))
    
    # Convert to grayscale image
    r = rgb2gray(io.imread(img_path))

    # Method to extract path: 

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

    # center and scale the track about (0,0) with max extent 1
    scaled_track = center_and_scale_track(longest_contour)

    # Sub sample - want one point every ~ 3.0 metres
    coarsened_track = coarsen_track(scaled_track, extra_args["smoothing"]/scale)

    # Write to GPX, including time info
    time = datetime.now() # starting time for gpx track
    speed = extra_args["speed"] # km/h
    speed = speed * 1000.0/3600.0 # convert km/h to m/s

    gpx = gpxpy.gpx.GPX()

    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    m_lat, m_lon = metres_to_latlng_conversion(center_position[0])
    print("m/lat: {}, m/lon: {}".format(m_lat, m_lon))

    for i in range(len(coarsened_track)):
        c = coarsened_track[i]
        if i > 0:
            prev_c = coarsened_track[i-1]
            dx = scale*np.sqrt(sum(pow(c-prev_c, 2)))
            dt = dx/speed
            time += timedelta(seconds=dt)

        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(center_position[0] - scale*c[0]/m_lat,
                                                          center_position[1] + scale*c[1]/m_lon,
                                                          elevation=10,
                                                          time=time))

    return gpx.to_xml()


def center_and_scale_track(gps_track: List[List[float]]) -> List[List[float]] :
    """
    Center track on (0,0) with max extent 1 in any direction
    """
    x_vals = [c[0] for c in gps_track]
    y_vals = [c[1] for c in gps_track]

    x_center = (max(x_vals) - min(x_vals))/2.0
    y_center = (max(y_vals) - min(y_vals))/2.0

    # Normalize the contour so it is center on 0,0 and has max extent 0.5 in any direction
    scaling = max(max(x_vals) - min(x_vals), max(y_vals) - min(y_vals))
    scaled_track = [(c - [x_center, y_center])/scaling for c in gps_track]

    return scaled_track


def coarsen_track(gps_track: List[List[float]], min_path_length: float) -> List[List[float]] :
    """ 
    Coarsen gps_track by requiring a minimum cumulative distance of min_path_length between consecutive points
    """
    coarsened_track = [gps_track[0]]
    dx = 0 # cumulative distance from last accepted point
    for i in range(1, len(gps_track)):
        c = gps_track[i]
        prev_c = gps_track[i-1]
        dx = dx + np.sqrt(sum(pow(c-prev_c, 2)))
        if dx > min_path_length:
            coarsened_track.append(c)
            dx = 0

    return coarsened_track