from flask import Flask, render_template, request, redirect, url_for
from forms import TaskForm, TagForm
import argparse
import sys

def _to_dict(cl):
	return dict((key, value.data) for (key, value) in cl.__dict__.items() if key in cl.white_list)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'just for exists'

@app.route('/add/<obj>/', methods=['get', 'post'])
def render(obj):
	if obj == "task":
		form = TaskForm()
		for tag in form.tags:
			tag.set_choices()
	elif obj == "tag":
		form = TagForm()
	else:
		return "Sorry, this page has not been developed yet"

	if form.validate_on_submit():
		d = _to_dict(form)
		form.add(d)
		return redirect(url_for('render', obj=obj))

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

	app.run(debug=True)