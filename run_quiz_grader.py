#!/usr/bin/python

###############################################################################
#
#   Quiz Grader Script
#
#   Copyright Tinker Academy 2014
###############################################################################

import os
import re
import sys
import syslog
import errno
import shutil
import xml.dom.minidom

from zipfile import ZipFile
from reportlab.pdfgen import canvas

BASE_CLASSES='/Users/ron/Dropbox/tinkeracademy/classes'
BASE_LOCAL='/Users/ron/Dropbox/tinkeracademy/students'
BASE_TEMP = '/Users/ron/scratch/quiz_grader'
EXTRACTED_DIR_NAME = 'extracted'

COURSES_LIST = [
	"TA-JAV-1",
	"TA-SCR-1",
]

QUIZ_FILE_NAME_LIST = [
	"Quiz2.odt",
]

def get_relative_file_paths_in_dir(dir_path):
	log_message('get_relative_file_paths_in_dir enter')
	relative_file_paths = []
	for root, dirs, files in os.walk(dir_path):
		rel_root = root.replace(dir_path, '')
		if rel_root and len(rel_root) > 0:
			if rel_root[0] == '/':
				rel_root = rel_root[1:]
			if rel_root:
				for file_ in files:
					relative_file_path = os.path.join(rel_root, file_)
					# log_message('get_relative_file_paths_in_dir adding relative_file_path=' + str(relative_file_path))
					relative_file_paths.append(relative_file_path)
	log_message('get_relative_file_paths_in_dir exit')
	return relative_file_paths

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

def copy_solutions_to_grader_dir():
	relative_paths = get_relative_file_paths_in_dir(BASE_CLASSES)
	for relative_path in relative_paths:
		for course in COURSES_LIST:
			if course in relative_path:		
				if "/solution/" in relative_path:
					base_file_name = os.path.basename(relative_path)
					if base_file_name in QUIZ_FILE_NAME_LIST:
						source_file_path = os.path.join(BASE_CLASSES, relative_path)
						target_file_path = os.path.join(BASE_TEMP, relative_path)
						target_dir_path = os.path.dirname(target_file_path)
						if not os.path.exists(target_dir_path):
							os.makedirs(target_dir_path)
						shutil.copy(source_file_path, target_file_path)	

def copy_quizzes_to_grader_dir():
	relative_paths = get_relative_file_paths_in_dir(BASE_LOCAL)
	for relative_path in relative_paths:
		for course in COURSES_LIST:
			if course in relative_path:		
				base_file_name = os.path.basename(relative_path)
				if base_file_name in QUIZ_FILE_NAME_LIST:
					source_file_path = os.path.join(BASE_LOCAL, relative_path)
					target_file_path = os.path.join(BASE_TEMP, relative_path)
					target_dir_path = os.path.dirname(target_file_path)
					if not os.path.exists(target_dir_path):
						os.makedirs(target_dir_path)
					shutil.copy(source_file_path, target_file_path)		

def unzip_quiz_file_contents():
	relative_paths = get_relative_file_paths_in_dir(BASE_TEMP)
	for relative_path in relative_paths:
		base_file_name = os.path.basename(relative_path)
		if base_file_name in QUIZ_FILE_NAME_LIST:
			absolute_path = os.path.join(BASE_TEMP, relative_path)
			if os.path.getsize(absolute_path) > 0:
				absolute_dir = os.path.dirname(absolute_path)
				absolute_extracted_dir = os.path.join(absolute_dir, EXTRACTED_DIR_NAME)
				if not os.path.exists(absolute_extracted_dir):
					os.makedirs(absolute_extracted_dir)
				try:
					zip_file = ZipFile(absolute_path)
					zip_file.extractall(absolute_extracted_dir)
				except:
					print 'error extracting ', absolute_path
					log_error()
			else:
				print 'error! unexpected content  (0 file size) in odt ', absolute_path
				log_message('error! unexpected content  (0 file size) in odt ' + str(absolute_path))							

def grade_quizzes():
	# copy_solutions_to_grader_dir()
	# copy_quizzes_to_grader_dir()
	# unzip_quiz_file_contents()
	prepare_reports()

def prepare_reports():
	relative_paths = get_relative_file_paths_in_dir(BASE_TEMP)
	for relative_path in relative_paths:
		prepare_quiz_report(relative_path)
		prepare_homework_report(relative_path)

