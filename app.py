

from time import strftime, time
from urllib.parse import urlencode
from flask import Flask, Response, flash, redirect, render_template, request, session, url_for
from datetime import datetime


from flask_mysqldb import MySQL

from camera import Video
import io
import xlwt

app = Flask(__name__)
app.secret_key = 'super secret key'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'attendance_system'

mysql = MySQL(app)


@app.route("/")
def Home():
    return render_template('home.html')


# USER LOGGED AND REGISTER FUNTIONS START

@app.route("/login")
def User():
    return render_template('user/login.html')



@app.route("/dashboard", methods=['GET', 'POST'])
def UserHome():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        msg = ""
        req = request.form
        print(req)
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT fullname FROM userregister WHERE username = %s AND password = %s', (username, password,))
        account = cur.fetchone()
        mysql.connection.commit()
        if account:
            global current_user

           

            print(format(*account))
            session['username'] = format(*account)
           
            
            return render_template('user/home.html')
        else:
            msg = "Incorrect username or password"
            return render_template('user/login.html', msg=msg)
        

    else:
        return render_template('user/login.html')




@app.route("/home")
def UserHomePage():

    return render_template('user/home.html')


@app.route("/events")
def Events():

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM eventdisplay")
    data = cur.fetchall()
    mysql.connection.commit()
    return render_template('user/events.html', data=data)


@app.route("/eventsChecked")
def AfterEvents():
    btnContent = request.args['btnContent']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM eventdisplay")
    data = cur.fetchall()
    mysql.connection.commit()
    return render_template('user/events.html', data=data, btnContent=btnContent)


@app.route("/logout")
def Logout():
    msg = ""
    session.clear()
    msg = "logout succesfully"
    return render_template('user/login.html', msg=msg)


@app.route("/signup")
def UserSignUp():
    return render_template('user/reg.html')


@app.route("/register", methods=['POST'])
def UserReg():

    if request.method == 'POST':

        req = request.form
        print(req)
        fullname = request.form['name']
        department = request.form['depart']
        rollno = request.form['rol']
        username = request.form['user']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO userregister (rollnumber,fullname,department,username,password) VALUES (%s,%s,%s,%s,%s)",
                    (rollno, fullname, department, username, password))

        mysql.connection.commit()
        session['name'] = fullname

        return redirect(url_for('FaceRegister'))

    else:
        return redirect(url_for('UserReg'))
        # return render_template('user/reg.html')


@app.route("/face-data")
def Face():
    return render_template('user/face.html')


@app.route("/face")
def FaceRegister():
    global current_user
    current_user="unknown"
    return render_template('user/faceRegister.html')

current_user="unknown"


@app.route("/attend", methods=['GET', 'POST'])
def Attend():
    status = ""
    msg = ""
    global current_user

    if request.method == 'POST':

        user = request.form['user']
        subject = request.form['subject']
        time = request.form['time']
        end = request.form['end']
        date = request.form['date']

        now = datetime.now()
        current_user=user

        print(user)
        print(end)

        current_time = now.strftime("%H:%M")
        print("Current Time =", current_time)

        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT rollnumber from userregister WHERE fullname = %s', (user,))
        data = format(*cur.fetchone())

        if(current_time >= time and current_time <= end):
            print("present")
            status = "Present"

        elif current_time < time:
            msg = "You came too early! please  join at sharp time "
            print(msg)
            return redirect(url_for('Events', msg=msg))

        else:
            print("absent")
            status = "Absent"

        cur.execute("INSERT IGNORE INTO attendance_report (rolnumber,name,subject,time,end,date,currentTime,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (data, user, subject, time, end, date, current_time, status))

        mysql.connection.commit()

        return render_template('user/face.html', subject=subject, time=time, date=date)
    else:
        return redirect(url_for('Face'))


@app.route("/attendance")
def Attendance():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM eventdisplay")
    data = cur.fetchall()
    mysql.connection.commit()
    return render_template('user/events.html')


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
              b'Content-Type:  image/jpeg\r\n\r\n' + frame +
              b'\r\n\r\n')


