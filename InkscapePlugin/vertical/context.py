from math import *
import sys

class GCodeContext:
    def __init__(self, xy_feedrate, z_feedrate, start_delay, stop_delay, pen_up_angle, pen_down_angle, z_height, finished_height,distance, x_home, y_home, register_pen, num_pages, continuous, file):
      self.xy_feedrate = xy_feedrate
      self.z_feedrate = z_feedrate
      self.start_delay = start_delay
      self.stop_delay = stop_delay
      self.pen_up_angle = pen_up_angle
      self.pen_down_angle = pen_down_angle
      self.z_height = z_height
      self.finished_height = finished_height
      self.distance = distance
      self.x_home = x_home
      self.y_home = y_home
      self.register_pen = register_pen
      self.num_pages = num_pages
      self.continuous = continuous
      self.file = file
      
      self.drawing = False
      self.last = None

      self.preamble = [
        #"(Scribbled version of %s @ %.2f)" % (self.file, self.xy_feedrate),
        #"( %s )" % " ".join(sys.argv),
        "G17 G20 G90 G94 G54\r\n",
        "G21 (metric ftw)\r\n",
        "$100=85\r\n",
        "$101=85\r\n",
        "G92 X0.0 Y%0.2f\r\n" % self.distance,
        "M03 (pen up)\r\n",
        "G00 X300.0 Y300.0\r\n",
        #"G90 (absolute mode)",
        #"G92 X%.2f Y%.2f Z%.2f (you are here)" % (self.x_home, self.y_home, self.z_height),
        ""
      ]

      self.postscript = [
        "",
				"(end of print job)\r\n",
				#"M300 S%0.2F (pen up)" % self.pen_up_angle,
				#"G4 P%d (wait %dms)" % (self.stop_delay, self.stop_delay),
				"G00 X300.0 Y300.0\r\n",
				#"G1 Z%0.2F F%0.2F (go up to finished level)" % (self.finished_height, self.z_feedrate),
				#"G1 X%0.2F Y%0.2F F%0.2F (go home)" % (self.x_home, self.y_home, self.xy_feedrate),
                #"M300 S255 (turn off servo)",
				#"M18 (drives off)",
      ]

      self.registration = [
        #"M400 S100",
        #"M401 S100",
        #"M17 (engage drives if YES, and continue)",
        #"M300 S%d (pen down)" % (self.pen_down_angle),
        #"G4 P%d (wait %dms)" % (self.start_delay, self.start_delay),
        #"M300 S%d (pen up)" % (self.pen_up_angle),
        #"G4 P%d (wait %dms)" % (self.stop_delay, self.stop_delay),
        #"M18 (disengage drives)",
        #"M01 (Was registration test successful?)",
        "\r\n"
      ]

      self.sheet_header = [
        "(start of sheet header)\r\n",
        "G92 X%.2f Y%.2f Z%.2f (you are here)\r\n" % (self.x_home, self.y_home, self.z_height),
      ]
      if self.register_pen == 'true':
        self.sheet_header.extend(self.registration)
      self.sheet_header.append("(end of sheet header)")

      self.sheet_footer = [
        #"(Start of sheet footer.)",
        #"M300 S%d (pen up)" % (self.pen_up_angle),
        #"G4 P%d (wait %dms)" % (self.stop_delay, self.stop_delay),
        #"G91 (relative mode)",
        #"G0 Z15 F%0.2f" % (self.z_feedrate),
        "G90 (absolute mode)",
        "G0 X%0.2f Y%0.2f F%0.2f" % (self.x_home, self.y_home, self.xy_feedrate),
        #"M01 (Have you retrieved the print?)",
        #"(machine halts until 'okay')",
        "G4 P%d (wait %dms)" % (self.start_delay, self.start_delay),
        #"G91 (relative mode)",
        #"G0 Z-15 F%0.2f (return to start position of current sheet)" % (self.z_feedrate),
        "G0 Z-0.01 F%0.2f (move down one sheet)" % (self.z_feedrate),
        "G90 (absolute mode)",
        #"M18 (disengage drives)",
        "(End of sheet footer)",
      ]

      self.loop_forever = [ "M30 (Plot again?)" ]

      self.codes = []

    def generate(self):
      if self.continuous == 'true':
        self.num_pages = 1

      codesets = [self.preamble]
      if (self.continuous == 'true' or self.num_pages > 1):
        codesets.append(self.sheet_header)
      elif self.register_pen == 'true':
        codesets.append(self.registration)
      codesets.append(self.codes)
      if (self.continuous == 'true' or self.num_pages > 1):
        codesets.append(self.sheet_footer)

      if self.continuous == 'true':
        codesets.append(self.loop_forever)
        for codeset in codesets:
          for line in codeset:
            print line
      else:
        for p in range(0,self.num_pages):
          for codeset in codesets:
            for line in codeset:
              print line
          for line in self.postscript:
            print line

    def start(self):
      #self.codes.append("M300 S%0.2F (pen down)" % self.pen_down_angle)
      #self.codes.append("G4 P%d (wait %dms)" % (self.start_delay, self.start_delay))
      self.codes.append("M04 (pen down)" )
      self.drawing = True

    def stop(self):
      #self.codes.append("M300 S%0.2F (pen up)" % self.pen_up_angle)
      #self.codes.append("G4 P%d (wait %dms)" % (self.stop_delay, self.stop_delay))
      self.codes.append("M03 (pen up)" )
      self.drawing = False

    def go_to_point(self, x, y, stop=False):
      if self.last == (x,y):
        return
      if stop:
        return
      else:
        if self.drawing: 
            #self.codes.append("M300 S%0.2F (pen up)" % self.pen_up_angle) 
            #self.codes.append("G4 P%d (wait %dms)" % (self.stop_delay, self.stop_delay))
            self.codes.append("M03 (pen up)")
            self.drawing = False
        #self.codes.append("G1 X%.2f Y%.2f F%.2f" % (x,y, self.xy_feedrate))
        self.codes.append("G1 X%.2f Y%.2f F%.2f\r\n" % ((x**2+y**2)**0.5,((self.distance-x)**2+y**2)**0.5, self.xy_feedrate))
      self.last = (x,y)
	
    def draw_to_point(self, x, y, stop=False):
      if self.last == (x,y):
          return
      if stop:
        return
      else:
        if self.drawing == False:
            self.codes.append("M04  (pen down)" )
            #self.codes.append("M300 S%0.2F (pen down)" % self.pen_up_angle)
            #self.codes.append("G4 P%d (wait %dms)" % (self.start_delay, self.start_delay))
            self.drawing = True
        #self.codes.append("G1 X%0.2f Y%0.2f F%0.2f" % (x,y, self.xy_feedrate))
        self.codes.append("G1 X%.2f Y%.2f F%.2f\r\n" % ((x**2+y**2)**0.5,((self.distance-x)**2+y**2)**0.5, self.xy_feedrate))
      self.last = (x,y)
