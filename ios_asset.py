#!python3

'''
 iOS photo/video asset functionality class
'''

import os
import photos
from objc_util import *
from pprint import pprint
import time
import app_config
import bb_logging
import bb_device
import bb_ftp_2
import helpers

class iosAsset (object):
	
	def __init__(self, asset):
		self.log = bb_logging.Logging(helpers.logger_name(__name__))
		self.asset = asset

	def filename_header(self):
		header = app_config.header
		if header == None or header == '':
			header = app_config.default_header
		return header
		
	def dirpath_header(self):
		target_root = os.path.join(os.sep, app_config.ftp_root)
		if app_config.save_by_device == True:
			target_root= os.path.join(target_root, bb_device.get_safe_device_name())
		return target_root
	
	def asset_type(self):
		types = {'image': '.jpg', 'video': '.mov'}	
		return types.get(self.asset.media_type, '.png')
		
	def create_filename(self):
		'''
			Create asset filename using its creation date
			Format: {header}-yyyy-MM-dd-hh-mm-ss
			
			Duplicate filenames are handled within the copy process.
		'''
		dt = self.asset.creation_date
		fmt_date = '{y:4d}{w}{m:0>2d}{w}{d:0>2}{w}'
		fmt_time = '{h:0>2}{w}{m:0>2}{w}{s:0>2}'
		name = self.filename_header()
		delimiter  = app_config.delimiter
		name += delimiter
		name += fmt_date.format(w=delimiter, y=dt.year, m=dt.month, d=dt.day)
		name += fmt_time.format(w=delimiter, h=dt.hour, m=dt.minute, s=dt.second)
		
		# Add file type extension
		name += self.asset_type()
		
		return name
		
	def create_date_dirpath(self):
		dt    = self.asset.creation_date
		year  = '{:4d}'.format(dt.year)
		month = '{:0>2d}'.format(dt.month)		
		tgt_path = os.path.join(self.dirpath_header(), '{}'.format(year))
		tgt_path = os.path.join(tgt_path, '{}{}{}'.format(year, app_config.delimiter, month))
		return tgt_path
				
	def copy_date_dir(self, ftp):
		filename = self.create_filename()
		dirpath = self.create_date_dirpath()
		ret = self.copy(filename, dirpath, ftp)
		return ret
		
	def create_album_dirpath(self, album_title):
		tgt_path = os.path.join(self.dirpath_header(), album_title)
		return tgt_path
				
	def copy_album_dir(self, album_title, ftp):
		filename = self.create_filename()
		dirpath = self.create_album_dirpath(album_title)
		ret = self.copy(filename, dirpath, ftp)
		return ret
				
	def resolve_duplicates(self, filename, dirpath, ftp):
		'''
			If a duplicate filename is found, return a new filename with a count
			concatenated to the original filname:
				Format: original-filename.xyz ==> original-filename-nnn.xyz
				
			If no duplicate is found, the original filename is returned
		'''
		fname, fext = os.path.splitext(filename)
		i = 0
		while True:
			if i == 0:
				new = '{}{}'.format(fname, fext)
			else:
				new = '{}{}{:03}{}'.format(fname, app_config.delimiter, i, fext)
				
			if ftp.file_exists(new, dirpath):
				i += 1
				self.log.info('===== Duplicate =====: {}'.format(os.path.join(dirpath, new)))
			else:
				return new

	def get_video_content(self):
		options = ObjCClass('PHVideoRequestOptions').new()
		options.version = 1		#PHVideoRequestOptionsVersionOriginal, use 0 for edited version
		image_manager = ObjCClass('PHImageManager').defaultManager()
		
		handled_asset = {'asset': None}		#One variable, but necessary due to nested function scoping
		buffer_pointer = None
		def handleAsset(_obj, asset, audioMix, info):
			a = ObjCInstance(asset)
			handled_asset['asset'] = a
		
		handler_block = ObjCBlock(handleAsset, argtypes=[c_void_p,]*4)
		
		image_manager.requestAVAssetForVideo(self.asset,
								options = options,
								resultHandler = handler_block)
		time.sleep(1)
										
		buffer_pointer = open(str(handled_asset['asset'].resolvedURL().resourceSpecifier()), 'rb')		
		return buffer_pointer
		
	def copy(self, filename, dirpath, ftp):
		'''
			Actually copy the file to the target ftp server
		'''
		fname = self.resolve_duplicates(filename, dirpath, ftp)
		if self.asset.media_type == 'image':	#pictures
			buffer = self.asset.get_image_data(original = False)
		else:	#videos
			buffer = self.get_video_content()
			
		if app_config.screen_progess == True:
			self.log.info('File: {}'.format(os.path.join(dirpath, fname)))
		return ftp.copy_file(dirpath, fname, buffer)			

