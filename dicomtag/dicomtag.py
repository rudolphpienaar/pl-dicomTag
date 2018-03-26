#                                                            _
# dicomtag ds app
#
# (c) 2016 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

import os

# import the Chris app superclass
from chrisapp.base import ChrisApp


class Dicomtag(ChrisApp):
    """
    This app generates a file of DICOM tag results, and optionally an html page..
    """
    AUTHORS         = 'FNNDSC (rudolph.pienaar@gmail.com)'
    SELFPATH        = os.path.dirname(os.path.abspath(__file__))
    SELFEXEC        = os.path.basename(__file__)
    EXECSHELL       = 'python3'
    TITLE           = 'Generate DICOM tag list'
    CATEGORY        = 'DICOM'
    TYPE            = 'ds'
    DESCRIPTION     = 'This app generates a file of DICOM tag results, and optionally an html page.'
    DOCUMENTATION   = 'http://wiki'
    VERSION         = '0.1'
    LICENSE         = 'Opensource (MIT)'
    MAX_NUMBER_OF_WORKERS = 1  # Override with integer value
    MIN_NUMBER_OF_WORKERS = 1  # Override with integer value
    MAX_CPU_LIMIT         = '' # Override with millicore value as string, e.g. '2000m'
    MIN_CPU_LIMIT         = '' # Override with millicore value as string, e.g. '2000m'
    MAX_MEMORY_LIMIT      = '' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_MEMORY_LIMIT      = '' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_GPU_LIMIT         = 0  # Specifies the number of GPUs
    MAX_GPU_LIMIT         = 0  # Specifies the number of GPUs

    # Fill out this with key-value output descriptive info (such as an output file path
    # relative to the output dir) that you want to save to the output meta file when
    # called with the --saveoutputmeta flag
    OUTPUT_META_DICT = {}
 
    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        """

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """



# ENTRYPOINT
if __name__ == "__main__":
    app = Dicomtag()
    app.launch()
