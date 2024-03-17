# WPILib-Python-Test

_NOTE: This documentation is old and will be updated when the robot code is more stable_

Robot code for the FRC 2024 "Crescendo" competition even though we probably won't be using it for 2024 (Womp-Womp)

**External Software**

_It is recommended to develop using Windows 10/11, since as of 1/25/2024 there is no native MacOS support for FRC Game Tools/Radio Configuration_

- [WPILib 2024](https://github.com/wpilibsuite/allwpilib/releases/tag/v2024.2.1) (Not needed for python development)
- [FRC Game Tools 2024](https://www.ni.com/en/support/downloads/drivers/download.frc-game-tools.html#500107) (Windows ONLY!)
- [FRC Radio Configurstion Utility 2024](https://firstfrc.blob.core.windows.net/frc2024/Radio/FRC_Radio_Configuration_24_0_1.zip) (Windows ONLY!)
  - [Israel Version](https://firstfrc.blob.core.windows.net/frc2024/Radio/FRC_Radio_Configuration_24_0_1_IL.zip) (עַם יִשְׂרָאֵל חַי)
- [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html)
  - NOTE: If Anaconda is already on your system, miniconda is not needed!

_NOTE: You can also use python's built in 'venv' library to create a virtual environment to test your code, but conda is a neater option IMO_

## Setup

To setup this code on your computer for development, follow the steps below:

**Windows/MacOS/Unix/GNU**
- Make sure all software is downloaded and installed (check "External software")
- Clone the repository
- If you are in Windows, open **Anaconda Powershell Prompt** (Any terminal should be fine for Linux and Mac users) and navigate to the parent directory in which the repository is stored on your local machine
- Build a new conda environment for robotpy using the commands below:
  - `conda env create -n WPILib`
  - `conda activate WPILib`
  - `conda install pip`
  - `pip install robotpy`
  - `robotpy sync`

## Running/Testing/Deploying

You can customize what specific tests you want to run in tests/pyfrc_test.py. (located in the directory of your repository)

To run tests, go the the working directory of your robot code in anaconda powershell and run `clear; robotpy test`

To whoever it may concern, I advise you to go follow the most recent RobotPy documentation for running and testing robot code on your local machine, as they will probably update it faster than I can update this README.
- [RobotPy Documentation](https://robotpy.readthedocs.io/en/stable/)
