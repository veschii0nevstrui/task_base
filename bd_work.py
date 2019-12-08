from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, create_engine, update, func, distinct, text
from sqlalchemy.exc import OperationalError

from contextlib import contextmanager

from flask_login import UserMixin, login_user, current_user

from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class User(Base, UserMixin):
	__tablename__ = 'users'

	id = Column(Integer(), primary_key=True)
	username = Column(String(100))
	login = Column(String(50), nullable=False, unique=True)
	password_hash = Column(String(200), nullable=False)
	level = Column(Integer(), nullable=False)
	approved = Column(Integer(), nullable=False)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def __init__(self, d):
		self.username = d.get('username', '')
		self.login = d.get('login', '')
		self.password_hash = generate_password_hash(d.get('password'))
		self.level = 0
		self.approved = 0

	def __repr__(self):
		return "<User('%s', '%s', '%s')>" % (self.id, self.name, self.level)


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer(), primary_key=True)
    tag = Column(String())
    parent = Column(Integer(), ForeignKey('tags.id'))

    def __init__(self, d):
        self.tag = d.get('tag', '')
        self.parent = d.get('parent', None)
        if self.parent == 0:
        	self.parent = None


    def __repr__(self):
        return "<Tag('%s', '%s')>" % (self.id, self.tag)


class Task(Base):
	__tablename__ = 'tasks'

	id = Column(Integer(), primary_key=True)
	name = Column(String(), nullable=False)
	complexity = Column(Integer())
	statement = Column(String())
	short_statement = Column(String())
	tutorial = Column(String())
	source = Column(String())
	todo = Column(String())

	def __init__(self, d):
		self.name = d.get('name', '')
		self.complexity = d.get('complexity', 0)
		self.statement = d.get('statement', '')
		self.short_statement = d.get('short_statement', '')
		self.tutorial = d.get('tutorial', '')
		self.source = d.get('source', '')
		self.todo = d.get('todo', '')
		
	def __repr__(self):
		return "<Task('%s', '%s', '%s', '%s')>" % (self.id, self.name, self.complexity, self.source)


class Tags_task(Base):
	__tablename__ = 'tags_task'

	task_id = Column(Integer(), ForeignKey('tasks.id'), primary_key=True)
	tag_id = Column(Integer(), ForeignKey('tags.id'), primary_key=True)

	def __init__(self, d):
		self.task_id = d.get('task_id', 0)
		self.tag_id = d.get('tag_id', 0)

	def __repr__(self):
		return "<Tags_task('%s', '%s')>" % (self.task_id, self.tag_id)


class Contest(Base):
	__tablename__ = 'contests'

	id = Column(Integer(), primary_key=True)
	name = Column(String(), nullable=False)
	year = Column(Integer(), nullable=False)
	description = Column(String())
	link = Column(String(), nullable=False)
	tutorial = Column(String())

	def __init__(self, d):
		self.name = d.get('name', '')
		self.year = d.get('year', 1970)
		self.description = d.get('description', '')
		self.link = d.get('link', '')
		self.tutorial = d.get('tutorial', '')

	def __repr__(self):
		return "<Contest('%s', '%s', '%s', '%s')>" % (self.id, self.name, self.year, self.link)

class Tasks_contest(Base):
	__tablename__ = 'tasks_contest'

	task_id = Column(Integer(), ForeignKey('tasks.id'), primary_key=True)
	contest_id = Column(Integer(), ForeignKey('contests.id'), primary_key=True)

	def __init__(self, d):
		self.task_id = d.get('task_id', 0)
		self.contest_id = d.get('contest_id', 0)

	def __repr__(self):
		return "<Tasks_contest('%s', '%s')>" % (self.task_id, self.contest_id)




with open("param") as f:
	debug = f.read()

	if debug == 'test':
		db = 'task_base_test'
	else:
		db = 'task_base'


engine = create_engine('mysql+pymysql://nevstrui:12345@localhost/%s' % db, pool_pre_ping=True)
Base.metadata.create_all(engine) #Я не понимаю, зачем эта строчка нужна, но в примерах она есть везде
Session = sessionmaker(bind=engine)

@contextmanager
def session_scope():
	session = Session()
	try:
		yield session
		session.commit()
	except:
		session.rollback()
		raise
	finally:
		session.close()


def get_user(user_id):
	with session_scope() as session:
		return session.query(User).get(user_id)

def add_user(user):
	with session_scope() as session:
		session.add(User(user))

def check_user(user):
	with session_scope() as session:
		u = session.query(User).filter(User.login == user['login']).first()
		if u:
			if u.check_password(user['password']):
				if u.approved:
					login_user(u)
					return "Ok"
				else:
					return "Подождите подтверждения, пожалуйста"
			else:
				return "Неправильный пароль"
		else:
			return "Нет такого логина"

def tag_dict():
	with session_scope() as session:
		ans = session.query(Tag)
		return [tag.__dict__ for tag in ans.all()]

