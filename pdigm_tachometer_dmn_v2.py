#!/usr/bin/env python
# coding: utf-8
##############################################################################
##                 How well can you control your thoughts?                  ##
##             The ability to modulate the DMN told in two parts:           ##
##                        Feedback and No-Feedback                          ##
##                                                                          ##
##                        R. Cameron Craddock, PhD                          ##
##                        Jonathan M. Lisinski, MS                          ##
##                         Stephen M. LaConte, PhD                          ##
##############################################################################


############################
#  Import various modules  #
############################

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, Controller, FunctionController
from VisionEgg.MoreStimuli import *
from VisionEgg.Textures import *
from math import *
import pygame
import OpenGL.GL as gl
from VisionEgg.DaqKeyboard import *
from VisionEgg.Text import *
from VisionEgg.WrappedText import *
from VisionEgg.ResponseControl import *
from string import *
import Image, ImageDraw # Python Imaging Library (PIL)
import os, sys

# to interact with the Lumina box
import pyxid

try:
    import Tkinter
except:
    pass

############################
# Define                   #
############################

LUMINA        = 1
DETREND       = 0
TCPIP         = 1    # Set 1 to receive data over TCP/IP
TCPIP_PORT    = 8000 # Port receiving TCP/IP data
TCPIP_GUI     = 1    # Open GUI to initialize TCP/IP 

#AFNI_IP='localhost'
#AFNI_PORT=5000
#AFNI_COM_GUI=1

ALPHA_MAX = 0.5
ALPHA_SCALE = 1.0

LUMINA_TRIGGER=4

# this is nparadigms x 2, where the second dimension is no feedback, and
# feedback (no feedback = 0, feedback = 1)
stim_files= \
    [ \
     ['DMN_TRACKING_nofb_normal_wander_v2.cfg',\
      'DMN_TRACKING_fb_normal_wander_v2.cfg'],\
     ['DMN_TRACKING_nofb_normal_focus_v2.cfg', \
      'DMN_TRACKING_fb_normal_focus_v2.cfg'], \
     ['DMN_TRACKING_nofb_swapped_wander_v2.cfg', \
      'DMN_TRACKING_fb_swapped_wander_v2.cfg'], \
     ['DMN_TRACKING_nofb_swapped_focus_v2.cfg', \
     'DMN_TRACKING_fb_swapped_focus_v2.cfg'], \
     ['SIMULATION_DMN_TRACKING_nofb_normal_wander_v2.cfg',\
      'SIMULATION_DMN_TRACKING_fb_normal_wander_v2.cfg'],\
     ['SIMULATION_DMN_TRACKING_nofb_normal_focus_v2.cfg', \
      'SIMULATION_DMN_TRACKING_fb_normal_focus_v2.cfg'], \
     ['SIMULATION_DMN_TRACKING_nofb_swapped_wander_v2.cfg', \
      'SIMULATION_DMN_TRACKING_fb_swapped_wander_v2.cfg'], \
     ['SIMULATION_DMN_TRACKING_nofb_swapped_focus_v2.cfg', \
     'SIMULATION_DMN_TRACKING_fb_swapped_focus_v2.cfg'], \
    ]

# default server address
if TCPIP:
    server_address=('127.0.0.1','%d'%(TCPIP_PORT))

####

if DETREND:
    from scipy import polyfit # for detrending

# parse out the name of this program and the paradigm
# name
prog_name = os.path.basename( sys.argv[0] )
pdigm_name = split( os.path.basename( sys.argv[0]), '.')[0]

