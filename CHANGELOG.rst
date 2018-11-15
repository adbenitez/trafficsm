===========================
Traffic Speed Map Changelog
===========================

Version 0.0.0a0
---------------

Released on November 15, 2018

tsm_downloader
^^^^^^^^^^^^^^
* **New:** ``downloader.sh`` Rewritten from scratch in Python3, and made available as a python package on PyPi.
* **New:** Added ``--imp``, ``--url``, ``--db``, ``--log``, ``--log-maxbytes``, ``--debug`` and ``--timeout`` arguments.
* **New:** XML data is saved to a database (sqlite3) instead of using XML files.
* **New:** Capture date is taken from the XML data instead of using the script run time, this avoids duplicate data if the script is run twice in the same XML file (ex. if the script is executed before the XML is updated on the server)
* **New:** Nominal values have been converted to integers to save disk space.
* **New:** Logs backups are compressed using gzip format.
* **New:** Created class DBManager.
* **New:** Created class RollingGzipFileHandler.

