#!/usr/bin/env python
#                                                             _
# dicomtag ds app
#
# (c) 2016 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

import  os
import  sys

# import the Chris app superclass
from    chrisapp.base   import ChrisApp

import  libtag

class Dicomtag(ChrisApp):
    """
    This app generates a file of DICOM tag results, and optionally an html page..
    """
    AUTHORS                 = 'FNNDSC (rudolph.pienaar@gmail.com)'
    SELFPATH                = os.path.dirname(os.path.abspath(__file__))
    SELFEXEC                = os.path.basename(__file__)
    EXECSHELL               = 'python3'
    TITLE                   = 'Generate DICOM tag list'
    CATEGORY                = 'DICOM'
    TYPE                    = 'ds'
    DESCRIPTION             = 'This app generates a file of DICOM tag results, and optionally an html page.'
    DOCUMENTATION           = 'http://wiki'
    VERSION                 = '0.1'
    LICENSE                 = 'Opensource (MIT)'
    MAX_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MIN_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MAX_CPU_LIMIT           = '' # Override with millicore value as ChrisApp.path, e.g. '2000m'
    MIN_CPU_LIMIT           = '' # Override with millicore value as ChrisApp.path, e.g. '2000m'
    MAX_MEMORY_LIMIT        = '' # Override with ChrisApp.path, e.g. '1Gi', '2000Mi'
    MIN_MEMORY_LIMIT        = '' # Override with ChrisApp.path, e.g. '1Gi', '2000Mi'
    MIN_GPU_LIMIT           = 0  # Specifies the number of GPUs
    MAX_GPU_LIMIT           = 0  # Specifies the number of GPUs

    # Fill out this with key-value output descriptive info (such as an output file path
    # relative to the output dir) that you want to save to the output meta file when
    # called with the --saveoutputmeta flag
    OUTPUT_META_DICT = {}
 
    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        """
        self.add_argument("-i", "--inputFile",
                            optional    = True
                            type        = ChrisApp.path,
                            help        = "input file",
                            dest        = 'inputFile')
        self.add_argument("-F", "--tagFile",
                            optional    = True
                            type        = ChrisApp.path,
                            help        = "file containing tags to parse",
                            dest        = 'tagFile',
                            default     = '')
        self.add_argument("-T", "--tagList",
                            optional    = True
                            type        = ChrisApp.path,
                            help        = "comma-separated tag list",
                            dest        = 'tagList',
                            default     = '')
        self.add_argument("-r",
                            optional    = True
                            help        = "display raw tags",
                            dest        = 'rawType',
                            default     = 'raw')
        self.add_argument("-I", "--imageFile",
                            optional    = True
                            type        = ChrisApp.path,
                            help        = "image file to convert DICOM input",
                            dest        = 'imageFile',
                            default     = '')
        self.add_argument("-o", "--outputFileStem",
                            optional    = True
                            type        = ChrisApp.path,
                            help        = "output file",
                            default     = "",
                            dest        = 'outputFileStem')
        self.add_argument("-d", "--outputDir",
                            optional    = True
                            type        = ChrisApp.path,
                            help        = "output image directory",
                            dest        = 'outputDir',
                            default     = '.')
        self.add_argument("-t", "--outputFileType",
                            optional    = True
                            type        = ChrisApp.path,
                            help        = "output image type",
                            dest        = 'outputFileType',
                            default     = '')
        self.add_argument("--printElapsedTime",
                            optional    = True
                            type        = bool,
                            help        = "print program run time",
                            dest        = 'printElapsedTime',
                            action      = 'store_true',
                            default     = False)
        self.add_argument("-x", "--man",
                            optional    = True
                            type        = bool,
                            help        = "man",
                            dest        = 'man',
                            action      = 'store_true',
                            default     = False)
        self.add_argument("-y", "--synopsis",
                            optional    = True
                            type        = bool,
                            help        = "short synopsis",
                            dest        = 'synopsis',
                            action      = 'store_true',
                            default     = False)
        

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        if options.man or options.synopsis:
            if options.man:
                str_help     = libtag.synopsis(False)
            else:
                str_help     = libtag.synopsis(True)
            print(str_help)
            sys.exit(1)

        str_outputFileStem, str_outputFileExtension     = os.path.splitext(options.outputFileStem)
        if len(str_outputFileExtension):
            str_outputFileExtension = str_outputFileExtension.split('.')[1]
        try:
            str_inputFileStem,  str_inputFileExtension      = os.path.splitext(options.inputFile)
        except:
            print(libtag.synopsis(False))
            sys.exit(1)

        if not len(options.outputFileType) and len(str_outputFileExtension):
            options.outputFileType = str_outputFileExtension

        if len(str_outputFileExtension):
            options.outputFileStem = str_outputFileStem

        b_htmlExt           =  str_outputFileExtension   == 'html'
        b_jsonExt           =  str_outputFileExtension   == 'json'

        if not b_htmlExt:
            C_dicomTag     = libtag.dicomTag(
                                    inputFile           = options.inputFile,
                                    outputDir           = options.outputDir,
                                    outputFileStem      = options.outputFileStem,
                                    outputFileType      = options.outputFileType,
                                    tagFile             = options.tagFile,
                                    tagList             = options.tagList,
                                    rawType             = options.rawType,
                                    imageFile           = options.imageFile
                                )

        if b_htmlExt:
            C_dicomTag   = libtag.dicomTag_html(
                                    inputFile           = options.inputFile,
                                    outputDir           = options.outputDir,
                                    outputFileStem      = options.outputFileStem,
                                    outputFileType      = options.outputFileType,
                                    tagFile             = options.tagFile,
                                    tagList             = options.tagList,
                                    imageFile           = options.imageFile
                                )


        # And now run it!
        libtag.misc.tic()
        C_dicomTag.run()
        if options.printElapsedTime: print("Elapsed time = %f seconds" % libtag.misc.toc())



# ENTRYPOINT
if __name__ == "__main__":
    app = Dicomtag()
    app.launch()
