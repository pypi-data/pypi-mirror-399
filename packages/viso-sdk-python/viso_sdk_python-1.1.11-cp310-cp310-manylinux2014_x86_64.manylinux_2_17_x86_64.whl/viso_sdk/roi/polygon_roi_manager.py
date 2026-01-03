"""
v 0.0.8-fix the shared reference bug
v 0.0.7-add exception when the point is not in the polygon
v 0.0.6-ROI add polygons parameter for the constructor
v 0.0.5-ROI is implemented by shapely
v 0.0.4-ROI points exception
v 0.0.2-customize for MOD container
v 0.0.1-multiple polygon exclude/include roi logic
"""
import cv2
import copy
import numpy as np
from shapely.geometry import Polygon, Point

from viso_sdk.constants import KEY
from viso_sdk.logging import exception_traceback
from viso_sdk.logging import get_logger

logger = get_logger("PolygonROIManager")


class RoiData:
    POLYGON_INFO = "polygon_roi"
    ROI_ID_KEY = "roi_id"
    ROI_LABEL_KEY = "label"
    INCLUDE_KEY = "include"
    POINTS_KEY = "points"
    POLYGON_EDGE = 1


class PolygonROIManager:

    def __init__(self, polygons=None, frame_sz=None):
        """
        check the point in polygon area
        :param polygons: polygon information in the previous roi node
        :param frame_sz: size of the frame
        """

        self.polygons = None
        # copy instantiates a new object with the same value as the original object
        if polygons:
            self.polygons = copy.deepcopy(polygons)

        self.rois = polygons

        if not frame_sz:
            self.frame_sz = [1.0, 1.0]
        else:
            self.frame_sz = [float(frame_sz[0]), float(frame_sz[1])]

        if self.rois:
            # Convert points to numpy arrays and create shapely polygons
            for polygon in self.rois:
                polygon[RoiData.POINTS_KEY] = np.array(polygon[RoiData.POINTS_KEY], dtype=np.float32)
                polygon['shapely_polygon'] = Polygon(polygon[RoiData.POINTS_KEY])

    def is_point_in_polygon(self, point, polygon):
        # Convert point to tuple
        point = tuple(point)

        # Use cv2.pointPolygonTest to check if the point is inside the polygon
        result = cv2.pointPolygonTest(polygon['points'], point, False)

        # If result is >= 0, the point is inside or on the polygon
        return result >= 0

    def is_point_in_any_excluded_intersection(self, point):
        point_shapely = Point(point)
        for i in range(len(self.rois)):
            for j in range(i + 1, len(self.rois)):
                poly1 = self.rois[i]
                poly2 = self.rois[j]
                intersection = poly1['shapely_polygon'].intersection(poly2['shapely_polygon'])
                if intersection.contains(point_shapely):
                    # Exclude if either polygon has include=False
                    if not poly1['include'] or not poly2['include']:
                        return True
        return False

    def is_point_in_included_intersection(self, point):
        point_shapely = Point(point)
        for i in range(len(self.rois)):
            for j in range(i + 1, len(self.rois)):
                poly1 = self.rois[i]
                poly2 = self.rois[j]
                intersection = poly1['shapely_polygon'].intersection(poly2['shapely_polygon'])
                if intersection.contains(point_shapely):
                    # Include if both polygons have include=True
                    if poly1[RoiData.INCLUDE_KEY] and poly2[RoiData.INCLUDE_KEY]:
                        return True
        return False

    def filter_in_roi(self, det_or_trk, frame_sz=None, anchor_pt=(0.5, 0.5)):
        """
        :param det_or_trk: this param is detection result or tracking result
        :param frame_sz: frame size of the image frame
        :param anchor_pt: anchored position of tracking result or detection result
        :return:
        """
        try:
            if not frame_sz:
                frame_sz = self.frame_sz

            if not self.rois:
                return det_or_trk

            stracks_in_roi = []
            for item in det_or_trk:
                has_info_attr = hasattr(item, 'info')
                # if det_or_trk is track, it has info attribute
                if has_info_attr:
                    (x, y, width, height) = item.info.get('rect', item.tlwh)
                else:
                    # customize for MOD
                    (x, y, width, height) = item.tlwh

                ref_pt = ((x + width * anchor_pt[0]),
                          (y + height * anchor_pt[1]))
                if width > 1.0 and height > 1.0:
                    ref_pt = (ref_pt[0] / frame_sz[0], ref_pt[1] / frame_sz[1])

                # Filter included polygons
                for polygon in self.rois:
                    if has_info_attr:
                        item.info[KEY.ROI_ID] = polygon.get(RoiData.ROI_ID_KEY, '')
                        item.info[KEY.ROI_NAME] = polygon.get(RoiData.ROI_LABEL_KEY, '')
                    else:
                        item.roi_id = polygon.get(RoiData.ROI_ID_KEY, '')
                        item.roi_name = polygon.get(RoiData.ROI_LABEL_KEY, '')

                    if len(polygon[RoiData.POINTS_KEY]) == 0:
                        stracks_in_roi.append(item)
                        continue

                    if polygon[RoiData.INCLUDE_KEY]:  # Only check included polygons
                        if (self.is_point_in_polygon(ref_pt, polygon) and (
                                not self.is_point_in_any_excluded_intersection(
                                    ref_pt) or self.is_point_in_included_intersection(ref_pt))):
                            stracks_in_roi.append(copy.deepcopy(item))

            return stracks_in_roi
        except Exception as e:
            exception_traceback(logger=logger, exception=e)
            return []