###############################
# TK window to get parameters #
# copied from the code in     #
# VisionEgg.TCPSERVER         #
###############################
class GetPdigmConfigWindow(Tkinter.Frame):
    def __init__(self,server_address,**kw): 
        try:
            Tkinter.Frame.__init__(self,**kw)
        except AttributeError,x:
            # restart Tk and see if that helps 
            tk=Tkinter.Tk() 
            Tkinter.Frame.__init__(self,tk,**kw)
        self.winfo_toplevel().title("%s Configuration"%(pdigm_name))
        self.server_address = server_address
        hostname,port = self.server_address
        self.clicked_ok = 0
        self.subjid  = Tkinter.StringVar()
        self.subjid.set('')
        self.fb  = Tkinter.StringVar()
        self.fb.set("-1")
        self.pdigm  = Tkinter.StringVar()
        self.pdigm.set("-1")
        self.hostname = Tkinter.StringVar()
        self.hostname.set(hostname)
        self.port = Tkinter.StringVar()
        self.port.set(port)
        row = 0
        Tkinter.Label(self,
            text="Subject ID:",\
            ).grid(row=row,column=0,sticky=Tkinter.E)
        Tkinter.Entry(self,textvariable=self.subjid).grid(row=row,column=1,\
            sticky=Tkinter.W+Tkinter.E,padx=10)
        row += 1
        Tkinter.Label(self,
            text="Feedback 0 (off) or 1 (on):",\
            ).grid(row=row,column=0,sticky=Tkinter.E)
        Tkinter.Entry(self,textvariable=self.fb).grid(row=row,column=1,\
            sticky=Tkinter.W+Tkinter.E,padx=10)
        row += 1
        Tkinter.Label(self,
            text="Paradigm number (0,1,2,4):",\
            ).grid(row=row,column=0,sticky=Tkinter.E)
        Tkinter.Entry(self,textvariable=self.pdigm).grid(row=row,column=1,\
            sticky=Tkinter.W+Tkinter.E,padx=10)

        if TCPIP:
            row += 1
            Tkinter.Label(self,
                text="Please enter the hostname and port you would like to listen"+\
                     " for connections on.",).grid(row=row,columnspan=2)
            row += 1
            Tkinter.Label(self,
                text="Hostname (blank means localhost):",\
                ).grid(row=row,column=0,sticky=Tkinter.E)
            Tkinter.Entry(self,textvariable=self.hostname).grid(row=row,column=1,\
                sticky=Tkinter.W+Tkinter.E,padx=10)
            row += 1
            Tkinter.Label(self, text="Port:",).grid(row=row,column=0,sticky=Tkinter.E)
            Tkinter.Entry(self,textvariable=self.port).grid(row=row,column=1,\
                sticky=Tkinter.W+Tkinter.E,padx=10)
            row += 1
            b = Tkinter.Button(self,text="Bind port and listen for connections",\
                command=self.click_ok)
        else:
            b = Tkinter.Button(self,text="OK",\
                command=self.click_ok)

        b.grid(row=row,columnspan=2)
        b.focus_force()
        b.bind('<Return>',self.click_ok)

    def click_ok(self,dummy_arg=None):
        subjid=self.subjid.get()

        try:
            fb=int(self.fb.get())
            print "setting fb as an int?? %d"%(fb)
        except:
            print "setting fb as a string?? %s"%(fb)
            fb=self.fb.get()

        try:
            pdigm=int(self.pdigm.get())
        except:
            pdigm=self.pdigm.get()

        if TCPIP:
            hostname = self.hostname.get()
            try:
                port = int(self.port.get())
            except:
                port = self.port.get()
            self.server_address = (hostname,port)
        self.clicked_ok = 1
        self.winfo_toplevel().destroy()

#bound = 0 
#if not bound: 
#  while not bound: # don't loop until the code is cleaner 
    #if confirm_address_with_gui and self.dialog_ok: 
         #window = GetServerAddressWindow(server_address) 
         #window.pack() 
         #window.mainloop() 
         #if not window.clicked_ok: 
             #return # User wants to quit 
         #server_address = window.server_address 
     #self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
     #self.server_socket.bind(server_address) 
     #bound = 1 

# check to make sure that the required command line 
# arguements were specified
if len(sys.argv) > 3:
    subjid = sys.argv[1]
    fb = int(sys.argv[2])
    pdigm = int(sys.argv[3])
    print "Executing: %s Subject ID: %s Feedback: " \
        "%d Paradigm: %d"%(prog_name, subjid, \
        fb, pdigm)
else:
    #print "Usage: %s <subjid> <feedback (0|1)> " \
        #"<pdigm index (1,2)>"%(prog_name)
    #sys.exit()
    window = GetPdigmConfigWindow(server_address)
    window.pack() 
    window.mainloop() 
    if not window.clicked_ok:
        sys.exit()
    subjid = window.subjid
    fb = window.fb
    pdigm = window.pdigm
    if TCPIP: 
        server_address = window.server_address 
    print "Executing: %s Subject ID: %s Feedback: " \
        "%d Paradigm: %d"%(prog_name, subjid, \
        fb, pdigm)

