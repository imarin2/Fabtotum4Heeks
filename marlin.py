import nc
import iso
import math
import datetime
import time

now = datetime.datetime.now()

class Format:
    def __init__(self, number_of_decimal_places = 3, add_leading_zeros = 1, add_trailing_zeros = False, dp_wanted = True, add_plus = False, no_minus = False, round_down = False):
        self.number_of_decimal_places = number_of_decimal_places
        self.add_leading_zeros = add_leading_zeros # fill the start of the number with zeros, so there are at least this number of digits before the decimal point
        self.add_trailing_zeros = add_trailing_zeros # fill the end of the number with zeros, as defined by "number_of_decimal_places"
        self.dp_wanted = dp_wanted
        self.add_plus = add_plus
        self.no_minus = no_minus
        self.round_down = round_down

    def string(self, number):
        if number == None:
            return 'None'
        f = float(number) * math.pow(10, self.number_of_decimal_places)
        s = str(f)
        
        if self.round_down == False:
            if f < 0: f = f - .5
            else: f = f + .5
            s = str(number)
            
        if math.fabs(f) < 1.0:
            s = '0'
            
        minus = False
        if s[0] == '-':
            minus = True
            if self.no_minus:
                s = s[1:]
        
        dot = s.find('.')
        if dot == -1:
            before_dp = s
            after_dp = ''
        else:
            before_dp = s[0:dot]
            after_dp = s[dot + 1: dot + 1 + self.number_of_decimal_places]

        before_dp = before_dp.zfill(self.add_leading_zeros)
        if self.add_trailing_zeros:
            for i in range(0, self.number_of_decimal_places - len(after_dp)):
                after_dp += '0'
        else:
            after_dp = after_dp.rstrip('0')
                 
        s = ''

        if minus == False:
            if self.add_plus == True:
                s += '+'
        s += before_dp
        if len(after_dp):
            if self.dp_wanted: s += '.'
            s += after_dp
            
        return s

class Address:
    def __init__(self, text, fmt = Format(), modal = True):
        self.text = text
        self.fmt = fmt
        self.modal = modal
        self.str = None
        self.previous = None
        
    def set(self, number):
        self.str = self.text + self.fmt.string(number)
        
    def write(self, writer):
        if self.str == None: return ''
        if self.modal:
            if self.str != self.previous:
                writer.write(self.str)
                self.previous = self.str            
        else:
            writer.write(self.str)
        self.str = None

class AddressPlusMinusMarlin(Address):
    def __init__(self, text, fmt = Format(), modal = True):
        Address.__init__(self, text, fmt, modal)
        self.str2 = None
        self.previous2 = None
        
    def set(self, number, text_plus, text_minus):
        Address.set(self, number)
        if float(number) > 0.0:
            self.str2 = text_plus
        else:
            self.str2 = text_minus

    def write(self, writer):
        if self.str2 == None: return ''
        if self.modal:
            if self.str2 != self.previous2:
                writer.write("\n")
                writer.write(self.str2 + writer.SPACE())
                self.previous2 = self.str2            
                writer.write(writer.SPACE())
        else:
	    writer.write("\n")
            writer.write(self.str2 + writer.SPACE())
            writer.write(writer.SPACE())
        Address.write(self, writer)
        self.str2 = None
	writer.write("\n")
	writer.write("G4 S3")


