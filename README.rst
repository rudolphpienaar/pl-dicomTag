################################
pl-dicomtag
################################


Abstract
********

This ChRIS `DS` app generates a file of DICOM tag results, and optionally an html page.

Run
***

Using ``docker run``
====================

Assign an "input" directory to ``/incoming`` and an output directory to ``/outgoing``

.. code-block:: bash

    docker run -v --rm $(pwd)/in:/incoming -v $(pwd)/out:/outgoing   \
            fnndsc/pl-dicomtag dicomtag.py            \
            /incoming /outgoing

For each subdir in `/incoming`, read the first DICOM image file and generate a tag list. Optionally also generate an HTML page containing a JPG image of the center of the series.

Make sure that the host ``$(pwd)/out`` directory is world writable!







