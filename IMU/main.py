from time import sleep, ticks_ms
from pinDef import PinDef
from imu import IMU
from accelOrientation import AccelOrientationEstimator
from gyroOrientation import GyroOrientationEstimator
#from magOrientation import MagnetometerOrientationEstimator
from gps import GPS
from complementaryFilter import ComplementaryFilter

# TVC rocket is assumed to only be accerating due to thrust (of which we know the direction) or drag (of which we know the direction)
# There might be a small acceleration in x and y direction due to side slipping of the rocket

def main():
    
    # Initialize GPS
    gpsFilterSize = 10
    baudrate = 9600
    gps = GPS(2, PinDef.GPS_write, PinDef.GPS_read, baudrate, gpsFilterSize)

    # Initialize the sensor
    imuFilterSize = 1
    freq = 400000
    imu = IMU(PinDef.IMU_sda, PinDef.IMU_scl, freq, imuFilterSize)
    
    # Initialize the acceleromter
    accel = AccelOrientationEstimator()
    
    # Initialize the gyroscope
    gyro = GyroOrientationEstimator()
    
    # Initialize the acceleromter
    #mag = MagnetometerOrientationEstimator()
    
    # Initialize the compementary filter
    compFilter = ComplementaryFilter()
    
    # Initialize time
    last_log_time = ticks_ms()  # Start time for logging interval

    # Running loop
    while True:
        # Keep track of time
        current_time = ticks_ms()
        
        # Get filtered IMU data
        imu.get_sensor_data()
        
        # Use data to estimate orientation
        accel.update_orientation(imu.accel_x, imu.accel_y, imu.accel_z)
        gyro.update_orientation(compFilter, imu.gyro_x, imu.gyro_y, imu.gyro_z)
        #mag.update_orientation(compFilter, imu.mag_x, imu.mag_y, imu.mag_z)

        # Get filtered GPS data
        #gps.get_gps_data()
        
        # Sensor fusion
        compFilter.update(accel, gyro)
   
        # Print all data for testing purposes
        #print(f"Latitude: {gps.latitude}, Longitude: {gps.longitude}")
        #print(f"Accelerometer Data (X, Y, Z): {imu.accel_x:.3f}g, {imu.accel_y:.3f}g, {imu.accel_z:.3f}g")
        #print(f"Gyro Data: X={imu.gyro_x} dps, Y={imu.gyro_y} dps, Z={imu.gyro_z} dps")
        #print(f"Gyro Data: X={gyro.orientation_x} d, Y={gyro.orientation_y} d, Z={gyro.orientation_z} d")
        #print(f"Accel Data: X={accel.roll} d, Y={accel.pitch} d")
        #print(f"Confidence: X={accel.confidence_roll*accel.confidence_magnitude} d, Y={accel.confidence_pitch*accel.confidence_magnitude} d")
        #print(f"Roll = {compFilter.roll}, Pitch = {compFilter.pitch}, Yaw = {compFilter.yaw}")
        
        #sleep(0.03)  # Adjust the delay as needed for your use case
        
        # Log data only every 0.03 seconds
        if current_time - last_log_time >= 30:
            print(f"Roll = {compFilter.roll:.2f}, Pitch = {compFilter.pitch:.2f}, Yaw = {compFilter.yaw:.2f}")
            last_log_time = current_time  # Reset log timer


if __name__ == "__main__":
    main()