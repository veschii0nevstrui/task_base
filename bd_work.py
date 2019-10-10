import json
import mysql.connector

def connect():
	conn = mysql.connector.connect(
		user='nevstrui',
		password='12345',
		host='127.0.0.1',
		database='task_base'
	)
	return conn

def tag_list():
	conn = connect()
	cursor = conn.cursor()

	cursor.execute("SELECT * FROM tags")

	ans = cursor.fetchall()
	
	cursor.close()
	conn.close()

	return ans

def add_tag(tag):
	conn = connect()
	cursor = conn.cursor()

	cursor.execute("INSERT INTO tags (tag) VALUES(%s)", [tag["tag"]])
	conn.commit()

	cursor.close()
	conn.close()

def add_task(task):
	'''
		task must be format like:
		{
			name: 				"task name",
			complexity: 		"approximate complexity in range 0..100".
			statement: 			"task statement", #TODO take tex-like format and compile it when need
			short_statement: 	"task_short_statement",
			tutorial: 			"task tutorial"	#TODO take tex-like format
			source:				"snark-readable task source",
			todo:				"description of future work with task"
			tags: 				"list of tags"
		}
	'''
	tags = task.pop("tags", None)

	placeholders = ', '.join(['%s'] * len(task))
	columns = ', '.join(task.keys())
	insert_task = "INSERT INTO tasks ( %s ) VALUES ( %s )" % (columns, placeholders)

	conn = connect()
	cursor = conn.cursor()

	cursor.execute(insert_task, list(task.values()))

	if tags != None:
		task_id = cursor.lastrowid
		for tag in tags:
			find_command = 'SELECT id FROM tags WHERE id = %s'
			cursor.execute(find_command, [tag])
			tag_id = cursor.fetchone()[0]

			insert_tag = 'INSERT INTO tags_task (task_id, tag_id) VALUES (%s, %s)'
			cursor.execute(insert_tag, [task_id, tag_id])


	conn.commit()

	cursor.close()
	conn.close()