def tag_list():
	tags = tag_dict()
	tag_name = {tag['id']: tag['tag'] for tag in tags}

	graph = {}
	for tag in tags:
		if tag['parent'] not in graph:
			graph[tag['parent']] = []

		graph[tag['parent']].append(tag['id'])

	ans = []

	def dfs(t_id, depth):
		if t_id != None:
			ans.append((t_id, ("-- " * depth) + tag_name[t_id]))
		if t_id not in graph:
			return
		for t in graph[t_id]:
			dfs(t, depth + 1)

	dfs(None, -1)

	return ans


def get_tag(t_id):
	with session_scope() as session:
		return session.query(Tag).filter(Tag.id == t_id).first().__dict__

def parent_set(t_id):
	if t_id == None:
		return set()
	
	with session_scope() as session:
		tag = session.query(Tag).filter(Tag.id == t_id).first().__dict__

	ans = parent_set(tag['parent'])
	ans.add(t_id)
	return ans

def add_tag(tag):
	with session_scope() as session:
		session.add(Tag(tag))

def update_tag(tag, t_id):
	if tag['parent'] == 0:
		tag['parent'] = None
	if int(t_id) in parent_set(tag['parent']):
		print("Here")
		raise Exception("Tag in his parent list")
	
	with session_scope() as session:
		session.query(Tag).filter(Tag.id == t_id).update(values=tag)



def get_task(t_id):
	with session_scope() as session:
		ans = session.query(Task).filter(Task.id == t_id)
		tags = session.query(Tag).join(Tags_task).filter(Tags_task.task_id == t_id)
		return [ans.first().__dict__, [t.__dict__ for t in tags.all()]]

def task_list():
	with session_scope() as session:
		ans = session.query(Task.id, Task.name)
		return [(id, str(id) + " " + name) for (id, name) in ans.all()]

def task_dict(tag_list):
	with session_scope() as session:
		if tag_list != []:
			good_tasks = session.query(Tags_task.task_id). \
						filter(Tags_task.tag_id.in_(tag_list)). \
						group_by(Tags_task.task_id). \
						having(func.count(distinct(Tags_task.tag_id)) >= len(tag_list)). \
						subquery()

			query = session.query(Task, func.group_concat(Tag.tag.op('separator')(text('"; "')))). \
					join(good_tasks).outerjoin(Tags_task).outerjoin(Tag). \
					group_by(Task.id)
		else:
			query = session.query(Task, func.group_concat(Tag.tag.op('separator')(text('"; "')))). \
						outerjoin(Tags_task, Task.id == Tags_task.task_id). \
						outerjoin(Tag).group_by(Task.id)

		ans = []
		for i in query.all():
			d = i[0].__dict__.copy()
			d['tags'] = i[1]
			ans.append(d)

		return ans

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

	tag_l = set()
	for tag in tags:
		tag_l |= parent_set(tag)

	with session_scope() as session:
		t = Task(task)
		session.add(t)
		session.commit()

		if tags != None:
			for tag in tag_l:
				session.add(Tags_task({'task_id': t.id, 'tag_id': tag}))

		if task['c_id'] != None:
			session.add(Tasks_contest({'contest_id': task['c_id'], 'task_id': t.id}))

def update_task(task, t_id):
	tags = task.pop("tags", None)

	tag_l = set()
	for tag in tags:
		tag_l |= parent_set(tag)

	with session_scope() as session:
		session.query(Task).filter(Task.id == t_id).update(values=task)
		session.query(Tags_task).filter(Tags_task.task_id == t_id).delete()
		
		if tags != None:
			for tag in tag_l:
				session.add(Tags_task({'task_id': t_id, 'tag_id': tag}))


def contest_list():
	with session_scope() as session:
		ans = session.query(Contest.id, Contest.name)
		return ans.all()

def get_contest(c_id):
	with session_scope() as session:
		contest = session.query(Contest).filter(Contest.id == c_id)
		good_tasks = session.query(Tasks_contest.task_id). \
						filter(Tasks_contest.contest_id == c_id). \
						subquery()

		query = session.query(Task, func.group_concat(Tag.tag.op('separator')(text('"; "')))). \
					join(good_tasks).outerjoin(Tags_task).outerjoin(Tag). \
					group_by(Task.id)

		tasks = []
		for i in query.all():
			d = i[0].__dict__.copy()
			d['tags'] = i[1]
			tasks.append(d)

		return (contest.first().__dict__, tasks)

def contest_dict():
	with session_scope() as session:
		query = session.query(Contest).all()
		return [i.__dict__.copy() for i in query]

def add_contest(contest):
	tasks = contest.pop('tasks', None)

	with session_scope() as session:
		c = Contest(contest)
		session.add(c)
		session.commit()

		if tasks != None:
			for task in tasks:
				session.add(Tasks_contest({'contest_id': c.id, 'task_id': task}))

def update_contest(contest, c_id):
	tasks = contest.pop('tasks', None)

	with session_scope() as session:
		session.query(Contest).filter(Contest.id == c_id).update(values=contest)
		session.query(Tasks_contest).filter(Tasks_contest.contest_id == c_id).delete()

		if tasks != None:
			for task in tasks:
				session.add(Tasks_contest({'task_id': task, 'contest_id': c_id}))