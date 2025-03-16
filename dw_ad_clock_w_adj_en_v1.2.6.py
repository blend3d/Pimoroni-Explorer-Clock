# Pimoroni Explorer Demo
# From: https://forums.pimoroni.com/t/pimoroni-explorer-kit-tutorial/26501/6
# Analog/ Digital clock - Tony Goodhew, Leicester UK - 6 Nov 2024
# Time Adjust - Tony Goodhew, Leicester UK - 23 Dec 2024
# Modified - David Warner, Detroit MI, US - 17 Mar 2025
# Uses the Multi-Sensor Stick (BME280 + LTR559 + LSM6DS3)

from explorer import display, i2c, button_a, button_b, button_c, button_z, button_x, button_y, YELLOW
from breakout_bme280 import BreakoutBME280
from breakout_ltr559 import BreakoutLTR559
import math, time, sys

# get display dimensions in pixels
WIDTH, HEIGHT = display.get_bounds()		# explorer display is 320*240
back_lt = 1.0								# backlight variable for cl_set_disp function (range is 0.0 to 1.0)

# set pen rgb (red, green, blue) colors
BLACK = display.create_pen(0, 0, 0)			
WHITE = display.create_pen(253, 240, 213)	# pure white is (255,255,255)
RED = display.create_pen(193, 18, 31)		# pure red is (255,0,0)
BLUE = display.create_pen(37, 87, 115)		# pure blue is (0,0,255)
  
# create lists for days and months 
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# create clock center, radius, and number placement delta values 
cx, cy, l = 212, 132, 105 	# clock face center x, y, and radius 
dx, dy = 12, 12				# clock face numbers x and y delta position value

# get current time and date: default epoch = (1970, 1, 1, 0, 0, 0, 3, 1) 
year, month, day, h, m, s, wd, _ = time.localtime()	

# is multi-sensor stick present? if not exit with message 
try:
    bme = BreakoutBME280(i2c, address=0x76)
    ltr = BreakoutLTR559(i2c)
except RuntimeError:
    display.set_layer(0)
    display.set_pen(RED)
    display.clear()
    display.set_pen(WHITE)
    display.text("Multi-Sensor", 60, 95, 320, 3)
    display.text("Stick missing", 60, 125, 320, 3)
    display.update()
    sys.exit()

# function to clear layers, set backlighting, and update display 
def cl_set_disp(bl):	# backlight value is passed to function when called
    display.set_backlight(bl)	
    display.set_layer(0)
    display.set_pen(BLACK)
    display.clear()
    display.set_layer(1)
    display.set_pen(BLACK)
    display.clear()
    display.update()

# function to clear layers, but not update display
def clean():    
    display.set_layer(0)
    display.set_pen(BLACK)
    display.clear()
    display.set_layer(1)
    display.set_pen(BLACK)
    display.clear()

# function for hour and minute hands
def hand(ang, long): 
    ang = ang-90
    ls = long/13	# was originally "long/10" for wider hands at pivot
    x0 = int(round(long * math.cos(math.radians(ang))))+cx
    y0 = int(round(long * math.sin(math.radians(ang))))+cy
    x1 = int(round(ls * math.cos(math.radians(ang+90))))+cx	# + x width coordinate perpindicular to hand length
    y1 = int(round(ls * math.sin(math.radians(ang+90))))+cy	# + y width coordinate perpindicular to hand length
    x2 = int(round(ls * math.cos(math.radians(ang-90))))+cx	# - x width coordinate perpindicular to hand length
    y2 = int(round(ls * math.sin(math.radians(ang-90))))+cy	# - y width coordinate perpindicular to hand length
    display.triangle(x0,y0,x1,y1,x2,y2)
    display.circle(cx,cy,int(ls))