def prepare_quiz_report(relative_path):
	if '/quiz/' in relative_path:
		for quiz in QUIZ_FILE_NAME_LIST:
			if relative_path.endswith(quiz):
				for course in COURSES_LIST:
					if course in relative_path:
						index = relative_path.index(course)
						quiz_path = relative_path[index:]
						solution_relative_path = quiz_path.replace('quiz', 'solution')
						solution_relative_path = os.path.join('courses', solution_relative_path)
						quiz_path = os.path.join(BASE_TEMP, relative_path)
						solution_path = os.path.join(BASE_TEMP, solution_relative_path)
						quiz_contents_path = os.path.join(os.path.dirname(quiz_path), 'extracted', 'content.xml')
						if os.path.exists(quiz_contents_path):
							print 'processing ', relative_path
							solution_contents_path = os.path.join(os.path.dirname(solution_path), 'extracted', 'content.xml')
							quiz_contents = xml.dom.minidom.parseString(read_content(quiz_contents_path))
							solution_contents = xml.dom.minidom.parseString(read_content(solution_contents_path))
							quiz_rows = get_table_rows(quiz_contents)
							solution_rows = get_table_rows(solution_contents)
							quiz_rows = get_answer_table_rows(quiz_rows)
							solution_rows = get_answer_table_rows(solution_rows)
							if len(quiz_rows) == len(solution_rows):
								for i in range(len(solution_rows)):
									quiz_row = quiz_rows[i]
									solution_row = solution_rows[i]
									if get_text(quiz_row) == 'Answer':
										if get_text(solution_row) == 'Answer':
											quiz_answer_row = get_sibling_table_row(quiz_row)
											solution_answer_row = get_sibling_table_row(solution_row)
											quiz_answer = get_text(quiz_answer_row)
											solution_answer = get_text(solution_answer_row)
											quiz_answer = quiz_answer.encode('utf-8')
											solution_answer = solution_answer.encode('utf-8')
											print 'student answer ', quiz_answer
											print 'solution answer ', solution_answer
											is_correct = grade_answer(quiz_answer, solution_answer)
											if is_correct:
												print 'the student got the RIGHT answer'
											else:
												print 'the student got the WRONG answer'
							else:
								print 'error! unexpected content (mismatch in row count) in odt content ', quiz_contents_path
								log_message('error! unexpected content (mismatch in row count) in odt content ' + str(quiz_contents_path))
							quiz_contents.unlink()
							solution_contents.unlink()

def prepare_homework_report(relative_path):
	pass

def grade_answer(quiz_answer, solution_answer):
	lc_solution_answer = solution_answer.lower()
	lc_solution_answer = lc_solution_answer.strip()
	lc_quiz_answer = quiz_answer.lower()
	if lc_quiz_answer:
		if is_numeric_answer(lc_solution_answer):
			if int(lc_solution_answer) == int(lc_quiz_answer):
				return True
		elif is_yes_no_answer(lc_solution_answer):
			quiz_answer_yes_no = extract_yes_no(lc_quiz_answer, lc_solution_answer)
			if quiz_answer and quiz_answer_yes_no == lc_solution_answer:
				return True
		elif is_x_y_answer(lc_solution_answer):
			quiz_answer_digits = extract_x_y_numbers(lc_quiz_answer)
			solution_answer_digits = extract_x_y_numbers(lc_solution_answer)
			if quiz_answer_digits == solution_answer_digits:
				return True
		elif is_comma_delim_answer(lc_solution_answer):
			solution_answer_comma = extract_comma_delim_answer(lc_solution_answer)
			quiz_answer_comma = extract_comma_delim_answer(lc_quiz_answer)
			if quiz_answer_comma == solution_answer_comma:
				return True
		else:
			if lc_solution_answer == lc_quiz_answer:
				return True
	return False

def represents_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def extract_yes_no(ans, sol):
	if sol == 'no' and 'no' in ans:
		return 'no'
	if sol == 'yes' and 'yes' in ans:
		return 'yes'
	return None

def extract_x_y_numbers(ans):
	numbers = []
	parts = re.split('x|y|,|\(|\)|=|\:|\+|-|\.| |\t|\n', ans)
	parts = [int(s) for s in parts if represents_int(s)]
	numbers.append(parts)
	numbers = sorted(numbers)
	return numbers

def is_comma_delim_answer(ans):
	if ',' in ans:
		return True
	return False

def extract_comma_delim_answer(ans):
	arr = []
	if ans:
		arr.extend([s.strip() for s in ans.split(',')])
	arr = sorted(arr)
	return arr

def is_x_y_answer(ans):
	return 'x:' in ans and 'y:' in ans	

def is_yes_no_answer(ans):
	return ans == 'no' or ans == 'yes'

def is_numeric_answer(ans):
	return represents_int(ans)

def get_answer_table_rows(rows):
	answer_rows = []
	for row in rows:
		if get_text(row) == 'Answer':
			answer_rows.append(row)
	return answer_rows

def get_sibling_table_row(row):
	candidate_row = row.nextSibling
	while candidate_row and candidate_row.nodeName != 'table:table-row':
		candidate_row = candidate_row.nextSibling
	return candidate_row

def get_table_rows(contents):
	rows = contents.getElementsByTagName('table:table-row')
	return rows

def get_text(node):
	rc = []
	build_text(node, rc)
	return ''.join(rc)

def build_text(node, rc):
	if node.nodeType == node.TEXT_NODE:
		rc.append(node.data)
	else:
		for childNode in node.childNodes:
			build_text(childNode, rc)

def read_content(file_path):
	# log_message('read_content enter')
	# log_message('read_content file_path='+str(file_path))
	content = None
	if os.path.isfile(file_path):
		file_handle = None
		try:
			file_handle = open(file_path, 'r')
			content = file_handle.read()
		except:
			log_error()
		finally:
			if file_handle:
				try:
					file_handle.close()
				except:
					log_error()
	# log_message('read_content exit')
	return content

def log_message(message):
	syslog.syslog("tinkeracademy message=" + str(message))

def log_error():
	type_,value_,traceback_ = sys.exc_info()
	syslog.syslog('tinkeracademy error=' + value_.message)

def main():
	grade_quizzes()

if __name__ == "__main__":
	main()