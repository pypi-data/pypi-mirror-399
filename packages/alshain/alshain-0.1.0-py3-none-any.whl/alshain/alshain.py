#!/usr/bin/env python3

import struct
from typing import Tuple

__version__ = '0.1.0'

BAUDRATE = 460800

class Protocol:
    _MSG_LEN = 10

    # General
    OP_WRITE = 0x01
    OP_READ = 0x02

    OP_DFU = 0x7e
    OP_ERROR = 0x7f


    # Peregine2
    OP_MOVE_A = 0x05
    OP_MOVE_B = 0x06

    OP_STATUS_A = 0x07
    OP_STATUS_B = 0x08

    OP_ENABLE_A = 0x09
    OP_ENABLE_B = 0x0A

    OP_SET_POS_A = 0x0B
    OP_SET_POS_B = 0x0C

    FLAG_STATUS_ENABLED = 0x20

    # Strix
    OP_MEASURE  = 0x00
    OP_DRIVE_VOLTAGE  = 0x12
    OP_DRIVE_CURRENT  = 0x13

    OP_GET_TEMPERATURE = 0x14
    OP_RAW_VOLTAGES = 0x16

    OP_MEASURE_VOLTAGE = 0x09

    OP_MEASURE_CURRENT = 0x10
    OP_MEASURE_EXT = 0x11

    OP_RAW_ADC = 0x22
    OP_SELF_TEST = 0x21

    OP_READ_TRIGGER =			0x18
    OP_ASYNC_MEASURE_VOLTAGE =	0x30
    OP_ASYNC_MEASURE_CURRENT =	0x31
    OP_ASYNC_MEASURE_EXT =		0x32
    OP_ASYNC_DRIVE_VOLTAGE =	0x33
    OP_ASYNC_DRIVE_CURRENT =	0x34
    OP_ASYNC_START_SWEEP =		0x35

    OP_SET_OUTPUT = 			0x40
    OP_SET_LOW_CURRENT_MODE = 	0x41



    # I2C related
    OP_I2C_TEMP = 0x13
    OP_I2C_MEM_W = 0x19
    OP_I2C_MEM_R = 0x20
    OP_I2C_QUERY = 0x21


    # Functions to encode messages
    @staticmethod
    def gen_write_msg( addr: int, key: int, value: int ) -> bytes:
        return struct.pack( ">BBIi", addr, Protocol.OP_WRITE, key, value )

    @staticmethod
    def gen_write_float_msg( addr: int, key: int, value: float ) -> bytes:
        return struct.pack( ">BBIf", addr, Protocol.OP_WRITE, key, value )

    @staticmethod
    def gen_read_msg( addr: int, key: int) -> bytes:
        return struct.pack( ">BBIi", addr, Protocol.OP_READ, key, 0 )

    @staticmethod
    def gen_action_msg( addr: int, action: int, key: int, value: int ) -> bytes:
        return struct.pack( ">BBIi", addr, action, key, value )

    @staticmethod
    def gen_action_msg_float( addr: int, action: int, key: int, value: int ) -> bytes:
        return struct.pack( ">BBIf", addr, action, key, value )

    @staticmethod
    def gen_action_msg( addr: int, action: int, key: int, value: int ) -> bytes:
        return struct.pack( ">BBIi", addr, action, key, value )
    
    @staticmethod
    def gen_action_msg_mem( addr: int, action: int, key: int, value: int ) -> bytes:
        return struct.pack( ">BBII", addr, action, key, value )

    @staticmethod
    def gen_action_msg_mem_float( addr: int, action: int, key: int, value: int ) -> bytes:
        return struct.pack( ">BBIf", addr, action, key, value )

    # Peregrine2
    @staticmethod
    def gen_move_a_msg( addr, target, speed, accel ):
        return struct.pack( ">BBihH", addr, Protocol.OP_MOVE_A, target, speed, accel )

    @staticmethod
    def gen_move_b_msg( addr, target, speed, accel ):
        return struct.pack( ">BBihH", addr, Protocol.OP_MOVE_B, target, speed, accel )

    @staticmethod
    def gen_status_a_msg( addr ):
        return struct.pack( ">BBihH", addr, Protocol.OP_STATUS_A, 0, 0, 0 )
    
    @staticmethod
    def gen_status_b_msg( addr ):
        return struct.pack( ">BBihH", addr, Protocol.OP_STATUS_B, 0, 0, 0 )


    # Functions to decode message

    @staticmethod
    def decode_error( msg: bytes ) -> Tuple[int, int]:
        (addr, op, error, extra) = struct.unpack( ">BBIi", msg )
        return error, extra

    @staticmethod
    def decode_read( msg: bytes ) -> Tuple[int, int]:
        (addr, op, key, value) = struct.unpack( ">BBIi", msg )
        return key, value

    @staticmethod
    def decode_read_float( msg: bytes ) -> Tuple[int, float]:
        (addr, op, key, value) = struct.unpack( ">BBIf", msg )
        return key, value

    @staticmethod
    def decode_action( msg: bytes ) -> Tuple[int, int]:
        (addr, op, key, value) = struct.unpack( ">BBIi", msg )
        return key, value

    @staticmethod
    def decode_action_mem( msg: bytes ) -> Tuple[int, int]:
        (addr, op, key, value) = struct.unpack( ">BBII", msg )
        return key, value

    @staticmethod
    def decode_action_mem_float( msg: bytes ) -> Tuple[int, float]:
        (addr, op, key, value) = struct.unpack( ">BBIf", msg )
        return key, value

    @staticmethod
    def decode_header( msg: bytes ) -> Tuple[int, int]:
        (addr, op) = struct.unpack_from( ">BB", msg )
        
        return addr, op 


    # Peregine2
    # Functions to decode message
    @staticmethod
    def decode_flags( flags ):
        out = {}
        out["RUNNING"] = ((flags >> 0) & 0x01) > 0
        out["LIMIT+"] = ((flags >> 2) & 0x01) > 0
        out["LIMIT-"] = ((flags >> 3) & 0x01) > 0
        out["INPOS"] = ((flags >> 4) & 0x01) > 0
        out["EMG_STOP"] = ((flags >> 7) & 0x01) > 0
        
        return out

    @staticmethod
    def decode_status( msg ):
        (addr, op, position, speed, flags) = struct.unpack( ">BBihH", msg )
        return position, speed*10, Protocol.decode_flags( flags )

    # Strix
    @staticmethod
    def decode_measure( msg: bytes ) -> Tuple[float, float]:
        (addr, op, voltage, current) = struct.unpack( ">BBff", msg )
        return voltage, current



