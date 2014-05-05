import emotiv
import gevent
import os
import sys
import numpy as np
from collections import deque
from numpy import array
import wx
import wxversion
import pygame
from pygame import FULLSCREEN
from pygame.locals import *
from decimal import *
from pybrain.tools.shortcuts import buildNetwork
from scipy import stats


print(wx.version())


def get_val(val):
    ret = 0.3 * float(val)
    if ret > 255:
        ret = 254

    return ret

x = 1024
y = 30
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)
pygame.init()
windowSurface = pygame.display.set_mode((700, 600), 0, 32)
pygame.display.set_caption('Hello world')

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# set up fonts
basicFont = pygame.font.SysFont(None, 36)

# set up the text
text = basicFont.render('Hello world!', True, WHITE, BLUE)
textRect = text.get_rect()
textRect.centerx = windowSurface.get_rect().centerx
textRect.centery = windowSurface.get_rect().centery

# draw the white background onto the surface
windowSurface.fill(WHITE)

# get a pixel array of the surface
pixArray = pygame.PixelArray(windowSurface)
pixArray[480][380] = BLACK
del pixArray

# draw the text onto the surface
windowSurface.blit(text, textRect)

# draw the window onto the screen
pygame.display.update()

# Create network with 16 inputs, 5 hidden layers and two outputs
net = buildNetwork(16, 16, 1)

lInd = 0
rInd = 0
output_a = deque([])
output_b = deque([])
immediate_a = deque([])
immediate_b = deque([])

left_training = deque([])
right_training = deque([])



# run the game loop