# function to set time manually 
def set_time():
    # button assignment: x = ^, y = v, z = >, c = <, a = set
            
    maxx = [12,31,2100,"",24,59]	# maximum values [mo, day, year, "space", hrs, min]
    minn = [1,1,2025,"",1,0]		# minimum values [mo, day, year, "space", hrs, min]
    val = [1,1,2025,"",12,30]		# initial selection [mo, day, year, "space", hrs, min]
      
    def show_vals(cur,val):
        for i in range(6):
            display.set_pen(WHITE)
            # display labels: (string, x, y, wordwrap, scale, angle, spacing)
            display.text("Month", 30, yt, 140, 2, 90)
            display.text("Day", 75, yt, 140, 2, 90)
            display.text("Year", 138, yt, 140, 2, 90)
            display.text("Hour 1 - 24", 213, yt, 140, 2, 90)
            display.text("Minute", 262, yt, 140, 2, 90)
            
            xx = 21 + i * 45 	# x-axis position for val display
            display.set_pen(RED)
            if cur == i:
                display.set_pen(YELLOW)
            display.text(str(val[i]),xx,yy,200,2)

    p = 0
    yt = 106	# yt is for label display hight on display
    yy = 76		# yy is for val display hight on display
    show_vals(p,val)
    display.update()  
    
    while button_a.value() == 1: # halt loop with "set" button'A'
        
        # draw icons on screen for buttons
        clean()											# clear layers but do not update display
        display.set_pen(WHITE)
        display.circle(18, 44, 5)   					# "set" dot, display.rectangle(x, y, r)
        display.text("Set", 35, 38, 100, 2)				# "set" text, display.text(text, x, y, wordwrap, scale)
        display.triangle(303, 38, 293, 51, 313, 51)		# "up" arrow, display.triangle(x1, y1, x2, y2, x3, y3)
        display.triangle(303, 127, 293, 114, 313, 114)	# "down" arrow, display.triangle(x1, y1, x2, y2, x3, y3)
        display.triangle(12, 195, 28, 205, 28, 185)		# "previous" arrow, display.triangle(x1, y1, x2, y2, x3, y3)
        display.triangle(311, 195, 295, 205, 295, 185)	# "next" arrow, display.triangle(x1, y1, x2, y2, x3, y3)
        
        if button_x.value() == 0:
            time.sleep(0.2)		# delay for pseudo button debounce
            val[p] = val[p] +1
            if val[p] > maxx[p]:
                val[p] = maxx[p]

        elif button_y.value() == 0:
            time.sleep(0.2)		# delay for pseudo button debounce
            val[p] = val[p] - 1
            if val[p] < minn[p]:
                val[p] = minn[p]
        elif button_z.value() == 0:
            time.sleep(0.2)		# delay for pseudo button debounce
            p = p + 1
            if p > 5:
                p = 0
        
        elif button_c.value() == 0:	# Note: eliminate 'c' button for 4 button displays
            time.sleep(0.2)		# delay for pseudo button debounce
            p = p - 1
            if p < 0:
                p = 5
        show_vals(p,val)
        display.update()
        time.sleep(0.1)
        
    cl_set_disp(back_lt)	# clear display and set backlight
    
    mo_set = val[0]
    day_set = val[1]
    yr_set = val[2]
    # val[3] is a space which is a string and will not work with machine.RTC()
    h_set = val[4]
    m_set = val[5]
        
    # update real time clock (rtc) with user entered values 
    rtc = machine.RTC()				# create real time clock object
    # set rtc time (yr, mo, day, weekday, h, m, s, sub-seconds)
    rtc.datetime((yr_set, mo_set, day_set, 0, h_set, m_set, 0, 0))	
    current_time = rtc.datetime()	# read the updated current time

# function to draw clock face and titles
def dr_clk_face():
    display.set_pen(BLUE)	# create large blue circle
    display.circle(cx,cy,l)	
    display.update()
    display.set_pen(WHITE)	# create white marks on ring every 6 degrees
    for angle in range(0,360,6):
        xx = int(round(l * math.cos(math.radians(angle))))
        yy = int(round(l * math.sin(math.radians(angle))))    
        display.line(cx,cy,cx+xx,cy+yy)
    display.set_pen(BLACK)	# overlay black circle on blue circle for 8 pixel thick blue ring effect
    display.circle(cx,cy,l-8)	
    display.set_pen(WHITE)	# overlay long white lines every 30 deg to correspond with clock facenumbers
    for angle in range(0,360,30):
        xx = int(round(l * math.cos(math.radians(angle))))
        yy = int(round(l * math.sin(math.radians(angle))))    
        display.line(cx,cy,cx+xx,cy+yy)
    
    display.set_pen(WHITE)	# sensor titles in white
    display.text("Ambient Light",5,80,300,1)
    display.text("Rel Humidity",5,120,300,1)
    display.text("Temperature",5,160,310,1)
    display.text("Air Pressure",5,200,300,1)

# test if year is current, if not call set_time() 
if year <= 2024:	# test if year is less than 2024
    set_time()

# call function to clear display layers, set backlighting, update display
cl_set_disp(back_lt)	# backlight set to 1.0 

#  call function to draw clock face and sensor titles
dr_clk_face()

