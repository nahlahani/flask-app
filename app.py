from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_wtf import FlaskForm
from wtforms.form import Form
from wtforms import StringField, TextAreaField, PasswordField, validators, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from flask_mysqldb import MySQL
app = Flask(__name__)
#Config MySQL
app.config['MYSQL_HOST']= 'localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='NEWPASSWORD'
app.config['MYSQL_DB']='articleapp'
app.config['MYSQL_CURSORCLASS'] ='DictCursor'
#init MYSQL
app.config['SECRET_KEY'] = '18fa55c8857033de91bfa3d59cb4467c'

mysql = MySQL(app)


@app.route('/')
@app.route('/home')
@app.route('/article')
def index():
	cur =mysql.connection.cursor()
	#Get Articles
	result = cur.execute("SELECT * FROM articles")

	articles = cur.fetchall()
	if result > 0:
		return render_template('home.html', articles = articles)
	else:
		return render_template('home.html')
	cur.close()

@app.route('/article/<string:id>')
def article(id):
	cur = mysql.connection.cursor()

	resutl = cur.execute("SELECT * FROM articles WHERE id= %s", [id])
	article = cur.fetchone()
	return render_template('article.html', article=article)


class LoginForm(FlaskForm):
	username=StringField('Username', validators=[DataRequired(), Length(min=2, max=6)])
	password=PasswordField('Password', validators=[DataRequired()] )
	submit = SubmitField('Login')

@app.route('/admin', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		if form.username.data == 'admin' and form.password.data == 'whatever':
			session['logged_in'] = True
			session['username']= form.username.data
			flash('You have Been logged in!', 'success')
			return redirect(url_for('index'))
		else:
			flash('Login Unsuccessful. Please Get the Fuck Out', 'danger')
	return render_template('admin.html', title='Admin Panel', form=form)



@app.route("/logout")
def logout():
	session.clear()
	flash('You are now logout', 'success')
	return redirect(url_for('login'))

class ArticleForm(Form):
	title = StringField('Title', [validators.Length(min=1, max=200)])
	body = TextAreaField('Body', [validators.Length(min=30)])


@app.route('/add_article', methods=['GET', 'POST'])
def add_article():
	form = ArticleForm(request.form)
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data

		cur=mysql.connection.cursor()

		cur.execute("INSERT INTO articles(title, body) VALUES(%s, %s)", (title, body))
		mysql.connection.commit()
		cur.close()
		flash('Article Created', 'success')
		return redirect(url_for('index'))

	return render_template('add_article.html', form = form)

#Edit Article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
def edit_article(id):
	cur = mysql.connection.cursor()
	#Get article by Id
	result = cur.execute("SELECT * FROM articles where id = %s", [id])
	article = cur.fetchone()
	#Get Form
	form = ArticleForm( request.form)
	#Populate article form fields
	form.title.data = article['title']
	form.body.data = article['body']

	if request.method == 'POST' and form.validate():
		title = request.form['title']
		body = request.form['body']

		cur= mysql.connection.cursor()
		cur.execute("UPDATE articles SET title=%s, body=%s WHERE id=%s", (title, body, id))
		mysql.connection.commit()
		cur.close()
		flash('Article Updated', 'sucess')
		return redirect(url_for('index'))
	return render_template('edit_article.html', form=form)

#DELETE ARTICLE
@app.route('/delete_article/<string:id>', methods=['POST'])
def delete_article(id):
	cur= mysql.connection.cursor()
	cur.execute("DELETE FROM articles WHERE id=%s", [id])
	mysql.connection.commit()
	cur.close()
	flash('article deleted', 'danger')
	return redirect(url_for('index'))


#Search 
@app.route('/result', methods=['GET', 'POST'])
def search():
	cur =mysql.connection.cursor()
	text= request.form["searchinput"]
	result=cur.execute("SELECT * FROM articles WHERE title = %s", [text])
	article=cur.fetchone()
	if result > 0:
		return render_template('result.html', article = article)
	else:
		return render_template('home.html')
	cur.close()

if __name__ == '__main__':
	app.secret_key='Secret010'
	app.run(debug=True)