@app.route('/video')
def video():
    print(Video())
    return Response(gen(Video()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# ENDED

# FACULTY LOGGED AND REGISTER FUNCTIONS

@app.route("/Falogin")
def FacultyLoginForm():
    return render_template('faculty/login.html')


@app.route("/Fasignup")
def FacultySignupForm():
    return render_template('faculty/reg.html')


@app.route("/Fadashboard", methods=['GET', 'POST'])
def FacultyHome():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        msg = ""
        req = request.form
        print(req)
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT fullname FROM faculty_register WHERE username = %s AND password = %s', (username, password,))
        account = cur.fetchone()
        mysql.connection.commit()
        if account:
            print(format(*account))
            session['username'] = format(*account)
            return render_template('faculty/home.html')
        else:
            msg = "Incorrect username or password"
            return render_template('faculty/login.html', msg=msg)

    else:
        return render_template('faculty/login.html')


@app.route("/Faevents")
def FacultyEvents():

    # subject = request.form['subject']
    # cur = mysql.connection.cursor()
    # cur.execute("SELECT subject FROM faculty_register where subject=%s",(subject))
    return render_template('faculty/events.html')


@app.route("/Fahome")
def FacultyRoot():

    return render_template('faculty/home.html')


@app.route("/FaReport")
def FacultyReport():

    cur = mysql.connection.cursor()
    cur.execute('SELECT DISTINCT * FROM attendance_report')
    data = cur.fetchall()
    mysql.connection.commit()
    return render_template('faculty/report.html', data=data)


@app.route("/FaMyevents")
def FacultyMyEvents():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM eventdisplay")

    data = cur.fetchall()

    mysql.connection.commit()
    return render_template('faculty/myevents.html', data=data)


@app.route("/FaUpdateForm", methods=['POST'])
def FacultyEventUpdate():
    id = request.form['id']
    subject = request.form['subject']
    time = request.form['time']
    end = request.form['end']
    date = request.form['date']
    return render_template('faculty/eventsUpdate.html', id=id, subject=subject, time=time, end=end, date=date)


@app.route("/FaUpdated", methods=['POST'])
def FaUpdated():

    if request.method == 'POST':
        id = request.form['id']
        subject = request.form['subject']
        time = request.form['time']
        end = request.form['end']
        date = request.form['date']
        cur = mysql.connection.cursor()
        cur.execute("""UPDATE eventdisplay SET subject=%s,time=%s,validTo=%s,date=%s  WHERE event_id=%s""",
                    (subject, time, end, date, id))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('FacultyMyEvents'))


@app.route('/delete/<int:id>', methods=['GET'])
def delete(id):
    # flash("Record Has Been Deleted Successfully")
    # cur = mysql.connection.cursor()
    # cur.execute("DELETE FROM students WHERE id=%s", (id_data,))
    # mysql.connection.commit()
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM eventdisplay WHERE event_id=%s", (id,))
    mysql.connection.commit()

    return redirect(url_for('FacultyMyEvents'))


@app.route("/Fastudents")
def FacultyStudentList():
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id,rollnumber,fullname,username FROM userregister")

    data = cur.fetchall()

    mysql.connection.commit()
    return render_template('faculty/students.html', data=data)


@app.route("/Faeventlist", methods=['POST'])
def FacultyEventsList():

    if request.method == 'POST':

        req = request.form
        print(req)
        sub = request.form['subject']
        time = request.form['time']
        validTo = request.form['validTo']
        date = request.form['date']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO eventdisplay (subject,time,validTo,date) VALUES (%s,%s,%s,%s)",
                    (sub, time, validTo, date))

        cur.execute("SELECT * FROM eventdisplay")

        data = cur.fetchall()
        print(data)

        mysql.connection.commit()

        return render_template('faculty/eventslist.html', data=data)

    else:
        return render_template('faculty/events.html')


