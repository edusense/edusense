# Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
# Use of this source code is governed by BSD 3-clause license.

import numpy as np
import cv2

threshold_detection = 0.5


def render_pose(key_pts, scale_w, scale_h):
    vertex = []
    lines = []
    for key_pt in key_pts:
        for pt in key_pt:
            if pt[0] != 0 and pt[1] != 0 and pt[2] > threshold_detection:
                vertex.append((pt[0]*scale_w, pt[1]*scale_h))
        line_draw = [[1, 2, 3, 4], [1, 5, 6, 7], [1, 8, 9, 10],
                     [1, 11, 12, 13], [1, 0, 14, 16], [0, 15, 17]]
        for limbs in line_draw:
            for i in range(0, len(limbs)-1):
                if key_pt[limbs[i]][0] != 0 and key_pt[limbs[i]][1] != 0 and key_pt[limbs[i]][2] > threshold_detection:
                    if key_pt[limbs[i+1]][0] != 0 and key_pt[limbs[i+1]][1] != 0 and key_pt[limbs[i+1]][2] > threshold_detection:
                        p1 = key_pt[limbs[i]][:2]
                        p2 = key_pt[limbs[i+1]][:2]
                        lines.append(
                            ((int(p1[0]*scale_w), int(p1[1]*scale_h)), (int(p2[0]*scale_w), int(p2[1]*scale_h))))
    return vertex, lines


def render_pose_scale(key_pts, scale_w, scale_h):
    vertex = []
    lines = []
    x_pts = []
    y_pts = []
    for key_pt in key_pts:
        for pt in key_pt:
            if pt[0] != 0 and pt[1] != 0 and pt[2] > threshold_detection:
                x_pts.append(pt[0])
                y_pts.append(pt[1])
                vertex.append((pt[0]*scale_w, pt[1]*scale_h))
        line_draw = [[1, 2, 3, 4], [1, 5, 6, 7], [1, 8, 9, 10],
                     [1, 11, 12, 13], [1, 0, 14, 16], [0, 15, 17]]
        for limbs in line_draw:
            for i in range(0, len(limbs)-1):
                if key_pt[limbs[i]][0] != 0 and key_pt[limbs[i]][1] != 0 and key_pt[limbs[i]][2] > threshold_detection:
                    if key_pt[limbs[i+1]][0] != 0 and key_pt[limbs[i+1]][1] != 0 and key_pt[limbs[i+1]][2] > threshold_detection:
                        p1 = key_pt[limbs[i]][:2]
                        p2 = key_pt[limbs[i+1]][:2]
                        try:
                            p_1_x = (p1[0] - min(x_pts)) / \
                                float(max(x_pts) - min(x_pts))
                            p_1_y = (p1[1] - min(y_pts)) / \
                                float(max(y_pts) - min(y_pts))
                            p_2_x = (p2[0] - min(x_pts)) / \
                                float(max(x_pts) - min(x_pts))
                            p_2_y = (p2[1] - min(y_pts)) / \
                                float(max(y_pts) - min(y_pts))
                            p_1_x = 0.1 + (0.8*p_1_x)
                            p_2_x = 0.1 + (0.8*p_2_x)
                            p_1_y = 0.1 + (0.8*p_1_y)
                            p_2_y = 0.1 + (0.8*p_2_y)
                            lines.append(
                                ((int(p_1_x*scale_w), int(p_1_y*scale_h)), (int(p_2_x*scale_w), int(p_2_y*scale_h))))
                        except:
                            continue
    return vertex, lines