class MemoryMap:
    def __init__( self, device: object, start_address: int ) -> None:
        self.device = device
        self.start_address = start_address
    
    def __getitem__(self, addr: int) -> float:
        return self.device.read_float( self.start_address + addr )
    
    def __setitem__(self, addr: int, value: float) -> float:
        return self.device.write_float( self.start_address + addr, value )



# Base class for all device drivers
class Device( object ):
    def __init__( self, com: object, address: int ) -> None:
        self.com = com
        self.address = address
    

    def _clear_buffer( self ) -> None:
        if self.com.in_waiting > 0:
            self.com.read( self.com.in_waiting )

    def write( self, key: int|Tuple, value: int ) -> None:
        self._clear_buffer()

        if isinstance(key, tuple):
            index = int(key[0])
            if key[1] == int:
                self.com.write( Protocol.gen_write_msg( self.address, index, int(value) ) )
            elif key[1] == float:
                self.com.write( Protocol.gen_write_float_msg( self.address, index, value ) )
        else:
            self.com.write( Protocol.gen_write_msg( self.address, int(key), int(value) ) )

        response = self.com.read( Protocol._MSG_LEN )
        _, op = Protocol.decode_header( response )
        if op == Protocol.OP_ERROR:
            raise IndexError

    def write_float( self, key: int|Tuple, value: float ) -> None:
        self._clear_buffer()
        
        if isinstance(key, tuple):
            index = int(key[0])
            if key[1] == int:
                self.com.write( Protocol.gen_write_msg( self.address, index, int(value) ) )
            elif key[1] == float:
                self.com.write( Protocol.gen_write_float_msg( self.address, index, value ) )
        else:
            self.com.write( Protocol.gen_write_float_msg( self.address, int(key), value ) )


        response = self.com.read( Protocol._MSG_LEN )
        _, op = Protocol.decode_header( response )
        if op == Protocol.OP_ERROR:
            raise IndexError



    def read( self, key: int|Tuple ) -> int|float:
        self._clear_buffer()
        
        if isinstance(key, tuple):
            index = int(key[0])
            self.com.write( Protocol.gen_read_msg( self.address, index ) )
        else:
            self.com.write( Protocol.gen_read_msg( self.address, int( key ) ) )
        
        response = self.com.read( Protocol._MSG_LEN )
        
        _, op = Protocol.decode_header( response )
        if op == Protocol.OP_ERROR:
            raise IndexError
        
        if isinstance(key, tuple):
            if key[1] == int:
                key, value = Protocol.decode_read( response )
            elif key[1] == float:
                key, value = Protocol.decode_read_float( response )
        else:
            key, value = Protocol.decode_read( response )
        return value

    def read_float( self, key: int ) -> float:
        self._clear_buffer()
        
        if isinstance(key, tuple):
            index = int(key[0])
            self.com.write( Protocol.gen_read_msg( self.address, index ) )
        else:
            self.com.write( Protocol.gen_read_msg( self.address, int( key ) ) )
        
        response = self.com.read( Protocol._MSG_LEN )
        
        _, op = Protocol.decode_header( response )
        if op == Protocol.OP_ERROR:
            raise IndexError
        
        if isinstance(key, tuple):
            if key[1] == int:
                key, value = Protocol.decode_read( response )
            elif key[1] == float:
                key, value = Protocol.decode_read_float( response )
        else:
            key, value = Protocol.decode_read_float( response )
        
        return value

    def mem_write( self, addr: int, value: int ) -> int:
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg_mem( self.address, Protocol.OP_I2C_MEM_W, addr, value ) )
        response = self.com.read( 10 )
        _, value = Protocol.decode_action( response )
        return value 
    
    def mem_read( self, addr: int ) -> int:
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg( self.address, Protocol.OP_I2C_MEM_R, addr, 0 ) )
        response = self.com.read( Protocol._MSG_LEN )
        _, value = Protocol.decode_action_mem( response )
        return value 


    def mem_write_float( self, addr: int, value: float ) -> float:
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg_mem_float( self.address, Protocol.OP_I2C_MEM_W, addr, value ) )
        response = self.com.read( Protocol._MSG_LEN )
        _, value = Protocol.decode_action( response )
        return value 
    
    def mem_read_float( self, addr: int ) -> float:
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg( self.address, Protocol.OP_I2C_MEM_R, addr, 0 ) )
        response = self.com.read( Protocol._MSG_LEN )
        _, value = Protocol.decode_action_mem_float( response )
        return value
    
    def _reboot_to_dfu( self ):
        self._clear_buffer()    
        self.com.write( Protocol.gen_action_msg( self.address, Protocol.OP_DFU, 0, 0 ) )


