from flask import *
from flask_bootstrap import *
from flask_mysqldb import *
import os
from werkzeug.security import *
from flask_ckeditor import*

app = Flask(__name__)
Bootstrap(app)
CKEditor(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '050724'
app.config['MYSQL_DB'] = 'blog_db'
app.config['MYSQL_CURSORCLASS'] ='DictCursor'
app.config['SECRET_KEY'] = os.urandom(24)

mysql = MySQL(app)



@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    result = cursor.execute("SELECT * FROM blog")
    if result > 0 :
        blogs = cursor.fetchall()
        cursor.close()
        return render_template('index.html', blogs = blogs)
    return render_template('index.html' , blogs = None)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/blogs/<int:id>')
def blogs(id):
    cursor = mysql.connection.cursor()
    result = cursor.execute("SELECT * FROM blog WHERE id = {}".format(id))
    if result > 0:
        blog = cursor.fetchone()
        print(blog)
        return render_template('blogs.html',  blog = blog )
    return "Blogs Not Found"


@app.route('/register', methods=["GET", "POST"])
def register(): 
    if request.method == "POST":
        user_details = request.form
        firstname = user_details["firstname"]
        lastname = user_details["lastname"]
        username = user_details["username"]
        email = user_details["email"]
        password = user_details["password"]
        confirmPassword = user_details["confirmPassword"]
        if password != confirmPassword:
            flash("Your password can not match!",'danger')
            return render_template('register.html')
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO user(first_name,last_name,nickname,email,password) VALUES(%s, %s, %s, %s, %s)",(firstname,lastname,username,email,generate_password_hash(password)))
        mysql.connection.commit()
        cursor.close()
        flash('Registration was succesfully! Please login!', 'success' ) 
        return redirect('/login/')
        
    return render_template('register.html')


@app.route('/login/', methods=["GET", "POST"])
def login():
    if request.method =="POST":
        user_details = request.form
        username = user_details['username']
        # password = user_details['password']  
        cursor = mysql.connection.cursor()
        res = cursor.execute("select * from user where nickname = %s",([username]))
        if res > 0:
            user = cursor.fetchone()
            if check_password_hash(user['password'],user_details['password']):
                session['login'] = True
                session['first_name'] = user['first_name']
                session['last_name'] = user['last_name']
                flash('Welcome  ' + session['first_name'] + '  You have successfully login  ' , 'success' ) 
            else:
                cursor.close
                flash('Your password was wrong. Try again', 'danger' )    
                return render_template('login.html')
        else:
            cursor.close()
            flash("user does not exists",'danger')
            return render_template('login.html')
        cursor.close()
        return redirect('/')

    return render_template('login.html')

@app.route('/write-blog', methods=["GET", "POST"])
def write_blog():
    if request.method == "POST":
        print("YES")
        blogpost = request.form
        title = blogpost['title']
        body = blogpost['body']
        author = session['first_name']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO blog(title,body,author) VALUES(%s, %s, %s)",(title,body,author))
        print("YES")
        mysql.connection.commit()
        cursor.close()
        flash("Your blog succesfully posted", "success") 
        return redirect('/') 
    return render_template('write-blog.html')


@app.route('/my-blogs/')
def my_blogs():
    author = session['first_name']
    cursor = mysql.connection.cursor()
    result = cursor.execute("SELECT * FROM blog WHERE author = %s",([author]))
    if result > 0:
        my_blogs = cursor.fetchall()
        return render_template('my-blogs.html', my_blogs = my_blogs)
    
    return render_template('my-blogs.html',my_blogs = None)


@app.route('/edit-blog/<int:id>', methods=["GET", "POST "])
def edit_blog(id):
    return render_template('edit-blog.html', blog_id=id)


@app.route('/delete-blog/<int:id>', methods=["POST"])
def delete_blog(id):
    return "Successfully deleted"


@app.route('/logout/')
def logout():
    session.clear()
    flash("You have been logged out","info")
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
