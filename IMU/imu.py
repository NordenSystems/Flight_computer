from machine import I2C, Pin
from struct import unpack, pack

class IMU:
    def __init__(self, sda_pin, scl_pin, freq, filter_size):
        self.i2c = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=freq)
        self.filter_size = filter_size

        # Accelerometer attributes
        self.accel_x_values = []
        self.accel_y_values = []
        self.accel_z_values = []
        self.ACCEL_ADDRESS = 0x19
        self.ACCEL_REG_CTRL1_A = 0x20
        self.ACCEL_REG_CTRL4_A = 0x23

        # Gyroscope attributes
        self.gyro_x_values = []
        self.gyro_y_values = []
        self.gyro_z_values = []
        self.GYRO_ADDRESS = 0x69
        self.GYRO_REG_CTRL1 = 0x20
        self.GYRO_REG_OUT_X_L = 0x28
        
        # Magnetometer attributes
        self.mag_x_values = []
        self.mag_y_values = []
        self.mag_z_values = []
        self.MAG_ADDRESS = 0x1E
        self.MAG_REG_CTRL1 = 0x20
        self.MAG_REG_OUT_X_L = 0x28

        # Configure all sensors
        self.configure_accelerometer()
        self.configure_gyroscope()
        self.configure_magnetometer()

    # Accelerometer methods
    def configure_accelerometer(self):
        self.i2c.writeto_mem(self.ACCEL_ADDRESS, self.ACCEL_REG_CTRL1_A, pack('B', 0x57))  # 100Hz, enable XYZ
        self.i2c.writeto_mem(self.ACCEL_ADDRESS, self.ACCEL_REG_CTRL4_A, pack('B', 0x00))  # ±2g

    def read_accelerometer_data(self):
        data = self.i2c.readfrom_mem(self.ACCEL_ADDRESS, 0x28 | 0x80, 6)
        x = unpack('<h', data[0:2])[0]
        y = unpack('<h', data[2:4])[0]
        z = unpack('<h', data[4:6])[0]
        return x, y, z

    def convert_to_g(self, raw_value, scale=16384):
        return raw_value / scale

    # Gyroscope methods
    def configure_gyroscope(self):
        self.i2c.writeto_mem(self.GYRO_ADDRESS, self.GYRO_REG_CTRL1, pack('B', 0x0F))  # Power on, 95Hz, enable XYZ

    def read_gyroscope_data(self):
        data = self.i2c.readfrom_mem(self.GYRO_ADDRESS, self.GYRO_REG_OUT_X_L | 0x80, 6)
        x = unpack('<h', data[0:2])[0]
        y = unpack('<h', data[2:4])[0]
        z = unpack('<h', data[4:6])[0]
        return x, y, z

    def convert_to_dps(self, raw_value, scale=16.4):
        """Convert raw gyroscope data to degrees per second (±500 dps range)."""
        return raw_value / scale

    # Magnetometer methods
    def configure_magnetometer(self):
        """Configure the magnetometer settings (check your sensor's datasheet)."""
        self.i2c.writeto_mem(self.MAG_ADDRESS, self.MAG_REG_CTRL1, pack('B', 0x70))  # Example config

    def read_magnetometer_data(self):
        """Read raw magnetometer data."""
        data = self.i2c.readfrom_mem(self.MAG_ADDRESS, self.MAG_REG_OUT_X_L | 0x80, 6)
        x = unpack('<h', data[0:2])[0]
        y = unpack('<h', data[2:4])[0]
        z = unpack('<h', data[4:6])[0]
        return x, y, z

    def convert_to_gauss(self, raw_value, scale=6842):
        """Convert raw magnetometer data to gauss (example scale, check your sensor)."""
        return raw_value / scale
    
    # Common methods
    def moving_average(self, data_list, new_value):
        data_list.append(new_value)
        if len(data_list) > self.filter_size:
            data_list.pop(0)
        return sum(data_list) / len(data_list)

    def get_sensor_data(self):
        # Accelerometer
        raw_x, raw_y, raw_z = self.read_accelerometer_data()
        accel_x = self.convert_to_g(raw_x)
        accel_y = self.convert_to_g(raw_y)
        accel_z = self.convert_to_g(raw_z)
        self.accel_x = self.moving_average(self.accel_x_values, accel_x)
        self.accel_y = self.moving_average(self.accel_y_values, accel_y)
        self.accel_z = self.moving_average(self.accel_z_values, accel_z)

        # Gyroscope
        raw_gx, raw_gy, raw_gz = self.read_gyroscope_data()
        gyro_x = self.convert_to_dps(raw_gx)
        gyro_y = self.convert_to_dps(raw_gy)
        gyro_z = self.convert_to_dps(raw_gz)
        self.gyro_x = self.moving_average(self.gyro_x_values, gyro_x)
        self.gyro_y = self.moving_average(self.gyro_y_values, gyro_y)
        self.gyro_z = self.moving_average(self.gyro_z_values, gyro_z)
        
        # Magnetometer
        raw_mx, raw_my, raw_mz = self.read_magnetometer_data()
        mag_x = self.convert_to_gauss(raw_mx)
        mag_y = self.convert_to_gauss(raw_my)
        mag_z = self.convert_to_gauss(raw_mz)
        self.mag_x = self.moving_average(self.mag_x_values, mag_x)
        self.mag_y = self.moving_average(self.mag_y_values, mag_y)
        self.mag_z = self.moving_average(self.mag_z_values, mag_z)

        return {
            "accel": {"x": self.accel_x, "y": self.accel_y, "z": self.accel_z},
            "gyro": {"x": self.gyro_x, "y": self.gyro_y, "z": self.gyro_z},
            "mag": {"x": self.mag_x, "y": self.mag_y, "z": self.mag_z},
        }
