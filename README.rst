*****************
Traffic Speed Map
*****************

A project to test my programming skills.
TSM is a web site for visualizing XML traffic data in useful ways, using maps and graphs to facilitate the analisis and knowledge extraction of the raw data.

.. note::

   This project is for educational purposes only.


How it works
============
The project have two main components:
* A downloader script that grabs the XML data and saves it to an sqlite3 database. This script is executed in a regular basis with the help of a cron service or similar.
* A Flask server that uses the database created by the downloader script to visualize the data in a web site.


Downloader script
=================
You need Python 3 and pip installed on your machine before installing the downloader scripts. To install the script execute the following command:

.. code-block:: bash

   $ python3 -m pip install tsm_downloader

After installation, the command ``tsm_downloader`` will be available. The script accepts arguments like the data URL, path to the database file, path to the log file, etc., to see the full list of arguments and how to use them issue the command:

.. code-block:: bash

   $ tsm_downloader --help

Updating the database
---------------------
When the script is executed it grabs the XML data from the given URL and exports it to the given sqlite3 database file, to update the database at regular intervals, execute the script using a service like cron, for example, to execute the script every two minutes, using the default data URL, creating/updating the database ``/var/tmp/traffic.db`` and saving logs to ``/var/log/tsm_downloader.log``, you could add the following line to your ``crontab`` file:

.. code-block::

   1-59/2 * * * * tsm_downloader --db /var/tmp/traffic.db --log /var/log/tsm_downloader.log >/dev/null 2>&1

Database specifications
-----------------------
The downloaded XML data is converted to entries in the ``link`` and ``capture`` tables on the database. Nominal values are converted to integer to save disk space. Storing the data in this database can reduce the size of the data to less than 1/4 of the original XML data's size. The database contains the following tables:

Table: code
^^^^^^^^^^^
This table contains the code associated to the nominal values in the database and the original value they have in the XML data. The primary key is the ``id`` column. The following table shows the description of every column in the table:

===========   ================================   =======   =======
Column Name   Description                        Type      Example
===========   ================================   =======   =======
id            A code number                      INTEGER   0
value         The original value represented     TEXT      HK

.. note::

   Client applications must use this conversion table to recover the original value of the data when reading the database.

Table: link
^^^^^^^^^^^
This table contains the properties of the road links. The primary key of the table is the tuple created by the start and end columns. The following table shows the description of every column in the table:

===========   ================================   =======   =======
Column Name   Description                        Type      Example
===========   ================================   =======   =======
start         The starting point of the link     INTEGER   3006
end           The ending point of the link       INTEGER   30069
region        Region of the traffic speed data   INTEGER   1
rt            Type of the road                   INTEGER   4
===========   ================================   =======   =======

Table: capture
^^^^^^^^^^^^^^
This table contains captures, realized at a date defined in the ``date`` column, of data related to the traffic speed on road links, defined in table ``link``. The primary key is the union of the link_start, link_end and date columns. The following table shows the description of every column in the table:

===========   ==============================   ===========   ===================
Column Name   Description                      Type          Example
===========   ==============================   ===========   ===================
link_start    The starting point of the link   foreign key   3006
link_end      The ending point of the link     foreign key   30069
rsl           Road Saturation Level            INTEGER       6
ts            Traffic speed                    REAL          44
date          Time of the speed measured       TEXT          2015-12-31T23:52:35
===========   ==============================   ===========   ===================

Log file
--------
When the log file is about the size specified with the option ``--log-maxbytes`` (10MB by default), it is moved to a compressed backup file (with the log name as preffix, plus the number of backup and the extension ".gz") and a new log file is created.


Flask server
============
**TODO**


License
=======

This project is **free software**, licensed under the GPL3+ License - see the `LICENSE <https://github.com/adbenitez/tsm/blob/master/LICENSE>`_ file for more details.
