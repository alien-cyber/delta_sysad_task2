
import psycopg2
from flask import Flask, render_template, request, session, url_for, redirect

app = Flask(__name__)
app.secret_key = '123456789'  

def get_db():
    conn = psycopg2.connect(
        host='db',
        database='postgres',
        user='postgres',
        password='postgres'
    )
    return conn

def close_db(conn, cur):
    cur.close()
    conn.close()

def exist_password(cur, user_type, rollno=None):
    if user_type == 'core':
        cur.execute('SELECT * FROM mentors WHERE username = %s', (user_type,))
        row = cur.fetchone()
        return row[5] is not None
    elif user_type == 'mentee':
        cur.execute('SELECT * FROM mentee_domain WHERE rollno = %s', (rollno,))
        row = cur.fetchone()
        return row[4] is not None
    elif user_type == 'mentor':
        cur.execute('SELECT * FROM mentors WHERE rollno = %s', (rollno,))
        row = cur.fetchone()
        return row[5] is not None
    return False

def get_info(cur, user_type, rollno=None):
    mentors, mentees, forms = [], [], []
    if user_type == 'core':
        cur.execute('SELECT * FROM mentors WHERE id != 1')
        mentors = cur.fetchall()
        cur.execute('SELECT * FROM mentee_domain')
        mentees = cur.fetchall()
        cur.execute('SELECT * FROM urls')
        forms = cur.fetchall()
    elif user_type == 'mentor':
        cur.execute('SELECT * FROM mentee_domain WHERE mentor_rollno = %s', (rollno,))
        mentees = cur.fetchall()
        cur.execute('SELECT * FROM urls')
        forms = cur.fetchall()
    else:
        cur.execute('SELECT * FROM urls WHERE rollno = %s', (rollno,))
        forms = cur.fetchall()
    return mentors, mentees, forms

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login/<user_type>', methods=('GET', 'POST'))
def create(user_type):
    session['user_type'] = user_type
    conn = get_db()
    cur = conn.cursor()

    msg = 'Enter roll No'
    if user_type == 'core':
        msg = 'CORE Login' if exist_password(cur, user_type=user_type) else 'CREATE PASSWORD this is only one time entry, remember it'
        close_db(conn, cur)
        return redirect(url_for('login', user_type=user_type, msg=msg))

    if request.method == 'POST':
        rollno = request.form['rollno']
        if user_type == 'mentor':
            cur.execute('SELECT * FROM mentors WHERE rollno = %s', (rollno,))
        else:  # mentee
            cur.execute('SELECT * FROM mentee_domain WHERE rollno = %s', (rollno,))
        
        row = cur.fetchone()
        if not row:
            msg = 'Incorrect rollno'
        else:
            msg = 'Enter password'
            session["rollno"] = rollno
            close_db(conn, cur)
            return redirect(url_for('login', user_type=user_type, msg=msg))

    close_db(conn, cur)
    return render_template('rollno_page.html', user_type=user_type, msg=msg)

@app.route('/login', methods=('GET', 'POST'))
def login():
    user_type = session['user_type']
    rollno = session.get('rollno')
    conn = get_db()
    cur = conn.cursor()

    msg = request.args.get('msg', 'Enter password')
    if user_type == 'core':
        msg = 'CORE Login' if exist_password(cur, user_type=user_type) else 'CREATE PASSWORD this is only one time entry, remember it'
        if request.method == 'POST':
            password = request.form['password']
            if not exist_password(cur, user_type=user_type):
                cur.execute('UPDATE mentors SET password = %s WHERE username = %s', (password, user_type))
                conn.commit()
            else:
                cur.execute('SELECT * FROM mentors WHERE username = %s', (user_type,))
                row = cur.fetchone()
                if row[5] != password:
                    msg = 'Password incorrect'
                    close_db(conn, cur)
                    return render_template('password_page.html', user_type=user_type, msg=msg)
            cur.execute('SELECT * FROM mentee_domain WHERE domain IS NULL')
            null_rows = cur.fetchall()
            msg = 'Assign mentors to mentees' if not null_rows else 'This mentees did not give domain preferences'
            
            close_db(conn, cur)
           

            
            return redirect(url_for('dashboard'))

    elif user_type in ['mentor', 'mentee']:
        if not exist_password(cur, user_type=user_type, rollno=rollno):
            msg = 'CREATE PASSWORD this is only one time entry, remember it'
        if request.method == 'POST':
            password = request.form['password']
            if not exist_password(cur, user_type=user_type, rollno=rollno):
                if user_type == 'mentor':
                    cur.execute('UPDATE mentors SET password = %s WHERE rollno = %s', (password, rollno))
                else:
                    cur.execute('UPDATE mentee_domain SET password = %s WHERE rollno = %s', (password, rollno))
                conn.commit()
            else:
                if user_type == 'mentor':
                    cur.execute('SELECT * FROM mentors WHERE rollno = %s', (rollno,))
                    row = cur.fetchone()
                    if row[5] != password:
                        msg = 'Password incorrect'
                        close_db(conn, cur)
                        return render_template('password_page.html', user_type=user_type, msg=msg)

                else:
                    cur.execute('SELECT * FROM mentee_domain WHERE rollno = %s', (rollno,))
                    
                    row = cur.fetchone()
                    
                    if row[4] != password:
                        msg = 'Password incorrect'
                        close_db(conn, cur)
                        return render_template('password_page.html', user_type=user_type, msg=msg)


            close_db(conn, cur)
            return redirect(url_for('dashboard'))

    close_db(conn, cur)
    return render_template('password_page.html', user_type=user_type, msg=msg)

