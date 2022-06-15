import json
import os
import threading
import time
from typing import Optional

import cv2

from Bob.communication.framework.fw_package_device import PackageListener, PackageDevice
from Bob.dbctrl.concrete.crt_database import JSONDatabase
from Bob.robot.framework.fw_robot import Robot
from Bob.visual.monitor.concrete.crt_camera import CameraMonitor
from Bob.visual.monitor.framework.fw_monitor import CameraListener
from Bob.visual.utils import visual_utils
from command_utils import getCommandsFromFileName


class FunctionListener(PackageListener, CameraListener):

    def __init__(self, device: PackageDevice, camera_monitor: CameraMonitor, robot: Robot):
        self.__id_counter = 0
        self._camera_monitor = camera_monitor
        self.package_device = device
        self.mode: str = ""

        self.__robot = robot

        db_charset = 'UTF-8'

        self.__object_db = JSONDatabase(open(f"db{os.path.sep}objects.json", encoding=db_charset))
        self.__face_db = JSONDatabase(open(f"db{os.path.sep}faces.json", encoding=db_charset))
        self.__stories_db = JSONDatabase(open(f"db{os.path.sep}stories.json", encoding=db_charset))
        self.__vocabularies_db = JSONDatabase(open(f"db{os.path.sep}vocabularies.json", encoding=db_charset))

        self.object_timer = 0
        self.face_timer = 0

    @staticmethod
    def formatDataToJsonString(id: int, type: str, content: str, data):
        sendData = {"id": id, "response_type": type, "content": content,
                    "data": data}
        return json.dumps(sendData, ensure_ascii=False)

    def onReceive(self, cmd: str):
        """
        當接收到互動介面所傳輸之指令時會被呼叫
        @param cmd:接收到之指令
        """

        print("receive:", cmd)

        if cmd == "DETECT_OBJECT" or cmd == "DETECT_INTER_OBJECT":
            # 開啟物品辨識Detector,關閉臉部辨識Detector
            self._camera_monitor.setDetectorEnable(1, False)
            self._camera_monitor.setDetectorEnable(2, True)
            self.mode = cmd

        elif cmd == "DETECT_FACE":
            # 開啟臉部辨識Detector,關閉物品辨識Detector
            self._camera_monitor.setDetectorEnable(1, True)
            self._camera_monitor.setDetectorEnable(2, False)
        elif cmd == "START_DETECT":
            pass
        elif cmd == "PAUSE_DETECT":
            pass
        elif cmd == "STOP_DETECT":
            pass
        elif cmd == "DB_GET_ALL":
            # 送出所有物品之資料
            all_data: json = self.__object_db.getAllData()
            jsonString = self.formatDataToJsonString(0, "json_object", "all_objects", all_data)
            print("Send:", jsonString)
            self.package_device.writeString(jsonString)

        elif cmd.startswith("STORY_GET"):
            l1 = cmd[10:]
            if l1 == "LIST":
                # 送出所有故事標題以及資訊
                print("list all")
                stories_list = []
                all_data: json = self.__stories_db.getAllData()
                for story in all_data:
                    stories_list.append(
                        {"id": story['id'], "name": (story['data']['name']), "total": (story['data']['total'])})

                jsonString = self.formatDataToJsonString(0, "json_array", "all_stories_info", stories_list)
                print("Send:", jsonString)
                self.package_device.writeString(jsonString)
            elif l1.startswith("STORY"):
                # 送出指定故事之所有內容
                story_id = l1[6:]
                print("get story", story_id)
                story_content = self.__stories_db.queryForId(story_id)
                jsonString = self.formatDataToJsonString(0, "json_object", "story_content", story_content['data'])
                print("Send:", jsonString)
                self.package_device.writeString(jsonString)
        elif cmd.startswith("DO_ACTION"):
            # 機器人做出動作 DO_ACTION [動作名稱].csv
            action = cmd[10:]
            threading.Thread(target=self.doAction, args=(action,)).start()
            # doAction(action)
        elif cmd == "STOP_ALL_ACTION":
            # 停止機器人所有動作
            self.__robot.stopAllAction()
        elif cmd == "ALL_VOCABULARIES":
            # 送出所有單字資訊
            print("get all vocabulary")
            vocabularies_content = self.__vocabularies_db.queryForId("vocabulary")
            print(vocabularies_content)
            jsonString = self.formatDataToJsonString(0, "json_array", "all_vocabularies", vocabularies_content['data'])
            print("Send:", jsonString)
            self.package_device.writeString(jsonString)

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
            if time.time() <= self.face_timer:
                return
            obj: Optional[json] = self.__face_db.queryForId(data[0]['emotion'])

            if obj is not None:
                data: json = obj['data']
                sendData = {"id": -1, "response_type": "json_object", "content": "single_object", "data": data}
                jsonString = json.dumps(sendData, ensure_ascii=False)
                print("Send:", jsonString)
                self.package_device.writeString(jsonString)
                self.face_timer = time.time() + 17

        elif detector_id == 2:
            labeledImage = image
            max_index = -1
            max_conf = -1
            i = 0
            for result in data:
                label = result['name'] + " " + str(round(result['conf'], 2))
                labeledImage = visual_utils.annotateLabel(image, (result['x']['min'], result['y']['min']),
                                                          (result['x']['max'], result['y']['max']), label,
                                                          overwrite=False)
                if result['conf'] > max_conf:
                    max_conf = result['conf']
                    max_index = i

                i = i + 1
            cv2.imshow("object", labeledImage)

            if time.time() <= self.object_timer:
                return

            selected_object = data[max_index]
            obj: Optional[json] = self.__object_db.queryForId(selected_object['name'])
            if obj is not None:
                data: json = obj['data']
                sendData = {"id": -1, "response_type": "json_object", "content": "single_object", "data": data}
                jsonString = json.dumps(sendData, ensure_ascii=False)
                print("Send:", jsonString)
                self.package_device.writeString(jsonString)
                self.object_timer = time.time() + 17

    def doAction(self, action):
        print("do action:", action)
        self.__robot.doCommands(getCommandsFromFileName(action))
