from flask import Flask , render_template ,redirect, url_for ,request ,flash
from flask_wtf import FlaskForm 
from wtforms import ValidationError
from wtforms import StringField, SubmitField , IntegerField
from wtforms.validators import InputRequired , Email , Length, AnyOf
import os
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager , UserMixin  
from flask_login import login_user , login_required , logout_user , current_user, login_required
from flask_bootstrap import Bootstrap
#from flask_migrate import Migrate
import datetime 




# this statement will convert this file into an flask application.
app = Flask(__name__)
#Bootstrap(app)

app.config['SECRET_KEY'] = 'secret'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'
login_manager.login_message_category = 'info'



# getting absolute path of current working directory and concatinating it with the string"/project.db"
# so now the db's path will be d:\\flask_project:\\project.db. Note here that .db is an EXTENSION.
# without .db extention the database file may not work as expected.
file_path = os.path.abspath(os.getcwd())+"/Project.db"

# establishing connection with the created database.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ file_path 
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

# set track_modifications to false as not current working on this project.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'secret'

# creating a sqlalchemy's object and passing this "file" as an argument.
db = SQLAlchemy(app)
#Migrate(app,db)

@login_manager.user_loader
def load_user(user_id):
    return Teachers.query.get(user_id) 
#####################################################
#################_-- FORMS ----------------------
class TeacherRegister(FlaskForm):
	full_name = StringField('Full Name', validators=[InputRequired(message="Enter Your Name Please")])
	lecture_key = StringField('Lecture Key',validators=[InputRequired(message="Enter Your Lecture key Please")])
	passcode = StringField('Password',validators=[InputRequired()])
	username = StringField('Username',validators=[InputRequired(message="Enter Your UserName Please"),Length(min=5,max=20,message="Username Too short")])

	submit = SubmitField('Register')

	def validate_lecture_key(self,lecture_key):
		teach = Teachers.query.filter_by(lecture_key=lecture_key.data).first()
		if teach:
			raise ValidationError('username is already taken,Please choose a different one.')

	def validate_username(self,username):
		key = Teachers.query.filter_by(username=username.data).first()
		if key:
			raise ValidationError('Lecture key is already taken,Please choose a different one.')

	

class LoginForm(FlaskForm):
	#name  = StringField('Name',validators=[InputRequired()])
	username = StringField('Username',validators=[InputRequired('Please enter you Username')])
	lecture_key =StringField('Lecture Key',validators=[InputRequired('Please enter youe lecture key')])
	passcode = StringField('Passcode',validators=[InputRequired('Enter the Passcode')])
	submit =SubmitField('LogIn')

class UpdateUsernameForm(FlaskForm):
	username = StringField('Enter New UserName',validators=[InputRequired(message="Enter Your UserName Please"),
		Length(min=5,max=20,message="Username Too short")])
	submit =SubmitField('Update UserName')

	def validate_username(self,username):
		key = Teachers.query.filter_by(username=username.data).first()
		if key:
			raise ValidationError('UserName is already taken,Please choose a different one.')

class UpdatelecturekeyForm(FlaskForm):
	lecture_key = StringField('Lecture Key',
		validators=[InputRequired(message="Enter Your Lecture key Please")])
	submit =SubmitField('Update Lecture Key')

	def validate_lecture_key(self,lecture_key):
		key = Teachers.query.filter_by(lecture_key=lecture_key.data).first()
		if key:
			raise ValidationError('Lecture Key is already taken,Please choose a different one.')


class TeacherAttendanceForm(FlaskForm):
	lecture_key = StringField('Lecture Key you want to search students for',
 		validators=[InputRequired(message="Enter Your Lecture key Please")])
	submit =SubmitField('Search Students')
	
	

class Student_form(FlaskForm):
	username = StringField('Full Name',validators=[InputRequired('Please enter you Username'),
		Length(min=3,max=10,message="Check your Name")])
	

	lecture_key =StringField('Lecture Key',validators=[InputRequired('Please enter youe lecture key')])
	
	roll_number=IntegerField('Roll Number',validators=[InputRequired('Please enter youe lecture key')])
		

	section_class=StringField('Enter your class and section',validators=[InputRequired('Enter your Class and Section'),
		Length(min=3,max=15)])
	


	submit =SubmitField('Mark My Present')

	def validate_lecture_key(self,lecture_key):
		a = Teachers.query.filter_by(lecture_key=lecture_key.data).first()
		if not a:
			raise ValidationError('No key Found!')
		
			


###############################################################################################
##############################  MODELS  ##########################

"""
Creating Tables In The DataBase.
"""


