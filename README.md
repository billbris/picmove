# picmove
iOS picture/video ftp file transfer

Firstly, this is not only my first somewhat/personally useful Python project, but my first Git repository as well.

Purpose:
  I needed a method to transfer all of my iPhone and iPad photos/video (re:media) to my "normal" working system.
  In the past, I have used Western Digital's picture transfer app to upload pictures to my external, network drive.  
  While this worked, the pictures had random names and followed no real timeline that I could determine.  It is also
  very slow, which may be the device more than the transfer.
  
  So, after discovering Pythonista I put it to work.  This set of scripts will allow you to select which (or all) of
  the iOS albums to upload and will rename them using the following pattern:
    <filename header>-YYYY-MM-DD-hh-mm-ss.{jpg|mov}
      where: 
        <filename header>:  A short string that appears at the front of every filename. Provided by the user before
                            upload begins.
       YYYY              :  Year in which picture/video was taken
       MM                :  Month in which picture/video was taken
       DD                :  Day in which picture/video was taken
       hh                :  Hour...
       mm                :  Minute...
       ss                :  Second...
       
       The separator, '-' can be changed in app_config.py
       
       Also, if a duplicate file is found on the remote server, a numeric suffix (nnn) is added to the end of the filename
       before the extension.  This starts at 001, etc.
       
There are two possible directory structures for the target server.  This is selected in app_config.py:
  1. Duplicate the album names as directories and copy the files in each iOS album into the directory of the same name.
  2. Use a date-based directory structure: YYYY/YYYY-MM
  
Regardless of the directory structure selected all directories are created under an application root directory that is 
defined in app_config.py (default: /ios_photos).

NOTE: It is assumed that these scripts are run using Pythonista and require python 3.5.1 (I have only tested this on 3.5.1
      and therefore that is the 'requirement').