if not subjid:
    print "invalid subject ID: %s"%(subjid)
    sys.exit()

# check the sanity of the command line arguements
if fb < 0 or fb > 1:
    print "Feedback: %d should be either 0 (no feedback) " \
        "or 1 (feedback)"%(fb)
    sys.exit()

# read in the stimulus labels
if pdigm < np.shape(stim_files)[0] and \
   fb < np.shape(stim_files)[1]:
    pfile=stim_files[pdigm][fb]
else:
    print "Do not have an entry for paradigm %d (%d)"%(pdigm,fb)
    sys.exit()

# open the paradigm file
try:
    f=open(pfile,'r')
except IOError:
    print 'Could not open %s. I/O error'%( \
         pfile )
    sys.exit(1)
#except IOError as (errno, strerror):
    #print 'Could not open %s. I/O error({0}): {1}'%( \
         ##pfile,errno, strerror)
    #sys.exit(1)

# read in the files and parse
# out the meaning
Num_Stim = -666
ISI = -666.0
FEEDBACK = -666    # set to 0 to disable feedback
Instructions = ''
left_strings=[]
right_strings=[]
stimulus_strings=[]
show_array=[]

line=''
line_count=1
stim_count=0
try:
    for line in f:
        line=line.strip()
        if line and not '#' in line:
            if 'ISI' in line:
                ISI=float(line.split(':')[1])
            elif 'NUMSTIM' in line:
                Num_Stim=int(line.split(':')[1])
            elif 'FEEDBACK' in line:
                FEEDBACK=int(line.split(':')[1])
            elif 'INSTRUCTION' in line:
                if Instructions:
                    Instructions = Instructions + '\n' + \
                        line.split(':')[1]
                else:
                    Instructions = line.split(':')[1]
            else:
                # assume it is a stimulus specifier
                vals=line.split(';')
                #print vals
                if len(vals) > 3:
                    left_strings.append( vals[0] )
                    right_strings.append( vals[1] )
                    stimulus_strings.append( vals[2] )
                    show_array.append(int( vals[3] ))
                    stim_count=stim_count+1
                else:
                    print 'Improperly formatted STIM string %s (%d): %s (%d)' \
                        %( line, len(vals), pfile, line_count )
        line_count=line_count+1

except IOError:
    print '%s I/O error(%d)'%( \
        pfile)
    sys.exit(1)
#except IOError as (errno):
    #print '%s I/O error(%d)'%( \
        #pfile, errno)
    #sys.exit(1)

except ValueError:
    print '%s (%d) %s. Could not convert data to an integer.'%( \
       pfile, line_count, line )
    sys.exit(1)

except:
    print '%s (%d) %s. Unexpected error %s, maybe error in formatting?'%( \
       pfile, line_count, line, sys.exc_info()[0])
    sys.exit(1)

f.close()

if not Instructions:
    print "Error: INSTRUCTION not specified"
    sys.exit(1)

if Num_Stim == -666:
    print "Error: NUMSTIM not specified"
    sys.exit(1)

if Num_Stim < 0:
    print 'Error: Invalid NUMSTIM specified (%d)'%(Num_Stim)
    sys.exit(1)

if ISI == -666.0:
    print "Error: ISI not specified."
    sys.exit(1)

if ISI < 0:
    print 'Error: Invalid ISI specified (%g)'%(ISI)
    sys.exit(1)

if FEEDBACK != 0 and FEEDBACK != 1:
    print 'Error: Invalid FEEDBACK specified (%d)'%(FEEDBACK)
    sys.exit(1)

if stim_count < Num_Stim:
    print 'Error: Fewer stimulus specifiers (%d) than NUMSTIM (%d)'%( \
        stim_count,Num_Stim)
    sys.exit(1)

if len( left_strings ) < Num_Stim or len( right_strings ) < Num_Stim or \
   len( stimulus_strings ) < Num_Stim or len( show_array ) < Num_Stim:
    print 'Error: One of the stim lists (l %d, r %d, s %d, sh %d)' \
          ' is shorter than expected %d' %( \
        len(left_strings),len(right_strings),len(stimulus_strings), \
        len(show_array),Num_Stim)
    sys.exit(1)

