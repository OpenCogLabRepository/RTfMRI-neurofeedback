#!/usr/bin/env python2.6

import numpy as np
import os, sys

# function to print header comments for label file
def print_header_comments( outfd ):
    header_comment_string = \
"""
# Configuration file for pdigm_tachometer.py
#
# R. Cameron Craddock
# Jonathan Lisinski
# Stephen LaConte
#
# Tachometer neurofeedback paradigm configuration file. The goal of 
# this file is to allow anyone to construct a analog-meter
# neurofeedback experiment by just editing this file and not mucking 
# with the python script.
#
# Lines beginning with \'#\' and blank lines are ignored. 
#
# The file must begin with at least fourt lines of the form 
# <command>:<value>, i.e. a command followed by a colon and 
# then a value. The commands that MUST occur at the beginning 
# of each file are ISI, NUMSTIM, FEEDBACK, and INSTRUCTION; 
# these are described below.
# 
# ISI:         Interstimulus interval in seconds. If multiple ISI
#              commands are received, the last one wins.
#
# NUMSTIM:     Total number of stimuli in paradigm, if the stim file
#              is shorter than this value an error will be produced
#              by the script. If the file is longer, values past 
#              NUMSTIM will be ignored. If multiple NUMSTIM commands
#              are received, the last one wins.
#
# FEEDBACK   : A value of 0 or 1 corresponding to whether or not the subject
#              should be given feedback during this experiment.
#              0 = No Feedback
#              1 = Feedback
#
# INSTRUCTION: A string of maximum 252 characters that will be wrapped
#              into a 28 x 9 character text box. This string will be
#              displayed at the beggining of the paradigm until the
#              script is initiated by the scanner trigger or \'5\' is
#              pressed. Intended as a means to instruct the subject
#              on the paradigm. The first space after the colon is 
#              considered part of the string. Strings from multiple
#              INSTRUCTION commands will be concatenated, seperated by
#              a newline \\n character. The fully constructed 
#              instruction will be truncated to 252 characters to avoid
#              VisionEgg crashes. 
#          
#              Feel free to be creative with the format. Control 
#              characters such as \\t and \\n should behave normally. 
#              Blank lines, or lines with only spaces ending with 
#              an \\n are ignored. Don't complain to me, this is a 
#              problem with VisionEGG. Also, don't expect fancy 
#              characters to work. Always make sure to precede every 
#              \\n with a character or a space, failure to do so will 
#              resulted in an error similar to:
#
#               \"UnboundLocalError: local variable \'line\' referenced 
#                 before assignment\" 
#
#              This is a problem with VisionEGG and may get fixed, so
#              go ahead and try it if you get frisky.
#
# All lines that are not these commands, and do not begin with a \'#\'
# are interpreted as similus specifiers. A stimulus specifier has the
# form:
#
# <LEFT TEXT>;<RIGHT TEXT>;<STIMULUS>;<SHOW>
#
# These values must be seperated by a semicolor ";", failure to do so
# will result in an error. Any additional values past these four will
# be ignored as long as they come after a semicolon ";". 
#
# <LEFT TEXT>  Specifies the string that is on the left side of the
#              tachometer 
# <RIGHT TEXT> Specifies the string that is on the right side of the
#              tachometer
# <STIMULUS>   Specifies the string that is presented bottom-center
#              of the tachometer in a larger font
# <SHOW>       Indicates wether the tach needle should show 
#              neurofeedback during the stimuli 1 indicates that
#              feedback is on and 9999 indicates that it is off. This
#              value can only be a 1 or 9999, otherwise error.
#
# The best way for you to understand what these values mean is to try
# out an example. The code below should work:
# 
# #Few lines for an example configuration
# ISI: 2.0
# NUMSTIM: 15
# FEEDBACK: 1
# INSTRUCTION:          FEEDBACK
# INSTRUCTION:      Control Your Mind
# # begin with baseline
# LOW;HIGH;Rest;9999
# LOW;HIGH;Rest;9999
# # decrease activity of brain region
# LOW;HIGH;DECREASE;9999
# LOW;HIGH;DECREASE;1
# LOW;HIGH;DECREASE;1
# LOW;HIGH;DECREASE;1
# LOW;HIGH;DECREASE;1
# # push a button, 2 seconds to do this
# LOW;HIGH;Push Button;9999
# # increase activity of brain region
# LOW;HIGH;INCREASE;9999
# LOW;HIGH;INCREASE;1
# LOW;HIGH;INCREASE;1
# LOW;HIGH;INCREASE;1
# LOW;HIGH;INCREASE;1
# # end with baseline
# LOW;HIGH;Rest;9999
# LOW;HIGH;Rest;9999
#
# I do not recommend that you write this file by hand, but rather write
# a script to generate this file
"""
    try:
        outfd.write(header_comment_string)
    except:
        print >> sys.stderr, 'Could not write to outfile %s' \
                %(sys.exc_info()[0])
        raise
    return

