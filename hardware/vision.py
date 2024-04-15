import limelight, limelightresults

from extras.debugmsgs import *

class LimelightCamera:
    '''
    # LimelightCamera

    Controlls a Limelight camera
    '''
    def __init__(self, id: int):
        # Search for limelights
        discovered_limelights = limelight.discover_limelights()
        debugMsg(f'Discovered Limelights: {discovered_limelights}')

        if discovered_limelights: # 'limelight.discover_limelights()' probably returns "None" if no limelights are discovered
            limelight_address = discovered_limelights[0] # Get the address of the first discovered limelight
            self.limelight = limelight.Limelight(limelight_address) # Construct a new limelight object given the address

            limelight.enable_websocket() # Enable websocket in a new thread for optmized performance
            while True:
                result = limelight.get_latest_results()

                parsed_result = limelightresults.parse_results(result)
                if parsed_result is not None:
                    print(parsed_result.pipeline_id)
                    print(parsed_result.parse_latency)

                    # Accessing arrays
                    for tag in parsed_result.fiducialResults:
                        print(tag.robot_pose_target_space, tag.fiducial_id) 