Num_Secs = float(Num_Stim)*ISI
print 'Paradigm is %d * %g = %g seconds long'%(Num_Stim, ISI, Num_Secs)
print 'Instructions: %s'%(Instructions)
print 'Feedback: %d'%(FEEDBACK)

## create a log file
filename = time.strftime ('%m-%d-%Y_%Hh-%Mm.txt');
filename = '_'.join ([subjid, pdigm_name, filename])

try:
    log=open(filename,'w')
except IOError:
    print 'Could not open %s. I/O error'%( \
         filename)
    sys.exit(1)
#except IOError as (errno, strerror):
    #print 'Could not open %s. I/O error({0}): {1}'%( \
         #filename,errno, strerror)
    #sys.exit(1)

# write configuration information to the logfile
log.write('#PARADIGM   : %s\n'%(pfile))
log.write('#FEEDBACK   : %d\n'%(FEEDBACK))
log.write('#DETREND    : %d\n'%(DETREND))
log.write('#TCPIP      : %d\n'%(TCPIP))
log.write('#ALPHA_SCALE: %d\n'%(ALPHA_SCALE))
log.write('#ALPHA_MAX  : %d\n'%(ALPHA_MAX))
log.write('#NUM STIM   : %d\n'%(Num_Stim))
log.write('#NUM SECS   : %5.2f\n'%(Num_Secs))

# write headers of the outputs, to simplify
log.write("Time Stamp; STIM; Left Text; Right Text; Stim Text;" \
          " Show; Sign; Classifier Output; Detrended Output;" \
          " Cumulative Score\n")
log.write("Time Stamp; KEYPRESS; Key Identifier\n")

#try:
    #ser = serial.Serial(0,300,timeout=0,parity=serial.PARITY_NONE,rtscts=1)
    ##ser = serial.Serial(0,9600,timeout=0,parity=serial.PARITY_EVEN,rtscts=1)
#except:
    #sys.stderr.write("could not open serial port\n")

## activate line below for test version of this program
#serial    sys.exit(1)

#################################
#  Initialize the various bits  #
#################################

# initialize communication with the lumina
if LUMINA == 1:
    ## initialize communication with the lumina
    devices=pyxid.get_xid_devices()

    if devices:
        lumina_dev=devices[0]
    else:
        print "Could not find Lumina device"
        sys.exit(1)

    print "attached lumina device", lumina_dev
    if lumina_dev.is_response_device():
        lumina_dev.reset_base_timer()
        lumina_dev.reset_rt_timer()
    else:
        print "Error: Lumina device is not a response device??"
        log.write("Error: Lumina device is not a response device??")
        sys.exit()

# setup TCPIP communication with real time system
if TCPIP:
  from VisionEgg.TCPController import *
  tcp_server = TCPServer(hostname='127.0.0.1',
               port=TCPIP_PORT,
               single_socket_but_reconnect_ok=1,
               confirm_address_with_gui=TCPIP_GUI)
  #tcp_server = TCPServer(hostname='',
               #port=TCPIP_PORT,
               #single_socket_but_reconnect_ok=1,
               #confirm_address_with_gui=TCPIP_GUI)
  if tcp_server.server_socket is None: # User wants to quit 
    sys.exit()

  tcp_listener = tcp_server.create_listener_once_connected()

# Initialize OpenGL graphics screen.
#screen = VisionEgg.Core.Screen(size=(1024,768),fullscreen=True,frameless=True)
screen = VisionEgg.Core.Screen(size=(1024,768),fullscreen=True,frameless=False)
#screen = get_default_screen()

# Set the background color to white (RGBA).
screen.parameters.bgcolor = (0.0,0.0,0.0,0.0)

screen_half_x = screen.size[0]/2
screen_half_y = screen.size[1]/2

#textAA = Text(text="NO FEEDBACK",
#              color=(1.0,1.0,1.0),
#              position=(screen_half_x,screen_half_y+20),
#              font_size=60,
#              anchor='center')


fonts=pygame.font.get_fonts()
#print "I Want this Font %s\n%s\n"%\
#    (fonts[122],pygame.font.match_font(fonts[98]))

