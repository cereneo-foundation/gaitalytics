from gait_analysis import file_utils

# This pipeline refactors gait event to a qtm suitable form
FILENAME = "./data/Gait LB - IOR 1.c3d"
FILENAME_SAVE = "./data/Gait LB - IOR 1_man.c3d"


def main():
    c3d_wrapper = file_utils.C3dFileWrapper(FILENAME)
    events_table = c3d_wrapper.get_events()
    # events_table = events_table.sort_values('time')
    for idx, event in events_table.iterrows():
        label = events_table.loc[idx, 'label'][0:3]
        print("%s , size %i" % (label, len(label)))
        events_table.loc[idx, 'label'] = label

    #events_table = events_table.sort_values('time')
    c3d_wrapper.set_events(events_table)
    c3d_wrapper.save_file(FILENAME_SAVE)
    print(events_table)


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