def render_pose_scale_3d(key_pts, vis, scale_w, scale_h):
    lines = []
    x_pts = []
    y_pts = []
    z_pts = []
    key_pt = []
    key_ptz = key_pts[0]
    viz = vis[0]
    for i in range(len(key_ptz[0])):
        key_pt.append((key_ptz[0][i], key_ptz[1][i], key_ptz[2][i], viz[i]))
        if viz[i] == True:
            x_pts.append(key_ptz[0][i])
            y_pts.append(key_ptz[1][i])
            z_pts.append(key_ptz[2][i])
    line_draw = [[0, 1], [1, 2], [2, 3], [3, 4], [1, 5], [5, 6], [
        6, 7], [1, 8], [8, 9], [9, 10], [1, 11], [11, 12], [12, 13]]
    for limbs in line_draw:
        for i in range(0, len(limbs)-1):
            if key_pt[limbs[i]][3] == True:
                if key_pt[limbs[i+1]][3] == True:
                    p1 = key_pt[limbs[i]][:3]
                    p2 = key_pt[limbs[i+1]][:3]
                    try:
                        p_1_x = (p1[0] - min(x_pts)) / \
                            float(max(x_pts) - min(x_pts))
                        p_1_y = (p1[1] - min(y_pts)) / \
                            float(max(y_pts) - min(y_pts))
                        p_1_z = (p1[2] - min(z_pts)) / \
                            float(max(z_pts) - min(z_pts))
                        p_2_x = (p2[0] - min(x_pts)) / \
                            float(max(x_pts) - min(x_pts))
                        p_2_y = (p2[1] - min(y_pts)) / \
                            float(max(y_pts) - min(y_pts))
                        p_2_z = (p2[2] - min(z_pts)) / \
                            float(max(z_pts) - min(z_pts))
                        p_1_x = 0.1 + (0.8*p_1_x)
                        p_2_x = 0.1 + (0.8*p_2_x)
                        p_1_y = 0.1 + (0.8*p_1_y)
                        p_2_y = 0.1 + (0.8*p_2_y)
                        p_1_z = 0.1 + (0.8*p_1_z)
                        p_2_z = 0.1 + (0.8*p_2_z)
                        lines.append(((int(p_1_x*scale_w), int(p_1_y*scale_h), int(p_1_z*-100)),
                                      (int(p_2_x*scale_w), int(p_2_y*scale_h), int(p_2_z*-100))))
                    except:
                        continue
    return lines


