#!/usr/bin/python 

import os
import sys
import syslog
import errno
import shutil

BASE_REMOTE='/Users/ron/Dropbox/students'
BASE_LOCAL='/Users/ron/Dropbox/tinkeracademy/students'


QUIZ_FILE_NAME_LIST = [
	"Quiz1.odt",
	"Quiz2.odt",
	"Quiz3.odt",
]

HOMEWORK_FILE_NAME_LIST = [
	"Homework2",
	"Homework2.sb2",	
	"Homework2.lua",
	"Homework2.zip",
	"Homework3",
	"Homework3.sb2",
	"Homework3.lua",
	"Homework3.zip",
]


def build_relative_file_paths(root_path, file_paths):
	log_message('build_relative_file_paths enter')
	rel_file_paths = []
	if root_path[-1] != '/':
		root_path = root_path + '/'
	for file_path in file_paths:
		rel_file_path = file_path.replace(root_path, '')
		rel_file_paths.append(rel_file_path)
	log_message('build_relative_file_paths exit')
	return rel_file_paths

def make_sure_path_exists(path):
	try:
		dirname = os.path.dirname(path)
		os.makedirs(dirname)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise

def build_absolute_file_paths(root_path, rel_file_paths):
	log_message('build_absolute_file_paths enter')
	abs_file_paths = []
	if root_path[-1] != '/':
		root_path = root_path + '/'
	for rel_file_path in rel_file_paths:
		abs_file_path = os.path.join(root_path, rel_file_path)
		abs_file_paths.append(abs_file_path)
	log_message('build_absolute_file_paths exit')
	return abs_file_paths

def collect_file_paths(root_path, file_name):
	file_paths = []
	for root, dirs, files in os.walk(root_path):
		for file_ in files:
			if file_ == file_name:
				file_path = os.path.join(root, file_)
				file_paths.append(file_path)
		for dir_ in dirs:
			if dir_ == file_name:
				file_path = os.path.join(root, dir_)
				file_paths.append(file_path)
	return file_paths

def copy_homework_or_quiz_file(quiz_or_homework_file_name, target_file_paths):
	ret = 1
	source_file_paths = collect_file_paths(BASE_REMOTE, quiz_or_homework_file_name)
	relative_file_paths = build_relative_file_paths(BASE_REMOTE, source_file_paths)
	target_file_paths.extend(build_absolute_file_paths(BASE_LOCAL, relative_file_paths))
	ret2 = copy_files(source_file_paths, target_file_paths)
	if ret2 == -1:
		log_error('failed to copy quiz or homework ' + quiz_or_homework_file_name)
	ret &= ret2
	return ret

def copy_quizzes():	
	for quiz_file_name in QUIZ_FILE_NAME_LIST:
		target_file_paths = []
		copy_homework_or_quiz_file(quiz_file_name, target_file_paths)

def copy_homeworks():	
	for homework_file_name in HOMEWORK_FILE_NAME_LIST:
		target_file_paths = []
		copy_homework_or_quiz_file(homework_file_name, target_file_paths)

def copy_files(source_file_paths, target_file_paths):
	log_message('copy_files enter')
	log_message('copy_files source_file_paths=' + str(source_file_paths))
	log_message('copy_files target_file_paths=' + str(target_file_paths))
	ret = 0
	n = len(source_file_paths)
	m = len(target_file_paths)
	if n == m:
		for i in range(0, n):
			source_file_path = source_file_paths[i]
			target_file_path = target_file_paths[i]
			make_sure_path_exists(source_file_path)
			make_sure_path_exists(target_file_path)
			if os.path.isdir(source_file_path):
				if os.path.exists(target_file_path):
					shutil.rmtree(target_file_path)
				shutil.copytree(source_file_path, target_file_path)
			else:
				shutil.copyfile(source_file_path, target_file_path)
	else:
		ret = -1
	log_message('copy_files exit')
	return ret

def log_message(message):
	syslog.syslog("tinkeracademy message=" + str(message))

def log_error():
	type_,value_,traceback_ = sys.exc_info()
	syslog.syslog('tinkeracademy error=' + value_.message)

def main():
	copy_quizzes()
	copy_homeworks()

if __name__ == "__main__":
	main()