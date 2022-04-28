import yolov5.detect
from Bob.detector.framework.detector import Detector, DetectListener


class ObjectDetector(Detector):

    def __init__(self, listener: DetectListener):
        super().__init__(listener)
        self.listener = listener

    def _detect(self):
        yolo = yolov5.detect.Yolo()
        yolo.run(source=0, listener=self.listener)
