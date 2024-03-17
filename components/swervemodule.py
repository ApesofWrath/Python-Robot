# Controlls the swerve module
# Stuck? https://github.com/robotpy/examples/blob/main/SwerveBot/swervemodule.py
# Stuck? https://robotpy.readthedocs.io/projects/wpimath/en/latest/wpimath.geometry/Translation2d.html
from extras.debugmsgs import *

from hardware.motors import CANSparkMax

import wpimath.kinematics
import wpimath.geometry
import wpimath.controller
import wpimath.trajectory
import wpimath.units

import rev, phoenix6

class SwerveModule:
    '''
    # SwerveModule
    Used by the drivetrain to controll each individual swerve module on the robot
    '''
    def __init__(self, driveMotorChannel, turnMotorChannel, turnEncoderChannel, location):

        # Location represents the distance (TODO: Find what unit of measurement for distance)
        # From the middle of the robot to any of the swerve modules
        self.location = wpimath.geometry.Translation2d(location[0], location[1])

        # Set up the turn (absolute) encoder
        try:
            self.absoluteEncoder = phoenix6.hardware.CANcoder(turnEncoderChannel) #TODO: Find what 'CANBus' is
        except Exception as e:
            errorMsg('Could not initialize absolute encoder:',e,__file__)

        try:
            # Set up the drive motor (motor that moves the robot in a direction)
            # and the turn motor (motor that turns the drive motor to change the direction of the robot)
            self.motorDrive = CANSparkMax(driveMotorChannel, 80)
            self.motorTurn = CANSparkMax(turnMotorChannel, 20)
        except Exception as e:
            errorMsg('Could not initialize motors [rev.CANSparkMax]:',e,__file__)

        try:
            # Set and configure the relative encoders
            self.motorDrive.setRelativeEncoder(
                (0.0508 * 2.0 * 3.141592653589 * ((14.0 / 50.0) * (25.0 / 19.0) * (15.0 / 45.0))),
                (0.0508 * (2.0 * 3.141592653589 * ((14.0 / 50.0) * (25.0 / 19.0) * (15.0 / 45.0))) / 60.0),
            )

            self.motorTurn.setRelativeEncoder(
                (2.0 * 3.141592653589 * ((14.0 / 50.0) * (10.0 / 60.0))),
                (2.0 * 3.141592653589 * ((14.0 / 50.0) * (10.0 / 60.0)) / 60.0)
            )
        except Exception as e:
            errorMsg('Could not configure relative encoders:',e,__file__)

        try:
            # Set up PID constrollers
            self.motorDrive.setPIDController(0.01, 0, 0, (1.0/73.0), [-1.0, 1.0])
            self.motorTurn.setPIDController(0.015, 0, 0.001, 0, [-1.0, 1.0])
        except Exception as e:
            errorMsg('Could not obtain PID controllers:',e,__file__)
        # TODO: Ask if I need to add code HERE that sets the starting positions of all parts of the swervemodule

    def getPosition(self):
        '''
        Returns the swerve module position based on encoders
        '''
        try:
            return wpimath.kinematics.SwerveModulePosition(
                wpimath.units.meters(self.motorDrive.relativeEncoder.getPosition()), 

                wpimath.geometry.Rotation2d(
                    wpimath.angleModulus(self.absoluteEncoder.get_absolute_position().value_as_double * 360.0)
                    )
                )
        except Exception as e:
            errorMsg('Could not get position:',e,__file__)
    
    def getState(self):
        '''
        Returns the speed (meters/second) from the drive encoder and the rotation from the turn encoder
        '''
        try:
            return wpimath.kinematics.SwerveModuleState(
                wpimath.units.meters_per_second(self.motorDrive.relativeEncoder.getVelocity()), # Speed of the drive motor

                wpimath.geometry.Rotation2d(
                    wpimath.angleModulus(self.absoluteEncoder.get_absolute_position().value_as_double * 360.0) # Angle of rotation
                )
            )
        except Exception as e:
            errorMsg('Could not get state:',e,__file__)
    
    def setDesiredState(self, desiredState):
        '''
        Sets desired state (speed & angle) of the swervemodule
        '''

        try:
            # Get the rotation of the absolute encoder
            encoderRotation = wpimath.geometry.Rotation2d(
                wpimath.units.degrees(
                    float(self.absoluteEncoder.get_absolute_position().value_as_double) * 360.0)
                )
        except Exception as e:
            errorMsg('Could not get encoder rotation:',e,__file__)

        try:
            # Get the currect state of the swerve module
            state = wpimath.kinematics.SwerveModuleState.optimize(
                desiredState, encoderRotation
            )
        except Exception as e:
            errorMsg('Could not get state:',e,__file__)

        state.speed *= ((state.angle - encoderRotation).cos()) # IDK check robotpy examples in swervedrive
        targetAngle = state.angle.degrees() # Target angle of the swervemodule

        try:
            # Get the target motor speed
            targetMotorSpeed = wpimath.units.radians_per_second(
                state.speed * wpimath.units.radians(2*3.14159) #TODO: Ask if I should use 'radians' or 'radiansToDegrees'
            )
        except Exception as e:
            errorMsg('Could not get target motor speed:',e,__file__)

        try:
            # Set refrence to the drive motor's PID controller
            self.motorDrive.PIDController.setReference(targetMotorSpeed, rev.CANSparkMax.ControlType.kVelocity)
        except Exception as e:
            errorMsg('Could not set reference to drive controller:',e,__file__)
        
        try:
            # Set the position of the turn motor through the relative encoder
            self.motorTurn.relativeEncoder.setPosition(self.absoluteEncoder.get_absolute_position().value_as_double * 360.0)
        except Exception as e:
            errorMsg('Could not set position to relative turn encoder:',e,__file__)

        try:
            # Set the reference to the turn motor's PId controller
            self.motorTurn.PIDController.setReference(float(targetAngle), rev.CANSparkMax.ControlType.kPosition)
        except Exception as e:
            errorMsg('Could not set reference to turn controller:',e,__file__)