# Pica readout
class Pica( Device ):

    # Parameters
    class Parameters:
        PULSE_ENABLE =           (0, int)
        RESULT =                 (1, float)

        V_LOW =                  (3, float)
        V_HIGH =                 (4, float)
        V_DIFF =                 (5, float)


        DAC_VOLTAGE =            (10, float)
        STATUS =                 (13, int)

        PULSE_AMPLITUDE =        (20, int)
        MEASUREMENT_RANGE =      (21, int)
        PULSE_BIAS =             (22, int)

        ANALOG_OUT_MODE =        (30, int)
        ANALOG_OUT_MIN =         (31, float)
        ANALOG_OUT_MAX =         (32, float)

        UPTIME =                 (61, int)
        FIRMWARE_VER =           (62, int)
        SERIAL_NUMBER =          (63, int)

        CALIB_COEFF_0 =           (100, float)
        CALIB_COEFF_1 =           (101, float)
        CALIB_COEFF_2 =           (102, float)
        CALIB_COEFF_3 =           (103, float)
    
    class Options:
        MODE_VOUT =                     (0)
        MODE_CURRENT_LOOP =             (1)

        STATUS_OK =                     (0)
        STATUS_ERROR =                  (1)

        RANGE_1024MV =                  (1024)
        RANGE_512MV =                   (512)
        RANGE_256MV =                   (256)

    class NVM:
        DEVICE_ADDRESS =          (4)
        PULSE_ENABLED =           (8)
        PULSE_AMPLITUDE =         (12)
        DAC_OFFSET =              (16)
        AVERAGES =                (20)
        ANALOG_OUT_MIN =          (24)
        ANALOG_OUT_MAX =          (28)
        MEASUREMENT_RANGE =       (32)
        SERIAL_NUMBER =           (36)
        PULSE_BIAS =              (40)

        CALIB_COEFF_0 =           (64)
        CALIB_COEFF_1 =           (68)
        CALIB_COEFF_2 =           (72)
        CALIB_COEFF_3  =          (76)
    
    def query_i2c( self, address: int ):
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg( self.address, Protocol.OP_I2C_QUERY, address, 0 ) )
        response = self.com.read( Protocol._MSG_LEN )
        _, value = Protocol.decode_read( response )
        return value


