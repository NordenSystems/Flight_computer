from machine import UART


class GPS:
    def __init__(self, uart_id, tx, rx, baudrate, filter_size):
        self.uart = UART(uart_id, baudrate=baudrate, tx=tx, rx=rx)
        self.latitude_filter = []
        self.longitude_filter = []
        self.FILTER_SIZE = filter_size
        self.latitude = 0
        self.longitude = 0
        self.time = 0
        self.status = "Invalid"
        self.latitude_filtered_unrounded = 0
        self.longitude_filtered_unrounded = 0

    @staticmethod
    def calculate_checksum(nmea_sentence):
        """
        Calculate the checksum of an NMEA sentence.
        """
        checksum = 0
        for char in nmea_sentence:
            checksum ^= ord(char)  # XOR each character
        hex_checksum = f"{checksum:02X}"  # Format checksum as 2-character uppercase hexadecimal
        return hex_checksum

    def validate_nmea_sentence(self, sentence):
        """
        Validate the checksum of an NMEA sentence.
        """
        if "*" in sentence:
            data, received_checksum = sentence.split("*")
            calculated_checksum = self.calculate_checksum(data[1:])  # Exclude the starting '$'
            return received_checksum.upper() == calculated_checksum.upper()
        return False

    @staticmethod
    def convert_to_decimal_degrees(value, direction):
        """
        Convert NMEA latitude/longitude to decimal degrees.
        """
        if not value:
            return None
        if len(value) >= 11:  # Longitude
            degrees = int(value[:3])
            minutes = float(value[3:])
        else:  # Latitude
            degrees = int(value[:2])
            minutes = float(value[2:])
        decimal_degrees = degrees + (minutes / 60.0)
        if direction in ['S', 'W']:
            decimal_degrees = -decimal_degrees
        return decimal_degrees

    def apply_filter(self, value, value_filter):
        """
        Apply a moving average filter.
        """
        value_filter.append(value)
        if len(value_filter) > self.FILTER_SIZE:
            value_filter.pop(0)
        return sum(value_filter) / len(value_filter)

    def read_nmea_sentence(self):
        """
        Read and validate an NMEA sentence from the GPS module.
        """
        if self.uart.any():
            line = self.uart.readline()
            try:
                sentence = line.decode('utf-8').strip()
                if sentence.startswith("$") and self.validate_nmea_sentence(sentence):
                    return sentence
            except UnicodeError:
                pass
        return None

    def get_gps_data(self):
        """
        Retrieve and filter latitude and longitude data from $GPGLL sentences.
        """
        nmea_sentence = self.read_nmea_sentence()
        if nmea_sentence and nmea_sentence.startswith("$GPGLL"):
            fields = nmea_sentence.split(",")
            if len(fields) >= 7:
                raw_latitude = fields[1]
                ns_indicator = fields[2]
                raw_longitude = fields[3]
                ew_indicator = fields[4]
                time_utc = fields[5]
                status = fields[6]

                latitude_raw = self.convert_to_decimal_degrees(raw_latitude, ns_indicator)
                longitude_raw = self.convert_to_decimal_degrees(raw_longitude, ew_indicator)

                if latitude_raw is not None and longitude_raw is not None:
                    self.latitude_filtered_unrounded = self.apply_filter(latitude_raw, self.latitude_filter)
                    self.longitude_filtered_unrounded = self.apply_filter(longitude_raw, self.longitude_filter)
                
                self.time = time_utc
                self.latitude = round(self.latitude_filtered_unrounded, 6)
                self.longitude = round( self.longitude_filtered_unrounded, 6)
                self.status = "Valid" if status == 'A' else "Invalid"

                return
        return

'''
# Example usage
if __name__ == "__main__":
    print("Initializing GPS...")
    gps = GPS(2, PinDef.GPS_write, PinDef.GPS_read, 9600, 10)

    while True:
        gps_data = gps.get_gps_data()
        if gps_data:
            print(f"Time (UTC): {gps_data['time_utc']}")
            print(f"Raw Latitude: {gps_data['latitude_raw']}, Filtered Latitude: {gps_data['latitude_filtered']}")
            print(f"Raw Longitude: {gps_data['longitude_raw']}, Filtered Longitude: {gps_data['longitude_filtered']}")
            print(f"Status: {gps_data['status']}")
        time.sleep(0.05)
'''