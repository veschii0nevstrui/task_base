from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, LoginManager, login_user, logout_user, current_user
from forms import TaskForm, TagForm, ContestForm, TagsForm, Tag, Task, LoginForm, RegisterForm
from bd_work import task_dict, get_task, update_task, tag_list, get_tag, update_tag, tag_dict, tag_list, contest_dict, get_contest, update_contest, get_user, add_user, check_user
import argparse
import sys

def _to_dict(cl):
	return dict((key, value.data) for (key, value) in cl.__dict__.items() if key in cl.white_list)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'just for exists'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return get_user(user_id)

@app.route('/login/', methods=['get', 'post'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		d = _to_dict(form)
		message = check_user(d)
		if message == "Ok":
			return redirect(url_for('main'))
		else:
			flash(message)
			return redirect(url_for('login'))

	return render_template(form.template, form=form)

@app.route('/logout/', methods=['get', 'post'])
@login_required
def logout():
	flash("Вы успешно вышли")
	logout_user()
	return redirect(url_for('main'))

@app.route('/register/', methods=['get', 'post'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		d = _to_dict(form)
		try:
			add_user(d)
		except:
			flash("Что-то пошло не так. Вероятно, такой пользователь уже существует")
			return redirect(url_for('register'))
		return redirect(url_for('login'))

	return render_template(form.template, form=form)


@app.route('/add/task/', methods=['get', 'post'])
@login_required
def add_task():
	form = TaskForm()
	c_id = request.args.get('c_id', None)

	form.set_choices()

	if form.validate_on_submit():
		d = _to_dict(form)
		d['c_id'] = c_id
		form.add(d)
		if c_id != None:
			return redirect(url_for('render_contest', c_id=c_id))
		else:
			return redirect(url_for('table_tasks'))

	return render_template(form.template, form=form, name="Add task")


@app.route('/add/tag/', methods=['get', 'post'])
@login_required
def add_tag():
	form = TagForm()

	form.set_choices()
	if form.validate_on_submit():
		d = _to_dict(form)
		try:
			form.add(d)
		except:
			flash("Что-то пошло не так. Вероятно, такой тег уже существует")
			return redirect(url_for('add_tag'))
		return redirect(url_for('table_tags'))


	return render_template(form.template, form=form, name="Add tag")

@app.route('/add/contest/', methods=['get', 'post'])
@login_required
def add_contest():
	c_id = request.args.get("c_id", None)
	if c_id == None:
		form = ContestForm()
	else:
		contest, tasks = get_contest(c_id)
		form = ContestForm(
			name = contest['name'],
			year = contest['year'],
			description = contest['description'],
			link = contest['link'],
			tutorial = contest['tutorial']
		)

	form.set_choices()

	if form.validate_on_submit():
		d = _to_dict(form)
		d['statement'] = form.statement
		form.add(d)
		return redirect(url_for('table_contests'))

	if c_id != None and tasks != []:
		for task in tasks:
			t = Task()
			t.task = task['id']
			t.csrf_token = form.csrf_token
			form.tasks.append_entry(t)
	else:
		t = Task()
		form.tasks.append_entry(t)

	form.set_choices()

	return render_template(form.template, form=form, name = "Add contest")


@app.route('/')
def main():
	return render_template("refs.html")

@app.route('/how_to')
def how_to():
	return render_template("how_to.html")

@app.route('/todo')
def todo():
	return render_template("todo.html")

@app.route('/tasks', methods=['get', 'post'])
@login_required
def table_tasks():
	form = TagsForm()
	form.set_choices()

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
@login_required
def table_contests():
	contests = contest_dict()
	return render_template("table_contests.html", contests=contests)


@app.route('/task/<t_id>')
@login_required
def render_task(t_id):
	task, tags = get_task(t_id)
	return render_template("task.html", task=task, tags=tags)

@app.route('/contest/<c_id>')
@login_required
def render_contest(c_id):
	contest, tasks = get_contest(c_id)
	return render_template("contest.html", contest=contest, tasks=tasks)


@app.route('/edit_task/<t_id>', methods=['get', 'post'])
@login_required
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

	form.set_choices()

	return render_template(form.template, form=form, name="Редактировать задачу")

@app.route('/edit_tag/<t_id>', methods = ['get', 'post'])
@login_required
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
@login_required
def edit_contest(c_id):
	contest, tasks = get_contest(c_id)
	form = ContestForm(
		name = contest['name'],
		year = contest['year'],
		description = contest['description'],
		link = contest['link'],
		tutorial = contest['tutorial']
		)

	form.set_choices()

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
	else:
		t = Task()
		form.tasks.append_entry(t)

	form.set_choices()

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

	app.run(host="0.0.0.0", debug=debug)