class MainApplication(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(800, 500))
        self.left_training_active = False
        self.left_training_mode = []
        right_training_mode = []
        self.right_training_active = False
        app = wx.App()
        self.timer_state = 8.0
        menubar = wx.MenuBar()
        file = wx.Menu()
        help = wx.Menu()
        file.Append(101, '&Save', 'Save current measurements')


        quit = wx.MenuItem(file, 105, '&Quit\tCtrl+Q', 'Quit the Application')
        file.AppendItem(quit)

        menubar.Append(file, '&File')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_TOOL, self.OnQuit, id=105)
        panel = wx.Panel(self, -1)
        self.panel = panel


        self.lMan = 0

        startButton = wx.Button(self.panel, -1, "Start", (0, 400))
        stopButton = wx.Button(self.panel, -1, "Stop", (100, 400))

        leftButton = wx.Button(self.panel, -1, "Train Left", (400, 30))
        rightButton = wx.Button(self.panel, -1, "Train Right", (500, 30))

        self.Bind(wx.EVT_BUTTON, self.StartSimulationButton, startButton)
        self.Bind(wx.EVT_BUTTON, self.StartSimulationButton, stopButton)

        self.Bind(wx.EVT_BUTTON, self.StartLeftButton, leftButton)
        self.Bind(wx.EVT_BUTTON, self.StartRightButton, rightButton)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        #self.Show()

        self.timer = wx.Timer(self, 1)
        self.count = 0
        #self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.Bind(wx.EVT_TIMER, self.StartSimulationButton, self.timer)



        self.maxCorr = 0
        self.text1 = wx.StaticText(panel, -1, "", (25, 25), style=wx.ALIGN_LEFT)
        self.text2 = wx.StaticText(panel, -1, "", (25, 45), style=wx.ALIGN_LEFT)
        self.text3 = wx.StaticText(panel, -1, "", (25, 65), style=wx.ALIGN_LEFT)
        self.text4 = wx.StaticText(panel, -1, "", (25, 85), style=wx.ALIGN_LEFT)
        self.text5 = wx.StaticText(panel, -1, "", (25, 105), style=wx.ALIGN_LEFT)
        self.text6 = wx.StaticText(panel, -1, "", (25, 125), style=wx.ALIGN_LEFT)
        self.text7 = wx.StaticText(panel, -1, "", (25, 145), style=wx.ALIGN_LEFT)
        self.text8 = wx.StaticText(panel, -1, "", (25, 165), style=wx.ALIGN_LEFT)
        self.text9 = wx.StaticText(panel, -1, "", (25, 185), style=wx.ALIGN_LEFT)
        self.text10 = wx.StaticText(panel, -1, "", (25, 205), style=wx.ALIGN_LEFT)
        self.text11 = wx.StaticText(panel, -1, "", (25, 225), style=wx.ALIGN_LEFT)
        self.text12 = wx.StaticText(panel, -1, "", (25, 245), style=wx.ALIGN_LEFT)
        self.text13 = wx.StaticText(panel, -1, "", (25, 265), style=wx.ALIGN_LEFT)
        self.text14 = wx.StaticText(panel, -1, "", (25, 285), style=wx.ALIGN_LEFT)
        self.text15 = wx.StaticText(panel, -1, "", (25, 305), style=wx.ALIGN_LEFT)
        self.text16 = wx.StaticText(panel, -1, "", (25, 325), style=wx.ALIGN_LEFT)

        self.timerText = wx.StaticText(panel, -1, "Training Countdown: ", (400, 100), style=wx.ALIGN_LEFT)


        self.text1.SetLabel("Waiting for output")

        #--------------------------------------------- Graphics stuff -----------------------------------------------------#












        #----------------------------------------------Emotiv Stuff----------------------------------------------------------#

        self.headset = emotiv.Emotiv()
        gevent.spawn(self.headset.setup)


        self.sensor_names = ["F3", "FC5", "AF3", "F7", "T7", "P7", "O1", "O2", "P8", "T8", "F8", "AF4", "FC6", "F4", "X", "Y"];
        self.plist = [] #contains the dequeues for storing previous values
        self.slist = []
        i = 0
        for name in self.sensor_names:
            self.queue = deque([8000, 8000, 8000, 8000, 8000, 8000, 8000, 8000, 1000, 1000])
            self.squeue = deque([10, 10, 10, 10, 10, 10, 10, 10, 10, 10])
            self.plist.append(self.queue)
            self.slist.append(self.squeue)
            i = i + 1

        for i in range(len(self.plist)):
            self.queue = self.plist[i] #save the deque in a list
            self.squeue = self.slist[i]
            #print(self.queue) #test print

        self.counter = 0
        self.clear = 0
        self.printString = ""

        self.timer.Start(100)


    def StartLeftButton(self, evt):
        print("Left Training Started")
        if (self.left_training_active == False):
            self.left_training_active = True

    def StartRightButton(self, evt):
        print("Right Training Started")
        if (self.right_training_active == False):
            self.right_training_active = True



    def OnTimer(self, evt):
        print("Hey")


    def OnQuit(self, event):
        self.Close()

    def StopSimulationButton(self, evt):
        headset.close()
        self.close()


    def StartSimulationButton(self,evt):
        #if __name__ == "__main__":
          try:
            #while True:
                packet = self.headset.dequeue()
                i = 0
                for name in self.sensor_names:
             #       print(name + " | " + str(packet.sensors[name]['quality']) + " | " + str(packet.sensors[name]['value']))
                    self.queue = self.plist[i]

                    self.queue.popleft()
                    self.queue.append(packet.sensors[name]['value'])
                    i = i + 1
                current_vals = []
                std_devs = []
                slist = []
                sdevs = []
                for i in range(len(self.plist)): # go through each queue
                    queue = self.plist[i]
                    squeue = self.slist[i]
                    average = 0

                    for j in range(len(queue)): # determine the average of the values over the last 10 entries
                        average = average + queue[j]

                    npar = np.array(queue)
                    average = average / 10
                    nAverage = np.mean(queue)
                    nStd = np.var(queue)
                    #print(nStd)
                    nnStd = np.std(squeue)

                    std_devs.append(nStd)


                    squeue.popleft()
                    squeue.append(nStd)
                    nnStd = np.std(squeue)


                    #print(str(squeue) + " || " + str(nStd))
                    if (i < len(self.plist) -1):
                        ar1 = np.array(queue)
                        ar2 = np.array(self.plist[i+1])
                        d = np.correlate(ar1, ar2)
                        if (d > self.maxCorr):
                            self.maxCorr = d
                        d = float(d) / float(self.maxCorr)
                        #print(d)




                    current_vals.append(packet.sensors[self.sensor_names[i]]['value'])
                    if (i == 0):
                        self.text1.SetLabel("Name: " + self.sensor_names[i] + \
                        ", Quality: " + str(packet.sensors[self.sensor_names[i]]['quality']) + \
                        ", Value: " + str(packet.sensors[self.sensor_names[i]]['value']))
                    if (i == 1):
                        self.text2.SetLabel("Name: " + self.sensor_names[i] + \
                        ", Quality: " + str(packet.sensors[self.sensor_names[i]]['quality']) + \
                        ", Value: " + str(packet.sensors[self.sensor_names[i]]['value']))
                    if (i == 2):
                        self.text3.SetLabel("Name: " + self.sensor_names[i] + \
                        ", Quality: " + str(packet.sensors[self.sensor_names[i]]['quality']) + \
                        ", Value: " + str(packet.sensors[self.sensor_names[i]]['value']))
                    if (i == 3):
                        self.text4.SetLabel("Name: " + self.sensor_names[i] + \
                        ", Quality: " + str(packet.sensors[self.sensor_names[i]]['quality']) + \
                        ", Value: " + str(packet.sensors[self.sensor_names[i]]['value']))
                    if (i == 4):
                        self.text5.SetLabel("Name: " + self.sensor_names[i] + \
                        ", Quality: " + str(packet.sensors[self.sensor_names[i]]['quality']) + \
                        ", Value: " + str(packet.sensors[self.sensor_names[i]]['value']))
                    if (i == 5):
                        self.text6.SetLabel("Name: " + self.sensor_names[i] + \
                        ", Quality: " + str(packet.sensors[self.sensor_names[i]]['quality']) + \
                        ", Value: " + str(packet.sensors[self.sensor_names[i]]['value']))
                    if (i == 6):
                        self.text7.SetLabel("Name: " + self.sensor_names[i] + \
                        ", Quality: " + str(packet.sensors[self.sensor_names[i]]['quality']) + \
                        ", Value: " + str(packet.sensors[self.sensor_names[i]]['value']))
                    if (i == 7):
                        self.text8.SetLabel("Name: " + self.sensor_names[i] + \
                        ", Quality: " + str(packet.sensors[self.sensor_names[i]]['quality']) + \
                        ", Value: " + str(packet.sensors[self.sensor_names[i]]['value']))
                    if (i == 8):
                        self.text9.SetLabel("Name: " + self.sensor_names[i] + \
                        ", Quality: " + str(packet.sensors[self.sensor_names[i]]['quality']) + \
                        ", Value: " + str(packet.sensors[self.sensor_names[i]]['value']))
                    if (i == 9):
                        self.text10.SetLabel("Name: " + self.sensor_names[i] + \
                        ", Quality: " + str(packet.sensors[self.sensor_names[i]]['quality']) + \
                        ", Value: " + str(packet.sensors[self.sensor_names[i]]['value']))
                    if (i == 10):
                        self.text11.SetLabel("Name: " + self.sensor_names[i] + \
                        ", Quality: " + str(packet.sensors[self.sensor_names[i]]['quality']) + \
                        ", Value: " + str(packet.sensors[self.sensor_names[i]]['value']))
                    if (i == 11):
                        self.text12.SetLabel("Name: " + self.sensor_names[i] + \
                        ", Quality: " + str(packet.sensors[self.sensor_names[i]]['quality']) + \
                        ", Value: " + str(packet.sensors[self.sensor_names[i]]['value']))
                    if (i == 12):
                        self.text13.SetLabel("Name: " + self.sensor_names[i] + \
                        ", Quality: " + str(packet.sensors[self.sensor_names[i]]['quality']) + \
                        ", Value: " + str(packet.sensors[self.sensor_names[i]]['value']))
                    if (i == 13):
                        self.text14.SetLabel("Name: " + self.sensor_names[i] + \
                        ", Quality: " + str(packet.sensors[self.sensor_names[i]]['quality']) + \
                        ", Value: " + str(packet.sensors[self.sensor_names[i]]['value']))
                    if (i == 14):
                        self.text15.SetLabel("Name: " + self.sensor_names[i] + \
                        ", Quality: " + str(packet.sensors[self.sensor_names[i]]['quality']) + \
                        ", Value: " + str(packet.sensors[self.sensor_names[i]]['value']))
                    if (i == 15):
                        self.text16.SetLabel("Name: " + self.sensor_names[i] + \
                        ", Quality: " + str(packet.sensors[self.sensor_names[i]]['quality']) + \
                        ", Value: " + str(packet.sensors[self.sensor_names[i]]['value']))



           # gevent.sleep(0)

                diff = []
                current_average = 0
                dd = 0

                for i in range(len(current_vals)):
                    current_average = current_average + current_vals[i]
                current_average = current_average / len(current_vals)


                for i in range(len(current_vals)):
                    mydoub = current_vals[i] / float(current_average)
                    diff.append(std_devs[i]) # Save the current variation

                #print(net.activate([2, 2, 2, 2, 2, 2, 2, 2, 2, 2]))
                result = net.activate(diff)
                output_a.append(result[0])
                #output_b.append(result[1])
                immediate_a.append(result[0])
                #immediate_b.append(result[1])


                modeA = stats.mode(output_a) # What is the most common value among the last 1000 entries
                #modeB = stats.mode(output_b)

                iModeA = stats.mode(immediate_a) # what is the most common value among the last 10 entries
                #iModeB = stats.mode(immediate_b)

                if (self.left_training_active == True):
                    left_training.append(np.abs(modeA[0] - iModeA[0])) # Save the difference of the 2 modes
                    self.timer_state = self.timer_state - .1
                    if (self.timer_state <= 0):
                        self.timer_state = 8.0
                        self.left_training_active = False
                        self.left_training_mode = stats.mode(left_training)
                        self.lMan = self.left_training_mode[0][0]
                self.timerText.SetLabel("Training Duration: " + str(self.timer_state))

                lInd = np.abs(modeA[0] - iModeA[0])
                #rInd = np.abs(modeB[0] - iModeB[0])

                #print(self.left_training_mode)
                #print("lman: " + str(self.lMan))

                if (lInd > 255):
                    lInd = 255
                #if (rInd > 255):
                #@    rInd = 255

                #print("MOD: " + str(lInd) + ", " + str(rInd) + " | " + str(modeA[0]) + ", " + str(modeB[0]))


                if (len(output_a) > 1000):
                    output_a.popleft()

                if (len(output_b) > 1000):
                    output_b.popleft()

                if (len(immediate_a) > 5):
                    immediate_a.popleft()

                if (len(immediate_b) > 5):
                    immediate_b.popleft()

                windowSurface.fill(BLACK)


                col = get_val(diff[0])
                #print(col)
                pygame.draw.circle(windowSurface, (col, 0, 255-col), (290, 130), 20, 0) # Front Mid Left -1

                col = get_val(diff[1])
                #print(col)
                pygame.draw.circle(windowSurface, (col, 0, 255-col), (200, 180), 20, 0) # - 2


                col = get_val(diff[2])
                #print(col)
                pygame.draw.circle(windowSurface, (col, 0, 255-col), (250, 50), 20, 0) # Front Left - 3


                col = get_val(diff[3])
                #print(col)
                pygame.draw.circle(windowSurface, (col, 0, 255-col), (160, 120), 20, 0) # - 4

                col = get_val(diff[4])
                #print(col)
                pygame.draw.circle(windowSurface, (col, 0, 255-col), (140, 220), 20, 0) # - 5

                col = get_val(diff[5])
                #print(col)
                pygame.draw.circle(windowSurface, (col, 0, 255-col), (190, 340), 20, 0) # - 6

                col = get_val(diff[6])
                #print(col)
                pygame.draw.circle(windowSurface, (col, 0, 255-col), (220, 400), 20, 0) # - 7

                col = get_val(diff[7])
                #print(col)
                pygame.draw.circle(windowSurface, (col, 0, 255-col), (430, 400), 20, 0) # - 8

                col = get_val(diff[8])
                #print(col)
                pygame.draw.circle(windowSurface, (col, 0, 255-col), (460, 340), 20, 0) # - 9

                col = get_val(diff[9])
                #print(col)
                pygame.draw.circle(windowSurface, (col, 0, 255-col), (510, 220), 20, 0) # - 10

                col = get_val(diff[10])
                #print(col)
                pygame.draw.circle(windowSurface, (col, 0, 255-col), (490, 120), 20, 0) # - 11

                col = get_val(diff[11])
                #print(col)
                pygame.draw.circle(windowSurface, (col, 0, 255-col), (400, 50), 20, 0) # Front Right - 12

                col = get_val(diff[12])
                #print(col)
                pygame.draw.circle(windowSurface, (col, 0, 255-col), (450, 180), 20, 0) # - 13

                col = get_val(diff[13])
                #print(col)
                pygame.draw.circle(windowSurface, (col, 0, 255-col), (360, 130), 20, 0) # Front Mid Right - 14


                pygame.draw.circle(windowSurface, (0, 255-lInd, lInd), (100, 500), 80, 0) # Left Indicator
                pygame.draw.circle(windowSurface, (0, 255-rInd, rInd), (570, 500), 80, 0) # Right Indicator


                #pygame.draw.circle(windowSurface, (col, 0, 255-col), (160, 280), 20, 0) # - 11
                #pygame.draw.circle(windowSurface, (col, 0, 255-col), (490, 280), 20, 0) # - 12



                text = basicFont.render('Hello world!', True, (255, 0, 0))
                textRect = text.get_rect()
                textRect.centerx = windowSurface.get_rect().centerx
                textRect.centery = windowSurface.get_rect().centery

                windowSurface.blit(text, textRect)
                pygame.draw.rect(windowSurface, BLACK, (textRect.left - 20, textRect.top - 20, textRect.width + 40, textRect.height + 40))

                pygame.display.update()


                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()





          except KeyboardInterrupt:
            self.headset.close()




    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.SetPen(wx.Pen(wx.BLACK, 4))
        dc.DrawLine(0, 0, 50, 50)



app = wx.App(False)
frame = MainApplication(None, -1, 'display')
frame.Show()
app.MainLoop()









