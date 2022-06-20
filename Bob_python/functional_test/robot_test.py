from device_config import getRobot
from command_utils import getCommandsFromFileName

robot = getRobot()
robot.open()

robot.enableAllServos(True)
robot.doCommands(getCommandsFromFileName("storyaction_start.csv"))

robot.close()
