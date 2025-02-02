import math

class AccelOrientationEstimator:
    def __init__(self):
        
        self.roll = 0.0
        self.pitch = 0.0
        
        self.confidence_magnitude = 0.0
        self.confidence_roll = 0.0
        self.confidence_pitch = 0.0
        
        self.magnitude_confidence_weight = 10
        self.magnitude_confidence_power = 4 # Must be even
        
        self.angle_confidence_weight = 7
        self.angle_confidence_power = 4 # Must be even

    def update_orientation(self, ax, ay, az):
        """
        Compute pitch and roll from accelerometer data.
        Estimate yaw from external source (e.g., gyroscope/magnetometer).
        """
        # Compute magnitude of acceleration
        magnitude = math.sqrt(ax**2 + ay**2 + az**2)
        
        # Normalize
        ax = ax/magnitude
        ay = ay/magnitude
        az = az/magnitude

        # Confidence based on acceleration magnitude based on : e^-(20*(x-1))^6 starts to decay from 0.98 1.02
        self.confidence_magnitude = math.exp(-(self.magnitude_confidence_weight*(magnitude-1))**self.magnitude_confidence_power)

        # Compute roll amd pitch
        self.roll = math.atan2(ay, az) * (180 / math.pi)
        self.pitch = math.atan2(-ax, math.sqrt(ay**2 + az**2)) * (180 / math.pi)
        
        # Compute allignment with gravity and confidence
        self.confidence_roll = 1-math.exp(-(self.angle_confidence_weight*(abs(ax)-1))**self.angle_confidence_power)
        self.confidence_pitch = 1-math.exp(-(self.angle_confidence_weight*(abs(ay)-1))**self.angle_confidence_power)

        return {}