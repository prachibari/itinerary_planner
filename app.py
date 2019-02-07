from flask import Flask, request,render_template,flash,redirect,url_for,session,jsonify
#from flask_jsonpify import jsonify
from flaskext.mysql import MySQL
import json
from flask_restful import Resource, Api
from forms import RegistrationForm,LoginForm,RequestResetForm,ResetPasswordForm,AdminForm
from flask_bcrypt import Bcrypt
import gc
from flask_mail import Mail,Message
import random
import string
import datetime
import dateutil.parser

###########################
from bokeh.charts import Histogram,Donut
import pandas as pd
import bokeh.charts as bc
from bokeh.resources import CDN
from bokeh.embed import components
#from bokeh.charts import defaults, vplot, hplot, show, output_file
#from bokeh.models import (HoverTool, FactorRange, Plot, LinearAxis, Grid,Range1d)
#from bokeh.models.widgets import Dropdown,Select,TextInput
#from bokeh.layouts import widgetbox,column
#from bokeh.models import ColumnDataSource
#from bokeh.io import curdoc
#from bokeh.plotting import figure
#############################

import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  auth_plugin='mysql_native_password',
  database='pythonproj'
)


app = Flask(__name__)
mysql = MySQL() 
bcrypt = Bcrypt()
lettersAndDigits = string.ascii_letters + string.digits

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'pythonproj'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['SECRET_KEY'] = '58458792afnki845'

#Email Configurations
app.config.update(
        DEBUG=True,
        MAIL_SERVER='smtp.googlemail.com',
        MAIL_PORT=465,
        MAIL_USE_SSL=True,
        MAIL_USERNAME='voyager.pythonproj@gmail.com', 
        MAIL_PASSWORD='')  

mail = Mail(app)
mysql.init_app(app)
api = Api(app)


if __name__ == '__main__':
    app.run(debug=True)

#defaults.width = 600
#defaults.height = 600

df_iplace = pd.read_sql("select ip.itinerary_id,ip.placeid,p.placename,p.city from itinerary_places ip inner join placedetails p on ip.placeid=p.placeid", con=mydb)   
#from bokeh.util.string import encode_utf8
#menu = [(tuple(df_iplace['city'].unique()))]
#menu = [("mumbai","pune")]
#dropdown = Dropdown(label="Dropdown button", button_type="warning", menu=menu)

#cname='Mumbai'

@app.route("/popular-places",methods=["GET","POST"])
def popular_places():
    try:    
        db=mysql.connect()
        mycursor =db.cursor()
        mycursor.execute("select distinct(city) from placedetails")
        cities=[]
        for row in mycursor:
            cities.append(row[0])
        form = AdminForm()
        form.city.choices = [(city,city) for city in cities]
        if request.method == 'POST' and form.validate_on_submit():
            cname = request.form['city']
            subset = df_iplace[df_iplace['city']==cname]
            places=subset['placename'].value_counts().to_frame()
            plot = bc.Bar(places.iloc[0:5,],label="index", values = "placename",plot_width=1000,
                       plot_height=700,legend="top_right",bar_width=0.3,min_border=30,
                       xlabel="Places",ylabel="Count")
            script, div = components(plot)
            return render_template("admin.html",form=form,script=script,title_text="Top 5 Places visited by people in ", div=div, bokeh_css=CDN.render_css(),bokeh_js=CDN.render_js(),city=cname)
        return render_template("admin.html",form=form)
    except:
        print("Exception occured in admin")
    finally:
        db.close()

        
        
@app.route("/temp",methods=["GET","POST"])
def popular_places_temp():
   
    print('in temp')
    db=mysql.connect()
    mycursor =db.cursor()
    mycursor.execute("select distinct(city) from placedetails")
    cities=[]
    for row in mycursor:
        cities.append(row[0])
    
    return render_template("admin.html",cities=cities)

    db.close()
@app.route("/loadplot/<city>",methods=["GET","POST"])    
def loadplot(city):
    cname = city
    subset = df_iplace[df_iplace['city']==cname]
    places=subset['placename'].value_counts().to_frame()
    plot = bc.Bar(places.iloc[0:5,],label="index", values = "placename",plot_width=1000,
               plot_height=700,legend="top_right",bar_width=0.3,min_border=30,
               xlabel="Places",ylabel="Count")
    script, div = components(plot)
    return render_template("plot.html",script=script,title_text="Top 5 Places visited by people in ", div=div, bokeh_css=CDN.render_css(),bokeh_js=CDN.render_js(),city=cname)