def render_face_scale(key_pts, scale_w, scale_h):
    vertex = []
    lines = []
    x_pts = []
    y_pts = []
    for key_pt in key_pts:
        for pt in key_pt:
            if pt[0] != 0 and pt[1] != 0 and pt[2] > threshold_detection:
                x_pts.append(pt[0])
                y_pts.append(pt[1])
                vertex.append((pt[0]*scale_w, pt[1]*scale_h))
        line_draw = [[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [48, 49, 50, 51, 52,
                                                             53, 54, 55, 56, 57, 58, 59, 48], [60, 61, 62, 63, 64, 65, 66, 67, 60]]
        for limbs in line_draw:
            for i in range(0, len(limbs)-1):
                if key_pt[limbs[i]][0] != 0 and key_pt[limbs[i]][1] != 0 and key_pt[limbs[i]][2] > threshold_detection:
                    if key_pt[limbs[i+1]][0] != 0 and key_pt[limbs[i+1]][1] != 0 and key_pt[limbs[i+1]][2] > threshold_detection:
                        p1 = key_pt[limbs[i]][:2]
                        p2 = key_pt[limbs[i+1]][:2]
                        try:
                            p_1_x = (p1[0] - min(x_pts)) / \
                                float(max(x_pts) - min(x_pts))
                            p_1_y = (p1[1] - min(y_pts)) / \
                                float(max(y_pts) - min(y_pts))
                            p_2_x = (p2[0] - min(x_pts)) / \
                                float(max(x_pts) - min(x_pts))
                            p_2_y = (p2[1] - min(y_pts)) / \
                                float(max(y_pts) - min(y_pts))
                            p_1_x = 0.1 + (0.8*p_1_x)
                            p_2_x = 0.1 + (0.8*p_2_x)
                            p_1_y = 0.1 + (0.8*p_1_y)
                            p_2_y = 0.1 + (0.8*p_2_y)
                            lines.append(
                                ((int(p_1_x*scale_w), int(p_1_y*scale_h)), (int(p_2_x*scale_w), int(p_2_y*scale_h))))
                        except:
                            continue
    return vertex, lines


def render_hands_scale(key_pts, scale_w, scale_h):
    sp_threshold_detection = 0
    vertex = []
    lines = []
    x_pts = []
    y_pts = []
    for key_pt in key_pts:
        for pt in key_pt:
            if pt[0] != 0 and pt[1] != 0 and pt[2] > sp_threshold_detection:
                x_pts.append(pt[0])
                y_pts.append(pt[1])
                vertex.append((pt[0]*scale_w, pt[1]*scale_h))
        line_draw = [[0, 17, 18, 19, 20], [0, 13, 14, 14, 15, 16], [
            0, 9, 10, 11, 12], [0, 5, 6, 7, 8], [0, 1, 2, 3, 4], [2, 5, 9, 13, 17]]
        for limbs in line_draw:
            for i in range(0, len(limbs)-1):
                if key_pt[limbs[i]][0] != 0 and key_pt[limbs[i]][1] != 0 and key_pt[limbs[i]][2] > sp_threshold_detection:
                    if key_pt[limbs[i+1]][0] != 0 and key_pt[limbs[i+1]][1] != 0 and key_pt[limbs[i+1]][2] > sp_threshold_detection:
                        p1 = key_pt[limbs[i]][:2]
                        p2 = key_pt[limbs[i+1]][:2]
                        try:
                            p_1_x = (p1[0] - min(x_pts)) / \
                                float(max(x_pts) - min(x_pts))
                            p_1_y = (p1[1] - min(y_pts)) / \
                                float(max(y_pts) - min(y_pts))
                            p_2_x = (p2[0] - min(x_pts)) / \
                                float(max(x_pts) - min(x_pts))
                            p_2_y = (p2[1] - min(y_pts)) / \
                                float(max(y_pts) - min(y_pts))
                            p_1_x = 0.1 + (0.8*p_1_x)
                            p_2_x = 0.1 + (0.8*p_2_x)
                            p_1_y = 0.1 + (0.8*p_1_y)
                            p_2_y = 0.1 + (0.8*p_2_y)
                            lines.append(
                                ((int(p_1_x*scale_w), int(p_1_y*scale_h)), (int(p_2_x*scale_w), int(p_2_y*scale_h))))
                        except:
                            continue
    return vertex, lines


def render_face(key_pts, scale_w, scale_h):
    vertex = []
    lines = []
    for key_pt in key_pts:
        for pt in key_pt:
            if pt[0] != 0 and pt[1] != 0 and pt[2] > threshold_detection:
                vertex.append((pt[0]*scale_w, pt[1]*scale_h))
        line_draw = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], [17, 18, 19, 20, 21], [22, 23, 24, 25, 26], [27, 28, 29, 30], [31, 32, 33, 34, 35], [
            36, 37, 38, 39, 40, 41, 36], [42, 43, 44, 45, 46, 47, 42], [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 48], [60, 61, 62, 63, 64, 65, 66, 67, 60]]
        for limbs in line_draw:
            for i in range(0, len(limbs)-1):
                if key_pt[limbs[i]][0] != 0 and key_pt[limbs[i]][1] != 0 and key_pt[limbs[i]][2] > threshold_detection:
                    if key_pt[limbs[i+1]][0] != 0 and key_pt[limbs[i+1]][1] != 0 and key_pt[limbs[i+1]][2] > threshold_detection:
                        p1 = key_pt[limbs[i]][:2]
                        p2 = key_pt[limbs[i+1]][:2]
                        lines.append(
                            ((int(p1[0]*scale_w), int(p1[1]*scale_h)), (int(p2[0]*scale_w), int(p2[1]*scale_h))))
    return vertex, lines


