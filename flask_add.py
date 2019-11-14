from flask import Flask, render_template, request, redirect, url_for
from forms import TaskForm, TagForm, ContestForm, TagsForm, Tag, Task
from bd_work import task_dict, get_task, update_task, tag_list, get_tag, update_tag, tag_dict, tag_list, contest_dict, get_contest, update_contest
import argparse
import sys

def _to_dict(cl):
	return dict((key, value.data) for (key, value) in cl.__dict__.items() if key in cl.white_list)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'just for exists'

@app.route('/add/<obj>/', methods=['get', 'post'])
def add(obj):
	if obj == "task":
		form = TaskForm()
	elif obj == "tag":
		form = TagForm()
	elif obj == 'contest':
		form = ContestForm()
	else:
		return "Sorry, this page has not been developed yet"

	form.set_choices()

	if form.validate_on_submit():
		d = _to_dict(form)
		form.add(d)
		return redirect(url_for('add', obj=obj))

	if obj == 'contest' and form.tasks.entries == []:
		task = Task()
		task.set_choices()
		form.tasks.append_entry(task)

	return render_template(form.template, form=form, name="Добавить задачу")

@app.route('/')
def main():
	return render_template("refs.html")

@app.route('/tasks', methods=['get', 'post'])
def table_tasks():
	form = TagsForm()
	for tag in form.tags:
		tag.set_choices()

	tag_list = []

	if form.validate_on_submit():
		tag_list = [str(i['tag']) for i in _to_dict(form)["tags"]]
	
	ans = task_dict(tag_list)
	return render_template("table_task.html", tasks=ans, form=form)

@app.route('/tags')
def table_tags():
	tags = tag_dict()
	tag_name = {t['id']: t['tag'] for t in tags}
	tag_l = tag_list()
	return render_template("table_tags.html", tags=tags, tag_name=tag_name, tag_list=tag_l)

@app.route('/contests')
def table_contest():
	contests = contest_dict()
	return render_template("table_contests.html", contests=contests)


@app.route('/task/<t_id>')
def render_task(t_id):
	task, tags = get_task(t_id)
	return render_template("task.html", task=task, tags=tags)

@app.route('/contest/<c_id>')
def render_contest(c_id):
	contest, tasks = get_contest(c_id)
	return render_template("contest.html", contest=contest, tasks=tasks)


@app.route('/edit_task/<t_id>', methods=['get', 'post'])
def edit_task(t_id):
	task, tags = get_task(t_id)
	form = TaskForm(
		name = task['name'],
		statement = task['statement'],
		short_statement = task['short_statement'],
		todo = task['todo'],
		tutorial = task['tutorial'],
		complexity = task['complexity'],
		source = task['source']
	)

	form.set_choices()

	if form.validate_on_submit():
		d = _to_dict(form)
		d['tags'] = [t['tag'] for t in d['tags']]
		update_task(d, t_id)
		return redirect(url_for('render_task', t_id=t_id))

	if tags != []:
		form.tags.pop_entry()

		for tag in tags:
			t = Tag()
			t.set_choices()
			t.tag = tag['id']
			t.csrf_token = form.csrf_token
			form.tags.append_entry(t)

	return render_template(form.template, form=form, name="Редактировать задачу")

@app.route('/edit_tag/<t_id>', methods = ['get', 'post'])
def edit_tag(t_id):
	tag = get_tag(t_id)
	form = TagForm(
		tag = tag['tag'],
		parent = tag['parent']
	)

	form.set_choices()

	if form.validate_on_submit():
		d = _to_dict(form)
		update_tag(d, t_id)
		return redirect(url_for('table_tags'))

	return render_template(form.template, form=form, name='Редактировать тег')

@app.route('/edit_contest/<c_id>', methods=['get', 'post'])
def edit_contest(c_id):
	contest, tasks = get_contest(c_id)
	form = ContestForm(
		name = contest['name'],
		year = contest['year'],
		description = contest['description'],
		link = contest['link'],
		tutorial = contest['tutorial']
		)

	for task in form.tasks:
		task.set_choices()

	if form.validate_on_submit():
		d = _to_dict(form)
		d['tasks'] = [t['task'] for t in d['tasks']]
		update_contest(d, c_id)
		return redirect(url_for('render_contest', c_id=c_id))

	if tasks != []:
		for task in tasks:
			t = Task()
			t.task = task['id']
			t.csrf_token = form.csrf_token
			form.tasks.append_entry(t)

	return render_template(form.template, form=form)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Just parse")
	parser.add_argument(
		"-d",
		"--debug", 
		type=int, 
		help="Run with debug", 
		default=1)

	args = parser.parse_args()

	debug = args.debug
	with open("param", "w") as f:
		if (debug):
			s = "test"
		else:
			s = "prod"
		f.write(s)

	print(s)

	app.run(host="0.0.0.0", debug=True)