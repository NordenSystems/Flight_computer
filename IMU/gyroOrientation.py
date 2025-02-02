import time

class GyroOrientationEstimator:
    def __init__(self):
        self.last_time = time.ticks_us()  # Initialize with current time
        self.roll = 0.0  # Orientation in degrees for X-axis
        self.pitch = 0.0  # Orientation in degrees for Y-axis
        self.yaw = 0.0  # Orientation in degrees for Z-axis

    def update_orientation(self, compFilter, gyro_x, gyro_y, gyro_z):
        """
        Update the orientation using angular velocity (dps) and time delta.
        """
        current_time = time.ticks_us()  # Current time in microseconds
        delta_time = time.ticks_diff(current_time, self.last_time) / 1_000_000  # Convert to seconds
        self.last_time = current_time  # Update the last time

        # Integrate angular velocity to calculate orientation
        self.roll = compFilter.roll + gyro_x * delta_time
        self.pitch = compFilter.pitch + gyro_y * delta_time
        self.yaw = compFilter.yaw + gyro_z * delta_time

        return {}