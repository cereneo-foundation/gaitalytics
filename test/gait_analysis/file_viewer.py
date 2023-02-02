from pyCGM2.Tools import btkTools
from pyCGM2.Utils import utils

# This pipeline refactors gait event to a qtm suitable form
FILENAME = "test/data/static.c3d"


def main():
    acq = btkTools.smartReader(FILENAME)
    acq.GetPoints()
    i = acq.BeginPoint()
    while i != acq.EndPoint():
        print(i.value().GetLabel())
        i.incr()




# Using the special variable
# __name__
if __name__ == "__main__":
    main()
