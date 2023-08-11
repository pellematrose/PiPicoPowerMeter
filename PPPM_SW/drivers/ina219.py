# Inspired from
# https://github.com/vantonyan/pico-micropython-examples/tree/VCP_Demo/Power_meter
# Completed by Per-Simon Saal

from micropython import const
import math

class ina219:
    
    REG_CONFIG = 0x00			#R/W
    REG_SHUNTVOLTAGE = 0x01		#R
    REG_BUSVOLTAGE = 0x02		#R
    REG_POWER = 0x03			#R
    REG_CURRENT = 0x04			#R
    REG_CALIBRATION = 0x05		#R/W

    def __init__(self, address, iic):
        self.address = address
        self.i2c = iic
        
    def vshunt(self):
        # Read Shunt register 1, 2 bytes
        reg_bytes = self.i2c.readfrom_mem(self.address, ina219.REG_SHUNTVOLTAGE, 2)
        reg_value = int.from_bytes(reg_bytes, 'big')
        if reg_value > 2**15: #negative
            sign = -1
            for i in range(16): 
                reg_value = (reg_value ^ (1 << i))
        else:
            sign = 1
        return (float(reg_value) * 1e-4 * sign) #1e-4
    
    def current(self):
        # Read current register
        reg_bytes = self.i2c.readfrom_mem(self.address, ina219.REG_CURRENT, 2)
        reg_value = int.from_bytes(reg_bytes, 'big')
        
        if reg_value > 2**15: #negative
            sign = -1
            for i in range(16): 
                reg_value = (reg_value ^ (1 << i))
        else:
            sign = 1
        return reg_value * current_lsb
    
    def vbus(self):
        # Read Vbus voltage
        reg_bytes = self.i2c.readfrom_mem(self.address, ina219.REG_BUSVOLTAGE, 2)
        reg_value = int.from_bytes(reg_bytes, 'big') >> 3
        return float(reg_value) * 0.004
    
    def power(self):
        # Read Power register
        reg_bytes = self.i2c.readfrom_mem(self.address, ina219.REG_POWER, 2)
        reg_value = int.from_bytes(reg_bytes, 'big')
        return float(reg_value) * 20 * current_lsb
        
    def configure(self, shunt, BRNG, PG, BADC, SADC, MODE):
        global current_lsb
        
        if PG == 0x03:
            pg = 0.32
        elif PG == 0x02:
            pg = 0.16
        elif PG == 0x01:
            pg = 0.08
        elif PG == 0x00:
            pg = 0.04
        else:
            pg = 0.32
                
        max_i = pg/shunt
        current_lsb = math.ceil((max_i/2**15)*1e5)/1e5 # round up 5th decimal place
        
        cal_reg_val = math.ceil(0.04096/(current_lsb*shunt))
        cal_reg_bytes = cal_reg_val.to_bytes(2, 'big')
        #print("CAL REG: %d" % cal_reg_val)
        
        config_reg = BRNG << 13 | PG << 11 | BADC << 7 | SADC << 3 | MODE
        config_bytes = config_reg.to_bytes(2, 'big')
        
        #print("Cal_reg_val: %d" % cal_reg_val)
        #i2c.writeto_mem(conf.address, conf.REG_CONFIG, b'\x01\x9F') # PG = 1 40mV
        #i2c.writeto_mem(conf.address, conf.REG_CONFIG, b'\x09\x9F') # PG = /2 80mV
        self.i2c.writeto_mem(self.address, ina219.REG_CONFIG, config_bytes) # PG = /8 320mV
        #self.i2c.writeto_mem(self.address, ina219.REG_CALIBRATION, b'\x00\x00')
        self.i2c.writeto_mem(self.address, ina219.REG_CALIBRATION, cal_reg_bytes)
        
