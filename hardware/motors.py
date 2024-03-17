# Module for controlling different motors
from extras.debugmsgs import *

import rev
import phoenix6

class CANSparkMax:
    '''
    # CANSparkMax
    Class for configuring and setting up a CANSparkMax motor
    '''
    def __init__(self, 
                channel: int,
                smartCurrentLimit: int,
                brushless = True,
                restoreFactoryDefaults = True, 
                setInverted = True, 
                idleMode = rev.CANSparkMax.IdleMode.kBrake):
        
        self.motor = rev.CANSparkMax(channel,
            rev.CANSparkMax.MotorType.kBrushless if brushless else rev.CANSparkMax.MotorType.kBrushed
        )

        # Configure motor
        self.motor.restoreFactoryDefaults(restoreFactoryDefaults) # Resets the motor to factory settings
        self.motor.setInverted(setInverted) # Invert the motor
        self.motor.setIdleMode(idleMode) # Sets the idle mode of the motor to brake (Motor brakes when not doing anything)
        self.motor.setSmartCurrentLimit(smartCurrentLimit) # Sets current limit for the motor

        # Encoder(s) which can be set to CANSparkMax
        self.relativeEncoder = None
        self.alternateEncoder = None

        # Controller(s) which can be set to CANSparkMax
        self.PIDController = None

    def setRelativeEncoder(self, positionConversionFactor: float, velocityConversionFactor: float):
        '''
        Configures and sets up a relative encoder to the motor
        '''
        self.relativeEncoder = self.motor.getEncoder()

        # Configure relative encoder conversion factor (Velocity values for the external turn encoder and the built in drive encoder)
        self.relativeEncoder.setPositionConversionFactor(positionConversionFactor)
        self.relativeEncoder.setVelocityConversionFactor(velocityConversionFactor)

    def setPIDController(self, P: float, I: float, D: float, FF: float, outputRange: float):
        '''
        Configures and sets up a PID controller to the motor
        '''
        if self.relativeEncoder == None:
            errorMsg('Cannot create PID controller without a relative encoder being set',None)

        self.PIDController = self.motor.getPIDController()
        self.PIDController.setFeedbackDevice(self.relativeEncoder)

        self.PIDController.setP(P)
        self.PIDController.setI(I)
        self.PIDController.setD(D)
        self.PIDController.setFF(FF)
        self.PIDController.setOutputRange(outputRange[0], outputRange[1])

class KrakenMotor:
    '''
    # KrakenMotor
    Class for configuring and setting up a Kraken motor
    '''
    def __init__(self,
        channel: int,
        canbus = '',
        velocity = 0,
        neutralMode = phoenix6.signals.NeutralModeValue.COAST,
        enableStatorCurrentLimit = True,
        statorCurrentLimit = 25.0,
        KP = 0,
        KI = 0,
        KD = 0,
        KV = 0,
        velocityWithSlot = 0,
        velocityWithEnableFOC = False):

        # Initialize the motor with the channel and canbus
        self.motor = phoenix6.hardware.TalonFX(channel, canbus)

        # Initialize the velocity duty cycle
        self.velocity = phoenix6.controls.VelocityDutyCycle(0)

        # Initialize the configurators of the Kraken motor
        self.outputConfig = phoenix6.configs.MotorOutputConfigs()
        self.limitConfig = phoenix6.configs.CurrentLimitsConfigs()
        self.slot0Config = phoenix6.configs.Slot0Configs()

        # Configure Kraken settings
        self.outputConfig.with_neutral_mode(neutralMode)

        self.limitConfig.with_supply_current_limit_enable(enableStatorCurrentLimit)
        self.limitConfig.with_stator_current_limit(statorCurrentLimit)

        # Configure Kraken PID values
        self.slot0Config.with_k_p(KP)
        self.slot0Config.with_k_i(KI)
        self.slot0Config.with_k_d(KD)
        self.slot0Config.with_k_v(KV)

        # Apply the configurators to the Kraken
        self.motor.configurator.apply(self.outputConfig)
        self.motor.configurator.apply(self.limitConfig)
        self.motor.configurator.apply(self.slot0Config)

        self.velocity.with_slot(velocityWithSlot)
        self.velocity.with_enable_foc(velocityWithEnableFOC)

    def linkTo(self, masterChannel: int, opposeMasterDirection: bool):
        '''
        Sets the controlls of the motor equal to the controlls of another Kraken motor
        '''
        self.motor.set_control(phoenix6.controls.Follower(masterChannel, opposeMasterDirection))