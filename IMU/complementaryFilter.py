class ComplementaryFilter:
    def __init__(self):
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        
        self.accelerometerWeight = 0.015  # Low weight for accelerometer (adjust if necessary)
        self.gyroWeight = 0.2  # Medium weight for gyro
        
        self.max_angular_velocity = 100 # Threshold for fast angular velocities
        self.min_angular_velocity = 10  # Threshold for low angular velocities

    def update(self, accel, gyro):
        # Calculate the total angular velocity (sum of all axes)
        angular_velocity = abs(gyro.roll) + abs(gyro.pitch) + abs(gyro.yaw)

        # Set dynamic weights based on angular velocity
        if angular_velocity < self.min_angular_velocity:
            # Trust the gyro more at low velocities, accelerometer adjusts for drift
            accelerometer_weight = self.accelerometerWeight
            gyro_weight = 1 - accelerometer_weight
        elif angular_velocity > self.max_angular_velocity:
            # Trust the accelerometer more at high velocities as gyro deviates at large velocities
            accelerometer_weight = 0.9
            gyro_weight = 1 - accelerometer_weight
        else:
            # Use both at medium velocities
            accelerometer_weight = 0.5
            gyro_weight = 1 - accelerometer_weight

        # Combine the accelerometer and gyro data using the weights
        self.roll = gyro_weight * gyro.roll + accelerometer_weight * accel.roll
        self.pitch = gyro_weight * gyro.pitch + accelerometer_weight * accel.pitch
        
        # Yaw remains from the gyro since accelerometer cannot estimate yaw
        self.yaw = gyro.yaw
        
        return {}
