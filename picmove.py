#!python3

'''
	picmove
	
	This is the entry point for the picmove photo/video ftp copy utility
	
'''
import sys
from pprint import pprint
import console
import app_config
import bb_logging
import helpers
from bb_ftp_2 import bbFTP
import ios_albums

log = bb_logging.Logging(app_config.logger_base)

def main():
	# Application setup
	log.initiaize_logging(app_config.log_filename)
	log.info('========== PICMOVE ==========')
	
	# Select ios album folders to copy
	albums_list = helpers.select_albums()
	if len(albums_list) == 0:
		close_app()
		
	#Create header to start each filename
	app_config.header = helpers.create_filename_header()
	if app_config.header == None:
		close_app()
		
	# Establish ftp connection
	ftp = bbFTP(
		app_config.server,   \
		app_config.user,     \
		app_config.password, \
		app_config.port,     \
		app_config.ftp_root)

	# Do not let device go to sleep during copy
	console.set_idle_timer_disabled(True)
	
	if ftp.connect():
		albums = ios_albums.iosAlbums(albums_list)
		albums.copy(ftp)
	
	# Permit device to sleep again
	console.set_idle_timer_disabled(False)
	
	close_app()
	
#Application shutdown
def close_app():
	log.info('=============================')
	log.stop()
	sys.exit()
	
if __name__ == '__main__':
	main()
