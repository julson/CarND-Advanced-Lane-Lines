# Calculates a set of object points to be used for camera calibration

import argparse
import glob
import os
import cv2
import pickle
import numpy as np

parser = argparse.ArgumentParser(description='Calculate points for camera calibration')
parser.add_argument('dest', default='dist_pickle.p', nargs='?', help='output pickle file')
parser.add_argument('--debug', dest='debug', action='store_true', help='creates a set of images with the detected corners drawn in ./out/calibration')
args = parser.parse_args()

objgrid = np.zeros((9*6, 3), np.float32)
objgrid[:,:2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)

objpts = [] # 3D points in real-world space
imgpts = [] # 2D points in image plane

images = glob.glob('camera_cal/calibration*.jpg')

for idx, filename in enumerate(images):
    print('Extracting corners from ' + filename)
    img = cv2.imread(filename)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (9, 6), None)

    if ret == True:
        objpts.append(objgrid)
        imgpts.append(corners)

        if args.debug == True:
            os.makedirs('out/calibration', exist_ok=True)
            cv2.drawChessboardCorners(img, (9, 6), corners, ret)
            cv2.imwrite('out/calibration/calibration{}.jpg'.format(idx), img)

if len(objpts) > 0 and len(imgpts) > 0:
    print('Writing to pickle file ' + args.dest)
    dist_pickle = {}
    dist_pickle['objectpoints'] = objpts
    dist_pickle['imagepoints'] = imgpts
    pickle.dump(dist_pickle, open(args.dest, 'wb'))
