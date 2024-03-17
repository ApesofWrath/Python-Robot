# Stuck? https://github.com/robotpy/examples/blob/main/SwerveBot/drivetrain.py
import wpimath.units
import wpimath.kinematics

import navx

from .swervemodule import SwerveModule

from extras.debugmsgs import *

# Load constants from the json file
import json
with open('constants.json') as jsonf:
	constants = json.load(jsonf)
	jsonf.close()

class Drivetrain():
	'''
	# Drivetrain

	Class that controlls components of the drivetrain (anything that moves the robot forwards, backwards, and sideways)
	'''
	def __init__(self):
		try:
			# Setup the gyro
			self.navx = navx.AHRS.create_spi()
			self.zeroGyro()
		except Exception as e:
			errorMsg('Issue initializing NavX:',e,__file__)
		
		# Each member variable represents a 'swervemodule.SwerveModule()' object
		self.swerveFrontLeft = SwerveModule(
			constants['MOTOR_CONSTANTS']['MOTOR_DRIVE_FRONT_LEFT_ID'],
			constants['MOTOR_CONSTANTS']['MOTOR_TURN_FRONT_LEFT_ID'],
			constants['MOTOR_CONSTANTS']['ENCODER_TURN_FRONT_LEFT_ID'],
			(constants['OFFSETS']['FRONT_LEFT'], constants['OFFSETS']['FRONT_LEFT'])
		)
		
		self.swerveFrontRight = SwerveModule(
			constants['MOTOR_CONSTANTS']['MOTOR_DRIVE_FRONT_RIGHT_ID'],
			constants['MOTOR_CONSTANTS']['MOTOR_TURN_FRONT_RIGHT_ID'],
			constants['MOTOR_CONSTANTS']['ENCODER_TURN_FRONT_RIGHT_ID'],
			(constants['OFFSETS']['FRONT_RIGHT'], -constants['OFFSETS']['FRONT_RIGHT'])
		)

		self.swerveBackLeft = SwerveModule(
			constants['MOTOR_CONSTANTS']['MOTOR_DRIVE_REAR_LEFT_ID'],
			constants['MOTOR_CONSTANTS']['MOTOR_TURN_REAR_LEFT_ID'],
			constants['MOTOR_CONSTANTS']['ENCODER_TURN_REAR_LEFT_ID'],
			(constants['OFFSETS']['REAR_LEFT'], -constants['OFFSETS']['REAR_LEFT'])
		)
		
		self.swerveBackRight = SwerveModule(
			constants['MOTOR_CONSTANTS']['MOTOR_DRIVE_REAR_RIGHT_ID'],
			constants['MOTOR_CONSTANTS']['MOTOR_TURN_REAR_RIGHT_ID'],
			constants['MOTOR_CONSTANTS']['ENCODER_TURN_REAR_RIGHT_ID'],
			(constants['OFFSETS']['REAR_RIGHT'], -constants['OFFSETS']['REAR_RIGHT'])
		)
		
		self.kinematics = wpimath.kinematics.SwerveDrive4Kinematics(
            self.swerveFrontLeft.location,
            self.swerveFrontRight.location,
            self.swerveBackLeft.location,
            self.swerveBackRight.location,
        )

		self.odometry = wpimath.kinematics.SwerveDrive4Odometry(
            self.kinematics,
            self.navx.getRotation2d(),
            (
                self.swerveFrontLeft.getPosition(),
                self.swerveFrontRight.getPosition(),
                self.swerveBackLeft.getPosition(),
                self.swerveBackRight.getPosition(),
            ),
        )

	def getRelativeSpeeds(self):
		'''
		Returns robot relative speeds that were derived from field relative speeds
		'''
		self.speeds = self.kinematics.toChassisSpeeds(
			(
				self.swerveFrontRight.getState(), 
				self.swerveBackRight.getState(), 
				self.swerveFrontLeft.getState(), 
				self.swerveBackLeft.getState()
			)
		)
		return wpimath.kinematics.ChassisSpeeds.fromFieldRelativeSpeeds(
			self.speeds.vx,
			self.speeds.vy,
			self.speeds.omega,
			self.navx.getRotation2d())

	def zeroGyro(self):
		'''
		Re-calibrates the NavX gyroscope
		'''
		# Zero the NavX gyro
		try:
			self.navx.zeroYaw()
		except Exception as e:
			errorMsg('Issue calibrating NavX:',e,__file__)

	def updateOdometry(self):
		'''
		Updates the field relative position of the robot
		'''
		
		self.odometry.update(
            self.navx.getRotation2d(),
            (
                self.swerveFrontLeft.getPosition(),
                self.swerveFrontRight.getPosition(),
                self.swerveBackLeft.getPosition(),
                self.swerveBackRight.getPosition(),
            )
        )

	def getOdometry(self):
		'''
		Returns the field relative position of the robot
		'''
		return self.odometry.getPose()
	
	def resetOdometry(self, initPose):
		'''
		Resets odometry of the robot
		'''
		self.odometry.resetPosition(
			self.navx.getRotation2d(),

			(
				self.swerveFrontRight.getPosition(),
				self.swerveBackRight.getPosition(),
				self.swerveFrontLeft.getPosition(),
				self.swerveBackLeft.getPosition(),
			),
			
			initPose
		)

	def drive(self, xSpeed: float, ySpeed: float, rotation: float, fieldRelative: bool, periodSeconds: wpimath.units.seconds):
		'''
		Drives the robot based on the imput from the xbox controller
		'''

		# Get the swerve-module states
		swerveModuleStates = self.kinematics.toSwerveModuleStates(
            wpimath.kinematics.ChassisSpeeds.discretize(
                (
                    wpimath.kinematics.ChassisSpeeds.fromFieldRelativeSpeeds(
                        xSpeed, ySpeed, rotation, self.navx.getRotation2d()
                    )
					
                    if fieldRelative
                    else wpimath.kinematics.ChassisSpeeds(xSpeed, ySpeed, rotation) # Return minimal output if not field relative
                ),
                periodSeconds
            )
        )

		# Renormalize speeds (compensates if any speeds are too fast/slow)
		wpimath.kinematics.SwerveDrive4Kinematics.desaturateWheelSpeeds(
            swerveModuleStates, constants['CALCULATIONS']['MODULE_MAX_SPEED']
        )

		# Set the desired states to each swerve motor
		self.swerveFrontLeft.setDesiredState(swerveModuleStates[0])
		self.swerveFrontRight.setDesiredState(swerveModuleStates[1])
		self.swerveBackLeft.setDesiredState(swerveModuleStates[2])
		self.swerveBackRight.setDesiredState(swerveModuleStates[3])