# This text box is 2/3 of the screen size wide and .5 of the scree high
# which translates to 28 characters wide and 9 characters high at 1024x768
# resolution with 40 point fixed font, some adjustments might be necessary

# concatenate string to first 252 characters
Instructions=Instructions[:252] if len(Instructions) > 252 else Instructions

textAA = WrappedText(text=Instructions,
         position=(screen.size[0]/6,screen.size[1]-screen.size[1]/4),
         size=(int((2.0/3.0)*screen.size[0]),
               int(.5*screen.size[1])),
         font_size=40,
         #font_name=pygame.font.match_font(fonts[122]),
         font_name=None,
         color=(1.0,1.0,1.0))

r = 200
ang = 0.0
tach_len = 20
tach_width = 2
tach1 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (0.8, 0.8, 1.0, 1.0), 
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = ang
)

ang = 10.0
tach2 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (0.7, 0.7, 1.0, 1.0), 
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = ang
)

ang = 20.0
tach3 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (0.6, 0.6, 1.0, 1.0), 
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = ang
)

ang = 30.0
tach4 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (0.5, 0.5, 1.0, 1.0), 
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = ang
)

ang = 40.0
tach5 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (0.4, 0.4, 1.0, 1.0), 
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA) 
    orientation = ang
)

ang = 50.0
tach6 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (0.3, 0.3, 1.0, 1.0), 
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)

    orientation = ang
)

ang = 60.0
tach7 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (0.2, 0.2, 1.0, 1.0), 
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = ang
)

ang = 70.0
tach8 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (0.1, 0.1, 1.0, 1.0), 
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = ang
)

ang = 80.0
tach9 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (0.0, 0.0, 1.0, 1.0), 
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = ang
)

ang = 90.0
tach10 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (1.8*tach_len, 3*tach_width),
    #color       = (1.0, 0.9, 0.0, 1.0),
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = ang
)

ang = 100.0
tach11 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (1.0, 0.8, 0.0, 1.0),
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = ang
)

ang = 110.0
tach12 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (1.0, 0.7, 0.0, 1.0),
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = ang
)

ang = 120.0
tach13 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (1.0, 0.6, 0.0, 1.0),
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = ang
)

ang = 130.0
tach14 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (1.0, 0.3, 0.0, 1.0), 
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = ang
)

ang = 140.0
tach15 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (1.0, 0.4, 0.0, 1.0),
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = ang
)

ang = 150.0
tach16 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (1.0, 0.3, 0.0, 1.0), 
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = ang
)

ang = 160.0
tach17 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (1.0, 0.2, 0.0, 1.0),
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = ang
)

ang = 170.0
tach18 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (1.0, 0.1, 0.0, 1.0),
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = ang
)

ang = 180.0
tach19 = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x + r*cos(ang*3.14159/180.0), \
                   screen_half_y + r*sin(ang*3.14159/180.0)),
    size        = (tach_len, tach_width),
    #color       = (1.0, 0.0, 0.0, 1.0),
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = ang
)

taskSize = 60
taskStimulus = Text(text="+",
    on    = 0,
    color=(1.0,1.0,1.0),
    position=(screen_half_x,screen_half_y - (taskSize+20)),
    font_size=taskSize,
    font_name=None,
    #font_name=pygame.font.match_font(fonts[122]),
    anchor='center'
)


arrow_unit = 0.65*screen.size[1]/10
shift_unit = 20.0
L = r-2.0*shift_unit
arrowStimulus = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x , screen_half_y + L/2.0),
    size        = (L, 2*tach_width),
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = 90.0
)

centerStim = Target2D(
    on         = 0,
    anchor      = 'center',
    position    = (screen_half_x , screen_half_y),
    size        = (10, 10.0),
    color       = (1.0, 1.0, 1.0, 1.0),
    orientation = 0.0 # Up
)

# switch the text between these two to change the sides
# for Wandering and Focused (i.e. to counterbalance)
tachLabelR = Text(text="Right Text",
            on    = 0,
            color=(1.0,1.0,1.0),
            position=(screen_half_x + r + tach_len + 1.5*shift_unit,
                      screen_half_y - shift_unit),
            font_size=30,
            font_name=None,
            #font_name=pygame.font.match_font(fonts[122]),
            anchor='center')

