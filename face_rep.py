import cv2
import dlib
import numpy as np
import os
import sys
import time
import pdb

 
class FACEREP(object):
    def __init__(self, options, logger):
        self.options = options
        self.logger = logger
        self.predictor = dlib.shape_predictor(options['predictor'])
        self. detector = dlib.get_frontal_face_detector()
        self.scale_factor = 1 
        self.feather_amount = 11
        # Amount of blur to use during colour correction, as a fraction of the
        # pupillary distance.
        self.colour_correct_blur_frac = 0.6

        FACE_POINTS = list(range(17, 68))
        MOUTH_POINTS = list(range(48, 61))
        RIGHT_BROW_POINTS = list(range(17, 22))
        LEFT_BROW_POINTS = list(range(22, 27))
        RIGHT_EYE_POINTS = list(range(36, 42))
        LEFT_EYE_POINTS = list(range(42, 48))
        NOSE_POINTS = list(range(27, 35))
        JAW_POINTS = list(range(0, 17))   
        self.left_eye_points = LEFT_EYE_POINTS
        self.right_eye_points = RIGHT_EYE_POINTS
        # Points used to line up the images.
        self.align_points = (LEFT_BROW_POINTS + RIGHT_EYE_POINTS + LEFT_EYE_POINTS + RIGHT_BROW_POINTS + NOSE_POINTS + MOUTH_POINTS)
         
        # Points from the second image to overlay on the first. The convex hull of each
        # element will be overlaid.
        # overlay_points = [
        #     LEFT_EYE_POINTS + RIGHT_EYE_POINTS + LEFT_BROW_POINTS + RIGHT_BROW_POINTS,
        #     NOSE_POINTS + MOUTH_POINTS,
        # ]
        self.overlay_points = [ LEFT_BROW_POINTS + RIGHT_EYE_POINTS + LEFT_EYE_POINTS + RIGHT_BROW_POINTS + NOSE_POINTS + MOUTH_POINTS, ]
         

    def get_landmarks(self, im):
        rects = self.detector(im, 1)
        if len(rects) > 1:
            raise "TooManyFaces"
        if len(rects) == 0:
            raise "NoFaces"
        return np.matrix([[p.x, p.y] for p in self.predictor(im, rects[0]).parts()])
     
    def annotate_landmarks(self, im, landmarks):
        im = im.copy()
        for idx, point in enumerate(landmarks):
            pos = (point[0, 0], point[0, 1])
            cv2.putText(im, str(idx), pos,
                        fontFace=cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                        fontScale=0.4,
                        color=(0, 0, 255))
            cv2.circle(im, pos, 3, color=(0, 255, 255))
        return im
     
    def draw_convex_hull(self, im, points, color):
        points = cv2.convexHull(points)
        cv2.fillConvexPoly(im, points, color=color)
     
    def get_face_mask(self, im, landmarks):
        im = np.zeros(im.shape[:2], dtype=np.float64)
        for group in self.overlay_points:
            self.draw_convex_hull(im, landmarks[group], color=1) 
        im = np.array([im, im, im]).transpose((1, 2, 0))
        im = (cv2.GaussianBlur(im, (self.feather_amount, self.feather_amount), 0) > 0) * 1.0
        im = cv2.GaussianBlur(im, (self.feather_amount, self.feather_amount), 0)
        return im
     
     #@return： transformation matrix
    def transformation_from_points(self, points1, points2):
        """
        Return an affine transformation [s * R | T] such that:
            sum ||s*R*p1,i + T - p2,i||^2
        is minimized.
        """
        # Solve the procrustes problem by subtracting centroids, scaling by the
        # standard deviation, and then using the SVD to calculate the rotation. See
        # the following for more details:
        #   https://en.wikipedia.org/wiki/Orthogonal_Procrustes_problem
     
        points1 = points1.astype(np.float64)
        points2 = points2.astype(np.float64)
     
        c1 = np.mean(points1, axis=0)
        c2 = np.mean(points2, axis=0)
        points1 -= c1
        points2 -= c2
     
        s1 = np.std(points1)
        s2 = np.std(points2)
        points1 /= s1
        points2 /= s2
     
        U, S, Vt = np.linalg.svd(points1.T * points2)
     
        # The R we seek is in fact the transpose of the one given by U * Vt. This
        # is because the above formulation assumes the matrix goes on the right
        # (with row vectors) where as our solution requires the matrix to be on the
        # left (with column vectors).
        R = (U * Vt).T
     
        return np.vstack([np.hstack(((s2 / s1) * R,
                                           c2.T - (s2 / s1) * R * c1.T)),
                             np.matrix([0., 0., 1.])])
     
    def read_im_and_landmarks(self, fname):
        im = cv2.imread(fname, cv2.IMREAD_COLOR)
        im = cv2.resize(im, (im.shape[1] * self.scale_factor,
                             im.shape[0] * self.scale_factor))
        s = self.get_landmarks(im)
     
        return im, s
     
    def warp_im(self, im, M, dshape):
        output_im = np.zeros(dshape, dtype=im.dtype)
        cv2.warpAffine(im,
                       M[:2],
                       (dshape[1], dshape[0]),
                       dst=output_im,
                       borderMode=cv2.BORDER_TRANSPARENT,
                       flags=cv2.WARP_INVERSE_MAP)
        return output_im
     
    def correct_colours(self, base_image, target_image, base_landmarks):
        blur_amount = self.colour_correct_blur_frac * np.linalg.norm(
                                  np.mean(base_landmarks[self.left_eye_points], axis=0) -
                                  np.mean(base_landmarks[self.right_eye_points], axis=0))
        blur_amount = int(blur_amount)
        if blur_amount % 2 == 0:
            blur_amount += 1
        base_image_blur = cv2.GaussianBlur(base_image, (blur_amount, blur_amount), 0)
        target_image_blur = cv2.GaussianBlur(target_image, (blur_amount, blur_amount), 0)
        
        # pdb.set_trace()
        # Avoid divide-by-zero errors.
        target_image_blur = np.add(target_image_blur, 128 * (target_image_blur <= 1.0))
     
        return (target_image.astype(np.float64) * base_image_blur.astype(np.float64) /
                                                    target_image_blur.astype(np.float64))
     
    def process(self):
        base_image, base_landmarks = self.read_im_and_landmarks(self.options['base'])
        target_image, target_landmarks = self.read_im_and_landmarks(self.options['target'])
         
        M =self. transformation_from_points(base_landmarks[self.align_points], target_landmarks[self.align_points])
         
        mask = self.get_face_mask(target_image, target_landmarks)
        warped_mask = self.warp_im(mask, M, base_image.shape)
        combined_mask = np.max([self.get_face_mask(base_image, base_landmarks), warped_mask], axis=0)
         
        warped_target_image = self.warp_im(target_image, M, base_image.shape)
        warped_corrected_target_image = self.correct_colours(base_image, warped_target_image, base_landmarks)

        output_im = base_image * (1.0 - combined_mask) + warped_corrected_target_image * combined_mask

        timestamp = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        outpath = os.path.join(self.options['output'],'%s_output.jpg'%timestamp)
        cv2.imwrite(outpath, output_im)
        return outpath


