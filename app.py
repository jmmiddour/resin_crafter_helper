from os import getenv
from flask import Flask, render_template, request, session, redirect, flash
from flask_session import Session
from sqlalchemy import text
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from db_model import DB, User, Project, Details
from queries import dup_user, add_user, get_user_id, get_last_ten, \
    add_new_project, dup_proj, get_all, del_rec
from helpers import apology, login_required


# Configure the application
app = Flask(__name__)

# Configure the database uri
uri = getenv('DATABASE_URI')
if uri.startswith('postgres://'):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connect my app to my database
DB.init_app(app)

# Ensure the templates are auto-reloaded
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
# Will store the session on the users disk vs digitially signed cookies,
#   which is done by default with Flask
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Create the index route
@app.route('/')
@login_required
def index():
    # Check to make sure the user is already logged in
    if not session.get("user_id"):
        # If the user is not logged in, redirect them to the login page
        return redirect("/login")

    # Get the user's first name from the database
    first = DB.engine.execute(text(
        'SELECT first_name FROM "user" WHERE id = :user_id'
    ), user_id=session.get("user_id")).one()

    # Get the dataframe with the list of projects for the user
    last_ten_projects = get_last_ten(session.get("user_id"))

    # Show the user the index page
    return render_template('index.html', project=last_ten_projects,
                           user=first[0])


