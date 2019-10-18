from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FormField, FieldList, SelectField
from wtforms.validators import DataRequired
from bd_work import add_task, add_tag, tag_list

class Tag(FlaskForm):
	tag = SelectField("Tag: ", validators=[DataRequired()], coerce=int)
	def set_choices(self):
		self.tag.choices = [(0, "")] + tag_list()


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

	white_list = set(["name", "complexity", "short_statement", "statement", "tutorial", "source", "tags", "todo"])
	template = "add_task.html"
	
	def add(self, d):
		if "tags" in d:
			d["tags"] = [i['tag'] for i in d["tags"]]
		add_task(d)

class TagForm(FlaskForm):
	tag = StringField("Tag: ", validators=[DataRequired()])
	submit = SubmitField("Submit")

	template = "add_tag.html"
	white_list = set(["tag"])

	def add(self, d):
		add_tag(d)
