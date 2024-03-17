from wpilib import DriverStation
import wpimath.units as units
from wpimath.geometry import Pose2d

import pathplannerlib.auto as auto
import pathplannerlib.config as config
import pathplannerlib.path as pplpath

# Load constants from the json file
import json
with open('constants.json') as jsonf:
	constants = json.load(jsonf)
	jsonf.close()

class PPL:
    '''
    # PPL
    Logic for following robot path with/without smart path compensation

    Uses pathplannerlib  
    '''
    def __init__(self, robot: object):
        self.paths = {} # Dictionary to store data to easilly get a path later on

        self.pathFollowerConfig = auto.AutoBuilder.configureHolonomic(
            robot.drivetrain.getOdometry(), # Robot pose supplier

            robot.drivetrain.resetOdometry(Pose2d()), # Method to reset odometry (will be called if your auto has a starting pose)

            robot.drivetrain.getRelativeSpeeds(), # ChassisSpeeds supplier. MUST BE ROBOT RELATIVE

            robot.drivetrain.drive( # Method that will drive the robot given ROBOT RELATIVE ChassisSpeeds
                robot.drivetrain.speeds.vx,
                robot.drivetrain.speeds.vy,
                robot.drivetrain.speeds.omega,
                False,
                robot.getPeriod()
            ),
            
            # Set up path follower
            auto.HolonomicPathFollowerConfig(
                config.PIDConstants(
                    constants["PATHPLANNER_CONSTANTS"]["TRANSLATION_PID_CONSTANTS"][0],
                    constants["PATHPLANNER_CONSTANTS"]["TRANSLATION_PID_CONSTANTS"][1],
                    constants["PATHPLANNER_CONSTANTS"]["TRANSLATION_PID_CONSTANTS"][2]
                ),
                config.PIDConstants(
                    constants["PATHPLANNER_CONSTANTS"]["ROTATION_PID_CONSTANTS"][0],
                    constants["PATHPLANNER_CONSTANTS"]["ROTATION_PID_CONSTANTS"][1],
                    constants["PATHPLANNER_CONSTANTS"]["ROTATION_PID_CONSTANTS"][2]
                ),
                units.meters_per_second(constants["PATHPLANNER_CONSTANTS"]["MAX_SPEED"]),
                units.meters(constants["PATHPLANNER_CONSTANTS"]["DRIVE_BASE_RADIUS"]),
                config.ReplanningConfig()
            ),

            self.shouldFlipPath(), # Supplier to control path flipping based on alliance color
            robot.drivetrain # Reference to drivetrain component to set requirements
        )

    def shouldFlipPath(self):
        '''
        Boolean supplier that controls when the path will be mirrored for the red alliance
        This will flip the path being followed to the red side of the field.
        THE ORIGIN WILL REMAIN ON THE BLUE SIDE
        '''
        return DriverStation.getAlliance() == DriverStation.Alliance.kRed
    
    def followPath(self, pathName: str):
        '''
        Runs a path baed on the file name of the path
        '''

        #[OLD IMPLEMENTATION. KEEP HERE FOR TESTING]

        path = pplpath.PathPlannerPath.fromPathFile(pathName)

        #Create a path following command using AutoBuilder. This will also trigger event markers.
        
        return auto.AutoBuilder.followPath(path)

        #return auto.PathPlannerAuto(pathName)

class SDRbt:
    '''
    # SDRbt
    Self-driving robot
    '''
    def __init__(self):
        pass # TODO: Make it work :)