tachLabelL = Text(text="Left Text",
            on    = 0,
            color=(1.0,1.0,1.0),
            position    = (screen_half_x - r - tach_len - 1.5*shift_unit, \
                           screen_half_y - shift_unit - 2.5*tach_width),
            font_size=30,
            font_name=None,
            #font_name=pygame.font.match_font(fonts[122]),
            anchor='center')

#tachLabelL = Target2D(
            #on = 0,
            #anchor      = 'center',
            #position    = (screen_half_x - r - tach_len - shift_unit, 
                            #screen_half_y - shift_unit - 2.5*tach_width), 
            #size        = (1.3*tach_len, 2.5*tach_width),
            #color       = (1.0, 1.0, 1.0, 1.0), 
            #orientation = 180 
#)


target_top = 0.8*screen.size[1] + shift_unit
target_bottom = 0.2*screen.size[1] - shift_unit
stim_range_half = (target_top - target_bottom)/2.0
score_factor = 90.0 / (30.0*0.5) # assume 30 maximum TRs at maximum -.5 
                                 # "score" to go from 90 to 0 deg

# Create a Viewport instance
viewport = Viewport(screen=screen, \
                    stimuli=[arrowStimulus,textAA,centerStim,taskStimulus,\
                             tach1,tach2,tach3,tach4,tach5,tach6,tach7,tach8,\
                             tach9,tach10,tach11,tach12,tach13,tach14,tach15,\
                             tach12,tach16,tach17,tach18,tach19,tachLabelR,\
                             tachLabelL])

# the Vision Egg's runtime control abilities.
p = Presentation( go_duration=(Num_Secs,'seconds'), \
                  trigger_go_if_armed=0, \
                  viewports=[viewport])


# calculate a few variables we need
next_stim_time = 0
direction = 1.0
last_direction = 1.0
arrow_scale = 0
arrowColor = 0
score = 90.0
first_loop = 1
start_time = 0
StimCount = -1
stimVis = 0
fbVis = 0
stimText = "+"
leftText = "left"
rightText = "right"

# some vars for receiving distance and detrending
tcp_dist = 0.0
dist = 0.0
dist_detrend= 0.0
dist_array = [];
time_array = [];
startDetrend = 0
detrendLag = 15 #TRs
currentTime = 0
currentTR = 0
currentShow = 1234 #to initialize value
currentSign = 1

#Record key presses to text file, end stimulus with 'esc'
def keydown(event):
    global currentTime

    #log the key press
    log.write("%5.3f; KEYPRESS; %s\n"%(currentTime,event.key))
    if event.key == pygame.locals.K_ESCAPE:         # Quit presentation 'p' 
        p.parameters.go_duration = (0, 'frames')    # with 'ESC' key

# determine what the current state should be
def getState(t):
    global ISI, next_stim_time, direction, last_direction, arrow_scale, score
    global first_loop, start_time, StimCount, stimVis, fbVis, stimText
    global score_factor, arrowColor, leftText, rightText
    global left_strings, right_strings, stimulus_strings, show_array
    global currentTime, currentShow, currentSign, currentTR

    # CC added for TCPIP and detrends
    global tcp_dist, dist_detrend, dist_array, time_array, dist
    global startDetrend, detrendLag
    global ALPHA_MAX, ALPHA_SCALE
    global lumina_dev

    currentTime = t

    if (first_loop == 1) and (p.parameters.trigger_go_if_armed):
        first_loop = 0
        start_time = VisionEgg.time_func()
        if TCPIP:
            tcp_listener.buffer="" # reset buffer

    if t > next_stim_time:
        StimCount = StimCount + 1
        currentShow = int(np.abs(show_array[StimCount]))
        currentSign = int(np.sign(show_array[StimCount]))
        stimText = stimulus_strings[StimCount]
        leftText = left_strings[StimCount]
        rightText = right_strings[StimCount]

        next_stim_time = next_stim_time + ISI

        if StimCount > detrendLag:
            startDetrend=True

