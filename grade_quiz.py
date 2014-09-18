

BASE_REMOTE='/Users/ron/Dropbox/students'
BASE_LOCAL='/Users/ron/Dropbox/tinkeracademy/students'


QUIZ_LIST = [
	"Quiz1.odt"
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
					log_message('get_relative_file_paths_in_dir adding relative_file_path=' + str(relative_file_path))
					relative_file_paths.append(relative_file_path)
	log_message('get_relative_file_paths_in_dir exit')
	return relative_file_paths


def collect_file_paths(root_path, file_name):
	file_paths = []
	for root, dirs, files in os.walk(root_path):
		for file_ in files:
			print 'file_', file_
	return file_paths

def copy_quiz(quiz_name):
	file_paths = collect_file_paths(BASE_REMOTE, )

def copy_quizzes():
	for quiz_name in QUIZ_LIST:
		copy_quiz(quiz_name)

def grade_quizzes():
	pass

def main():
	copy_quizzes()
	grade_quizzes()

if __name__ == "__main__":
	main()