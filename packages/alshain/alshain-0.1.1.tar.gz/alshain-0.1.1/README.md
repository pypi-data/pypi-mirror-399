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

# Enable photometer source
dev.write( alshain.Pica.Parameters.PULSE_ENABLE, 1 )

# Read results
print( dev.read( alshain.Pica.Parameters.RESULT ) )

```

```python

# Strix SMU
import alshain
import serial
import sys

# Serial port as first command line parameter
com = serial.Serial( sys.argv[1], alshain.BAUDRATE, timeout = 5.0 )

smu = alshain.Strix( com, address = 1 )

voltage, current = smu.measure()

```

```python

# Sylphium eco laser driver
import alshain
import serial
import sys

# Serial port as first command line parameter
com = serial.Serial( sys.argv[1], alshain.BAUDRATE, timeout = 0.25 )

laser = alshain.Sylphium( com, address = 1 )

# Set driver operating range to 3A
laser.write( alshain.Sylphium.Parameters.IRANGE, alshain.Sylphium.Options.IRANGE_3A )

# Set laser diode drive voltage to 12 V
laser.write( alshain.Sylphium.Parameters.V_SET, 12.0 )

# Set diode current limit to 250mA
laser.write( alshain.Sylphium.Parameters.I_LIMIT, 250e-3 )

# Enable laser output
laser.enable_output( True )

# Use either external or internal modulation to drive the diode

# Disable laser
laser.enable_output( False )
```