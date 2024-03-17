# Streamlines implementation of periphierals like xbox controllers, keybaords, button stations, etc.
import wpilib
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter

from extras.debugmsgs import *
import numpy as np

# Load constants from the json file
import json
with open('constants.json') as jsonf:
	constants = json.load(jsonf)
	jsonf.close()

class XboxController():
    '''
    # XboxController
    Module which streamlines controll of an Xbox controller
    '''
    def __init__(self, instance: object):
        '''
        Constructs the controller class

        The 'instance' argument should be the object of your robot
        '''
        self.instance = instance # The instance should be the name of the class of your robot

        # Define our controller
        self.wpilibController = wpilib.XboxController(constants['CONTROLLER_CONSTANTS']['CONTROLLER_MAIN_ID'])

        # Slew rate limiters to make joystick inputs more gentle; 1/3 sec from 0 to 1.
        self.xSpeedLimiter = SlewRateLimiter(constants['CONTROLLER_CONSTANTS']['CONTROLLER_RATE_LIMIT'])
        self.ySpeedLimiter = SlewRateLimiter(constants['CONTROLLER_CONSTANTS']['CONTROLLER_RATE_LIMIT'])
        self.rotLimiter = SlewRateLimiter(constants['CONTROLLER_CONSTANTS']['CONTROLLER_RATE_LIMIT'])

        # Define our swervemodule speeds
        self.xSpeed = 0
        self.ySpeed = 0
        self.rot = 0 # Rotation of robot (rotates robot without moving its X and Y position)

        # An array of all of the boolean values that we can bind a macro too
        self.values = np.array([
            self.wpilibController.getStartButtonReleased(),
            self.wpilibController.getAButtonReleased(),
            self.wpilibController.getBButtonReleased(),
            self.wpilibController.getXButtonReleased(),
            self.wpilibController.getYButtonReleased(),
            self.wpilibController.getLeftBumperReleased(),
            self.wpilibController.getRightBumperReleased(),
            self.wpilibController.getLeftStickButtonReleased(),
            self.wpilibController.getRightStickButtonReleased()
        ])

        # Eack key can be set in 'constants.json' to carry out a function in annother python script
        self.macroNames = [constants['CONTROLLER_CONSTANTS']['MACROS'][key] for key in ['START', 'A', 'B', 'X', 'Y', 'L_BUMPER', 'R_BUMPER', 'L_STICK', 'R_STICK']]

    def executeMacros(self, macros = None): # Add this to the 'robotPeriodic()' method
        '''
        Use boolean indexing to execute functions for pressed buttons
        '''

        # Update array of values
        self.values = np.array([
            self.wpilibController.getStartButtonReleased(),
            self.wpilibController.getAButtonReleased(),
            self.wpilibController.getBButtonReleased(),
            self.wpilibController.getXButtonReleased(),
            self.wpilibController.getYButtonReleased(),
            self.wpilibController.getLeftBumperReleased(),
            self.wpilibController.getRightBumperReleased(),
            self.wpilibController.getLeftStickButtonReleased(),
            self.wpilibController.getRightStickButtonReleased()
        ])


        trueValues = np.where(self.values == True)[0]

        for index in trueValues:
            try:
                if macros is not None and self.macroNames[index] in macros:
                    macroToCall = getattr(self.instance, self.macroNames[index])

                    if macroToCall and callable(macroToCall):
                        macroToCall()
                    else:
                        debugMsg(f"Method '{self.macroNames[index]}' not found or not callable.", None)

                elif macros == None:
                    # If the user did not filter specific macros, just execute all macros if their cooresponding buttons were pressed
                    macroToCall = getattr(self.instance, self.macroNames[index])

                    if macroToCall and callable(macroToCall):
                        macroToCall()
                    else:
                        debugMsg(f"Method '{self.macroNames[index]}' not found or not callable.", None)
            except Exception as e:
                debugMsg(f'While indexing macros: {e}')
        
    def getSwerveValues(self):
        '''
        Returns calculated values from xbox controller input to appropriate drivetrain values (explicitly for swervemodules)
        '''
        # Get the x speed. We are inverting this because Xbox controllers return
        # negative values when we push forward.
        self.xSpeed = (
            -self.xSpeedLimiter.calculate(
                applyDeadband(self.wpilibController.getLeftX(), 0.02)) * constants['CALCULATIONS']['CHASSIS_MAX_SPEED']
        )

        # Get the y speed or sideways/strafe speed. We are inverting this because
        # we want a positive value when we pull to the left. Xbox controllers
        # return positive values when you pull to the right by default.
        self.ySpeed = (
            -self.ySpeedLimiter.calculate(
                applyDeadband(self.wpilibController.getLeftY(), 0.02)) * constants['CALCULATIONS']['CHASSIS_MAX_SPEED']
        )

        # Get the rate of angular rotation. We are inverting this because we want a
        # positive value when we pull to the left (remember, CCW is positive in
        # mathematics). Xbox controllers return positive values when you pull to
        # the right by default.
        self.rot = (
            -self.rotLimiter.calculate(
                applyDeadband(self.wpilibController.getRightX(), 0.02)) * constants['CALCULATIONS']['CHASSIS_MAX_SPEED']
        )

    def rumble(self, intensity: float = 0.0): # Sets the vibration intensity of the xbox controller
        self.wpilibController.setRumble(self.wpilibController.RumbleType.kBothRumble, intensity)