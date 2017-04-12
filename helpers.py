#!python3
import photos
import dialogs
import re
import os
import sys
import app_config

'''
	Collection of helper functions for the iOS operating system
'''
def logger_name(module_name):
	result = '{0: <20}'.format(app_config.logger_base+'.'+module_name)
	return result
	
def select_albums():
	'''
		Create a multi-select list of photo/video albums.  Those selected
		will have their contents copied.
	'''
	ALBUMS     = 'Albums'
	ALL_ALBUMS = 'All Albums'
	all_albums = photos.get_smart_albums()+photos.get_albums()
	titles = []
	titles += [x.title for x in all_albums]
	titles = sorted(list(set(titles)))	#convert list to set to remove duplicates, if any
	
	selected_titles = dialogs.list_dialog(ALBUMS, [ALL_ALBUMS] + titles, True)
	
	# Build return list.  If dialog was cancelled, return zero length list
	if selected_titles != None:
		if ALL_ALBUMS in selected_titles:
			selected_titles = titles
			
		ret_list = [x for x in all_albums if x.title in selected_titles]
	else:
		ret_list = []
		
	return(ret_list)
	
def create_filename_header():
	'''
		Each filename will begin with the string entered.  
	'''
	reg = re.compile('^[\w]*$')	#accepts any alphanumeric character and underscores
	
	while True:
		header = dialogs.text_dialog('New filename header')
		if header == None:							#user pressed cancel
			break;
		else:
			m = reg.match(header)
			if reg.match(header) != None:  #alphanumeric
				break;
	return(header)
	
	