# =============== main loop ================
while True:
    # draw time set button for manual time set
    display.circle(312, 200, 3)			# "set" dot, display.rectangle(x, y, r)
    display.text("Set",305,210,320,1)	# "set" text
    
    # goto time setting routine upon button 'Z' input
    while button_z.value() == 0:
        time.sleep(0.3) 	# delay for pseudo button debounce
        set_time()			# call set_time function
        dr_clk_face()		# call draw clock face upon return from set time function
    
    # draw face numbers
    display.set_pen(BLACK)
    display.circle(cx,cy,93) 	# clear centre of clock face
    display.set_pen(WHITE)
    display.text("9",118 +dx,108 +dy,320,3)	# dx = 12 pixel x delta 
    display.text("3",268 +dx,108 +dy,320,3)	# dy = 10 pixel y delta
    display.text("10",128 +dx,70 +dy,320,3)	# TODO, low priority: delta was for quick clock face move during tests, remove when done
    display.text("2",258 +dx,70 +dy,320,3)
    display.text("1",230 +dx,45 +dy,320,3)
    display.text("11",160 +dx,45 +dy,320,3)
    display.text("12",193 +dx,37 +dy,320,3)
    display.text("6",193 +dx,186 +dy,320,3)	
    display.text("7",156 +dx,176 +dy,320,3)
    display.text("5",230 +dx,176 +dy,320,3)
    display.text("4",258 +dx,150 +dy,320,3)
    display.text("8",130 +dx,150 +dy,320,3)
    
    # draw hands
    mang = int((m + s/60)* 6)   # angle of minute hand
    hang = int((h + m/60 )* 30)	# angle of hour hand
    display.set_pen(BLUE)
    hand(mang,90)
    display.set_pen(RED)      
    hand(hang,65)
    lens = 93					# length of second hand
    sang = 6 * s - 90			# angle of second hand
    xs = int(round(lens * math.cos(math.radians(sang))))
    ys = int(round(lens * math.sin(math.radians(sang))))
    display.set_pen(WHITE)
    display.line(cx,cy,cx+xs,cy+ys)
    display.circle(cx,cy,3)
    
    # convert 24 hours to 12 hours with am/pm "time of day" (tod) labels
    tod = "AM"			# start with am
    if h >= 12:			# check if hours are greater than 12
        tod = "PM"		# if true time of day is pm
        h -= 12			# if true subtract 12 hours
    if h == 0:			# check for zero, ie noon or midnight
        h = 12			# if true add 12 hours
    
    # assemble digital time
    ss = f"{s:02}"			# f-string formats value to two digits and, 
    ms = f"{m:02}"			# adding a leading zero if needed
    hs = f"{h:02}"
    dt = f"{hs}:{ms}:{ss}"	# concatenate hr, min, and sec with colons(:) in-between
    
    # clear text areas on display
    display.set_pen(BLACK)
    display.rectangle(5,10,170,18)	# time area
    display.rectangle(5,50,90,18)	# date area
    display.rectangle(5,90,101,18)	# lux area
    display.rectangle(5,130,80,18)	# humidity
    display.rectangle(5,170,105,28)	# temperature
    display.rectangle(5,210,115,18)	# pressure
    
    # write digital time and tod
    display.set_pen(BLUE)
    display.text(dt,5,10,320,3)
    display.text(tod,125,10,320,3)
        
    # read the sensors and convert to us measures
    prox, a, b, c, d, e, lux = ltr.get_reading()
    temperature, pressure, humidity = bme.read()
    temp_f = round(((temperature*1.8)+32),1)			# convert temp to °F, round to 1 place
    pressure_inhg = round((pressure*0.0002952998),2) 	# convert press to inHg, round to 2 places
    
    # display sensor readings
    display.set_pen(RED)
    display.text(str(int(lux))+" lx",5,90,320,3)		# display lux, integers only
    display.text(str(int(humidity)) +" %", 5,130,320,3)	# display humidity, integers only
    display.text(str(temp_f)+" °F",5,170,320,3) 		# display temperature
    display.text(str(pressure_inhg)+" in",5,210,320,3)	# display pressure
        
    # update time and date values
    year, month, day, h, m, s, wd, _ = time.localtime()
    display.set_pen(WHITE)
    display.text(days[wd],5,40,320,1)						# wd is weekday (ie., monday, tuesday, ...)
    display.set_pen(BLUE)
    display.text(str(day)+" "+months[month-1],5,50,320,3)	# [month-1] make time month value equal list[0] 
    display.update()
    time.sleep(0.1) 