####    # note: When run with SVR testing, the input values
####    #       will range from (-inf,inf), most likely (-5,5) 
    if TCPIP:
        tcp_buffer=str(tcp_listener.buffer)
        #print "%s (%s)" %('tcp_data', tcp_buffer)
        tcp_data=tcp_buffer.replace('\000', ''); # remove null byte
        #print "%s (%s) (%s)" %('tcp_data', tcp_data, tcp_buffer)

        if tcp_data != '\000' and tcp_data != "" and \
            "nan" not in tcp_data.lower():

            vals=tcp_data.split(",")
            if len(vals) > 1:
                tcp_dist=float(vals[1])
            else:
                tcp_dist=float(tcp_data)

            tcp_listener.buffer="" # reset buffer
            dist_array = dist_array + [tcp_dist]
            time_array = time_array + [t]
            if DETREND == 1: 
                if startDetrend:
                    dist_detrend = detrendDist(time_array, dist_array)
                else:
                    dist_detrend = tcp_dist
                arrow_scale=dist_detrend
            else:
                arrow_scale=tcp_dist

            if currentShow == 9999 or FEEDBACK == 0:
                fbVis = 0
                score = 90.0
                arrowColor = 0
            else:
                fbVis = 1
                arrowColor = 1
                # increment the score
                score = score - currentSign*arrow_scale*score_factor
                if score < 0:
                    score = 0
                elif score > 180:
                    score = 180
    
            log.write("%5.3f; STIM; %s; %s; %s; %d; %d; %5.3f; %5.3f; %5.3f\n" \
                %(t, leftText, rightText, stimText, currentShow, \
                  currentSign, tcp_dist, arrow_scale, score))

    # handle anything that comes in on the button boxes
    #print "About to test LUMINA",
    #print lumina_dev
    if LUMINA == 1:
        lumina_dev.poll_for_response()
        while lumina_dev.response_queue_size() > 0:
            response = lumina_dev.get_next_response() 
            if response["pressed"]: 
                print "Lumina received: %s, %d"%(response["key"],response["key"])
                if response["key"] == 4:
                    log.write("%5.3f; TR; %s\n"%(currentTime,currentTR))
                    currentTR=currentTR+1
                else:
                    log.write("%5.3f; LUMINA; %d\n"%(currentTime,response["key"]))

    #print "TESTED LUMINA"
    return 1

def myRightLabel(t):
    global rightText
    return rightText

def myLeftLabel(t):
    global leftText
    return leftText

def myFixation(t):
    global stimText
    return stimText

def myArrowOn(t):
    global fbVis
    return fbVis

# define location of target
def get_line_location(t):
    global direction
    temp = (0.5*screen.size[1], 0.8*screen.size[1])
    if direction == -1.0 :
        temp = (0.5*screen.size[0], 0.2*screen.size[1])

    if direction == 1.0  :
        temp = (0.5*screen.size[0], 0.8*screen.size[1])

    return temp

# define direction of arrow
def get_arrow_direction(t):
    global score
    return score

# define size of arrow
def get_arrow_size(t):
    global score

    if arrow_scale < 1  :
        size = (score, 10)

    if arrow_scale > 0 :
        size = (score, 10)

    return size

# define size of arrow
def get_arrow_position(t):
    global score, shift_unit, screen_half_x, screen_half_y, L
    position_x = screen_half_x + L/2.0*cos(score*3.14159/180.0)
    position_y = screen_half_y + L/2.0*sin(score*3.14159/180.0)
    #position_x = screen_half_x 
    #position_y = screen_half_y

    return (position_x, position_y)

#define color of arrow
def get_arrow_color(t):
    global arrowColor

    if arrowColor == 1:
        r = 1.0
        g = 0.0
        b = 0.0
        a = 1.0
    else:
        r = 1.0
        g = 1.0
        b = 1.0
        a = 1.0

    return (r,g,b,a)


def getSvmData(t):
    global dist_detrend
    return str(dist_detrend)

def detrendDist(time,dist):
    if DETREND:
        (slope,offset)=polyfit(time,dist,1)
    else:
        slope=1
        offset=0

    curr_dist = dist[-1]
    curr_time = time[-1]

    return curr_dist-(slope*curr_time+offset)

def sign(number):
    try:return number/abs(number)
    except ZeroDivisionError:return 1

def return_one(t):
    return 1

