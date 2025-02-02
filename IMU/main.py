from time import sleep, ticks_ms
from pinDef import PinDef
from imu import IMU
from accelOrientation import AccelOrientationEstimator
from gyroOrientation import GyroOrientationEstimator
from magOrientation import MagnetometerOrientationEstimator
from complementaryFilter import ComplementaryFilter

class Orientation:
    def __init__(self):
        # Initialize the sensor
        freq = 400000
        self.imu = IMU(PinDef.IMU_sda, PinDef.IMU_scl, freq)

        # Initialize estimators
        self.accel = AccelOrientationEstimator()
        self.gyro = GyroOrientationEstimator()
        self.mag = MagnetometerOrientationEstimator()

        # Initialize complementary filter
        self.compFilter = ComplementaryFilter()

    def update(self):
        # Get filtered IMU data
        self.imu.get_sensor_data()
        print(self.imu.mag_x)

        # Estimate orientation
        self.accel.update_orientation(self.imu.accel_x, self.imu.accel_y, self.imu.accel_z)
        self.gyro.update_orientation(self.compFilter, self.imu.gyro_x, self.imu.gyro_y, self.imu.gyro_z)
        self.mag.update_orientation(self.compFilter, self.imu.mag_x, self.imu.mag_y, self.imu.mag_z) # Reading wrong address

        # Apply sensor fusion
        self.compFilter.update(self.accel, self.gyro, self.mag)

def main():
    orientation = Orientation()
    
    while True:
        orientation.update()
        #print(f"Roll = {orientation.compFilter.roll:.2f}, Pitch = {orientation.compFilter.pitch:.2f}, Yaw = {orientation.compFilter.yaw:.2f}")
        #print(f"Yaw = {orientation.compFilter.yaw:.2f}")
        #print(f"Mx = {orientation.imu.mag_x:.2f}, My = {orientation.imu.mag_y:.2f}, Mz = {orientation.imu.mag_z:.2f}")
        sleep(0.03)  # delay for stability

if __name__ == "__main__":
    main()
