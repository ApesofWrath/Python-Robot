from extras.debugmsgs import * # Formatted messages used for debugging

from components.drivetrain import Drivetrain
from components.controller import XboxController

from pathplannerlib.auto import NamedCommands
from autonomous.autonomous import PPL

from wpilib import TimedRobot

# Load constants from the json file
import json
with open('constants.json') as jsonf:
	constants = json.load(jsonf)
	jsonf.close()

# Create the robot class (his name is terrance)
class terrance(TimedRobot):
    def robotInit(self):
        # Robot initialization
        self.drivetrain = Drivetrain()
        successMsg('Drivetrain initialized')

        try:
            self.controller = XboxController(self) # Link the xbox controller to the terrance class
            successMsg('Xbox controller initialized')
        except Exception as e:
            errorMsg('Issue in initializing xbox controller:', e, __file__)

        self.PPL = PPL(self)

        '''
        THIS IS TEMPORARY DONT HARASS ME ABOUT IT :3

        try:
            # Register Named Commands
            for command in constants["PATHPLANNER_CONSTANTS"]["AUTONOMOUS_COMMANDS"].keys():
                # Register's a command that runs an auton command based on the given string name of the function
                NamedCommands.registerCommand(str(command), autonCommand(str(command)))
        except Exception as e:
            errorMsg('Could not register commands to PPL:',e,__file__)
        '''

    def robotPeriodic(self):
        # TODO: Add proccesses that should always be running at all times here
        pass
    
    def disabledPeriodic(self):
        # TODO: Add functionality
        pass

    def autonomousInit(self): # Called at the begining of autonomous mode
        debugMsg('Entering autonomous mode') # Called only at the beginning of autonomous mode.
        self.controller.rumble(0.5) # Vibrate xbox controller to let driver know they are in auton mode
        self.PPL.followPath('Example Path') # Run the autonomous command

    def autonomousPeriodic(self): # Called every 20ms in autonomous mode.
        self.driveWithJoystick(False) # Disable joystick controll in autonomous mode
        self.drivetrain.updateOdometry()

    def autonomousExit(self): # Called when exiting autonomous mode
        debugMsg('Exiting autonomous mode')

    def teleopInit(self): # Called only at the begining of teleop mode
        debugMsg('Entering tele-operated mode')
        self.controller.rumble(0.0) # Stop vibrating xbox controller to let driver know they are in teleop mode

    def teleopPeriodic(self): # Called every 20 milliseconds in teleop mode
        self.driveWithJoystick(True) # Enable drive mode with joystick

    def teleopExit(self): # Called when exiting teleop mode
        debugMsg('Exiting tele-operated mode')

    def driveWithJoystick(self, state: bool):  # Custom method to drive with joystick
        self.controller.getSwerveValues()
        self.drivetrain.drive(self.controller.xSpeed, 
                              self.controller.ySpeed, 
                              self.controller.rot, 
                              state, 
                              self.getPeriod())

    '''
    
    MACROS:
        Below, add functions that can be linked to specific buttons 
        on a compatible peripherial device
    
    '''
    def zeroGyro(self):
        self.drivetrain.zeroGyro()

    def slowDownSwerve(self):
        pass

    def resetSwerveSpeed(self):
        pass