def render_hands(key_pts, scale_w, scale_h):
    vertex = []
    lines = []
    for key_pt in key_pts:
        for pt in key_pt:
            if pt[0] != 0 and pt[1] != 0 and pt[2] > threshold_detection:
                vertex.append((pt[0]*scale_w, pt[1]*scale_h))
        line_draw = [[0, 17, 18, 19, 20], [0, 13, 14, 14, 15, 16],
                     [0, 9, 10, 11, 12], [0, 5, 6, 7, 8], [0, 1, 2, 3, 4]]
        for limbs in line_draw:
            for i in range(0, len(limbs)-1):
                if key_pt[limbs[i]][0] != 0 and key_pt[limbs[i]][1] != 0 and key_pt[limbs[i]][2] > threshold_detection:
                    if key_pt[limbs[i+1]][0] != 0 and key_pt[limbs[i+1]][1] != 0 and key_pt[limbs[i+1]][2] > threshold_detection:
                        p1 = key_pt[limbs[i]][:2]
                        p2 = key_pt[limbs[i+1]][:2]
                        lines.append(
                            ((int(p1[0]*scale_w), int(p1[1]*scale_h)), (int(p2[0]*scale_w), int(p2[1]*scale_h))))
    return vertex, lines


def render_pose_draw(key_pts, frame, color_pose, color_legs):
    for key_pt in key_pts:
        line_draw = [[1, 2, 3, 4], [1, 5, 6, 7]]
        for limbs in line_draw:
            for i in range(0, len(limbs)-1):
                if key_pt[limbs[i]][0] != 0 and key_pt[limbs[i]][1] != 0:
                    if key_pt[limbs[i+1]][0] != 0 and key_pt[limbs[i+1]][1] != 0:
                        p1 = key_pt[limbs[i]][:2]
                        p2 = key_pt[limbs[i+1]][:2]
                        cv2.line(frame, (int(p1[0]), int(p1[1])), (int(
                            p2[0]), int(p2[1])), color_pose, 3, 16)
        line_draw = [[1, 8, 9, 10, 11], [8, 12, 13, 14]]
        for limbs in line_draw:
            for i in range(0, len(limbs)-1):
                if key_pt[limbs[i]][0] != 0 and key_pt[limbs[i]][1] != 0:
                    if key_pt[limbs[i+1]][0] != 0 and key_pt[limbs[i+1]][1] != 0:
                        p1 = key_pt[limbs[i]][:2]
                        p2 = key_pt[limbs[i+1]][:2]
                        cv2.line(frame, (int(p1[0]), int(p1[1])), (int(
                            p2[0]), int(p2[1])), color_legs, 3, 16)
    return frame


def render_face_draw(key_pts, frame):
    for key_pt in key_pts:
        for pt in key_pt:
            if pt[0] != 0 and pt[1] != 0 and pt[2] > threshold_detection:
                cv2.circle(frame, (int(pt[0]), int(pt[1])), 3, [
                           255, 255, 255], -1)
        line_draw = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], [17, 18, 19, 20, 21], [22, 23, 24, 25, 26], [27, 28, 29, 30], [31, 32, 33, 34, 35], [
            36, 37, 38, 39, 40, 41, 36], [42, 43, 44, 45, 46, 47, 42], [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 48], [60, 61, 62, 63, 64, 65, 66, 67, 60]]
        for limbs in line_draw:
            for i in range(0, len(limbs)-1):
                if key_pt[limbs[i]][0] != 0 and key_pt[limbs[i]][1] != 0 and key_pt[limbs[i]][2] > threshold_detection:
                    if key_pt[limbs[i+1]][0] != 0 and key_pt[limbs[i+1]][1] != 0 and key_pt[limbs[i+1]][2] > threshold_detection:
                        p1 = key_pt[limbs[i]][:2]
                        p2 = key_pt[limbs[i+1]][:2]
                        cv2.line(frame, (int(p1[0]), int(p1[1])), (int(
                            p2[0]), int(p2[1])), [255, 255, 255], 2, 16)
    return frame


