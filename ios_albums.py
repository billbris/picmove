#!python3

'''
 iOS photo/video album functionality class
'''

import photos
import dialogs
from pprint import pprint
import app_config
import bb_logging
import helpers
import ios_asset
import bb_ftp_2

class iosAlbums (object):
	
	def __init__(self, albums):
		self.albums = albums
		self.log = bb_logging.Logging(helpers.logger_name(__name__))
		
	def copy(self, ftp):
		'''
			Entry point for copying album contents.  
			Main purpose is to determine the directory format type needed.
		'''
		self.log.info('In albums.copy')
		if app_config.dir_structure == 'album':
			self.log.info('copy album structure')
			self.copy_album_dir(ftp)
		elif app_config.dir_structure == 'date':
			self.log.info('copy date structure')
			self.copy_date_dir(ftp)
		else:
			self.log.error('Invalid album dir_structure in app_config {}' \
				.format(app_config.dir_structure))
	
	def unique_asset_ids(self):	
		unique = {asset.local_id for album in self.albums for asset in album.assets}
		return list(unique)
			
	def display_results(self, success_count, error_count):
		self.log.info('RESULTS:')
		self.log.info('Successful copies: {}'.format(success_count))
		self.log.info('Unsuccessful:      {}'.format(error_count))
		
	def copy_date_dir(self, ftp):
		'''
			Target directory structure: 
				/app_config.ftp_root/(device_name)/YYYY/YYYY-MM/*.*
				
			NOTE: All the assets in all of the albums are combined so that
						the duplicates can be removed.
		'''
		copy_count = 0
		error_count = 0
		asset_id_list = self.unique_asset_ids()
		for asset_id in asset_id_list:
			asset = ios_asset.iosAsset(photos.get_asset_with_local_id(asset_id))
			ret = asset.copy_date_dir(ftp)
			if ret == True:
				copy_count += 1
			else:
				error_count += 1
			self.display_results(copy_count, error_count)
		
	def copy_album_dir(self, ftp):
		'''
			Target directory structure: 
				/app_config.ftp_root/(device_name)/(album_name)/*.*
				
			NOTE: No effort is made to remove duplicates that exist
						across albums
		'''
		copy_count = 0
		error_count = 0
		for album in self.albums:
			for asset in album.assets:
				a = ios_asset.iosAsset(asset)
				ret = a.copy_album_dir(album.title, ftp)
				if ret == True:
					copy_count += 1
				else:
					error_count += 1
				self.display_results(copy_count, error_count)				
		
	def list(self):
		pprint(self.albums)
		
		
if __name__ == '__main__':
	album_list = helpers.select_albums()
	albums = iosAlbums(album_list)
	albums.copy()