@app.route("/users")
def users():
    users = pd.read_csv("users.xlsx")
    #df_users = pandas.read_sql("select city,email from users  group by city", con=mydb)
    #df_users.rename(columns={ df_users.columns[1]: "count" },inplace=True)
    #cities = df_users['city']
    #users = df_users['count'].astype(float).values
    #donut_from_df = Donut(users,values=users['Email'],label=users['City'],agg='count')
    hover = HoverTool(tooltips=[('Pct', '@pct')],mode='vline')
    users['']
    donut_from_df = bc.Donut(users['City'],level_spacing=[0.0, 0.01])
    
    '''    
    donut_from_df = Donut(df_users, label = "city",xlabel="city",ylabel="users",
                      values="count",
                      title="Users Per city",
                      title_text_font_size=str(32)+"pt",
                      level_spacing=[0.0, 0.01])'''
    #show(donut_from_df)
    script, div = components(donut_from_df)  
    return """
    <!doctype html>
    <head>
     <title>Popular places</title>
     {bokeh_css}
    </head>
    <body>
     <h1>Most Popular Places visited by people!
     {div}
    
     {bokeh_js}
     {script}
    </body>
     """.format(script=script, div=div, bokeh_css=CDN.render_css(),
     bokeh_js=CDN.render_js())
     #return render_template(script=script,div=div, bokeh_css=CDN.render_css(),bokeh_js=CDN.render_js())
        
@app.route("/dem")
def visualisation():
     current_city_name = request.args.get("city_name")
     if current_city_name == None:
         current_city_name = "Mumbai"
     subset = df_iplace[df_iplace['city']==dropdown.value]
     #plot = create_figure(current_city_name) 
     plot = bc.Bar(subset, "placename", values = "placename", agg="count",plot_width=1000,
                   plot_height=1000,title = "Popular places") 
     
 # Generate the script and HTML for the plot
     script, div = components(plot)

     # Return the webpage
     return """
    <!doctype html>
    <head>
     <title>Popular places</title>
     {bokeh_css}
    </head>
    <body>
     <h1>Most Popular Places visited by people!
     {div}
    
     {bokeh_js}
     {script}
    </body>
     """.format(script=script, div=div, bokeh_css=CDN.render_css(),
     bokeh_js=CDN.render_js())
    
@app.route("/landing_page")
def showLandingPage():
    return render_template('landing_page.html')

@app.route("/viewplace",methods=["POST"])
def viewPlace():
    try:
        cityName= request.form['placeName']
        output={}
        db= mysql.connect()
        mycursor =db.cursor()
        mycursor.execute("select * from placedetails where City='"+cityName+"'")
        counter=1
        for row in mycursor:
            output.update({'place'+str(counter):{'placeid':row[0],'cityname':row[1],'name':row[2],'rating':row[3],'numofreview':row[4],'imagename':row[5],'desc':row[6],'shortdesc':row[7],'address':row[8],'review1':row[9],'review2':row[10],'review3':row[11]}})
            counter+=1
        res={'places':output}
    except:
         print('Exception occurred')
    finally:
        db.close()
    return json.dumps(res)

@app.route("/searchCity",methods=["POST"])
def searchCity():    
    try:
        searchTerm= request.form['searchTerm']    
        output={}
        db= mysql.connect()
        mycursor =db.cursor()
        mycursor.execute("select distinct(City) from placedetails where upper(City) like '"+searchTerm+"%'")    
        for row in mycursor:
            output.update({row[0]:row[0]})        
        res={'places':output}   
    except:
        print('Exception occurred')
    finally:
        db.close()
    return json.dumps(res)

@app.route("/addPlaceToItinerary",methods=["POST"])
def addPlaceToItinerary():
    try:
        placeid=request.form['placeid']
        itineraryid=request.form['itineraryid']
        print(placeid)
        print(itineraryid)
        res={'response':'200'}
    except:
        print('Exception occurred')
        return json.dumps(res)
   
