#! python3

log_filename = 'picmove.log'
logger_base  = 'picmove'

# ftp 
server      = 'DORNOCH'
user        = 'bill'
password    = 'Spartan86'
port        = 2021
ftp_root    = '/'

#file naming 
dir_structure  = "album"				#possible:	"date" yyyy/yyyy-mm, "album"
#dir_structure  = "date"					#possible:	"date" yyyy/yyyy-mm, "album"
actually_copy  = True						# For testing... 
screen_progess = True
default_header = "IOS"						# If no header added use this
header = ""											# This is set in the application (global)
delimiter = "-"
dir_delimiter = "/"
ftp_root = "ios_photos"
save_by_device = True						#use device name as directory name under root
exception_dir = "exceptions"
except_header = "EXCEPT"