@app.route("/Falogout")
def FacultyLogout():
    msg = ""
    session.clear()
    msg = "Logout success"
    return render_template('faculty/login.html', msg=msg)


@app.route("/Faregister", methods=['POST'])
def FacultyRegister():

    if request.method == 'POST':
        msg = ""
        req = request.form
        print(req)
        fullname = request.form['name']
        department = request.form['depart']
        subject = request.form['subject']
        username = request.form['user']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO faculty_register (fullname,department,subject,username,password) VALUES (%s,%s,%s,%s,%s)",
                    (fullname, department, subject, username, password))
        mysql.connection.commit()
        session['name'] = fullname
        msg = "Register Succefully"
        return render_template('faculty/login.html', msg=msg)

    else:
        return render_template('faculty/reg.html')


# ENDED


@app.route("/adminlogin")
def AdminLoginForm():

    return render_template('admin/login.html')


@app.route("/ahome")
def AHome():
    return render_template('admin/home.html')


@app.route("/adownload")
def ADownload():
    return render_template('admin/report.html')


@app.route("/adminhome", methods=['GET', 'POST'])
def AdminHome():
    msg = ""
    username = request.form['username']
    password = request.form['password']
    print(username, password)
    if(username == 'admin' and password == 'password'):

        return render_template('admin/home.html')
    else:
        msg = "Incorrect Username or Password"
        return render_template('admin/login.html')


@app.route("/records", methods=['GET', 'POST'])
def Records():
    subject = request.form['subject']
    time = request.form['time']
    date = request.form['date']
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM attendance_report WHERE subject = %s AND time= %s AND date = %s", (subject, time, date))
    data = cur.fetchall()
    mysql.connection.commit()
    if request.method == 'POST':

        return render_template('admin/home.html', data=data)


@app.route("/download", methods=['GET', 'POST'])
def Download():
    subject = request.form['subject']
    time = request.form['time']
    date = request.form['date']
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM attendance_report WHERE subject = %s AND time= %s AND date = %s", (subject, time, date))
    data = cur.fetchall()
    mysql.connection.commit()
    if request.method == 'POST':

        #output in bytes
        output = io.BytesIO()
        # create WorkBook object
        workbook = xlwt.Workbook()
        # add a sheet
        sh = workbook.add_sheet('Student Report')

        # add headers
        sh.write(0, 0, 'Id')
        sh.write(0, 1, 'Roll Number')
        sh.write(0, 2, 'Fullname')
        sh.write(0, 3, 'Subject')
        sh.write(0, 4, 'Time')
        sh.write(0, 5, 'End')
        sh.write(0, 6, 'Date')
        sh.write(0, 7, 'Arrives')
        sh.write(0, 8, 'Status')

        idx = 0
        for row in data:
            sh.write(idx+1, 0, int(row[0]))
            sh.write(idx+1, 1, row[1])
            sh.write(idx+1, 2, row[2])
            sh.write(idx+1, 3, row[3])
            sh.write(idx+1, 4, row[4])
            sh.write(idx+1, 5, row[5])
            sh.write(idx+1, 6, row[6])
            sh.write(idx+1, 7, row[7])
            sh.write(idx+1, 8, row[8])
            idx += 1

        workbook.save(output)
        output.seek(0)

        return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition": "attachment;filename=student_report.xls"})


@app.route("/clearRecord", methods=['GET', 'POST'])
def ClearRecords():
    cur = mysql.connection.cursor()
    cur.execute("TRUNCATE TABLE attendance_report")
    mysql.connection.commit()
    return render_template('admin/home.html')


@app.route("/clearAllData", methods=['GET', 'POST'])
def Reset():
    cur = mysql.connection.cursor()
    cur.execute("TRUNCATE TABLE attendance_report")
    cur.execute("TRUNCATE TABLE eventdisplay")
    cur.execute("TRUNCATE TABLE faculty_register")
    cur.execute("TRUNCATE TABLE userregister")
    mysql.connection.commit()
    return render_template('home.html')


if __name__ == "__main__":

    app.run(debug=True)
