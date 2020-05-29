import serial
import time
 
# Open grbl serial port
s = serial.Serial('/dev/ttyUSB7',115200)
 
# Open g-code file
f = open('NewG.gcode','r');
 
# Wake up grbl
s.write("\r\n\r\n")
time.sleep(2)   # Wait for grbl to initialize
s.flushInput()  # Flush startup text in serial input
 
# Stream g-code to grbl
for line in f:
    print line
    l = line.strip() # Strip all EOL characters for streaming
    if l == 'M2':
	data = 'G01 Z0'
	s.write(data + '\n')
    	print 'Sending: ' + data
	s.write(l + '\n') # Send g-code block to grbl
	print 'Sending: ' + l
	grbl_out = s.readline() # Wait for grbl response with carriage return
	print ' : ' + grbl_out.strip()
    else:
	s.write(l + '\n') # Send g-code block to grbl
	print 'Sending: ' + l
	grbl_out = s.readline() # Wait for grbl response with carriage return
	print ' : ' + grbl_out.strip()
    #time.sleep(1)
 
# Wait here until grbl is finished to close serial port and file.
#raw_input("  Press <Enter> to exit and disable grbl.")
# Close file and serial port
f.close()
s.close()
