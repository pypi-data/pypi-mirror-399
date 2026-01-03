import numpy as np
import os

from .context import line_racer

# todo: intensity correction definition first, so we dont have to download anything


def test_line_racer_exomol():

    lr = line_racer.line_racer

    # define states file
    upper_state = "           1 54321.54321    211     110      19   e"
    lower_state = "           2 73760.69115    245     122      31   e"

    os.makedirs("exomol_tests/", exist_ok=True)
    with open("exomol_tests/exomol.states", "w") as f:
        f.write(upper_state + "\n")
        f.write(lower_state + "\n")

    # define transition file
    transition = "           1            2 1.2345E-01   187.010999"

    with open("exomol_tests/exomol.trans", "w") as f:
        f.write(transition + "\n")

    # define partition function
    partition1 = "   797.0        295.2217"
    partition2 = "  1800.0        800.0860"

    with open("exomol_tests/exomol.pf", "w") as f:
        f.write(partition1 + "\n")
        f.write(partition2 + "\n")

    temperatures = [797.0, 1800]
    pressures = list(np.logspace(-6, 3, 5))

    # create line racer object
    exomol_test_racer = lr.LineRacer(database="exomol",
                                     input_folder="exomol_tests/",
                                     mass=18.0,
                                     species_isotope_dict={"1H2-16O": 1.0},
                                     temperatures=temperatures,
                                     pressures=pressures,
                                     )


# todo: these are the read in tests
# todo: also do tests for the processing of many lines, could maybe be done using the calculate one pt point function?
# todo: test also the other databases




