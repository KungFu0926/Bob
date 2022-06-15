import cv2

from Bob.visual.monitor.concrete.crt_camera import CameraMonitor
#Must Import before deepface
from Bob.visual.detector.concrete.object_detect_yolov5 import ObjectDetector
# Must Import after yolov5
from Bob.visual.detector.concrete.face_detect_deepface import FaceDetector
from Bob.visual.monitor.framework.fw_monitor import CameraListener
from Bob.visual.utils import visual_utils


class TestListener(CameraListener):

    def onImageRead(self, image):
        cv2.imshow("face", image)
        cv2.imshow("object", image)

    def onDetect(self, detector_id, image, data):
        if detector_id == 1:
            labeledImage = image
            for result in data:
                label = result['emotion']
                labeledImage = visual_utils.annotateLabel(labeledImage, (result['x']['min'], result['y']['min']),
                                                          (result['x']['max'], result['y']['max']), label,
                                                          overwrite=False)
            cv2.imshow("face", labeledImage)
        elif detector_id == 2:
            labeledImage = image
            for result in data:
                label = result['name'] + " " + str(round(result['conf'], 2))
                labeledImage = visual_utils.annotateLabel(image, (result['x']['min'], result['y']['min']),
                                                          (result['x']['max'], result['y']['max']), label,
                                                          overwrite=False)
            cv2.imshow("object", labeledImage)


monitor = CameraMonitor(0)
monitor.registerDetector(FaceDetector(1), False)
monitor.registerDetector(ObjectDetector(2), False)
monitor.setDetectorEnable(1, True)
monitor.setDetectorEnable(2, True)

monitor.setListener(TestListener())
monitor.start()

# while True:
#     ret, frame = cam.read()
#     face_detector.detect(frame)
#
#     for result in face_detector.detect(frame):
#         label = result['emotion']
#         visual_utils.annotateLabel(frame, (result['x']['min'], result['y']['min']),
#                                    (result['x']['max'], result['y']['max']), label)
#     cv2.imshow("result", frame)
#     cv2.waitKey(1)