# Peregrine2 motion controller
class Peregrine2( Device ):
    class Parameters:
        ENCODER_A =       (0)
        ENCODER_B =       (1)
        POSITION_A =      (2)
        POSITION_B =      (3)

        TARGET_A =        (4)
        TARGET_B =        (5)

        STEPRATE_A =      (6)
        STEPRATE_B =      (7)

        ENABLED_A =       (8)
        ENABLED_B =       (9)
        

        PATH_A_T =        (10)
        PATH_A_T0 =       (11)
        PATH_A_T1 =       (12)
        PATH_A_T2 =       (13)

        PATH_B_T =        (14)
        PATH_B_T0 =       (15)
        PATH_B_T1 =       (16)
        PATH_B_T2 =       (17)

        PATH_A_X0 =       (18)
        PATH_A_X1 =       (19)
        PATH_B_X0 =       (20)
        PATH_B_X1 =       (21)

        LIMIT_A_MINUS =  (30)
        LIMIT_A_PLUS =   (31)
        LIMIT_B_MINUS =  (32)
        LIMIT_B_PLUS =   (33)


        LIMIT_A_MINUS_MODE = (34)
        LIMIT_A_PLUS_MODE = (35)
        LIMIT_B_MINUS_MODE = (36)
        LIMIT_B_PLUS_MODE = (37)


        DRIVE_CFG_A =   (40)
        DRIVE_CFG_B =   (41)

        MOTOR_DIR_A =   (42)
        MOTOR_DIR_B =   (43)


        ERROR_GAIN_A =  (50)
        LQR_K0_A =      (51)
        LQR_K1_A =      (52)
        DEADZONE_A =    (53)
        SLEWRATE_A =    (54)

        ERROR_GAIN_B =  (55)
        LQR_K0_B =      (56)
        LQR_K1_B =      (57)
        DEADZONE_B =    (58)
        SLEWRATE_B =    (59)

        EMG_STOP =       (70)
        # Peregrine sets EMG_STOP_LATCH to 1 when emergency stop activated. User must clear it manually.
        # Clears also in power loss
        EMG_STOP_LATCH = (71)


        IMON0 =         (100)
        IMON1 =         (101)
        A0 =            (102)
        A1 =            (103)
        A2 =            (104)
        VMON =          (105)

        GPIO0 =         (106)
        GPIO1 =         (107)

        IDAC1 =         (110)
        IDAC2 =         (111)

        MODULE_A =      (90)
        MODULE_B =      (91)


        HBRIDGE_PWM_A =   (92)
        HBRIDGE_PWM_B =   (93)

        FDIR_MAX_ERROR_A = (120)
        FDIR_STATE_A =     (121)
        
        FDIR_MAX_ERROR_B = (122)
        FDIR_STATE_B =     (123)

        ANALOG_THRESHOLD_0 =    (130)
        ANALOG_TH_0_HYST =      (131)
        ANALOG_TH_0_POS_A =     (132)
        ANALOG_TH_0_POS_B =     (133)
        ANALOG_TH_0_STATE =     (134)
        
        ANALOG_THRESHOLD_1 =    (135)
        ANALOG_TH_1_HYST =      (136)
        ANALOG_TH_1_POS_A =     (137)
        ANALOG_TH_1_POS_B =     (138)
        ANALOG_TH_1_STATE =     (139)

        SERVO_LOOP_ENABLED_A =    (140)
        SERVO_LOOP_ENABLED_B =    (141)


        USER_HOMED_A =       (2000)
        USER_HOMED_B =       (2001)
        USER_HOMED_STAGE =   (2002)

    class Options:
        MODULE_UNKNOWN =      (0)
        MODULE_STEPPER =      (1)
        MODULE_HBRIDGE =      (2)

        LIMIT_SWITCH_DISABLED =    (0)
        LIMIT_SWITCH_ENABLED =     (1)
        LIMIT_SWITCH_INVERTED =    (2)
    
    class NVM:
        DEVICE_ADDRESS =          (4)
    

    def read_temperature( self, key: int ) -> float:
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg( self.address, Protocol.OP_I2C_TEMP, int( key ), 0 ) )
        response = self.com.read( Protocol._MSG_LEN )
        
        _, op = Protocol.decode_header( response )
        if op == Protocol.OP_ERROR:
            raise IndexError
        
        key, value = Protocol.decode_read( response )
        return (value / 32) * 0.125

    def status_a( self ):
        self._clear_buffer()
        self.com.write( Protocol.gen_status_a_msg( self.address ) )
        response = self.com.read( Protocol._MSG_LEN )
        return Protocol.decode_status( response ) 

    def status_b( self ):
        self._clear_buffer()
        self.com.write( Protocol.gen_status_b_msg( self.address ) )
        response = self.com.read( Protocol._MSG_LEN )
        return Protocol.decode_status( response ) 

    def move_a( self, pos, speed, accel ):
        self._clear_buffer()
        self.com.write( Protocol.gen_move_a_msg( self.address, int(pos), int(speed/32), int(accel/32)  ) )
        response = self.com.read( Protocol._MSG_LEN )
        return Protocol.decode_status( response ) 

    def move_b( self, pos, speed, accel ):
        self._clear_buffer()
        self.com.write( Protocol.gen_move_b_msg( self.address, int(pos), int(speed/32), int(accel/32)  ) )
        response = self.com.read( Protocol._MSG_LEN )
        return Protocol.decode_status( response ) 
    
    def enable_a( self, mode: bool ):
        self._clear_buffer()
        
        if mode:
            self.com.write( Protocol.gen_action_msg( self.address, Protocol.OP_ENABLE_A, 0, 1 ) )
        else:
            self.com.write( Protocol.gen_action_msg( self.address, Protocol.OP_ENABLE_A, 0, 0 ) )
        _ = self.com.read( Protocol._MSG_LEN )

    def enable_b( self, mode: bool ):
        self._clear_buffer()
        
        if mode:
            self.com.write( Protocol.gen_action_msg( self.address, Protocol.OP_ENABLE_B, 0, 1 ) )
        else:
            self.com.write( Protocol.gen_action_msg( self.address, Protocol.OP_ENABLE_B, 0, 0 ) )
        _ = self.com.read( Protocol._MSG_LEN )

    def set_position_a( self, position: int ):
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg( self.address, Protocol.OP_SET_POS_A, 0, position ) )
        _ = self.com.read( Protocol._MSG_LEN )

    def set_position_b( self, position: int ):
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg( self.address, Protocol.OP_SET_POS_B, 0, position ) )
        _ = self.com.read( Protocol._MSG_LEN )