if __name__ == '__main__':  
      import time
      import logging
      from argparse import ArgumentParser
    
      parser = ArgumentParser(description='fileName')
      parser.add_argument("--version", action="version", version="fileName 1.0")
      parser.add_argument("-b", "--base", action="store", dest="base", default="", help='base image')
      parser.add_argument("-t", "--target", action="store", dest="target", default="", help='target image')
      parser.add_argument("-p", "--pred", action="store", dest="predictor", default=r"D:\Documents\GitHub\Tools\model\shape_predictor_68_face_landmarks.dat", help='predictor path')
      parser.add_argument("-l", "--log", type=str, action="store", dest="report", default="report.txt", help='output file')
      parser.add_argument("-o", "--output", type=str, action="store", dest="output", default="", help='output path')
    
      args = parser.parse_args()
      options = vars(args)
    
      logger = logging.getLogger()
      formatter = logging.Formatter('[%(asctime)s][*%(levelname)s*][%(filename)s:%(lineno)d|%(funcName)s] - %(message)s', '%Y%m%d-%H:%M:%S')
      file_handler = logging.FileHandler('LOG-FACEREP.txt', 'w','utf-8')
      file_handler.setFormatter(formatter)
      logger.addHandler(file_handler)
    
      stream_handler = logging.StreamHandler()
      stream_handler.setFormatter(formatter)
      logger.addHandler(stream_handler)
      logger.setLevel(logging.INFO)
    
      allStartTP = time.time()
      appInst = FACEREP(options, logger)
      outpath = appInst.process()
      allEndTP = time.time()
      os.system("%s"%options['base'])
      os.system("%s"%options['target'])
      os.system("%s"%outpath)
      logger.info("Operation Finished [Time Cost:%0.3f Seconds]" % float(allEndTP - allStartTP))
    
    