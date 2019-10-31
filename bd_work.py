from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, create_engine, update, func, distinct, text

from contextlib import contextmanager

Base = declarative_base()

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer(), primary_key=True, auto_increment=True)
    tag = Column(String())

    def __init__(self, d):
        self.tag = d.get('tag', '')

    def __repr__(self):
        return "<Tag('%s', '%s')>" % (self.id, self.tag)


class Task(Base):
	__tablename__ = 'tasks'

	id = Column(Integer(), primary_key=True, auto_increment=True)
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



with open("param") as f:
	debug = f.read()

	if debug == 'test':
		db = 'task_base_test'
	else:
		db = 'task_base'

engine = create_engine('mysql+pymysql://nevstrui:12345@localhost/%s' % db)
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



def tag_list():
	with session_scope() as session:
		ans = [(t.id, t.tag) for t in session.query(Tag)]

	return ans

def task_dict(tag_list):
	with session_scope() as session:
		if tag_list != []:
			good_tasks = session.query(Tags_task.task_id). \
						filter(Tags_task.tag_id.in_(tag_list)). \
						group_by(Tags_task.task_id). \
						having(func.count(distinct(Tags_task.tag_id)) >= len(tag_list)). \
						subquery()
		else:
			good_tasks = session.query(Tags_task.task_id).group_by(Tags_task.task_id).subquery()

		query = session.query(Task, func.group_concat(Tag.tag.op('separator')(text('"; "')))). \
					join(good_tasks).join(Tags_task).join(Tag). \
					group_by(Task.id)
	
		ans = []
		for i in query.all():
			d = i[0].__dict__.copy()
			d['tags'] = i[1]
			ans.append(d)

		return ans


def get_task(t_id):
	with session_scope() as session:
		ans = session.query(Task).filter(Task.id == t_id)
		tags = session.query(Tag).join(Tags_task).filter(Tags_task.task_id == t_id)
		return [ans.first().__dict__, [t.__dict__ for t in tags.all()]]

def add_tag(tag):
	with session_scope() as session:
		session.add(Tag(tag))


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

	with session_scope() as session:
		t = Task(task)
		session.add(t)
		session.commit()

		if tags != None:
			for tag in tags:
				session.add(Tags_task({'task_id': t.id, 'tag_id': tag}))


def update_task(task, t_id):
	tags = task.pop("tags", None)

	with session_scope() as session:
		session.query(Task).filter(Task.id == t_id).update(values=task)
		session.query(Tags_task).filter(Tags_task.task_id == t_id).delete()
		
		if tags != None:
			for tag in tags:
				session.add(Tags_task({'task_id': t_id, 'tag_id': tag}))