@app.route('/dashboard', methods=('GET', 'POST'))
def dashboard():
    user_type = session['user_type']
    rollno = session.get('rollno')
    conn = get_db()
    cur = conn.cursor()
    if user_type == 'core':
        mentors,mentees,forms=get_info(cur,user_type=user_type)
        cur.execute('SELECT * FROM mentors WHERE username=%s',(user_type,))
        current_user=cur.fetchone()
        cur.execute('SELECT * FROM mentee_domain WHERE domain IS NULL')
        null_rows = cur.fetchall()
       
        if null_rows:
            msg="these mentees didnt give domain preferences,SO cant allocate mentors to mentees yet"
            
        else:
            msg="View mentors and mentees"
            cur.execute('SELECT * FROM mentee_domain WHERE mentor_rollno IS NULL')
            rows=cur.fetchall()
            null_rows=[]
            
            if rows:
                msg="allocate mentors to mentees"
                null_rows=["allocate"]
            
                
    elif user_type =="mentor":
        mentors,mentees,forms=get_info(cur,user_type=user_type,rollno=rollno)
        cur.execute('SELECT * FROM mentors WHERE rollno=%s',(rollno,))
        current_user=cur.fetchone()
        cur.execute('SELECT * FROM mentors WHERE rollno=%s',(rollno,))
        row=cur.fetchone()
        if row[6]:
            msg="view mentees"
            null_rows=[]
        else:
            msg="core has not allocated mentees to you yet"
            null_rows=["somthing"]
    else:
        mentors,mentees,forms=get_info(cur,user_type=user_type,rollno=rollno)
        cur.execute('SELECT * FROM mentee_domain WHERE rollno=%s',(rollno,))
        current_user=cur.fetchone()
        cur.execute('SELECT * FROM urls WHERE rollno=%s',(rollno,))
        row=cur.fetchone()
        if row:
            msg="submit task"
            null_rows=["something"]
        else:
            msg="choose domain"
            null_rows=[]
    
    close_db(conn, cur)
    return render_template('dashboard.html',role=user_type, current_user=current_user,null_rows=null_rows, mentors=mentors, mentees=mentees, forms=forms,msg=msg)

@app.route('/submit_domain', methods=['POST'])
def submit_domain():
    rollno = session.get('rollno')
    conn = get_db()
    cur = conn.cursor()
    
    selected_domains = request.form.getlist('domain')
    domains=''
    for domain in selected_domains:
        if domain=='w':
            domains+='web,'
            cur.execute("INSERT INTO urls (domain,rollno) VALUES (%s, %s)",('web', rollno))
        elif domain=='s':
            domains+='sysad,'
            cur.execute("INSERT INTO urls (domain,rollno) VALUES (%s, %s)",('sysad', rollno))
        else:
            domains+='app,'
            cur.execute("INSERT INTO urls (domain,rollno) VALUES (%s, %s)",('app', rollno))
    conn.commit() 
    cur.execute('UPDATE mentee_domain SET domain = %s WHERE rollno = %s', (domains, rollno))
    conn.commit()
    
    
    
    close_db(conn, cur)
    return redirect(url_for('dashboard'))
    
@app.route('/submit_url', methods=['POST'])
def submit_url():
    rollno = session.get('rollno')
    conn = get_db()
    cur = conn.cursor()
    domains= request.form.to_dict()
    for domain, url in domains.items():
      if url:
          cur.execute('''DELETE FROM urls
WHERE rollno=%s AND domain=%s;''',(rollno,domain)
)
          cur.execute(
    """
    INSERT INTO urls (domain, rollno, url) 
    VALUES (%s, %s, %s) ;
    """,
    (domain, rollno, url)
)
   
      
    conn.commit() 
    close_db(conn, cur)
    return redirect(url_for('dashboard'))
@app.route('/allocate_mentor', methods=['POST'])
def allocate_mentor():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM mentors WHERE rollno is not NULL')
    mentors=cur.fetchall()
    web=[]
    sysad=[]
    app=[]
    for mentor in mentors:
        first=mentor[3][0]
        if first in ['W','w']:
            web.append(mentor)
        elif first in ['s','S']:
            sysad.append(mentor)
        else:
            app.append(mentor)
    cur.execute('SELECT * FROM mentee_domain ')
    mentees=cur.fetchall()
    capacity_w=web[0][4]
    capacity_s=sysad[0][4]
    capacity_a=web[0][4]
    for mentee in mentees:
        mentee_domains=mentee[3]
        mentee_domains = mentee_domains.split(',')
        for domain in mentee_domains:
            if domain:
                if domain[0] in ['w','W']:
                    if capacity_w>0:
                        mentor_rollno=web[0][2]
                        capacity_w -= 1
                    else:
                        web.pop(0)
                        capacity_w=web[0][4]
                        mentor_rollno=web[0][2]
                        capacity_w -= 1
                elif domain[0] in ['s','S']:
                    if capacity_s>0:
                        mentor_rollno=sysad[0][2]
                        capacity_s -= 1
                    else:
                        sysad.pop(0)
                        capacity_w=sysad[0][4]
                        mentor_rollno=sysad[0][2]
                        capacity_s -= 1
                else:
                    if capacity_a>0:
                        mentor_rollno=app[0][2]
                        capacity_a -= 1
                    else:
                        app.pop(0)
                        capacity_w=app[0][4]
                        mentor_rollno=app[0][2]
                        capacity_a -= 1


                cur.execute('UPDATE mentee_domain SET mentor_rollno = %s WHERE rollno= %s', (mentor_rollno,mentee[2]))
                cur.execute('UPDATE mentors SET assigned = %s WHERE rollno= %s', ('yes',mentor_rollno))
    
    conn.commit()
    close_db(conn, cur)
    return redirect(url_for('dashboard'))          



if __name__ == '__main__':
    app.run(debug=True)