###### Configuration details
# inter-stimulus interval
inter_stim_interval=2.0

# durations for the blocks organized into sub-blocks that we will use to flip
# the left-right strings
stim_durations=[[ 15, 45, 30 ],  \
                [ 15, 45, 30 ],  \
                [ 30, 45, 15 ],  \
                [ 30, 45, 15 ]]

# strings to use for creating filenames
block_sides=["normal","swapped"]

# strings that will serve as the stimuli for sub_block_conditions
stimulus_strings=["Wander","Focus"]

# the labels that will be applied to the left and right sides of the analog
# meter, these should be considered in the context of the classifier to be 
# used. The paradigm is designed so that positive classifier output
# corresponds to moving the arrow to the right, so the right string should
# correspond to positive classifier output. This will be swapped during which
# time the classifier output will be multiplied by -1 (corresponding to 
# sub_block_show = -1)
left_right_strings=["Focused","Wandering"]

# in case we want to do something different between blocks
inter_block_delay=1
inter_block_instruction=['Push Button']
inter_block_show=9999

# "warm up" time between conditions
warm_up_delay=1
warm_up_show=9999

# baseline durations [beginning, end] and stimulus
baseline_durations=[15,15]
baseline_string=["Rest"]
baseline_show=9999

# instructions for the task, the first instruction
# i.e. instructions[0] are given for No Feedback runs
# instructions[1] are given for Feedback runs.
instructions = ["        No Feedback", \
                "          Feedback"]

# Short instruction names that will be used creating a
# filename for the paradigm configuration file.
# instructions_short_names[0] corresponds to No Feedback
# instructions_short_names[1] corresponds to Feedback
instructions_short_names=["NoFB","FB"]

###### END Configuration details

num_stims=np.sum(stim_durations) + \
          np.sum(baseline_durations) + \
          (np.prod(np.shape(stim_durations))-1) * inter_block_delay + \
          (np.prod(np.shape(stim_durations))-1) * warm_up_delay;

