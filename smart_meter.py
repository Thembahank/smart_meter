from utils import find_tty_usb, convert_to_str
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import time


class SmartMeter(object):

	"""
	1. Sets up a smart meter connection
	2. Specifies a serial port to connect to
	3. Methods to read and write data (to csv)
	"""

    def __init__(self, retries, com_method, baudrate,
                 stopbits, parity, bytesize, timeout):
    	"""Sets up parameters for modbus connection to the smart meter

    	Parameters
    	----------
    	retries :  The number of times a packet read request must be made, int
    	com_method : 'rtu' or 'ascii', string
    	baudrate : Baudrate set on the smart meter, eg. 19200, int
    	stopbits : Number of stopbits set on the smart meter, eg. 1, int
    	parity : Parity set on the smart meter, eg. 'N', string
    	bytesize : Size of packet, eg. 8, int
    	timeout : Number of seconds before a request times out, eg. 0.1, float
    	"""
        self.retries = retries
        self.com_method = com_method
        self.baudrate = baudrate
        self.stopbits = stopbits
        self.parity = parity
        self.bytesize = bytesize
        self.timeout = timeout

    def connect(self, vendor, product):
        """Connects to a specific port. The serial port on RPi is subject
        to change. Thus, a method finds the address of FT232 chip

        Parameters
        ----------
        vendor: string
        product: string

        """
        self.meter_port = find_tty_usb(vendor, product)
        print("Connecting to %s" % (self.meter_port))
        self.client = ModbusClient(
            retries=self.retries, method=self.com_method,
            baudrate=self.baudrate, stopbits=self.stopbits, parity=self.parity,
            bytesize=self.bytesize, timeout=self.timeout, port=self.meter_port)
        print("Connected to smart meter over: %s" % (self.client.port))

    def read_from_meter(self, meter_id, base_register, block_size,
                        params_indices):
        """Reads data from meter correpsonding to the param indices
        specified

        Parameters
        -----------

        meter_id : ID set on the meter (eg. 1, 2), int
        base_register : Base register for block of registers to read, int
        block_size : Number of register bytes in this block, int
        params_indices : List of indices relative to base_register, list

        Returns
        -------
        data: Comma separated values correpsonding to parameters whose indices
        were specified
        """
        binary_data = self.client.read_holding_registers(
            base_register, block_size, unit=meter_id)
        data = ""
        for i in range(0, (block_size - 1), 2):
            for j in params_indices:
                if(j == i):
                    data = data + str(int(time.time())) + "," + \
                        convert_to_str(
                            (binary_data.registers[i + 1] << 16) + binary_data.registers[i])

        data = data[:-1] + "\n"
        return data

    def write_csv(self, csv_path, data):
        """Writes a comma separted row of data into the csv

        Parameters
        ----------
        csv_path : Complete path of the CSV file
        data : string representation of row to write
        """
        with open(csv_path, 'a') as f:
            f.write(data)