# Strix SMU
class Strix( Device ):
    class Parameters:
        AUTORANGING =         (0, int)
        COMPLIANCE_VOLTAGE =  (1, float)
        COMPLIANCE_CURRENT =  (2, float)
        AVERAGES =            (3, int)
        TRIGGER_MODE =        (4, int)

        FOURWIRE_MODE =       (5, int)
        GUARD_MODE =          (6, int)

        THERMAL_MODE =        (7, int)
        TEMPCO_MODE =         (8, int)

        PLC_SYNC_MODE =       (9, int)

        ADC_VOLTAGE_GAIN =    (10, int)
        LARGE_CURRENT_GAIN =  (11, int)
        EXT_VOLTAGE_GAIN =    (12, int)

        HEATER_TARGET =       (13, float)

        ADC_SAMPLERATE =      (14, int)

        ASYNC_STATE =         (15, int)

        ASYNC_RETRIGGER =     (16, int)

        DATA_MAX_COUNT =      (17, int)

        HEATER_STATE =        (18, int)

        ASYNC_CHANNEL =       (19, int)


        COMP_VDRIVE_DIV10_0 = (20, float)
        COMP_VDRIVE_DIV10_1 = (21, float)
        COMP_VDRIVE_DIV10_2 = (22, float)
        COMP_VDRIVE_DIV10_3 = (23, float)

        COMP_VDRIVE_1X_0 = (24, float)
        COMP_VDRIVE_1X_1 = (25, float)
        COMP_VDRIVE_1X_2 = (26, float)
        COMP_VDRIVE_1X_3 = (27, float)

        COMP_VDRIVE_10X_0 = (28, float)
        COMP_VDRIVE_10X_1 = (29, float)
        COMP_VDRIVE_10X_2 = (30, float)
        COMP_VDRIVE_10X_3 = (31, float)


        COMP_VMEAS_1X_0 = (32, float)
        COMP_VMEAS_1X_1 = (33, float)
        COMP_VMEAS_1X_2 = (34, float)
        COMP_VMEAS_1X_3 = (35, float)

        COMP_VMEAS_8X_0 = (36, float)
        COMP_VMEAS_8X_1 = (37, float)
        COMP_VMEAS_8X_2 = (38, float)
        COMP_VMEAS_8X_3 = (39, float)

        COMP_VMEAS_64X_0 = (40, float)
        COMP_VMEAS_64X_1 = (41, float)
        COMP_VMEAS_64X_2 = (42, float)
        COMP_VMEAS_64X_3 = (43, float)

        COMP_IMEAS_1_0 = (44, float)
        COMP_IMEAS_1_1 = (45, float)
        COMP_IMEAS_1_2 = (46, float)
        COMP_IMEAS_1_3 = (47, float)

        COMP_IMEAS_2_0 = (48, float)
        COMP_IMEAS_2_1 = (49, float)
        COMP_IMEAS_2_2 = (50, float)
        COMP_IMEAS_2_3 = (51, float)

        COMP_IMEAS_3_0 = (52, float)
        COMP_IMEAS_3_1 = (53, float)
        COMP_IMEAS_3_2 = (54, float)
        COMP_IMEAS_3_3 = (55, float)

        COMP_IMEAS_4_0 = (56, float)
        COMP_IMEAS_4_1 = (57, float)
        COMP_IMEAS_4_2 = (58, float)
        COMP_IMEAS_4_3 = (59, float)


        COMP_IDRIVE_1_0 = (60, float)
        COMP_IDRIVE_1_1 = (61, float)
        COMP_IDRIVE_1_2 = (62, float)
        COMP_IDRIVE_1_3 = (63, float)

        COMP_IDRIVE_2_0 = (64, float)
        COMP_IDRIVE_2_1 = (65, float)
        COMP_IDRIVE_2_2 = (66, float)
        COMP_IDRIVE_2_3 = (67, float)

        COMP_IDRIVE_3_0 = (68, float)
        COMP_IDRIVE_3_1 = (69, float)
        COMP_IDRIVE_3_2 = (70, float)
        COMP_IDRIVE_3_3 = (71, float)

        COMP_IDRIVE_4_0 = (72, float)
        COMP_IDRIVE_4_1 = (73, float)
        COMP_IDRIVE_4_2 = (74, float)
        COMP_IDRIVE_4_3 = (75)

        TEMPCO_VDRIVE_DIV10_GAIN =  (76, float)
        TEMPCO_VDRIVE_DIV10_T0 =    (77, float)

        TEMPCO_VDRIVE_1X_GAIN =     (78, float)
        TEMPCO_VDRIVE_1X_T0 =       (79, float)

        TEMPCO_VDRIVE_10X_GAIN =    (80, float)
        TEMPCO_VDRIVE_10X_T0 =      (81, float)

        TEMPCO_VMEAS_1X_GAIN =      (82, float)
        TEMPCO_VMEAS_1X_T0 =        (83, float)

        TEMPCO_VMEAS_8X_GAIN =      (84, float)
        TEMPCO_VMEAS_8X_T0 =        (85, float)

        TEMPCO_VMEAS_64X_GAIN =     (86, float)
        TEMPCO_VMEAS_64X_T0 =       (87, float)

        TEMPCO_IMEAS_1_GAIN =       (88, float)
        TEMPCO_IMEAS_1_T0 =         (89, float)

        TEMPCO_IMEAS_2_GAIN =       (90, float)
        TEMPCO_IMEAS_2_T0 =         (91, float)

        TEMPCO_IMEAS_3_GAIN =       (92, float)
        TEMPCO_IMEAS_3_T0 =         (93, float)

        TEMPCO_IMEAS_4_GAIN =       (94, float)
        TEMPCO_IMEAS_4_T0 =         (95, float)

        TEMPCO_IDRIVE_1_GAIN =       (96, float)
        TEMPCO_IDRIVE_1_T0 =         (97, float)

        TEMPCO_IDRIVE_2_GAIN =       (98, float)
        TEMPCO_IDRIVE_2_T0 =         (99, float)

        TEMPCO_IDRIVE_3_GAIN =       (100, float)
        TEMPCO_IDRIVE_3_T0 =         (101, float)

        TEMPCO_IDRIVE_4_GAIN =       (102, float)
        TEMPCO_IDRIVE_4_T0 =         (103, float)

        COMP_4W_VMEAS_0 =             (104, float)
        COMP_4W_VMEAS_1 =             (105, float)
        COMP_4W_VMEAS_2 =             (106, float)
        COMP_4W_VMEAS_3 =             (107, float)

        COMP_4W_VDRIVE_0 =             (108, float)
        COMP_4W_VDRIVE_1 =             (109, float)
        COMP_4W_VDRIVE_2 =             (110, float)
        COMP_4W_VDRIVE_3 =             (111, float)

        TEMPCO_4W_VMEAS_GAIN =        (112, float)
        TEMPCO_4W_VMEAS_T0 =          (113, float)

        TEMPCO_4W_VDRIVE_GAIN =        (114, float)
        TEMPCO_4W_VDRIVE_T0 =          (115, float)


        COMP_VEXT_1X_0 =             (116, float)
        COMP_VEXT_1X_1 =             (117, float)
        COMP_VEXT_1X_2 =             (118, float)
        COMP_VEXT_1X_3 =             (119, float)

        COMP_VEXT_8X_0 =             (120, float)
        COMP_VEXT_8X_1 =             (121, float)
        COMP_VEXT_8X_2 =             (122, float)
        COMP_VEXT_8X_3 =             (123, float)

        COMP_VEXT_64X_0 =             (124, float)
        COMP_VEXT_64X_1 =             (125, float)
        COMP_VEXT_64X_2 =             (126, float)
        COMP_VEXT_64X_3 =             (127, float)

        TEMPCO_VEXT_1X_GAIN =        (128, float)
        TEMPCO_VEXT_1X_T0 =          (129, float)

        TEMPCO_VEXT_8X_GAIN =        (130, float)
        TEMPCO_VEXT_8X_T0 =          (131, float)

        TEMPCO_VEXT_64X_GAIN =        (132, float)
        TEMPCO_VEXT_64X_T0 =          (133, float)

        COMPLIANCE_MODE =     (134, int)
        ASYNC_SWEEP_DWELL =   (135, int)
        SERIAL_NUMBER =       (136, int)
        FIRMWARE_VER =		  (137, int)
        UPTIME =			  (138, int)

        DATA_PTR =             (139, int)
        DATA_START =           (140, int)
        DATA_IN_START =        (140, int)
        DATA_OUT_START =       (440, int)

        IDAC_CURRENT  =  (697, int)
        CVC_GAIN      =  (698, int)
        OUTPUT_STATE  =  (699, int)


    class Options:
        DISABLE_4WIRE_MODE = 0
        ENABLE_4WIRE_MODE = 1

        GUARD_MODE_DRIVE = 0
        GUARD_MODE_SENSE = 1

        AUTORANGING_ON = 0
        AUTORANGING_OFF = 1

        MODE_TRIGGER_FREE =           (0)
        MODE_TRIGGER_50Hz =           (1)
        MODE_TRIGGER_60Hz =           (2)
        MODE_TRIGGER_EDGE_SINGLE_1 =  (3)
        MODE_TRIGGER_EDGE_SYNC_1 =    (4)
        MODE_TRIGGER_EDGE_SINGLE_2 =  (5)
        MODE_TRIGGER_EDGE_SYNC_2 =    (6)

        MODE_TRIGGER_EDGE_SINGLE_12 = (7)
        MODE_TRIGGER_EDGE_SYNC_12 =   (8)

        SET_TRIGGER_1 =           (1)
        SET_TRIGGER_2 =           (2)
        SET_TRIGGER_12 =          (3)
        RELEASE_TRIGGER_1 =       (4)
        RELEASE_TRIGGER_2 =       (5)
        RELEASE_TRIGGER_12 =      (6)

        MODE_HEATER_OFF = 0
        MODE_HEATER_AUTO = 1

        MODE_TEMPCO_OFF =         (0)
        MODE_TEMPCO_ON =          (1)

        MODE_RETRIGGER_SINGLE =   (0)
        MODE_RETRIGGER_BURST =    (1)
        MODE_RETRIGGER_LOOP =     (2)
        MODE_RETRIGGER_SWEEP =    (3)

        MODE_PLC_SYNC_NONE =         (0)
        MODE_PLC_SYNC_50HZ =         (1)
        MODE_PLC_SYNC_60HZ =         (2)




        ASYNC_IDLE =					(0)
        ASYNC_M_WAIT_TRIGGER_EDGE = 	(1)
        ASYNC_M_AUTORANGING =			(2)
        ASYNC_M_WAIT_SYNC_TRIGGER =		(3)
        ASYNC_M_PLC_SYNC =				(4)
        ASYNC_M_READ_ADC =				(5)

        ASYNC_DV_WAIT_TRIGGER_EDGE = 	(10)
        ASYNC_DV_SET_DRIVE =			(11)

        ASYNC_DC_WAIT_TRIGGER_EDGE = 	(20)
        ASYNC_DC_SET_DRIVE =			(21)
        ASYNC_DWELL =					(30)

        ASYNC_CHANNEL_VOLTAGE =			(0)
        ASYNC_CHANNEL_CURRENT =			(1)
        ASYNC_CHANNEL_EXT =				(2)


        MODE_COMPLIANCE_LIMIT =   (0)
        MODE_COMPLIANCE_DISABLE_OUTPUT = (1)

        OUTPUT_DISABLED =         (0)
        OUTPUT_ENABLED =          (1)

        LOW_CURRENT_MODE_OFF =   (0)
        LOW_CURRENT_MODE_ON  =   (1)

        IDAC_CURRENT_OFF =		(0)
        IDAC_CURRENT_10uA =		(1)
        IDAC_CURRENT_50uA =  	(2)
        IDAC_CURRENT_100uA =  	(3)
        IDAC_CURRENT_250uA =  	(4)
        IDAC_CURRENT_500uA =  	(5)
        IDAC_CURRENT_1000uA =  	(6)
        IDAC_CURRENT_1500uA =  	(7)
    

    class NVM:
        DEVICE_ADDRESS =         (4)
        SERIAL_NUMBER =          (8)

    def __init__(self, com, address, classic: bool = False ):
        super().__init__(com, address)
        self.data = MemoryMap( self, Strix.Parameters.DATA_START )
        self.is_classic = classic
    

    def set_drive_voltage( self, voltage: float ) -> float:
        self._clear_buffer()
        
        if self.is_classic:
            voltage = -voltage

        self.com.write( Protocol.gen_action_msg_float( self.address, Protocol.OP_DRIVE_VOLTAGE, 0, voltage ) )
        response = self.com.read( Protocol._MSG_LEN )
        _, value = Protocol.decode_action( response )
        return value 

    def set_drive_current( self, current: float ) -> float:
        self._clear_buffer()

        if self.is_classic:
            current = -current

        self.com.write( Protocol.gen_action_msg_float( self.address, Protocol.OP_DRIVE_CURRENT, 0, current ) )
        response = self.com.read( Protocol._MSG_LEN )
        _, value = Protocol.decode_action( response )
        return value 

    def measure( self ) -> Tuple[float, float]:
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg_float( self.address, Protocol.OP_MEASURE, 0, 0 ) )
        response = self.com.read( Protocol._MSG_LEN )
        voltage, current = Protocol.decode_measure( response )

        if self.is_classic:
            voltage, current = -voltage, -current

        return voltage, current

    def get_temperature( self ) -> Tuple[float, float]:
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg_float( self.address, Protocol.OP_GET_TEMPERATURE, 0, 0 ) )
        response = self.com.read( Protocol._MSG_LEN )
        key, value = Protocol.decode_action( response )
        temp_driver = value * 0.0078125
        temp_adc = key * 0.03125
        return temp_driver, temp_adc
    
    def get_raw_voltages( self ) -> Tuple[float, float]:
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg_float( self.address, Protocol.OP_RAW_VOLTAGES, 0, 0 ) )
        response = self.com.read( Protocol._MSG_LEN )
        voltage, current = Protocol.decode_measure( response )
        return voltage, current


    def measure_voltage( self ) -> float:
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg_float( self.address, Protocol.OP_MEASURE_VOLTAGE, 0, 0 ) )
        response = self.com.read( Protocol._MSG_LEN )
        voltage, current = Protocol.decode_measure( response )
        return voltage
    
    def measure_current( self ) -> float:
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg_float( self.address, Protocol.OP_MEASURE_CURRENT, 0, 0 ) )
        response = self.com.read( Protocol._MSG_LEN )
        voltage, current = Protocol.decode_measure( response )

        if self.is_classic:
            current = -current

        return current

    def _read_raw_adc( self, cfg: int ) -> Tuple[int, int]:
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg( self.address, Protocol.OP_RAW_ADC, cfg, 0 ) )
        response = self.com.read( Protocol._MSG_LEN )
        key, value = Protocol.decode_action( response )
        return key, value

    def _self_test( self ) -> Tuple[float, float]:
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg( self.address, Protocol.OP_SELF_TEST, 0, 0 ) )
        response = self.com.read( Protocol._MSG_LEN )
        v_avdd, v_ref = Protocol.decode_measure( response )
        
        return v_avdd*4, v_ref*4 - v_avdd

    def self_test( self ):
        l_vavdd = []
        l_vref = []
        for i in range( 4 ):
            v_vadd, v_ref = self._self_test()
            l_vavdd.append( v_vadd )
            l_vref.append( v_ref )

        min_vref = min( l_vref )
        max_vref = max( l_vref )

        min_vavdd = min( l_vavdd )
        max_vavdd = max( l_vavdd )

        vref_pp = max_vref - min_vref
        vavdd_pp = max_vavdd - min_vavdd

        print("vref:", l_vref[-1], "vref_pp", vref_pp)
        print("vavdd:", l_vavdd[-1], "vavdd_pp", vavdd_pp)

        if l_vref[-1] < 2.4:
            return False
        
        if l_vavdd[-1] < 4.8:
            return False

        if vref_pp > 0.02:
            return False
        
        if vavdd_pp > 0.01:
            return False

        return True
        

    def measure_ext( self ) -> float:
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg_float( self.address, Protocol.OP_MEASURE_EXT, 0, 0 ) )
        response = self.com.read( Protocol._MSG_LEN )
        voltage, current = Protocol.decode_measure( response )
        return voltage

    def async_set_drive_voltage( self, voltage: float ) -> int:
        self._clear_buffer()

        if self.is_classic:
            voltage = -voltage

        self.com.write( Protocol.gen_action_msg_float( self.address, Protocol.OP_ASYNC_DRIVE_VOLTAGE, 0, voltage ) )
        response = self.com.read( Protocol._MSG_LEN )
        key, value = Protocol.decode_action( response )
        return value 

    def async_set_drive_current( self, current: float ) -> int:
        self._clear_buffer()
        
        if self.is_classic:
            current = -current

        self.com.write( Protocol.gen_action_msg_float( self.address, Protocol.OP_ASYNC_DRIVE_CURRENT, 0, current ) )
        response = self.com.read( Protocol._MSG_LEN )
        key, value = Protocol.decode_action( response )
        return value 


    def is_async_done( self ) -> bool:
        async_state = self.read( Strix.Parameters.ASYNC_STATE )
        return async_state == Strix.Options.ASYNC_IDLE


    def async_measure_voltage( self ) -> None:
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg_float( self.address, Protocol.OP_ASYNC_MEASURE_VOLTAGE, 0, 0 ) )
        response = self.com.read( Protocol._MSG_LEN )
        voltage, current = Protocol.decode_measure( response )
        
    def async_measure_current( self ) -> None:
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg_float( self.address, Protocol.OP_ASYNC_MEASURE_CURRENT, 0, 0 ) )
        response = self.com.read( Protocol._MSG_LEN )
        voltage, current = Protocol.decode_measure( response )

    def async_measure_ext( self ) -> None:
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg_float( self.address, Protocol.OP_ASYNC_MEASURE_EXT, 0, 0 ) )
        response = self.com.read( Protocol._MSG_LEN )
        voltage, current = Protocol.decode_measure( response )

    def async_start_sweep( self, read_channel: int, write_channel: int  ) -> None:
        self._clear_buffer()
        
        self.com.write( Protocol.gen_action_msg_float( self.address, Protocol.OP_ASYNC_START_SWEEP, read_channel, write_channel ) )
        response = self.com.read( Protocol._MSG_LEN )
        voltage, current = Protocol.decode_measure( response )

    def enable_output( self, output_state: bool ) -> None:
        self._clear_buffer()
        
        if output_state:
            self.com.write( Protocol.gen_action_msg( self.address, Protocol.OP_SET_OUTPUT, 1, 1 ) )
        else:
            self.com.write( Protocol.gen_action_msg( self.address, Protocol.OP_SET_OUTPUT, 0, 0 ) )
            
        response = self.com.read( Protocol._MSG_LEN )
        key, value = Protocol.decode_action( response )
    
    def set_low_current_mode( self, mode: bool ) -> None:
        self._clear_buffer()
        
        if mode:
            self.com.write( Protocol.gen_action_msg( self.address, Protocol.OP_SET_LOW_CURRENT_MODE, 1, 1 ) )
        else:
            self.com.write( Protocol.gen_action_msg( self.address, Protocol.OP_SET_LOW_CURRENT_MODE, 0, 0 ) )
            
        response = self.com.read( Protocol._MSG_LEN )
        key, value = Protocol.decode_action( response )



# Led Driver
class LedDriver( Device ):
    class Parameters:
        VMON =            (1, float)
        CURRENT_RANGE =   (2, int)

        CH0_VALUE =       (10, int)
        CH0_CURRENT =     (11, float)


        CH1_VALUE =       (20, int)
        CH1_CURRENT =     (21, float)

        TEMPERATURE =     (3, float)


    class NVM:
        DEVICE_ADDRESS =   (4)


