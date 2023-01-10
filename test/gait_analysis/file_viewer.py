from gait_analysis import file_utils

# This pipeline refactors gait event to a qtm suitable form
FILENAME = "./data/Gait LB - IOR 1.c3d"


def main():
    c3d_wrapper = file_utils.C3dFileWrapper(FILENAME)
    events = c3d_wrapper.get_events()
    print(events)


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
