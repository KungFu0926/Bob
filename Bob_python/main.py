"""Run inference with a YOLOv5 model on images, videos, directories, streams

Usage:
    $ python path/to/object_detect.py --source path/to/img.jpg --weights yolov5s.pt --img 640
"""
from Bob.function_listener import FunctionListener
from Bob.visual.detector.concrete.face_detect_deepface import FaceDetector
from Bob.visual.detector.concrete.object_detect_yolov5 import ObjectDetector
from Bob.visual.monitor.concrete.crt_camera import CameraMonitor
from device_config import getSerialBluetooth, getRobot


class MainProgram:
    @staticmethod
    def main():
        try:
            robot = getRobot()
            robot.open()
            robot.enableAllServos(True)

            camera_monitor = CameraMonitor(0)

            camera_monitor.registerDetector(FaceDetector(1), False)
            camera_monitor.registerDetector(ObjectDetector(2, conf=0.4), False)
            package_device = getSerialBluetooth()
            listener = FunctionListener(package_device, camera_monitor, robot)
            package_device.setListener(listener)
            camera_monitor.setListener(listener)
            package_device.start()
            camera_monitor.start()
        except (KeyboardInterrupt, SystemExit):
            print("Interrupted!!")


if __name__ == '__main__':
    MainProgram.main()
