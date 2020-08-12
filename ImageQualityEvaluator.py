import cv2
import math
import numpy as np


class ImageQualityEvaluator:
    def __init__(self, model_path: str, range_path: str, image1_path: str, image2_path: str, skala: int):
        self.model_path = model_path    # brisque model path
        self.range_path = range_path    # brisque model path
        self.image1 = cv2.imread(image1_path)
        self.width = int(math.ceil(self.image1.shape[1] * skala / 100))     # width and height of input image
        self.height = int(math.ceil(self.image1.shape[0] * skala / 100))
        self.dim = (self.width, self.height)
        self.results = {'BRISQUE': None, 'MSE': None, 'PSNR': None, 'SSIM': None, 'GMSD': None}
        self.maps = {'MSE': None, 'PSNR': None, 'SSIM': None, 'GMSD': None}  # dict definition for optional usage of
        # quality maps coming from cv2.quality
        if self.image1 is not None:
            self.image1 = cv2.resize(self.image1, self.dim, interpolation=cv2.INTER_AREA)   # scalling image
        self.image2 = cv2.imread(image2_path)   # load 2nd image for comparison

    def brisque(self):  # brisque quality metric
        result_static = cv2.quality.QualityBRISQUE_compute(self.image2, self.model_path, self.range_path)
        res = np.array(list(result_static))
        result_static = res[0]

        return result_static

    def mse(self):  # mse quality metric
        result_static, quality_map = cv2.quality.QualityMSE_compute(self.image1, self.image2)
        res = np.array(list(result_static))
        result_static = np.mean(res[:-1])

        return result_static, quality_map

    def psnr(self):  # brisque quality metric
        result_static, quality_map = cv2.quality.QualityPSNR_compute(self.image1, self.image2)
        res = np.array(list(result_static))
        result_static = np.mean(res[:-1])

        return result_static, quality_map

    def ssim(self):  # ssim quality metric
        result_static, quality_map = cv2.quality.QualitySSIM_compute(self.image1, self.image2)
        res = np.array(list(result_static))
        result_static = np.mean(res[:-1])

        return result_static, quality_map

    def gmsd(self):  # gmsd quality metric
        result_static, quality_map = cv2.quality.QualityGMSD_compute(self.image1, self.image2)
        res = np.array(list(result_static))
        result_static = np.mean(res[:-1])

        return result_static, quality_map

    def generateResults(self, opcja: int):
        if opcja < 1:
            return None, None
        if opcja == 1 or opcja == 2:
            self.results['BRISQUE'] = self.brisque()
        if opcja == 1 or opcja == 3:
            self.results['MSE'], self.maps['MSE'] = self.mse()

        if opcja == 1 or opcja == 4:
            self.results['PSNR'], self.maps['PSNR'] = self.psnr()

        if opcja == 1 or opcja == 5:
            self.results['SSIM'], self.maps['SSIM'] = self.ssim()

        if opcja == 1 or opcja == 6:
            self.results['GMSD'], self.maps['GMSD'] = self.gmsd()

        return self.results
