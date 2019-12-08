from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FormField, FieldList, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired, URL, Optional
from bd_work import add_task, add_tag, add_contest, tag_list, task_list, contest_list

class LoginForm(FlaskForm):
	login = StringField("Login: ", validators=[DataRequired()])
	password = PasswordField("Password: ", validators=[DataRequired()])
	remember = BooleanField("Remember Me: ")
	submit = SubmitField()

	white_list = set(['login', 'password', 'remember'])
	template = "login.html"

class RegisterForm(FlaskForm):
	login = StringField("Login: ", validators=[DataRequired()])
	password = PasswordField("Password: ", validators=[DataRequired()])
	username = StringField("Name: ", validators=[DataRequired()])
	submit = SubmitField()

	white_list = set(['login', 'password', 'username'])
	template = "register.html"

class Tag(FlaskForm):
	tag = SelectField("Tag: ", validators=[DataRequired()], coerce=int, choices=[(0, "")] + tag_list())
	def set_choices(self):
		self.tag.choices = [(0, "")] + tag_list()

class Task(FlaskForm):
	task = SelectField("Task: ", validators=[DataRequired()], coerce=int, choices=[(0, "")] + task_list())
	def set_choices(self):
		self.task.choices = [(0, "")] + task_list()

class TaskForm(FlaskForm):
	name = StringField("Name: ", validators=[DataRequired()])
	short_statement = TextAreaField("Short statement: ", validators=[DataRequired()])
	statement = TextAreaField("Statement: ")
	tutorial = TextAreaField("Tutorial: ")
	complexity = StringField("Complexity: ")
	source = StringField("Source: ")
	todo = StringField("Todo: ")
	tags = FieldList(FormField(Tag), min_entries=1, max_entries=20) #!!!
	submit = SubmitField("Submit")
	contest_id = None

	white_list = set(["name", "complexity", "short_statement", "statement", "tutorial", "source", "tags", "todo"])
	template = "add_task.html"

	def set_choices(self):
		for tag in self.tags:
			tag.set_choices()
	
	def add(self, d):
		if "tags" in d:
			d["tags"] = [i['tag'] for i in d["tags"]]
		add_task(d)


class TagForm(FlaskForm):
	tag = StringField("Tag: ", validators=[DataRequired()])
	parent = SelectField("Parent: ", coerce=int, choices=[(0, "")] + tag_list())
	submit = SubmitField("Submit")

	template = "add_tag.html"
	white_list = set(["tag", "parent"])

	def set_choices(self):
		self.parent.choices = [(0, "")] + tag_list()

	def add(self, d):
		add_tag(d)

class ContestForm(FlaskForm):
	name = StringField("Name: ", validators=[DataRequired()])
	year = StringField("Year: ", validators=[DataRequired()])
	description = TextAreaField("Description: ")
	link = StringField("Link: ", validators=[DataRequired(), URL()])
	tutorial = StringField("Tutorial link: ", validators=[Optional(), URL()])
	tasks = FieldList(FormField(Task), min_entries=0, max_entries=20) #!!!
	submit = SubmitField()

	white_list = set(["name", "year", "description", "link", "tutorial", "tasks"])
	template = "add_contest.html"

	def set_choices(self):
		for task in self.tasks:
			task.set_choices()

	def add(self, d):
		d['tasks'] = [i['task'] for i in d['tasks']]
		add_contest(d)

class TagsForm(FlaskForm):
	tags = FieldList(FormField(Tag), min_entries=1, max_entries=20) #!!!
	submit = SubmitField("Submit")

	white_list = set(["tags"])