class Teachers(UserMixin,db.Model):
	id = db.Column(db.Integer,primary_key = True)
	
	full_name = db.Column(db.String(50),nullable=False)
	
	username = db.Column(db.String(50),nullable=False,unique=True)
	
	lecture_key= db.Column(db.String(50),unique=True, nullable=False)



	def __init__(self,full_name,lecture_key,username):
		self.full_name = full_name 
		self.lecture_key = lecture_key
		self.username = username

class Students(db.Model , UserMixin):
	id = db.Column(db.Integer,primary_key=True)

	full_name = db.Column(db.String(50),nullable=False)

	roll_number = db.Column(db.Integer,nullable=False)



	section_class = db.Column(db.String(50),nullable = False )

	time = db.Column(db.DateTime,nullable=False,default=datetime.datetime.now) 
	#time = db.Column(db.DateTime,nullable=False,default=datetime.datetime.now)

	lecture_key=db.Column(db.String(50),nullable=False)


	def __init__(self,full_name, roll_number , section_class , lecture_key):
		self.full_name =full_name 
		self.roll_number=roll_number
		self.section_class =section_class 
		self.lecture_key=lecture_key


	

###---------------------------








@app.route('/')
def index():
	
	return redirect(url_for('Student_atten'))  

@app.route('/register',methods=['GET','POST'])
def register():
	form = TeacherRegister()
	if current_user.is_authenticated:
		flash('Already logged In','primary')
		return redirect(url_for('attendance'))

	if form.validate_on_submit():
		if form.passcode.data == '89125806':
		
		    teach_ob = Teachers(full_name=form.full_name.data, lecture_key=form.lecture_key.data, username=form.username.data)
		    db.session.add(teach_ob)
		    db.session.commit()
		    flash('Registered Successfully,login to continue.','success')
		    return redirect('login')
		flash('Passcode Incorrect','danger')
		return redirect('home')
	return render_template('register.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
	form = LoginForm()
	if current_user.is_authenticated:
		flash('Already logged In','primary')
		return redirect(url_for('attendance'))
	if form.validate_on_submit():
		if form.passcode.data=='89125806':
			teach = Teachers.query.filter_by(username=form.username.data).first()
			if (teach and teach.lecture_key == form.lecture_key.data):
				login_user(teach)
				flash('Logged In!', 'success')
				return redirect(url_for('account')) ##account
			else:
				flash('Please check your credentials','danger')
				redirect(url_for('login'))
		else:
			flash('Passcode Incorrect','danger')
			redirect(url_for('login'))

	return render_template('login.html',form=form)





@app.route('/logout')
def logout():
	flash('Logged Out!','danger')
	logout_user()
	return redirect(url_for('login'))

	

#@app.route('/attendance')
#def attendance():
#	return render_template('attendance.html')

@app.route('/account')
@login_required
def account():
	return render_template('account.html')





@app.route('/update_username',methods=['GET','POST'])
@login_required
def update_username():
	form=UpdateUsernameForm()
	if form.validate_on_submit():
		current_user.username =  form.username.data
		db.session.commit()
		flash('UserName Updated','success')
		return redirect(url_for('account'))
	return render_template('update_username.html',form=form)

@app.route('/update_lecture_key',methods=['GET','POST'])
@login_required
def update_lecture_key():
	form=UpdatelecturekeyForm()
	if form.validate_on_submit():
		current_user.lecture_key =  form.lecture_key.data
		db.session.commit()
		flash('Lecture Key Updated','success')
		return redirect(url_for('account'))
	return render_template('update_lecture_key.html',form=form)


@app.route('/get_attendance',methods=['GET','POST'])
@login_required 
def get_data():
	form = TeacherAttendanceForm()
	if form.validate_on_submit():
		gt = Students.query.filter_by(lecture_key=form.lecture_key.data).all()
		if gt:
			return render_template('present_student.html',gt=gt)
		else:
			flash('No Student Found','info')
	return render_template('get_data.html',form=form)

		
	



@app.route('/students_attendance',methods=['GET','POST'])
def Student_atten():
	form = Student_form()
	if form.validate_on_submit():
		
		stu = Students(full_name=form.username.data, roll_number=form.roll_number.data
		, section_class=form.section_class.data, lecture_key=form.lecture_key.data)
		db.session.add(stu)
		
		db.session.commit()
		flash('Marked Your Present, THANK YOU','success')
		return redirect(url_for('login')) ###change it to home
	return render_template('students_attendance.html',form=form)


	        
    #teach = Teachers.query.filter_by(lecture_key=form.lecture_key.data).first()
	#if not teach:
	#		flash('Invalid Lecture Key','danger')
	#		return redirect(url_for('login'))
	#else:

	   # if request.method == 'POST':

if __name__ == '__main__':
	app.run()

	

	
