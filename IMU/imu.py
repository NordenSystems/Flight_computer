from machine import I2C, Pin
from struct import unpack, pack

class IMU:
    def __init__(self, sda_pin, scl_pin, freq):
        # Initialze the I2C connection
        self.i2c = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=freq)

        # Accelerometer attributes
        self.ACCEL_ADDRESS = 0x19
        self.ACCEL_REG_CTRL1_A = 0x20
        self.ACCEL_REG_CTRL4_A = 0x23

        # Gyroscope attributes
        self.GYRO_ADDRESS = 0x69
        self.GYRO_REG_CTRL1 = 0x20
        self.GYRO_REG_OUT_X_L = 0x28
        
        # Magnetometer attributes
        self.MAG_ADDRESS = 0x1E
        self.MAG_REG_CTRL1 = 0x20
        self.MAG_REG_OUT_X_L = 0x28       # Wrong registry, reads \x10\x00\x00\x00\x00\x00

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
        self.i2c.writeto_mem(self.MAG_ADDRESS, self.MAG_REG_CTRL1, pack('B', 0x70))
        self.i2c.writeto_mem(self.MAG_ADDRESS, self.MAG_REG_CTRL1, pack('B', 0x70))

    def read_magnetometer_data(self):
        """Read raw magnetometer data."""
        data = self.i2c.readfrom_mem(self.MAG_ADDRESS, self.MAG_REG_OUT_X_L | 0x80, 6) # Wrong registry, reads \x10\x00\x00\x00\x00\x00
        x = unpack('<h', data[0:2])[0]
        y = unpack('<h', data[2:4])[0]
        z = unpack('<h', data[4:6])[0]
        return x, y, z

    def convert_to_gauss(self, raw_value, scale=6842):
        """Convert raw magnetometer data to gauss (example scale, check your sensor)."""
        raw_value = float(raw_value)  # Ensure it's a float for division
        scaled = raw_value / scale
        return scaled


    
    # Common methods
    def get_sensor_data(self):
        # Accelerometer
        raw_x, raw_y, raw_z = self.read_accelerometer_data()
        self.accel_x = self.convert_to_g(raw_x)
        self.accel_y = self.convert_to_g(raw_y)
        self.accel_z = self.convert_to_g(raw_z)

        # Gyroscope
        raw_gx, raw_gy, raw_gz = self.read_gyroscope_data()
        self.gyro_x = self.convert_to_dps(raw_gx)
        self.gyro_y = self.convert_to_dps(raw_gy)
        self.gyro_z = self.convert_to_dps(raw_gz)
        
        # Magnetometer
        raw_mx, raw_my, raw_mz = self.read_magnetometer_data()
        print(raw_mx)
        self.mag_x = self.convert_to_gauss(raw_mx)
        self.mag_y = self.convert_to_gauss(raw_my)
        self.mag_z = self.convert_to_gauss(raw_mz)