for fb in range(2):
    for start_side in range(len(left_right_strings)):
        for start_cond in range(len(stimulus_strings)):

            filename='DMN_TRACKING_%s_%s_%s_v2.cfg'% \
                ( instructions_short_names[fb].lower(), \
                  block_sides[start_side].lower(), \
                  stimulus_strings[start_cond].lower() )

            lbl_filename='DMN_TRACKING_%s_%s_%s_v2.1D'% \
                ( instructions_short_names[fb].lower(), \
                  block_sides[start_side].lower(), \
                  stimulus_strings[start_cond].lower() )


            print >> sys.stderr, 'Creating %s'%( filename )

            # open the paradigm file
            try:
                outf=open(filename,'w')
            except IOError as (errno, strerror):
                print 'Could not open %s. I/O error({0}): {1}'%( \
                    filename,errno, strerror)
                sys.exit(1)

            # Print header comments to the file
            print_header_comments( outf )

            # print header commands to the file
            outf.write(":".join(["ISI",str(inter_stim_interval)])+"\n")
            outf.write(":".join(["NUMSTIM",str(num_stims)])+"\n")
            outf.write(":".join(["FEEDBACK",str(fb)])+"\n")
            for i in instructions[fb].split("\n"):
                outf.write(":".join(["INSTRUCTION",i])+"\n")

            # open the label file
            try:
                lbl_outf=open(lbl_filename,'w')
            except IOError as (errno, strerror):
                print 'Could not open %s. I/O error({0}): {1}'%( \
                    lbl_filename,errno, strerror)
                outf.close()
                sys.exit(1)

            # write a header to the label file
            lbl_outf.write("#Focus_Wander\tSwapped_Normal\tCensor\n")

            # get the left a right strings
            LR_strings = left_right_strings
            stim_sign = 1
            # swap the strings if we so desire
            if start_side == 1:
                LR_strings=LR_strings[::-1]
                stim_sign = -1

            # cache a copy of the stimulus
            # strings and swap if necessary
            stim_strings = stimulus_strings
            if start_cond == 1:
                stim_strings=stim_strings[::-1]

            # first we handle the baseline
            if baseline_durations:
                if baseline_string:
                    bstr=baseline_string[0]
                else:
                    bstr="Baseline"

                for i in range(baseline_durations[0]):
                    outf.write(";".join(LR_strings+ \
                        [bstr]+[str(baseline_show)])+ \
                        "\n")
                    lbl_outf.write("0\t0\t%d\n"%(baseline_show))

            sub_block_count=0
            for block_num in range(np.shape(stim_durations)[0]):

                for sub_block_num in range(np.shape(stim_durations)[1]):

                    if sub_block_count > 0:
                        # if this is not the first subblock then print the
                        # inter-subblock stimuli
                        for i in range(inter_block_delay):
                            if inter_block_instruction:
                                outf.write(";".join(LR_strings +\
                                    inter_block_instruction + \
                                    [str(inter_block_show)]) + "\n")
                                lbl_outf.write("0\t%d\t%d\n" \
                                    %((-1)**(block_num%2), \
                                    inter_block_show))

                        # if we have a warm_up, then do it
                        for i in range(warm_up_delay):
                            outf.write(";".join(LR_strings+\
                                [stim_strings[\
                                   sub_block_count%len(stim_strings)]]+\
                                [str(stim_sign*warm_up_show)])+ "\n")
                            lbl_outf.write("0\t%d\t%d\n" \
                                %((-1)**(block_num%2), \
                                 warm_up_show))

                    # now print the stims for this block
                    for i in range(stim_durations[block_num][sub_block_num]):
                       outf.write(";".join(LR_strings+\
                           [stim_strings[\
                              sub_block_count%len(stim_strings)]]+\
                           [str(stim_sign*fb)])+ "\n")
                       lbl_outf.write("%d\t%d\t1\n" \
                           %( (-1)**(sub_block_count%2), \
                              (-1)**(block_num%2)))

                    sub_block_count=sub_block_count+1

                # swap the left and right strings and the sign
                LR_strings = LR_strings[::-1]
                stim_sign = -1 * stim_sign
            
            # handle the post-baseline
            if len(baseline_durations)==2:
                if baseline_string:
                    bstr=baseline_string[0]
                else:
                    bstr="Baseline"

                for i in range(baseline_durations[1]):
                    outf.write(";".join(LR_strings+ \
                        [bstr]+[str(baseline_show)])+ \
                        "\n")
                    lbl_outf.write("0\t0\t%d\n"%(baseline_show))

            # finished with the output files, so close them
            outf.close()
            lbl_outf.close()

            # use waver to make an ideal timecourse
            ideal_filename='DMN_TRACKING_%s_%s_%s_v2_ideal.1D'% \
                ( instructions_short_names[fb].lower(), \
                  block_sides[start_side].lower(), \
                  stimulus_strings[start_cond].lower() )

            # construct the command
            os.system(" ".join(["waver", "-WAV", \
                       "-dt", str(inter_stim_interval), \
                       "-numout", str(num_stims), \
                       "-input", "%s\'[0]\'"%(lbl_filename), \
                       ">",ideal_filename]))
