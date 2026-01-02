# Alshain
Python library for Alshain Oy devices

## Quick start

```python

# Pica photometer readout
import alshain
import serial
import sys

# Serial port as first command line parameter
com = serial.Serial( sys.argv[1], alshain.BAUDRATE, timeout = 0.25 )

dev = alshain.Pica( com, address = 1 )

dev.write( alshain.Pica.Parameters.PULSE_ENABLE, 1 )
print( dev.read( alshain.pica.Parameters.RESULT ) )

```

```python

# Strix SMU
import alshain
import serial
import sys

# Serial port as first command line parameter
com = serial.Serial( sys.argv[1], alshain.BAUDRATE, timeout = 0.25 )

smu = alshain.Strix( com, address = 1 )

voltage, current = smu.measure()

```