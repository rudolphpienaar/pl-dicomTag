#!/usr/bin/env python
#
# NAME
#
#        dicomTag.py
#
# DESCRIPTION
#
#       'dicomTag' reads an input DICOM file
#       and returns information about the tag
#       (i.e. meta) data.
#
# HISTORY
#
# 25 November 2015
# o Initial design and coding.
#

# System imports
import      os
import      sys
import      getpass
import      argparse
import      time
import      glob
import      numpy               as      np
from        random              import  randint
import      re
import      json
import      pprint
import      csv

# System dependency imports
import      nibabel             as      nib
import      pydicom             as      dicom
import      pylab
import      matplotlib.cm       as      cm

# Project specific imports
import      pfmisc
import      error              

import      pudb

class dicomTag(object):
    """
        dicomTag accepts a DICOM file as input, as well as list of tags and
        then returns in either HTML or JSON format the relevant header
        information.
    """

    _dictErr = {
        'imageFileSpecFail'   : {
            'action'        : 'trying to parse image file specified, ',
            'error'         : 'wrong format found. Must be [<index>:]<filename>',
            'exitCode'      : 1},
        'inputDICOMFileFail'   : {
            'action'        : 'trying to read input DICOM file, ',
            'error'         : 'could not access/read file -- does it exist? Do you have permission?',
            'exitCode'      : 10},
        'inputTAGLISTFileFail': {
            'action'        : 'trying to read input <tagFileList>, ',
            'error'         : 'could not access/read file -- does it exist? Do you have permission?',
            'exitCode'      : 20
            }
    }

    def mkdir(self, newdir):
        """
        works the way a good mkdir should :)
            - already exists, silently complete
            - regular file in the way, raise an exception
            - parent directory(ies) does not exist, make them as well
        """
        if os.path.isdir(newdir):
            pass
        elif os.path.isfile(newdir):
            raise OSError("a file with the same name as the desired " \
                        "dir, '%s', already exists." % newdir)
        else:
            head, tail = os.path.split(newdir)
            if head and not os.path.isdir(head):
                self.mkdir(head)
            if tail:
                os.mkdir(newdir)

    def tic(self):
        """
            Port of the MatLAB function of same name
        """
        self.tic_start = time.time()

    def toc(self, *args, **kwargs):
        """
            Port of the MatLAB function of same name

            Behaviour is controllable to some extent by the keyword
            args:
        """
        global Gtic_start
        f_elapsedTime = time.time() - self.tic_start
        for key, value in kwargs.items():
            if key == 'sysprint':   return value % f_elapsedTime
            if key == 'default':    return "Elapsed time = %f seconds." % f_elapsedTime
        return f_elapsedTime

    def name(self, *args):
        '''
        get/set the descriptive name text of this object.
        '''
        if len(args):
            self.__name__ = args[0]
        else:
            return self.__name__

    def description(self, *args):
        '''
        Get / set internal object description.
        '''
        if len(args):
            self.str_desc = args[0]
        else:
            return self.str_desc

    @staticmethod
    def urlify(astr, astr_join = '_'):
        # Remove all non-word characters (everything except numbers and letters)
        astr = re.sub(r"[^\w\s]", '', astr)

        # Replace all runs of whitespace with an underscore
        astr = re.sub(r"\s+", astr_join, astr)

        return astr

    def __init__(self, **kwargs):

        def imageFileName_process(str_imageFile):
            pudb.set_trace()
            b_OK                = False
            l_indexAndFile      = str_imageFile.split(':')
            if len(l_indexAndFile) == 1:
                b_OK            = True
                self.str_outputImageFile    = l_indexAndFile[0]
            if len(l_indexAndFile) == 2:
                b_OK            = True
                self.str_outputImageFile    = l_indexAndFile[1]
                self.str_imageIndex         = l_indexAndFile[0]
            if not b_OK:
                self.dp.qprint("Invalid image specifier.", comms = 'error')
                error.fatal(self, 'imageFileSpecFail')
            if len(self.str_outputImageFile):
                self.b_convertToImg         = True

        def tagList_process(str_tagList):
            self.str_tagList            = str_tagList
            if len(self.str_tagList):
                self.b_tagList          = True
                self.l_tag              = self.str_tagList.split(',')

        def tagFile_process(str_tagFile):
            self.str_tagFile            = str_tagFile
            if len(self.str_tagFile):
                self.b_tagFile          = True
                with open(self.str_tagFile) as f:
                    self.l_tag          =  [x.strip('\n') for x in f.readlines()]

        def outputFile_process(str_outputFile):
            self.str_outputFileType     = str_outputFile
            self.l_outputFileType       = self.str_outputFileType.split(',')

        #
        # Object desc block
        #
        self.str_desc                  = ''
        self.__name__                  = "libtag"

        # Directory and filenames
        self.str_workingDir            = ''
        self.str_inputDir              = ''
        self.str_inputFile             = ''
        self.str_extension             = ''
        self.str_fileIndex             = ''
        self.l_inputDirTree            = []
        self.str_outputFileStem        = ''
        self.str_outputFileType        = ''
        self.l_outputFileType          = []
        self.str_outputDir             = ''
        self.d_outputTree              = {}

        self.str_stdout                = ''
        self.str_stderr                = ''
        self.exitCode                  = 0

        # The actual data volume and slice
        # are numpy ndarrays
        self.dcm                       = None
        self.str_outputFormat          = ''
        self.l_tagRaw                  = []     # tag list
        self.d_dcm                     = {}     # dict convert of raw dcm
        # Following are filtered by tagList
        self.d_dicom                   = {}     # values directly from dcm ojbect
        self.d_dicomSimple             = {}     # formatted dict convert

        # String representations of different outputFormats
        self.strRaw                    = ''
        self.str_json                  = ''
        self.str_dict                  = ''
        self.str_col                   = ''
        self.str_raw                   = ''

        # Image conversion
        self.b_convertToImg            = False
        self.str_outputImageFile       = ''
        self.str_imageIndex            = ''

        # A logger
        self.dp                        = pfmisc.debug(    
                                            verbosity   = 0,
                                            level       = -1,
                                            within      = self.__name__
                                            )
        self.log                       = pfmisc.Message()
        self.log.syslog(True)
        self.tic_start                 = 0.0
        self.pp                        = pprint.PrettyPrinter(indent=4)

        # Tags
        self.b_tagList                 = False
        self.b_tagFile                 = False
        self.str_tagList               = ''
        self.str_tagFile               = ''
        self.l_tag                     = []

        # Flags
        self.b_printToScreen            = False

        for key, value in kwargs.items():
            if key == "inputDir":           self.str_inputDir          = value
            if key == "inputFile":          self.str_inputFile         = value
            if key == "extension":          self.str_extension         = value
            if key == "outputDir":          self.str_outputDir         = value
            if key == "outputFileStem":     self.str_outputFileStem    = value
            if key == "outputFileType":     outputFile_process(value) 
            if key == 'printToScreen':      self.b_printToScreen       = value
            if key == 'imageFile':          imageFileName_process(value)
            if key == 'tagFile':            tagFile_process(value)
            if key == 'tagList':            tagList_process(value)

        if not len(self.str_inputDir): self.str_inputDir = '.'
        pudb.set_trace()

    def dirTree_create(self, **kwargs):
        """
        Return dir, files down a tree anchored in **kwargs
        """

        str_topDir  = "."
        l_dirs      = []
        l_files     = []
        b_status    = False
        str_path    = ''

        for k, v in kwargs.items():
            if k == 'root':  str_topDir  = v

        for root, dirs, files in os.walk(str_topDir):
            b_status = True
            str_path = root.split(os.sep)
            if dirs:
                l_dirs.append([root + '/' + x for x in dirs])
            if files:
                l_files.append([root + '/' + y for y in files])
        
        return {
            'status':   True,
            'l_dir':    l_dirs,
            'l_files':  l_files
        }

    def dirTree_prune(self, **kwargs):
        """
        Returns a dictionary of files to process. Dictionary key is
        the directory basename (relative to <inputDir>), value is
        the filename to process.
        """
        
        d_prune         = {}
        l_files         = []
        b_imageIndexed  = False

        for k, v in kwargs.items():
            if k == 'filelist':     l_files     = v

        for series in l_files:
            if len(self.str_extension):
                series = [x for x in series if self.str_extension in x]
            if self.b_convertToImg:
                if self.str_imageIndex == 'm':
                    seriesFile = series[int(len(series)/2)]
                    b_imageIndexed  = True
                if self.str_imageIndex == 'f':
                    seriesFile = series[:-1]
                    b_imageIndexed  = True
                if self.str_imageIndex == 'l':
                    seriesFile = series[0]
                    b_imageIndexed  = True
                if not b_imageIndexed:
                    seriesFile = series[int(self.str_imageIndex)]
            else:
                seriesFile  = series[0]
            str_path = os.path.dirname(seriesFile)
            str_file = os.path.basename(seriesFile)
            d_prune[str_path] = str_file 
        
        return {
            'status':   True,
            'd_prune':  d_prune
        }


    def tagsFindOnFile(self, **kwargs):
        """
        Return the tag information for given file.
        """

        str_file        = ''
        str_result      = ''
        b_formatted     = False
        str_outputFile  = ''

        for k, v in kwargs.items():
            if k == 'file':     str_file    = v

        str_localFile      = os.path.basename(str_file)
        if len(str_file):
            self.dcm       = dicom.read_file(str_file)
            self.d_dcm     = dict(self.dcm)
            self.strRaw    = str(self.dcm)
            self.l_tagRaw  = self.dcm.dir()
            d_dicomJSON    = {}

            if self.b_tagFile or self.b_tagList:
                l_tagsToUse     = self.l_tag
            else:
                l_tagsToUse     = self.l_tagRaw

            if 'PixelData' in l_tagsToUse:
                l_tagsToUse.remove('PixelData')
            for key in l_tagsToUse:
                self.d_dicom[key]       = self.dcm.data_element(key)
                try:
                    self.d_dicomSimple[key] = getattr(self.dcm, key)
                except:
                    self.d_dicomSimple[key] = "no attribute"
                d_dicomJSON[key]        = str(self.d_dicomSimple[key])

            for str_outputFormat in self.l_outputFileType:
                # pudb.set_trace()
                if str_outputFormat == 'json':
                    self.str_json           = json.dumps(
                                                d_dicomJSON, 
                                                indent              = 4, 
                                                sort_keys           = True
                                                )
                    b_formatted     = True
                if str_outputFormat == 'dict':
                    self.str_dict           = self.pp.pformat(self.d_dicomSimple)
                    b_formatted     = True
                if str_outputFormat == 'col':
                    for tag in l_tagsToUse:
                        self.str_col        += '%30s\t%s\n' % (tag , self.d_dicomSimple[tag])
                    b_formatted     = True
                if str_outputFormat == 'raw' or str_outputFormat == 'html':
                    for tag in l_tagsToUse:
                        self.str_raw        += '%s\n' % (self.d_dicom[tag])

            if '%' in self.str_outputFileStem:
                pudb.set_trace()
                l_tags          = self.str_outputFileStem.split('%')[1:]
                l_tagsToSub     = [i for i in self.l_tagRaw if any(i in b for b in l_tags)]
                for tag in l_tagsToSub:
                    self.str_outputFileStem = self.str_outputFileStem.replace('%' + tag, self.d_dicomSimple[tag])
                str_outputFile  = self.str_outputFileStem
            else:
                str_outputFile  = self.str_outputFileStem

        return {
            'formatted':        b_formatted,
            'd_dicom':          self.d_dicom,
            'd_dicomSimple':    self.d_dicomSimple,
            'd_dicomJSON':      d_dicomJSON,
            'dcm':              self.dcm,
            'str_outputFile':   str_outputFile,
            'str_inputFile':    str_localFile,
            'dstr_result':      {
                'json':         self.str_json,
                'dict':         self.str_dict,
                'col':          self.str_col,
                'raw':          self.str_raw
            }
        }

    def img_create(self, dcm):
        '''
        Create the output jpg of the file.
        :return:
        '''
        try:
            pylab.imshow(dcm.pixel_array, cmap=pylab.cm.bone)
            pylab.savefig(self.str_outputImageFile)
        except:
            pass

    def outputs_generate(self, **kwargs):
        """
        Generate output reports
        """

        def html_make(str_inputFile, str_rawContent):
            str_img     = ""
            if self.b_convertToImg:
                str_img = "<img src=%s>" % self.str_outputImageFile
            htmlPage = '''
                <!DOCTYPE html>
                <html>
                <head>
                <title>DCM tags: %s</title>
                </head>
                <body>
                %s
                    <pre>
                %s
                    </pre>
                </body>
                </html> ''' % (str_inputFile, str_img, str_rawContent)
            return htmlPage

        self.mkdir(self.str_outputDir)
        for path in self.d_outputTree:
            d_outputInfo    = self.d_outputTree[path]
            os.chdir(self.str_outputDir)
            self.mkdir(path)
            os.chdir(path)
            if self.b_convertToImg:
                self.img_create(d_outputInfo['dcm'])
            for str_outputFormat in self.l_outputFileType:
                if str_outputFormat == 'json': 
                    with open(d_outputInfo['str_outputFile']+'.json', 'w') as f:
                        f.write(d_outputInfo['dstr_result']['json'])
                if str_outputFormat == 'dict': 
                    with open(d_outputInfo['str_outputFile']+'-dict.txt', 'w') as f:
                        f.write(d_outputInfo['dstr_result']['dict'])
                if str_outputFormat == 'col': 
                    with open(d_outputInfo['str_outputFile']+'-col.txt', 'w') as f:
                        f.write(d_outputInfo['dstr_result']['col'])
                if str_outputFormat == 'raw': 
                    with open(d_outputInfo['str_outputFile']+'-raw.txt', 'w') as f:
                        f.write(d_outputInfo['dstr_result']['raw'])
                if str_outputFormat == 'html': 
                    with open(d_outputInfo['str_outputFile']+'.html', 'w') as f:
                        f.write(
                            html_make(  d_outputInfo['str_inputFile'],
                                        d_outputInfo['dstr_result']['raw'])
                        )
                if str_outputFormat == 'csv':
                    with open(d_outputInfo['str_outputFile']+'.csv', 'w') as f:
                        w = csv.DictWriter(f, d_outputInfo['d_dicomJSON'].keys())
                        w.writeheader()
                        w.writerow(d_outputInfo['d_dicomJSON'])
                
    def run(self):
        '''
        The main 'engine' of the class.

        Here we walk down the <inputDir> and in each directory,
        we parse a DICOM input for the tag info. Tags are kept 
        in a dictionary structure that mimics the <inputDir>
        hierarchy.
        
        '''

        os.chdir(self.str_inputDir)
        str_cwd         = os.getcwd()
        d_tree          = self.dirTree_create(root = ".")
        d_filtered      = self.dirTree_prune(filelist = d_tree['l_files'])

        for k, v in d_filtered['d_prune'].items():
            self.d_outputTree[k]    = self.tagsFindOnFile(file = os.path.join(k, v))

        pudb.set_trace()
        self.outputs_generate()
        os.chdir(str_cwd)

    def echo(self, *args):
        self.b_echoCmd         = True
        if len(args):
            self.b_echoCmd     = args[0]

    def echoStdOut(self, *args):
        self.b_echoStdOut      = True
        if len(args):
            self.b_echoStdOut  = args[0]

    def stdout(self):
        return self.str_stdout

    def stderr(self):
        return self.str_stderr

    def echoStdErr(self, *args):
        self.b_echoStdErr      = True
        if len(args):
            self.b_echoStdErr  = args[0]

    def dontRun(self, *args):
        self.b_runCmd          = False
        if len(args):
            self.b_runCmd      = args[0]

    def workingDir(self, *args):
        if len(args):
            self.str_workingDir = args[0]
        else:
            return self.str_workingDir

