import serial
import time
# Open grbl serial port
s = serial.Serial('/dev/ttyUSB0',115200)
#print "a"
# Open g-code file
f = open('/home/matteo/Scrivania/riritest3.gcode','r');
#for line in f:
#    print line
# Wake up grbl
s.write("$$\r\n\r\n")
s.flushInput()
s.write("$\r\n\r\n")
s.write("G90\r\n")
s.write("\r\n\r\n")
time.sleep(2) # Wait for grbl to initialize
s.flushInput() # Flush startup text in serial input
#print f.readlines()
# Stream g-code to grbl
for line in f:
    l = line.strip() # Strip all EOL characters for consistency
    #print "a"
    print 'Sending: ' + l,
    s.write(l + '\n') # Send g-code block to grbl
    grbl_out = s.readline() # Wait for grbl response with carriage return
    print ' : ' + grbl_out.strip()
# Wait here until grbl is finished to close serial port and file.
raw_input(" Press <Enter> to exit and disable grbl.")
# Close file and serial port
f.close()
s.close() 