class Creator(iso.Creator):
    def __init__(self):
        iso.Creator.__init__(self)
        self.output_block_numbers = False
        self.output_tool_definitions = False
	self.output_arcs_as_lines = True
        #self.output_g43_on_tool_change_line = True
        self.drillExpanded = True
	self.s = AddressPlusMinusMarlin('S', fmt = Format(number_of_decimal_places = 2), modal = False)

    def SPACE_STR(self): return ' '

    def FEED(self): return('G1')
    def RAPID(self): return('G0')
    def TOOL(self): return('')
    def tool_change(self, id): return
    def METRIC(self): return('')
    def set_plane(self, plane): return

    def SPINDLE_CW(self): return('M3')
    def SPINDLE_CCW(self): return('M4')

    def write_spindle(self):
        self.write(self.SPACE())
        self.s.write(self)

    def rapid(self, x=None, y=None, z=None, a=None, b=None, c=None ):
        if self.same_xyz(x, y, z, a, b, c): return
        self.on_move()

        if self.g0123_modal:
            if self.prev_g0123 != self.RAPID():
                self.write(self.SPACE() + self.RAPID())
                self.prev_g0123 = self.RAPID()
        else:
            self.write(self.SPACE() + self.RAPID())
        self.write_preps()
        if (x != None):
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.X() + (self.fmt.string(x + self.shift_x)))
            else:
                dx = x - self.x
                self.write(self.SPACE() + self.X() + (self.fmt.string(dx)))
            self.x = x
        if (y != None):
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.Y() + (self.fmt.string(y + self.shift_y)))
            else:
                dy = y - self.y
                self.write(self.SPACE() + self.Y() + (self.fmt.string(dy)))

            self.y = y
        if (z != None):
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.Z() + (self.fmt.string(z + self.shift_z)))
            else:
                dz = z - self.z
                self.write(self.SPACE() + self.Z() + (self.fmt.string(dz)))

            self.z = z

        if (a != None):
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.A() + (self.fmt.string(a)))
            else:
                da = a - self.a
                self.write(self.SPACE() + self.A() + (self.fmt.string(da)))
            self.a = a

        if (b != None):
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.B() + (self.fmt.string(b)))
            else:
                db = b - self.b
                self.write(self.SPACE() + self.B() + (self.fmt.string(db)))
            self.b = b

        if (c != None):
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.C() + (self.fmt.string(c)))
            else:
                dc = c - self.c
                self.write(self.SPACE() + self.C() + (self.fmt.string(dc)))
            self.c = c
        self.write_misc()
        self.write_spindle()
        self.write('\n')

    def feed(self, x=None, y=None, z=None, a=None, b=None, c=None):
        if self.same_xyz(x, y, z, a, b, c): return
        self.on_move()
        if self.g0123_modal:
            if self.prev_g0123 != self.FEED():
                self.write(self.SPACE() + self.FEED())
                self.prev_g0123 = self.FEED()
        else:
            self.write(self.SPACE() + self.FEED())
        self.write_preps()
        dx = dy = dz = 0
        if (x != None):
            dx = x - self.x
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.X() + (self.fmt.string(x + self.shift_x)))
            else:
                self.write(self.SPACE() + self.X() + (self.fmt.string(dx)))
            self.x = x
        if (y != None):
            dy = y - self.y
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.Y() + (self.fmt.string(y + self.shift_y)))
            else:
                self.write(self.SPACE() + self.Y() + (self.fmt.string(dy)))

            self.y = y
        if (z != None):
            dz = z - self.z
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.Z() + (self.fmt.string(z + self.shift_z)))
            else:
                self.write(self.SPACE() + self.Z() + (self.fmt.string(dz)))

            self.z = z

        if (a != None):
            da = a - self.a
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.A() + (self.fmt.string(a)))
            else:
                self.write(self.SPACE() + self.A() + (self.fmt.string(da)))
            self.a = a

        if (b != None):
            db = b - self.b
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.B() + (self.fmt.string(b)))
            else:
                self.write(self.SPACE() + self.B() + (self.fmt.string(db)))
            self.b = b

        if (c != None):
            dc = c - self.c
            if (self.absolute_flag ):
                self.write(self.SPACE() + self.C() + (self.fmt.string(c)))
            else:
                self.write(self.SPACE() + self.C() + (self.fmt.string(dc)))
            self.c = c

        if (self.fhv) : self.calc_feedrate_hv(math.sqrt(dx*dx+dy*dy), math.fabs(dz))
        self.write_feedrate()
        self.write_misc()
        self.write_spindle()
        self.write('\n')


#    def SPACE(self):
#        if self.start_of_line == True:
#            self.start_of_line = False
#            return ''
#        else:
#            return ' '

    def PROGRAM(self): return None
    def PROGRAM_END(self): return('G4 S5\nM05')

        
############################################################################
## Begin Program 

    def program_begin(self, id, comment):
        self.write( ('(Created with Marlin post processor ' + str(now.strftime("%Y/%m/%d %H:%M")) + ')' + '\n') )
        iso.Creator.program_begin(self, id, comment)

nc.creator = Creator()


