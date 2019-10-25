import json
import pymysql

def connect():
	with open("param") as f:
		debug = f.read()

	if debug == 'test':
		db = 'task_base_test'
	else:
		db = 'task_base'

	conn = pymysql.connect(
		user='nevstrui',
		password='12345',
		host='127.0.0.1',
		database=db,
		cursorclass=pymysql.cursors.DictCursor
	)
	return conn

def tag_list():
	conn = connect()
	cursor = conn.cursor()

	cursor.execute("SELECT * FROM tags")

	ans = [(tag['id'], tag['tag']) for tag in cursor.fetchall()]
	
	cursor.close()
	conn.close()

	return ans

def task_dict(tag_list):
	conn = connect()
	cursor = conn.cursor()

	s = "WHERE tag_id IN (" + ", ".join(tag_list) + ")"

	if tag_list == []:
		s = ""

	query = '''
		SELECT tasks.id, name, short_statement, GROUP_CONCAT(tags.tag SEPARATOR ", ") as tags, complexity, source, todo 
		FROM (
			SELECT task_id FROM tags_task %s
			GROUP BY task_id
			HAVING COUNT(DISTINCT tag_id) >= %s
		) s INNER JOIN tasks ON s.task_id = tasks.id
		INNER JOIN tags_task ON s.task_id = tags_task.task_id
		INNER JOIN tags ON tags_task.tag_id = tags.id
		GROUP BY tasks.id 
		''' % (s, str(len(tag_list)))

	cursor.execute(query)
	ans = cursor.fetchall()


	cursor.close()
	conn.close()

	return ans

def get_task(t_id):
	conn = connect()
	cursor = conn.cursor()

	cursor.execute("SELECT id, name, short_statement, statement, tutorial, complexity, source, todo FROM tasks WHERE id=%s", [t_id])
	ans = cursor.fetchall()

	cursor.execute('''
		SELECT tags.id, tag
		FROM 
			tasks LEFT JOIN tags_task ON tasks.id = tags_task.task_id
			LEFT JOIN tags ON tags_task.tag_id = tags.id
		WHERE tasks.id = %s
		''', [t_id])
	tags = cursor.fetchall()

	cursor.close()
	conn.close()

	return [ans[0], tags]

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
			tags: 				"list of id"
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
			insert_tag = 'INSERT INTO tags_task (task_id, tag_id) VALUES (%s, %s)'
			cursor.execute(insert_tag, [task_id, tag])


	conn.commit()

	cursor.close()
	conn.close()

def update_task(task, t_id):
	tags = task.pop("tags", None)

	template = ', '.join([str(k) + "=%s" for k, v in task.items()])
	query = "UPDATE tasks SET %s WHERE id=%s" % (template, "%s")
	
	conn = connect()
	cursor = conn.cursor()

	print(query)
	
	cursor.execute(query, list(task.values()) + [t_id])
	cursor.execute("DELETE FROM tags_task WHERE task_id=%s", [str(t_id)])

	if tags != None:
		for tag in tags:
			insert_tag = "INSERT INTO tags_task (task_id, tag_id) VALUES (%s, %s)"
			cursor.execute(insert_tag, [t_id, tag['tag']])

	conn.commit()

	cursor.close()
	conn.close()