from gait_analysis import file_utils

# This pipeline refactors gait event to a qtm suitable form
FILENAME = "./data/191023_S08_TM_PGV0.17_BH_NS_MoCgapfilled_EventsAdded.c3d"
FILENAME_SAVE = "./data/191023_S08_TM_PGV0.17_BH_NS_MoCgapfilled_EventsAdded_test.c3d"


def main():
    c3d_wrapper = file_utils.C3dFileWrapper(FILENAME)
    events_table = c3d_wrapper.get_events()
    events_table = events_table.sort_values('time')
    counter = {'Left': 1, 'Right': 1}
    for idx, event in events_table.iterrows():
        if event['label'] == "Foot_Strike":
            events_table.loc[idx, 'label'] = event['context'] + "_stance" + str(counter[event['context']])
            counter[event['context']] += 1
            print(counter)

    events = events_table.sort_index()
    c3d_wrapper.set_events(events)
    c3d_wrapper.save_file(FILENAME_SAVE)
    print(events)


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
