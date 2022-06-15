import cv2

from Bob.visual.monitor.concrete.crt_camera import CameraMonitor
from Bob.visual.detector.concrete.face_detect_deepface import FaceDetector
from Bob.visual.monitor.framework.fw_monitor import CameraListener
from Bob.visual.utils import visual_utils


class TestListener(CameraListener):

    def onImageRead(self, image):
        cv2.imshow("face", image)

    def onDetect(self, detector_id, image, data):
        if detector_id == 1:
            labeledImage = image
            for result in data:
                label = result['emotion']
                labeledImage = visual_utils.annotateLabel(labeledImage, (result['x']['min'], result['y']['min']),
                                                          (result['x']['max'], result['y']['max']), label,
                                                          overwrite=False)
            cv2.imshow("face", labeledImage)


monitor = CameraMonitor(0)
monitor.registerDetector(FaceDetector(1), False)
monitor.setDetectorEnable(1, True)
monitor.setListener(TestListener())
monitor.start()