def render_hands_draw(key_pts, frame):
    for key_pt in key_pts:
        for pt in key_pt:
            if pt[0] != 0 and pt[1] != 0 and pt[2] > threshold_detection:
                cv2.circle(frame, (int(pt[0]), int(pt[1])), 3, [
                           255, 255, 255], -1)
        line_draw = [[0, 17, 18, 19, 20], [0, 13, 14, 14, 15, 16],
                     [0, 9, 10, 11, 12], [0, 5, 6, 7, 8], [0, 1, 2, 3, 4]]
        for limbs in line_draw:
            for i in range(0, len(limbs)-1):
                if key_pt[limbs[i]][0] != 0 and key_pt[limbs[i]][1] != 0 and key_pt[limbs[i]][2] > threshold_detection:
                    if key_pt[limbs[i+1]][0] != 0 and key_pt[limbs[i+1]][1] != 0 and key_pt[limbs[i+1]][2] > threshold_detection:
                        p1 = key_pt[limbs[i]][:2]
                        p2 = key_pt[limbs[i+1]][:2]
                        cv2.line(frame, (int(p1[0]), int(p1[1])), (int(
                            p2[0]), int(p2[1])), [255, 255, 255], 2, 16)
    return frame


def mean_point(p1, p2):
    return ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)


def get_shirt_color(frame, pose):
    try:
        p1 = (pose[1][0], pose[1][1])
        p2 = (pose[8][0], pose[8][1])
        p3 = (pose[11][0], pose[11][1])
        if p1[0] == 0 or p1[1] == 0 or p2[0] == 0 or p2[1] == 0 or p3[0] == 0 or p3[1] == 0:
            return [21, 30, 189], None
        p4 = mean_point(p2, p3)
        p_mid = mean_point(p1, p4)
        crop_img = frame[int(p_mid[1]-50):int(p_mid[1]+50),
                         int(p_mid[0]-50):int(p_mid[0]+50)]
        pts = [p_mid]
        color = []
        for pt in pts:
            for tx in range(-25, 25):
                for ty in range(-25, 25):
                    color.append(frame[int(pt[1]) + tx, int(pt[0]) + ty])
        clr = np.mean(np.array(color), axis=0)
        return clr, crop_img
    except:
        return [21, 30, 189], None


def get_pant_color(frame, pose):
    try:
        p1 = (pose[8][0], pose[8][1])
        p2 = (pose[9][0], pose[9][1])
        p3 = (pose[11][0], pose[11][1])
        p4 = (pose[12][0], pose[12][1])
        if p1[0] == 0 or p1[1] == 0 or p2[0] == 0 or p2[1] == 0 or p3[0] == 0 or p3[1] == 0 or p4[0] == 0 or p4[1] == 0:
            return [189, 96, 21], None
        p_1 = mean_point(p1, p2)
        p_2 = mean_point(p3, p4)
        crop_img = frame[int(p_1[1]-25):int(p_1[1]+25),
                         int(p_1[0]-25):int(p_1[0]+25)]
        pts = [p_1, p_2]
        color = []
        for pt in pts:
            for tx in range(-5, 5):
                for ty in range(-5, 5):
                    color.append(frame[int(pt[1]) + tx, int(pt[0]) + ty])
        clr = np.mean(np.array(color), axis=0)
        return clr, crop_img
    except:
        return [189, 96, 21], None


def get_skin_color(frame, pose):
    try:
        color = []
        p1 = (pose[0][0], pose[0][1])
        p2 = (pose[1][0], pose[1][1])
        if p1[0] == 0 or p1[1] == 0 or p2[0] == 0 or p2[1] == 0:
            return [148, 205, 255]
        p_1 = mean_point(p1, p2)
        pts = [p_1]
        color = []
        for pt in pts:
            for tx in range(-5, 5):
                for ty in range(-5, 5):
                    color.append(frame[int(pt[1]) + tx, int(pt[0]) + ty])
        clr = np.mean(np.array(color), axis=0)
        return clr
    except:
        return [148, 205, 255]


def get_master_plot_points(master_legend, source_ip):
    ip_provider = master_legend[:, 2]
    ip_provider_unique = set(ip_provider)