@app.route("/register",methods=["POST","GET"])
def register():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        userDetails = request.form
        fname = userDetails['fname']
        lname = userDetails['lname']
        city= userDetails['city']
        email = userDetails['email']
        password = bcrypt.generate_password_hash(str(userDetails['password'])).decode('utf-8')
        con = mysql.connect()
        cursor = con.cursor()
        res = cursor.execute("SELECT * from USERS WHERE Email = %s;",(email))
        if int(res) > 0:
            flash("Email Id already exists, please try another one",'danger')
            return render_template('register.html',form=form)
        else:
            cursor.execute("INSERT INTO USERS(FirstName,LastName,Email,Password,City) VALUES (%s, %s, %s, %s, %s);",(fname,lname,email,password,city))
            con.commit()
            flash('Account created successfully {0}!You can now login.'.format(form.fname.data),'success')
            gc.collect()
            return redirect(url_for('login')) 
    return render_template('register.html',form=form)

@app.route("/login",methods=["POST","GET"])
def login():
    form = LoginForm()
    form1 = RegistrationForm()
    if form.validate_on_submit():
        userDetails = request.form
        con = mysql.connect()
        cursor = con.cursor()
        res = cursor.execute("SELECT * from USERS WHERE Email = %s;",(userDetails['email']))
        if int(res) > 0:
            passw = cursor.fetchone()[3]
            if bcrypt.check_password_hash(passw,str(userDetails['password'])):
                session['username']=userDetails['email']
                return redirect(url_for('showLandingPage'))
            else:
                flash("Incorrect password",'error')
                return render_template('login.html',form=form)
        else:
            flash('Please Sign Up','error')
            return render_template('register.html',form=form1)
    else:
        return render_template('login.html',form=form)
        
           
@app.route("/logout")
def logout():
    print('logging out {0}'.format(session.pop('username')))
    session.clear()
    session.pop('username',None)
    #flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('showLandingPage'))


@app.route("/reset-password",methods=["POST","GET"])
def forgot_password():
    '''This function will generate a token once password reset request has been received. '''
    con = mysql.connect()
    cursor = con.cursor()
    form = RequestResetForm()
    if form.validate_on_submit():
        userDetails = request.form
        res = cursor.execute("SELECT * from USERS WHERE Email = %s;",(userDetails['email']))
        if int(res) > 0:
            recipient = userDetails['email']
            session['username']=userDetails['email']
            print("Generating token ")
            token = ''.join(random.choice(lettersAndDigits) for i in range(8))
            ts=datetime.datetime.now()
            cursor.execute("INSERT INTO PASSWORD_RESET(Email,Token,Timestamp) VALUES (%s,%s,%s)",(recipient,token,ts))
            con.commit()
            msg = Message("Password Reset Request",
                          sender="voyager.pythonproj@gmail.com",
                          recipients=[recipient]) 
            msg.html = render_template('mail.html',token=token)
            mail.send(msg)
            print('Mail Sent')
            flash("Mail Sent")
        else:
            flash("User doesnot exist","danger")
    con.close()
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset-password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    '''This function will update the new password for the user.'''
    username = session['username']
    valid = verify_reset_token(token)
    con = mysql.connect()
    cursor = con.cursor()
    if valid is False:
        flash('This URL has expired', 'warning')
        return redirect(url_for('forgot_password'))
    form = ResetPasswordForm()
    userDetails = request.form
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(str(userDetails['password'])).decode('utf-8')
        res = cursor.execute("SELECT * from USERS WHERE Email = %s;",(username))
        if int(res) > 0:
            cursor.execute("UPDATE USERS SET Password = %s WHERE Email = %s",(password,username))
            con.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('login'))
        else:
            print("Record Not found")
            flash("Email id does not exist","error")
    con.close()
    return render_template('reset_token.html', title='Reset Password', form=form)

def verify_reset_token(token):
    '''This function will validate the URL for resetting new password.
    It is active only for 2 hours '''
    username = session['username']
    print(username)
    con = mysql.connect()
    cursor = con.cursor()
    cursor.execute("SELECT * from PASSWORD_RESET WHERE Email = %s;",(username))
    for row in cursor:
        if row[1] == token:
            old = row[2]
    gend = dateutil.parser.parse(old, ignoretz=True)
    new =  datetime.datetime.now()
    diff = new-gend
    mins = divmod(diff.days*86400+diff.seconds,60)
    if mins[0] > 120:
        return False
    else:
        return True
    cursor.close()
    con.close()