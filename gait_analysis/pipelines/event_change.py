from gait_analysis import file_utils

# This pipeline refactors gait event to a qtm suitable form
FILENAME = "./data/191023_S08_TM_PGV0.17_BH_NS_MoCgapfilled_EventsAdded.c3d"
FILENAME_SAVE = "./data/191023_S08_TM_PGV0.17_BH_NS_MoCgapfilled_EventsAdded_test.c3d"


def main():
    c3d_wrapper = file_utils.C3dFileWrapper(FILENAME)
    events_table = c3d_wrapper.get_events()
    # events_table = events_table.sort_values('time')
    for idx, event in events_table.iterrows():
        if event['label'] == "Foot_Strike":
            if event['context'] == 'Left':
                events_table.loc[idx, 'label'] = "LHS"
            else:
                events_table.loc[idx, 'label'] = "RHS"
        elif event['label'] == "Foot_Off":
            if event['context'] == 'Left':
                events_table.loc[idx, 'label'] = "LTO"
            else:
                events_table.loc[idx, 'label'] = "RTO"
        events_table.loc[idx, 'context'] = ""
    #events_table = events_table.sort_values('time')
    c3d_wrapper.set_events(events_table)
    c3d_wrapper.save_file(FILENAME_SAVE)
    print(events_table)


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
