from flask import Flask, render_template, request, redirect, url_for
from forms import TaskForm, TagForm

def _to_dict(cl):
	return dict((key, value.data) for (key, value) in cl.__dict__.items() if key in cl.white_list)

app = Flask(__name__, template_folder="./")
app.config['SECRET_KEY'] = 'just for exists'

@app.route('/add/<obj>/', methods=['get', 'post'])
def render(obj):
	if obj == "task":
		form = TaskForm()
	elif obj == "tag":
		form = TagForm()
	else:
		return "Sorry, this page has not been developed yet"

	if form.validate_on_submit():
		d = _to_dict(form)
		form.add(d)
		return redirect(url_for('render', obj=obj))

	return render_template('add_task.html', form=form)

if __name__ == "__main__":
	app.run(debug=True)