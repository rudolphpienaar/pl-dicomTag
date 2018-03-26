################################
pl-dicomTag
################################


Abstract
********

This app generates a file of DICOM tag results, and optionally an html page.

Run
***

Using ``docker run``
====================

Assign an "input" directory to ``/incoming`` and an output directory to ``/outgoing``

.. code-block:: bash

    docker run -v --rm $(pwd)/in:/incoming -v $(pwd)/out:/outgoing   \
            fnndsc/pl-dicomTag dicomtag.py            \
            /incoming /outgoing

This will ...

Make sure that the host ``$(pwd)/out`` directory is world writable!







