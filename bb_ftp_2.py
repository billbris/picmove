#! python3

import ftplib
from ftplib import FTP
import socket
import os
from pathlib import Path
import bb_logging
import bb_device
import config

class Singleton(type):
	'''
		Metaclass to insure any class that derives from this as a metaclass will 
		follow the singleton class pattern and will only have one instance.
	'''
	_instances = {}
	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]
		
class bbFTP(metaclass=Singleton):
	def __init__(self, server, user,  password, port=21, root='/'):
		self.log = bb_logging.Logging(__name__)
		self.server = server
		self.user_name = user
		self.password = password
		self.ftp = None
		self.ftp_port = port
		self.root_dir = root
		self.mlsd = None
		
	def connect(self):
		'''
			Connect and log in to the remote ftp server
		'''			
		try:
			ip = socket.gethostbyname(self.server)
			self.log.info('FTP Server: {} - {}'.format(self.server, ip))
			self.ftp = FTP()
			self.ftp.connect(host=ip, port=self.ftp_port)
			self.ftp.login(self.user_name, self.password)
			self.mlsd = self.mlsd_support()
			return True	
		except ftplib.all_errors as e:
			errorcode_string = str(e).split(None, 1)
			self.log.error('FTP Error while connecting:{}'.format(errorcode_string))
			self.mlsd = None
			self.ftp = None
			return False
			
	def disconnect(self):
		'''
			Disconnect the current connection and reset all settings
		'''
		try:
			self.ftp.quit()
			self.ftp = None
		except ftplib.all_errors as e:
			errorcode_string = str(e).split(None, 1)
			self.log.error('FTP Error while connecting:{}'.format(errorcode_string))
			
	def mlsd_support(self):
		'''
			There are two methods of finding if a directory exists on the ftp server,
			the older method parses the result of the LIST command, the newer method
			uses the MLSD command which provides a better method.
			
			Not all ftp servers support MLSD, so this function searches the available
			commands (HELP command) to determine if MLSD is supported.
		'''
		if self.mlsd != None:
			return self.mlsd
		else:
			hlp = self.ftp.sendcmd('HELP')
			res_list = ' '.join((hlp.splitlines())[1:-1])
			return(res_list.find('MLSD') != -1)
			
	def get_current_directory(self):
		try:
			return(self.ftp.pwd())
		except ftplib.all_errors as e:
			errorcode_string = str(e).split(None, 1)
			self.log.error('FTP error while getting current directory: {}'.format(errorcode_string))	
			
	def home_dir(self):
		try:
			self.ftp.cwd(self.root_dir)
		except ftplib.all_errors as e:
			errorcode_string = str(e).split(None, 1)
			self.log.error('FTP error while changing current directory to \'home\':{}'.format(errorcode_string))
			
	def dir_exists_mlsd(self, fullpath):
		if fullpath == os.sep:
			return True		
		try:
			ret = False
			splitpath = os.path.split(os.path.normpath(fullpath))
			directory = splitpath[1]
			base = splitpath[0]
			if directory in [name for name, data in list(self.ftp.mlsd(path=base, facts=['type'])) \
				if data['type'] == 'dir']:
				ret = True
			return ret
		except ftplib.all_errors as e:
			errorcode_string = str(e).split(None, 1)
			self.log.error('FTP error while dir existence: {}'.format(errorcode_string))
			self.log.error('\tBase directory: {}'.format(base))
			self.log.error('\tSub directory:  {}'.format(directory))
			return False
					
	def dir_exists_list(self, fullpath):
		if fullpath == os.sep:
			return True
		splitpath = os.path.split(os.path.normpath(fullpath))
		directory = splitpath[1]
		base = splitpath[0]		
		files = []
		try:
			self.ftp.cwd(base)
			result = self.ftp.retrlines('LIST', files.append)
			for file in files:
				properties = file.split()
				name = properties[-1]
				dir = True if properties[0][0] == 'd' else False
				if name == directory:
					return dir
		except ftplib.all_errors as e:
			errorcode_string = str(e).split(None, 1)
			self.log.error('FTP error while dir exists LIST: {}'.format(errorcode_string))
			self.log.error('\tBase directory: {}'.format(base))
			self.log.error('\tSub directory:  {}'.format(directory))
			return False			
		return False
		
	def dir_exists(self, directory):
		if self.mlsd_support() == True:
			return self.dir_exists_mlsd(directory)
		else:
			return self.dir_exists_list(directory)
			
	def file_exists(self, filename, fullpath):
		try:
			current_cwd = self.ftp.pwd()  #Save starting directory
			self.ftp.cwd(fullpath)        #Move to file's directory
			dirfiles = self.ftp.nlst()    #Get list of files in directory
			ret = filename in dirfiles    #See if filename is dir listing
			self.ftp.cwd(current_cwd)     #Reset to initial directory
			return ret
		except ftplib.all_errors as e:
			errorcode_string = str(e).split(None, 1)
			if errorcode_string[0] != '550': #Directory not found
				self.log.error('FTP error while file exists: {}'.format(errorcode_string))
			return False
							
	def create_directory(self, fullpath):
		'''
			Create any/all directories in the fullpath directory string
		'''
		if fullpath != '':
			try:
				self.ftp.cwd(fullpath)
			except ftplib.all_errors as e:
				errorcode_string = str(e).split(None, 1)
				#self.log.error('FTP create dir: {}'.format(errorcode_string))
				if errorcode_string[0] == '550': #Directory not found
					self.create_directory(os.sep.join(fullpath.split(os.sep)[:-1]))
					self.ftp.mkd(fullpath)
					self.ftp.cwd(fullpath)
	
	def copy_file(self, dirpath, filename, buffer):
		'''
			Copy the file to the ftp server.  
			The parameter, fullpath, contains the path and filename.
		'''
		retry = 0
		while retry < 3:
			try:
				if config.actually_copy == True:
					self.create_directory(dirpath)
					fullpath = os.path.join(dirpath, filename)
					self.ftp.storbinary("STOR "+fullpath, buffer)
					return True
			except ftplib.all_errors as e:
				errorcode_string = str(e).split(None, 1)
				self.log.error('FTP error while copying file: {}'.format(errorcode_string))
				self.log.error('\tFile: {}'.format(fullpath))
				retry += 1
				continue
		self.log.error('Attempted copy {} times: {}'.format(retry, fullpath))
		return False
			
	def split_path(self, path):
		allparts = []
		while 1:
			parts = os.path.split(path)
			if parts[0] == path:		#sentinel for absolute paths
				allparts.insert(0, parts[0])
				break
			elif parts[1] == path:	#sentinel for relative paths
				allparts.insert(0, parts[1])
				break
			else:
				path = parts[0]
				allparts.insert(0,parts[1])
		return allparts			
		
									
if __name__ == '__main__':
	ftp = bbFTP('DORNOCH', 'bill', 'Sparta86', 2021, '/')
	mlsd = ftp.mlsd_support()
	print ('MLSD: {}'.format(mlsd))
	print('Current Directory: {}'.format(ftp.get_current_directory()))
	
	dir_list = ['/', '/ios_photos', '/ios_photos/2015', '/ios_photos/2015/2015-04', \
		'/ios_photos/2018', "/ios_photos/Bill's iPad/2016/2016-08", \
		"/ios_photos/Bill's iPad/2016/2016-13"]
		
	newdir = ['/testdir', '/testdir/level1/level2', '/testtest/foo/goo/hoo/boo/doo']
	
	filelist = [
		('Paul-2015-04-26-14-02-06.jpg', '/ios_photos/2015/2015-04'),
		('Paul-2016-07-22-09-44-39.jpg', '/ios_photos/2016/2016-07'),
		('foobar.jpg', '/ios_photos')
		]	
	
	for filename, dir in filelist:
		result = ftp.file_exists(filename, dir)
		print ('dir: {} file:{} exists: {}'.format(dir, filename, result))
		
	ftp.disconnect()
	
	
