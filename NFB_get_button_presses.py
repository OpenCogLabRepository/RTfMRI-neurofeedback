
# coding: utf-8

# In[105]:

import os
import numpy as np

def parse_logfile(log_lines):

    stat_dict = None

    # initialize counters
    waiting_for_button = 0
    num_misses = 0
    num_hits = 0
    false_alarms = 0
    total_buttons = 0
    button_start_time = 0.0
    mean_reaction_time = 0.0

    # go through the list of strings and count the number of button presses (and missed presses)
    for l in log_lines:
        if '#' in l:
            continue
        l = l.rstrip()
        v = l.split(';')

        if len(v) == 10:
            if "Push Button" in v[4]:
                total_buttons = total_buttons + 1
                button_start_time = float(v[0])
                if waiting_for_button == 1:
                    num_misses = num_misses+1
                waiting_for_button = 1
        elif len(v) == 3:
            if "LUMINA" in v[1]:
                if waiting_for_button == 1:
                    rt = (float(v[0])-button_start_time)
                    # count reaction times > 10s as misses + false alarm
                    if rt > 10.0:
                        num_misses += 1
                        false_alarms +=  1
                    else:
                        num_hits += 1
                        mean_reaction_time += rt
                else:
                    false_alarms += 1
                waiting_for_button = 0
    if num_hits > 0:
        mean_reaction_time /= float(num_hits)
    else:
        mean_reaction_time = np.nan

    stat_dict = {"total_buttons": total_buttons,
                 "num_hits": num_hits,
                 "num_misses": num_misses,
                 "false_alarms": false_alarms,
                 "mean_reaction_time": mean_reaction_time}

    return stat_dict

        


def main():

    import argparse
    import os
    import pandas as pd

    parser = argparse.ArgumentParser()


    parser.add_argument("directory", type=str,
                        help="full path to the directory holding the log files to be processed")

    parser.add_argument("out_file", type=str,
                        help="name of the output file")

    args = parser.parse_args()

    stat_dicts = []

    if os.path.isdir(args.directory):

        file_count = 0
        for filename in os.listdir(args.directory):

            if filename.endswith(".txt"):
                file_count += 1

                file_path = os.path.join(args.directory, filename)
                if os.path.isfile(file_path):

                    pat_id = os.path.basename(filename)

                    print "Processing %s => %s" % (pat_id, file_path)

                    with open(file_path) as infd:

                        log_lines=infd.readlines()

                        sess_dict=parse_logfile(log_lines)

                        if sess_dict:
                            sess_dict['pat_id'] = pat_id
                            stat_dicts.append(sess_dict)
                        else:
                            raise Exception("Could not parse logfile (%s) contents"%(file_path))
                else:
                    print "%s doesn't seem to be file?"%(file_path)

        if stat_dicts:
            nfb_stat_df = pd.DataFrame(stat_dicts)
            nfb_stat_df.to_csv(args.out_file)
        else:
            print "No NFB logging information found in %d possible logfiles."%(file_count)

    else:
        raise Exception("%s is not a directory"%(args.directory))

if __name__ == "__main__":

    main()