# Create the registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Allows the user to register for an account to login to the application.

    The user fills out a form with:
        - first and last name
        - a user name
        - password
        - email address
    """
    # Forget any user_id
    session.clear()

    # If POST is sent as the request method...
    if request.method == "POST":
        first = request.form.get('first')  # Get user's first name
        last = request.form.get('last')  # Get user's last name
        name = request.form.get('username')  # Get user's username
        password = request.form.get('password')  # Get user's password
        conf_pass = request.form.get('confirmation')  # Confirm matching password
        email_add = request.form.get('email_add')  # Get user's email address

        # If the user does not enter a first name...
        if not first:
            return apology("Need to enter a first name. Please try again!")

        # If the user does not enter a last name...
        if not last:
            return apology("Need to enter a last name. Please try again!")

        # If the user does not enter a username...
        if not name:
            return apology("Need to enter a username. Please try again!")

        # If the user did not enter their password twice...
        if not password or not conf_pass:
            return apology(
                "Need to enter your password twice. Please try again!"
            )

        # If the user does not enter an email address...
        if not email_add:
            return apology("Need to enter an email address. Please try again!")

        # If the user's passwords do not match
        if password != conf_pass:
            return apology("Your passwords do not match. Please try again!")

        # If that username is already in the data base
        if dup_user(name):
            return apology(
                "Username already exists.\nLog in or try another username."
            )

        else:
            # Hash the user's password to store in the database
            hashed_pw = generate_password_hash(password)
            # Add the username and hashed password into the user database table
            add_user(first, last, name, hashed_pw, email_add)

            # Get the row where the username is in the data base
            rows = get_user_id(name)
            print(rows)

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(
                    rows[0]["password"], request.form.get("password")
            ):
                return apology("invalid username and/or password", 403)

            # Remember which user has logged in
            # Stores the users "id" in the Flask session by taking the 1 and only
            #   row in the rows list and grabbing the value from the "id" column
            session["user_id"] = rows[0]['id']

            # Send the user to the portfolio page
            return redirect("/")

    else:  # Otherwise, sent a GET request, need to send to register form
        return render_template('register.html')


# Create login route
@app.route('/login', methods=["GET", "POST"])
def login():
    """
    Log the user into the application
    """
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = DB.engine.execute(text('SELECT * FROM "user" WHERE username = :name'),
                                 name=request.form.get("username")).all()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]['password'], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        # Stores the users "id" in the Flask session by taking the 1 and only
        #   row in the rows list and grabbing the value from the "id" column
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect('/')

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template('login.html')


# Create a route for the user to logout
@app.route('/logout')
def logout():
    """
    Log user out of the application
    """
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect('/')


# Create route for adding a project
@app.route('/add', methods=["GET", "POST"])
@login_required
def add():
    """
    Functionality for the user to add a new project to their account
    """
    # Check to make sure the user is already logged in
    if not session.get("user_id"):
        # If not logged in, redirect the user to the login page
        return redirect("/login")

    if request.method == "POST":
        # Create a dictionary to hold all parameters needed
        proj_dict = {
            'user_id': None, 'name': 'name',
            'mold_img': 'mold_img', 'res_img': 'res_img',
            'resin_brand': 'resin_brand', 'resin_type': 'resin_type',
            'amt': 'amount', 'unit': 'unit', 'colors': 'color',
            'color_amts': 'color_amt', 'color_types': 'color_type',
            'glitters': 'glitter', 'glitter_amts': 'glitter_amt',
            'time_to_pour_mins': 'time_to_pour',
            'notes': 'notes', 'pouring_time_mins': 'pouring_time',
            'time_to_demold_hrs': 'demolding_time',
            'result_scale': 'res_scale', 'start_rm_temp_f': 'start_rm_temp',
            'end_rm_temp_f': 'end_rm_temp'
        }

        # Get the users id number
        user_id = session.get("user_id")

        # If project name is already in the data base
        if dup_proj(request.form.get('name'), user_id):
            return apology(
                "You have already used\nthat project name.\n\nPlease try another name."
            )

        else:
            # Iterate through the dictionary of project parameters
            for key, val in proj_dict.items():
                # Get the values from the form if they are not empty
                if request.form.get(val) is not None:
                    new_val = request.form.get(val)
                    proj_dict[key] = new_val

                else:
                    proj_dict[key] = None

            # Set the user_id parameter in the dictionary
            proj_dict['user_id'] = user_id
            # Add the new project to the database using function from queries.py
            add_new_project(proj_dict)

            # Display a message on the home page to let the user know their
            #   project was successfully added to the database
            flash('Your project has been added successfully!')
            # Redirect user to the home page
            return redirect('/')

    # If the request method is 'GET' show the form to add a project
    return render_template('add.html')


# Create a route for removing a project
@app.route('/remove', methods=["GET", "POST"])
@login_required
def remove():
    """
    Functionality for the user to remove a project from their account
    """
    # Check to make sure the user is already logged in
    if not session.get("user_id"):
        # If not logged in, redirect the user to the login page
        return redirect("/login")

    # Query a list of all projects on the user's account
    projects = get_all(session.get("user_id"))

    # Get a list of all project names
    user_projects = [i[1] for i in projects]

    # Remove the project user selects
    if request.method == "POST":
        del_rec(request.form.get('name'), session.get('user_id'))
        flash(f'Project "{request.form.get("name")}" has been successfully removed!')
        return redirect('/')

    return render_template('remove.html', names=user_projects)


# Create a route for editing a project
@app.route('/edit')
@login_required
def edit():
    """
    Functionality for user to edit a project already in their account
    """
    # Check to make sure the user is already logged in
    if not session.get("user_id"):
        # If not logged in, redirect the user to the login page
        return redirect("/login")

    return render_template('edit.html')


# Create a route for displaying all projects
@app.route('/all_projects')
@login_required
def all_projects():
    """
    Functionality to view all the projects currently in the user's account
    """
    # Check to make sure the user is already logged in
    if not session.get("user_id"):
        # If not logged in, redirect the user to the login page
        return redirect("/login")

    # Get user's first name
    first = DB.engine.execute(text(
        'SELECT first_name FROM "user" WHERE id = :user_id'
    ), user_id=session.get("user_id")).one()

    # Query a list of all projects on the user's account
    projects = get_all(session.get("user_id"))

    # Create a list of all column names to display
    cols = ['Project Name', 'Link to Mold Image', 'Brand of Resin',
            'Type of Resin', 'Amount of Resin', 'Measurement Unit', 'Color(s)',
            'Amount of Color(s)', 'Type of Color(s)', 'Glitter(s)',
            'Amount of Glitter(s)', 'Time Until Pour in Minutes',
            'Pouring Time in Minutes', 'Hours until De-molding',
            'Starting Room Temp in Fahrenheit',
            'Ending Room Temp in Fahrenheit', 'Result Scale',
            'Link to Result Image', 'Additional Notes']

    return render_template('all_projects.html', project=projects,
                           cols=cols, user=first[0])


# Create route for display just one project
@app.route('/display')
@login_required
def display():
    """
    Functionality to display just one project in the users account
    """
    # Check to make sure the user is already logged in
    if not session.get("user_id"):
        # If not logged in, redirect the user to the login page
        return redirect("/login")

    return render_template('project.html')


# Create a route for editing account information
@app.route('/edit_act')
@login_required
def edit_act():
    """
    Functionality for user to edit their account details
    """
    # Check to make sure the user is already logged in
    if not session.get("user_id"):
        # If not logged in, redirect the user to the login page
        return redirect("/login")

    return render_template('edit_act.html')


# Create a route to create the database
@app.route('/rch_create_db_jmm')
def create_db():
    """
    Backdoor to create the database
    :return:
    """
    if not User().username:
        # Create the database
        DB.create_all()
        DB.session.commit()  # Commit the changes
        DB.session.close()  # Close the database connection

    # Redirect to home page
    return redirect('/')


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == '__main__':
    app.run(debug=True)