def synopsis(ab_shortOnly = False):
    scriptName = os.path.basename(sys.argv[0])
    shortSynopsis =  '''
    NAME

	    %s - print DICOM file header information down a file system tree.

    SYNOPSIS

            %s                                       \\
                     -I|--inputDir <inputDir>               \\
                        [-i|--inputFile <inputFile>]        \\
                        [-e|--extension <DICOMextension>]   \\
                        [-F|--tagFile <tagFile>] |          \\
                        [-T|--tagList <tagList>] |          \\
                    [-m|--image <imageFile>]                \\
                    [-d|--outputDir <outputDir>]            \\
                    [-o|--output <outputFileStem>]          \\
                    [-t|--outputFileType <outputFileType>]  \\
                    [-p|--printToScreen]                    \\
                    [-x|--man]				                \\
		            [-y|--synopsis]

    BRIEF EXAMPLE

	    %s -l tagList.txt -i slice.dcm

    ''' % (scriptName, scriptName, scriptName)

    description =  '''
    DESCRIPTION

        `%s` extracts the header information of DICOM files and echoes to
        stdout as well as to an output report-type file -- this can be a raw
        output, a json-type output, or html-type output.

        The script accepts an <inputDir>, and then from this point an os.walk
        is performed to extract all the subdirs. Each subdir is examined for
        DICOM files (in the simplest sense by a file extension mapping) and 
        either the head, tail, middle (or other indexed) file is examined for
        its tag information.

        Optionally, the tag list can be constrained either by passing a
        <tagFile> containing a line-by-line list of tags to query, or
        by passing a comma separated list of tags directly.

        Finally, an image conversion can also be performed (and embedded
        within the output html file, if an html conversion is specified).

    ARGS

        -I|--inputDir <inputDir>
        Input DICOM directory to examine. By default, the first file in this
        directory is examined for its tag information. There is an implicit
        assumption that each <inputDir> contains a single DICOM series.

        -i|--inputFile <inputFile>
        An optional <inputFile> specified relative to the <inputDir>. If 
        specified, then do not perform a directory walk, but convert only 
        this file.

        -e|--extension <DICOMextension>
        An optional extension to filter the DICOM files of interest from the 
        <inputDir>.

        [-O|--outputDir <outputDir>]
        The directory to contain all output files.

        NOTE: If neither -F nor -T are specified, a '-r raw' is
        assumed.

        -F|--tagFile <tagFile>
        Read the tags, one-per-line in <tagFile>, and print the
        corresponding tag information in the DICOM <inputFile>.

        -T|--tagList <tagList>
        Read the list of comma-separated tags in <tagList>, and print the
        corresponding tag information parsed from the DICOM <inputFile>.

        -m|--image <[<index>:]imageFile>
        If specified, also convert the <inputFile> to <imageFile>. If the
        name is preceded by an index and colon, then convert this indexed 
        file in the particular <inputDir>.

        -o|--outputFileStem <outputFileStem>
        The output file stem to store data. This should *not* have a file
        extension, or rather, any "." in the name are considered part of 
        the stem and are *not* considered extensions.

        [-t|--outputFileType <outputFileType>]
        A comma specified list of output types. These can be:

            o <type>    <ext>       <desc>
            o raw       -raw.txt    the raw internal dcm structure to string
            o json      json        a json representation
            o html      html        an html representation with optional image
            o dict      -dict.txt   a python dictionary
            o col       -col.txt    a two-column text representation (tab sep)
            o csv       csv         a csv representation

        [-p|--printToScreen]
        If specified, will print tags to screen.

        [-x|--man]
        Show full help.

        [-y|--synopsis]
        Show brief help.

    EXAMPLES

        o See https://github.com/FNNDSC/scripts/blob/master/dicomTag.py for more help and source.

    ''' % (scriptName)
    if ab_shortOnly:
        return shortSynopsis
    else:
        return shortSynopsis + description

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="'dicomTag.py' prints the DICOM header information of a given input DICOM file.")
    parser.add_argument("-I", "--inputDir",
                        help    = "input dir",
                        dest    = 'inputDir')
    parser.add_argument("-i", "--inputFile",
                        help    = "input file",
                        dest    = 'inputFile',
                        default = '')
    parser.add_argument("-e", "--extension",
                        help    = "DICOM file extension",
                        dest    = 'extension',
                        default = '')
    parser.add_argument("-F", "--tagFile",
                        help    = "file containing tags to parse",
                        dest    = 'tagFile',
                        default = '')
    parser.add_argument("-T", "--tagList",
                        help    = "comma-separated tag list",
                        dest    = 'tagList',
                        default = '')
    parser.add_argument("-r",
                        help    = "display raw tags",
                        dest    = 'rawType',
                        default = 'raw')
    parser.add_argument("-m", "--imageFile",
                        help    = "image file to convert DICOM input",
                        dest    = 'imageFile',
                        default = '')
    parser.add_argument("-o", "--outputFileStem",
                        help    = "output file",
                        default = "",
                        dest    = 'outputFileStem')
    parser.add_argument("-O", "--outputDir",
                        help    = "output image directory",
                        dest    = 'outputDir',
                        default = '.')
    parser.add_argument("-t", "--outputFileType",
                        help    = "list of output report types",
                        dest    = 'outputFileType',
                        default = '')
    parser.add_argument("--printElapsedTime",
                        help    = "print program run time",
                        dest    = 'printElapsedTime',
                        action  = 'store_true',
                        default = False)
    parser.add_argument("-p", "--printToScreen",
                        help    = "print output to screen",
                        dest    = 'printToScreen',
                        action  = 'store_true',
                        default = False)
    parser.add_argument("-x", "--man",
                        help    = "man",
                        dest    = 'man',
                        action  = 'store_true',
                        default = False)
    parser.add_argument("-y", "--synopsis",
                        help    = "short synopsis",
                        dest    = 'synopsis',
                        action  = 'store_true',
                        default = False)
    args = parser.parse_args()

    if args.man or args.synopsis:
        if args.man:
            str_help     = synopsis(False)
        else:
            str_help     = synopsis(True)
        print(str_help)
        sys.exit(1)

    C_dicomTag     = dicomTag(
                            inputDir            = args.inputDir,
                            inputFile           = args.inputFile,
                            extension           = args.extension,
                            outputDir           = args.outputDir,
                            outputFileStem      = args.outputFileStem,
                            outputFileType      = args.outputFileType,
                            tagFile             = args.tagFile,
                            tagList             = args.tagList,
                            printToScreen       = args.printToScreen,
                            imageFile           = args.imageFile
                        )

    # And now run it!
    C_dicomTag.tic()
    C_dicomTag.run()
    if args.printElapsedTime: print("Elapsed time = %f seconds" % C_dicomTag.toc())
    sys.exit(0)
