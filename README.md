[![DOI](https://zenodo.org/badge/9342/OpenCogLabRepository/RTfMRI-neurofeedback.svg)](https://zenodo.org/badge/latestdoi/9342/OpenCogLabRepository/RTfMRI-neurofeedback)

# Real-time fMRI Neurofeedback Task Stimulus

R. Cameron Craddock<sup>1,2,†</sup>, Jonathan Lisinski<sup>3</sup>, Stephen M. LaConte<sup>3,4,5</sup>

<sup>1</sup>Nathan S. Kline Institute for Psychiatric Research, Orangeburg, NY, <sup>2</sup>Child Mind Institute, New York, NY, <sup>3</sup>Virginia Tech Carilion Research Institute, Roanoke, VA, <sup>4</sup>School of Biomedical Engineering and Sciences, Virginia Polytechnic Institute and State University, Blacksburg, VA, <sup>5</sup>Departments of Emergency Medicine and Emergency Radiology, Virginia Tech Carilion School of Medicine, Roanoke, VA

<sup>†</sup>Contact [ccraddock@nki.rfmh.org](mailto:ccraddock@nki.rfmh.org) with any comments or questions.

This stimuli was developed for conducting real-time fMRI based default mode network neurofeedback experiments (Craddock et al. 2012, LaConte et al. 2011).

The Neurofeedback task stimulus is implemented in Python using the [VisionEGG](http://visionegg.org/) library. The script displays the current level of activity of a brain area or network using an analog meter (see Fig. 1). On the meter, zero is straight up and down, and negative and positive values are on either side. The left and right side of the scale are labeled with strings that describe a behavior that is associated with the level of activity. For example, in the default mode network (DMN) example, low activity is referred to as "Focused" and high activity is "Wandering". The current task instruction is centered beneath the meter in a large font.

![Fig. 1 Example of stimuli.](analog_meter.png?raw=true "Fig. 1 Example of analog meter.")

*Figure 1. Analog meter stiluli for "focus" and "wander" conditions. During "feedback" tasks the needle moves left or right based on DMN activity. The needle does not move during "no-feedback" tasks.*

The task has two modes, "feedback" and "no feedback". During feedback the needle moves to the left and right to indicate the current level of activity. In no-feedback the needle does not move, it remains in zero position for the entire task. The activity displayed on the meter is received as a string over a TCP/IP connection. Once received the data is converted into a floating point number and optionally linearly detrended using all previously collected values. The value is converted to an angular change using 3° per .5 of signal. The angular change is then added to the needle position moving it to the left or right. In this way, the needle position represents a windowed average of activity. This is down to smooth and stabilize the needle's movements. Although this data can be received from a variety of sources, the task was designed and has been tested to work with the [AFNI's 3dsvm real-time plugin](http://lacontelab.org/3dsvm.htm).

## Example fMRI Experiment

A proof of concept experiment was conducted in 13 healthy controls to test their ability to modulate the Default Mode Network using the realt-time fMRI neurofeedback task (Craddock et al. 2012). The ability to modulate the network was evaluated by correlating the time course of DMN activation with a regressor describing the task instructions. Figure 2 provides example DMN spatial maps, time courses of activity, and the task regressor for the best performing (top) and worse performing (bottom) participants. The correlation between the best performing participant's DMN activity and task regressor, although there was considerable high frequency fluctuations. The worst participant had some very large motion spikes, which considerably degraded their behavior.

![Fig. 2 Example of task results for best and worst participants from an initial experiment with the real-time fMRI Neurofeedback paradigm.](CCD_best_worst.png?raw=true "Example of task results for best and worst participants from an initial experiment with the real-time fMRI Neurofeedback paradigm.")

*Figure 2. Example of task results for best and worst participants from an initial experiment with the real-time fMRI Neurofeedback paradigm. Spatial maps of the DMN that was extracted from each participant. The correlation between DMN activity and task regressor is obvious in the best participant, but not in the worst.*

## Usage Notes
This task requires that the [VisionEGG](http://visionegg.org/) ecosystem be installed.

The task can record button presses from a Lumina button box or keyboard. Once started, the task will ask the user to input a participant ID, to indicate whether the task is being run in "feedback" or "no feedback" mode, and to select a task number that will be used to select a task configuration file (described later), and a TCP/IP port number. The task will then wait to receive a TCP connection from the remote client. Once the connection is received, the task waits to receive a trigger from the scanner as either a keypress or from a Lumina box.

At the beginning of top of the task python script are constants that configure task behavior

    LUMINA        = 1 # set to 1 to use LUMINA for input
    DETREND       = 0 # set to 1 to detrend receved values
    TCPIP         = 1 # Set to 1 to receive data over TCP/IP
    TCPIP_PORT    = 8000 # Port receiving TCP/IP data
    TCPIP_GUI     = 1  # Open GUI to initialize TCP/IP

    LUMINA_TRIGGER = 4 # Value that indicates a TRIGGER signal from the scanner

The task script can use a variety of different configurations that are selected by a task number that is configured on startup. This functionality was added to make it easy to counterbalance the ordering of task blocks across participants, but can be used to support a variety of different tasks and permutations.


    # 2 dimensional array that maps feedback status and
    # task number to configuration file. The row index
    # corresponds to task number and the column to the
    # task type 0 = 'no feedback', 1 = 'feedback'
    stim_files= \
        [ \
            [ 'task-0_no-feedback.cfg', 'task-0_feedback.cfg'],
            [ 'task-1_no-feedback.cfg', 'task-1_feedback.cfg'],
            [ 'task-2_no-feedback.cfg', 'task-2_feedback.cfg'],
            [ 'task-3_no-feedback.cfg', 'task-3_feedback.cfg'],
        ]

These values are used to select a configuration file (described below) that is used to determine the instructions, task timing information, and the labels of the left and right sides of the analog meter.

The configuration files specify the labels of the left and right sides of the analog meter, task instructions, and timing information. This should make it easy to customize the task and to handle counterbalancing. Extensive descriptions of the file format are provided in the header of the supplied config files. It may be easier to write a python script to generate the various config files for an experiment. An example script for generating these files is provided in ```create_stim_cfg.py```.

## Scoring Responses
Responses and response times can be extracted from the output log files using the ```NFB_get_button_presses.py``` Python script. This script requires the [Pandas](http://pandas.pydata.org/) library.

## Acknowledgements
This task is a modification of a analog meter feedback paradigm implemented in VisionEGG by J. Lisinski and S. LaConte. Support for the DMN application of this task was provided by a NARSAD Young Investigator Award and NIMH BRAINS R01MH101555 to RCC.

## References 

Craddock, R.C., Lisinski, J.M., Chiu, P., Mayberg, H.S., LaConte, S.M., (**2012**). Real-Time Tracking and Biofeedback of the Default Mode Network., *Proceedings of the Organization of Human Brain Mapping 18th Annual Meeting*, Beijing, China.

LaConte, S. M. (**2011**). Decoding fMRI brain states in real-time. *NeuroImage*, 56(2), 440–454. [doi:10.1016/j.neuroimage.2010.06.052](http://dx.doi.org/10.1016/j.neuroimage.2010.06.052)
