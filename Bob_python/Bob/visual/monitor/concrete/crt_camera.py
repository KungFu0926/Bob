import cv2

from Bob.visual.monitor.framework.fw_monitor import VideoMonitor


class CameraMonitor(VideoMonitor):

    def __init__(self, device: int):
        super().__init__()
        self.__webcam = cv2.VideoCapture(device)

    def run(self):
        while self.isOpen():
            ret, frame = self.__webcam.read()
            if not ret:
                continue
            if not self._listener is None:
                self._listener.onImageRead(frame)

            self._detect(frame)

            cv2.waitKey(1)
        self.__webcam.release()
