from Bob.bluetooth_utils.utils import BluetoothServer, ClientConnectionListener
from Bob.function_listener import FunctionListener
from Bob.visual.detector.concrete.face_detect_deepface import FaceDetector
from Bob.visual.detector.concrete.object_detect_yolov5 import ObjectDetector
from Bob.visual.monitor.concrete.crt_camera import CameraMonitor
from device_config import getSocketBluetooth, getRobot


class ConnectListener(ClientConnectionListener):

    def __init__(self):
        self.__robot = getRobot()
        self.__robot.open()
        self.__robot.enableAllServos(True)
        self.camera_monitor = CameraMonitor(0)
        self.camera_monitor.registerDetector(FaceDetector(1), False)
        self.camera_monitor.registerDetector(ObjectDetector(2, conf=0.4), False)
        self.camera_monitor.start()

    def onConnected(self, socket):
        print("Monitor start")
        package_device = getSocketBluetooth(socket)
        listener = FunctionListener(package_device, self.camera_monitor, self.__robot)
        self.camera_monitor.setListener(listener)
        package_device.setListener(listener)
        package_device.start()


class MainProgram:
    @staticmethod
    def main():
        try:
            server = BluetoothServer(ConnectListener())
            server.start()

        except (KeyboardInterrupt, SystemExit):
            print("Interrupted!!")


if __name__ == '__main__':
    MainProgram.main()
