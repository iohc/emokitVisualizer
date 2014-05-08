emokitVisualizer
================

Visualizer and Neural Network simulation based on emokit

This is a port based off the emokit by Cody Brocious (http://github.com/daeken) and Kyle Machulis (http://github.com/qdot)

All files are the same, except I have modified files in /python/emokit

To run the modifications I have created, python neuralNetwork.py

! It doesn't work well yet  -- There are quite a few issues. !


The basic premise is this: There is a visualizer that shows the statistical variance of each sensor. (http://imgur.com/F4FsecU)

You can use this to monitor the change (over the course of one second) of each sensor.

At the start of the program, the monitor records a baseline by asking you to remain calm. These values are used in a fully recurrent neural network developed with pybrain. After the training period is complete the raw sensor values are piped into a 16 input one output neural network. The value of the neural network is *supposed* to correlate to some intended action. 

Current issues: 

It seems difficult for people to maintain the "blank slate" mindset for more than a few seconds. Thus the training session for the neural net is limited to approx. 50 entries. 

A related issue is, because of the limited number of training cycles, there is often no change in the actual output of the network and the value we would expect from the values displayed in the visualizer. 

I still don't know how to determine expected behavior for the general public. It's an issue I'm still working on. 

------------------------------------------------------------------------------------------------------------------------------------

This software has the same license as the original, which is basically public domain. 

If you wish to contribute, awesome! Shoot me an email at baldwindc@gmail.com if you wish to join the development. 


