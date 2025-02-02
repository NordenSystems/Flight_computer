import math

class MagnetometerOrientationEstimator:
    def __init__(self):
        self.yaw = 0.0  # Initialize yaw

    def update_orientation(self, compFilter, mx, my, mz):
        """
        Computes yaw estimation using the magnetometer.
        Used later to compensate for gyro drift.
        """
        # Convert roll and pitch from degrees to radians
        roll_rad = math.radians(compFilter.roll)
        pitch_rad = math.radians(compFilter.pitch)

        # Compensate magnetometer readings for tilt
        mx_comp = mx * math.cos(pitch_rad) + mz * math.sin(pitch_rad)
        my_comp = mx * math.sin(roll_rad) * math.sin(pitch_rad) + my * math.cos(roll_rad) - mz * math.sin(roll_rad) * math.cos(pitch_rad)

        # Compute yaw in degrees
        self.yaw = math.degrees(math.atan2(-my_comp, mx_comp))