def lumina_trigger():
    global lumina_dev

    lumina_dev.poll_for_response()
    while lumina_dev.response_queue_size() > 0:
        response=lumina_dev.get_next_response()
        if response['key'] == 4:
            lumina_dev.clear_response_queue()
            print "TRIGGER RECEIVED!"
            return 1
    return 0
    
    

#######################
#  Define controllers #
#######################
###### Create an instance of the Controller class
if LUMINA == 1:
    trigger_in_controller = FunctionController(during_go_func=return_one, \
        between_go_func=lumina_trigger)
else:
    trigger_in_controller = KeyboardTriggerInController(pygame.locals.K_5)

stimulus_on_controller = ConstantController(during_go_value=1, \
                           between_go_value=0)
stimulus_off_controller = ConstantController(during_go_value=0, \
                           between_go_value=1)
state_controller = FunctionController(during_go_func=getState)
target_location_controller = FunctionController( \
                           during_go_func=get_line_location)
right_label_controller = FunctionController(during_go_func=myRightLabel)
left_label_controller = FunctionController(during_go_func=myLeftLabel)
task_controller = FunctionController(during_go_func=myFixation)
arrow_direction_controller = FunctionController( \
                           during_go_func=get_arrow_direction)

arrow_position_controller = FunctionController( \
                           during_go_func=get_arrow_position)
arrow_color_controller = FunctionController(during_go_func=get_arrow_color)
myArrowOnControl = FunctionController(during_go_func=myArrowOn)

#############################################################
#  Connect the controllers with the variables they control  #
#############################################################
# Actually listens to the TCP socket
if TCPIP: p.add_controller(None, None, tcp_listener)

p.add_controller(p,'trigger_go_if_armed',trigger_in_controller)
p.add_controller(textAA,'on', stimulus_off_controller )
#p.add_controller(textA,'on', stimulus_off_controller )
#p.add_controller(textB,'on', stimulus_off_controller )
#p.add_controller(textC,'on', stimulus_off_controller )
#p.add_controller(textD,'on', stimulus_off_controller )
p.add_controller(taskStimulus,'on', stimulus_on_controller)
p.add_controller(centerStim,'on', stimulus_on_controller)
p.add_controller(tach1,'on', stimulus_on_controller)
p.add_controller(tach2,'on', stimulus_on_controller)
p.add_controller(tach3,'on', stimulus_on_controller)
p.add_controller(tach4,'on', stimulus_on_controller)
p.add_controller(tach5,'on', stimulus_on_controller)
p.add_controller(tach6,'on', stimulus_on_controller)
p.add_controller(tach7,'on', stimulus_on_controller)
p.add_controller(tach8,'on', stimulus_on_controller)
p.add_controller(tach9,'on', stimulus_on_controller)
p.add_controller(tach10,'on', stimulus_on_controller)
p.add_controller(tach11,'on', stimulus_on_controller)
p.add_controller(tach12,'on', stimulus_on_controller)
p.add_controller(tach13,'on', stimulus_on_controller)
p.add_controller(tach14,'on', stimulus_on_controller)
p.add_controller(tach15,'on', stimulus_on_controller)
p.add_controller(tach16,'on', stimulus_on_controller)
p.add_controller(tach17,'on', stimulus_on_controller)
p.add_controller(tach18,'on', stimulus_on_controller)
p.add_controller(tach19,'on', stimulus_on_controller)
p.add_controller(tachLabelR,'on', stimulus_on_controller)
p.add_controller(tachLabelL,'on', stimulus_on_controller)

p.add_controller(arrowStimulus,'on', stimulus_on_controller)
p.add_controller(arrowStimulus,'orientation', arrow_direction_controller )
p.add_controller(arrowStimulus,'position', arrow_position_controller )


p.add_controller(arrowStimulus,'color', arrow_color_controller )
p.add_controller(tachLabelR,'text', right_label_controller )
p.add_controller(tachLabelL,'text', left_label_controller )
p.add_controller(taskStimulus,'text', task_controller)
p.add_controller(p, 'trigger_go_if_armed', state_controller)
p.parameters.handle_event_callbacks = [(pygame.locals.KEYDOWN, keydown)]

#######################
#  Run the stimulus!  #
#######################

p.go()
#p.export_movie_go(frames_per_sec=0.5,filename_base='movie/frame_')
log.close
f.close
