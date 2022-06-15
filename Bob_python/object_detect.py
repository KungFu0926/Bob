import cv2

from Bob.visual.monitor.concrete.crt_camera import CameraMonitor
from Bob.visual.detector.concrete.object_detect_yolov5 import ObjectDetector
from Bob.visual.monitor.framework.fw_monitor import CameraListener
from Bob.visual.utils import visual_utils


class TestListener(CameraListener):

    def onImageRead(self, image):
        cv2.imshow("object", image)

    def onDetect(self, detector_id, image, data):
        if detector_id == 1:
            labeledImage = image
            for result in data:
                label = result['name'] + " " + str(round(result['conf'], 2))
                labeledImage = visual_utils.annotateLabel(labeledImage, (result['x']['min'], result['y']['min']),
                                                          (result['x']['max'], result['y']['max']), label, False)
            cv2.imshow("object", labeledImage)


monitor = CameraMonitor(0)
monitor.registerDetector(ObjectDetector(1, conf=0.65), False)
monitor.setDetectorEnable(1, True)
monitor.setListener(TestListener())
monitor.start()
