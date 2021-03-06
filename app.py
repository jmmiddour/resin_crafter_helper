from os import getenv
from flask import Flask, render_template, request, session, redirect, flash
from flask_session import Session
from sqlalchemy import text
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from base64 import b64encode

from db_model import DB, User
from queries import dup_user, add_user, get_user, get_last_ten, \
    add_new_project, dup_proj, get_all, del_rec, get_single, edit_project, \
    user_details, edit_user
from helpers import apology, login_required


# Configure the application
app = Flask(__name__)

# Ensure the templates are auto-reloaded
app.config['TEMPLATES_AUTO_RELOAD'] = True

"""
Configure the database uri
"""
uri = getenv('DATABASE_URI')

if uri.startswith('postgres://'):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connect my app to my database
DB.init_app(app)


# Ensure responses aren't cached after a specified time
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 1000
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
# Will store the session on the users disk vs digitally signed cookies,
#   which is done by default with Flask
app.config.from_object(__name__)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Create the index route
@app.route('/')
# @login_required  # Decorator to ensure user is logged in
def index():
    """
    The main route and the first thing that all users see
    """
    # Show the user the welcome page
    return render_template('index.html')


# Create the home route
@app.route('/home')
@login_required  # Decorator to ensure user is logged in
def home():
    """
    The main route and the first thing that all users see
    """
    # Get the user's first name from the database
    first = DB.engine.execute(text(
        'SELECT first FROM "user" WHERE id = :user_id'
    ), user_id=session.get("user_id")).one()

    # Get a list of the last ten projects added by the user
    last_ten_projects = get_last_ten(session.get("user_id"))

    # Show the user their home page
    return render_template('home.html', project=last_ten_projects,
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
            rows = get_user(name)
            # rows = user_details(user_id)

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(
                    rows[0]['password'], request.form.get("password")
            ):
                return apology("invalid username and/or password", 403)

            # Remember which user has logged in
            # Stores the users "id" in the Flask session by taking the 1 and only
            #   row in the rows list and grabbing the value from the "id" column
            session["user_id"] = rows[0]['id']

            # Display a message on the home page to let the user know their
            #   project was successfully added to the database
            flash(
                f'Your registration is complete and you have been logged in successfully!'
            )
            # Send the user to the portfolio page
            return redirect("/home")

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
        row = get_user(request.form.get("username"))

        # Ensure username exists and password is correct
        if len(row) != 1 or not check_password_hash(row[0]['password'], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        # Stores the users "id" in the Flask session by taking the 1 and only
        #   row in the rows list and grabbing the value from the "id" column
        session["user_id"] = row[0]["id"]

        # Display a message on the home page to let the user know their
        #   project was successfully added to the database
        flash(f'You have been logged in successfully!')
        # Redirect user to home page
        return redirect('/home')

    # User reached route via GET (as by clicking a link or via redirect)
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


# Create a route for editing account information
@app.route('/edit_act', methods=["GET", "POST"])
@login_required  # Decorator to ensure user is logged in
def edit_act():
    """
    Functionality for user to edit their account details
    """
    # # Check to make sure the user is already logged in
    # check_valid_login()

    # Create a dictionary to hold all parameters needed
    user_dict = {
        'id': None, 'first': None, 'last': None, 'username': None,
        'password': None, 'email': None
    }

    # Grab the user information from the database
    user = user_details(session.get("user_id"))

    # Iterate through the dictionary to add the values from the database for
    #   the project specified
    i = 0  # Create a counter to increment
    for k, _ in user_dict.items():
        # Change the value in the dictionary to the value at the current location
        user_dict[k] = user[i]
        i += 1  # Increment the index location value by 1

    if request.method == "POST":
        # Iterate through the dictionary of project parameters
        for key, val in user_dict.items():
            if key != 'id' and key != 'username':
                if key == 'password':
                    # Get user's new password
                    password = request.form.get('password')
                    # Confirm matching new password
                    conf_pass = request.form.get('confirmation')

                    # If the user's passwords do not match
                    if password != conf_pass:
                        return apology("Your passwords do not match. Please try again!")

                    # Hash the user's password to store in the database
                    hashed_pw = generate_password_hash(password)

                    # Add new hashed password to user dictionary
                    user_dict['password'] = hashed_pw

                # Get the values from the form if they are different
                elif request.form.get(key) != user_dict[key]:
                    user_dict[key] = request.form.get(key)

                # Otherwise, continue iterating and change nothing
                user_dict[key] = user_dict[key]

        # Add the new project to the database using function from queries.py
        edit_user(user_dict)

        # Display a message on the home page to let the user know their
        #   project was successfully added to the database
        flash(f'Your account has been edited successfully!')
        # Redirect user to the home page
        return redirect('/')

    return render_template('edit_act.html', user=user_dict)


# Create route for adding a project
@app.route('/add', methods=["GET", "POST"])
@login_required  # Decorator to ensure user is logged in
def add():
    """
    Functionality for the user to add a new project to their account
    """
    # # Check to make sure the user is already logged in
    # check_valid_login()

    if request.method == "POST":
        # Create a dictionary to hold all parameters needed
        proj_dict = {
            'user_id': None, 'name': 'name', 'mold_img': '',
            'resin_brand': 'resin_brand', 'resin_type': 'resin_type',
            'amt': 'amount', 'unit': 'unit', 'colors': 'color',
            'color_amts': 'color_amt', 'color_types': 'color_types',
            'glitters': 'glitter', 'glitter_amts': 'glitter_amt',
            'glitter_types': 'glitter_types',
            'time_to_pour_hrs': 'time_to_pour_hrs',
            'time_to_pour_mins': 'time_to_pour_mins',
            'pouring_time_hrs': 'pouring_time_hrs',
            'pouring_time_mins': 'pouring_time_mins',
            'time_to_demold_hrs': 'demolding_time_hrs',
            'time_to_demold_mins': 'demolding_time_mins',
            'start_temp': 'start_temp', 'start_temp_unit': 'start_temp_unit',
            'end_temp': 'end_temp', 'end_temp_unit': 'end_temp_unit',
            'demold_temp': 'demold_temp', 'demold_temp_unit': 'demold_temp_unit',
            'result_scale': 'res_scale', 'res_img': '', 'notes': 'notes',
            'mold_img_type': '', 'res_img_type': ''
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
                if (key == 'amt') or (key == 'time_to_pour_hrs'
                ) or (key == 'time_to_pour_mins') or (key == 'pouring_time_hrs'
                ) or (key == 'pouring_time_mins') or (key == 'time_to_demold_hrs'
                ) or (key == 'time_to_demold_mins') or (key == 'start_temp'
                ) or (key == 'end_temp') or (key == 'demold_temp'):
                    if request.form.get(val):
                        proj_dict[key] = int(request.form.get(val))

                    else:
                        proj_dict[key] = 0

                # Get the values from the form if they are not empty
                elif request.form.get(val) and (
                        key != 'mold_img' or key != 'mold_img_type' or
                        key != 'res_img' or key != 'res_img_type'):
                    proj_dict[key] = request.form.get(val)

                else:
                    proj_dict[key] = None

            # Check if the key is the mold_img,
            #   because it needs to be added differently
            mold_pic = request.files['mold_img']
            if mold_pic.filename:
                proj_dict['mold_img'] = b64encode(mold_pic.read()).decode('utf-8')
                proj_dict['mold_img_type'] = mold_pic.mimetype.split('/')[1]

            # Check if the key is the result_img,
            #   because it needs to be added differently
            res_pic = request.files['res_img']
            if res_pic.filename:
                proj_dict['res_img'] = b64encode(res_pic.read()).decode('utf-8')
                proj_dict['res_img_type'] = res_pic.mimetype.split('/')[1]

            # Set the user_id parameter in the dictionary
            proj_dict['user_id'] = user_id
            # Add the new project to the database using function from queries.py
            add_new_project(proj_dict)

            # Display a message on the home page to let the user know their
            #   project was successfully added to the database
            flash(f'Your project "{request.form.get("name")}" has been added successfully!')
            # Redirect user to the home page
            return redirect('/')

    # If the request method is 'GET' show the form to add a project
    return render_template('add.html')


# Create a route for removing a project
@app.route('/remove', methods=["GET", "POST"])
@login_required  # Decorator to ensure user is logged in
def remove():
    """
    Functionality for the user to remove a project from their account
    """
    # # Check to make sure the user is already logged in
    # check_valid_login()

    # Query a list of all projects on the user's account
    projects = get_all(session.get("user_id"))

    # Get a list of all project names
    user_projects = [row[1] for row in projects]

    # Remove the project user selects
    if request.method == "POST":
        del_rec(request.form.get('name'), session.get('user_id'))
        flash(f'Project "{request.form.get("name")}" has been successfully removed!')
        return redirect('/')

    return render_template('remove.html', names=user_projects)


# Create a route for picking a project for editing
@app.route('/pick_edit', methods=["GET", "POST"])
@login_required  # Decorator to ensure user is logged in
def pick_edit():
    """
    Functionality for user to pick which project they want to edit that is
        already in their account.
    """
    # # Check to make sure the user is already logged in
    # check_valid_login()

    # Create a list of project names for dropdown selection
    projects = get_all(session.get("user_id"))
    user_projects = [row[1] for row in projects]

    if request.method == "POST":
        # Redirect user to the edit page
        return redirect(f'/edit/{request.form.get("project")}')

    # If the request method is 'GET' show the form to add a project
    return render_template('pick_edit.html', names=user_projects)


# Create a route for editing a project
@app.route('/edit/<project>', methods=["GET", "POST"])
@login_required  # Decorator to ensure user is logged in
def edit(project):
    """
    Functionality for user to edit a project already in their account
    """
    # # Check to make sure the user is already logged in
    # check_valid_login()

    # Create a dictionary to hold all parameters needed
    proj_dict = {
        'id': None, 'name': None, 'mold_img': None, 'mold_img_type': None,
        'result_img': None, 'result_img_type': None, 'notes': None,
        'user_id': None, 'project_id': None, 'resin_brand': None,
        'resin_type': None, 'amount': None, 'unit': None,
        'colors': None, 'color_amts': None, 'color_types': None,
        'glitters': None, 'glitter_amts': None, 'glitter_types': None,
        'time_to_pour_hrs': None, 'time_to_pour_mins': None,
        'pouring_time_hrs': None, 'pouring_time_mins': None,
        'time_to_demold_hrs': None, 'time_to_demold_mins': None,
        'result_scale': None, 'start_temp': None, 'start_temp_unit': None,
        'end_temp': None, 'end_temp_unit': None, 'demold_temp': None,
        'demold_temp_unit': None
    }

    # Grab the project id from the database for the project name given
    projects = get_all(session.get("user_id"))
    project_id = [row[:1] for row in projects if project in row[1]]

    # Get the details for the project name given
    project_details = get_single(project_id[0])

    # Iterate through the dictionary to add the values from the database for
    #   the project specified
    i = 0  # Create a counter to increment
    for k, _ in proj_dict.items():
        # Change the value in the dictionary to the value at the current location
        proj_dict[k] = project_details[i]
        i += 1  # Increment the index location value by 1

    if request.method == "POST":
        # Iterate through the dictionary of project parameters
        for key, val in proj_dict.items():
            if key != 'id' and key != 'name' and key != 'user_id' and key != 'project_id':
                # Check if the key is the mold_img,
                #   because it needs to be handled differently
                if key == 'mold_img':
                    mold_pic = b64encode(
                        request.files['mold_img'].read()).decode('utf-8')

                    if mold_pic != proj_dict[key] and mold_pic:
                        proj_dict[key] = mold_pic

                # Check if the key is the result_img,
                #   because it needs to be added differently
                elif key == 'result_img':
                    res_pic = b64encode(
                        request.files['result_img'].read()).decode('utf-8')

                    if res_pic != proj_dict[key] and res_pic:
                        proj_dict[key] = res_pic

                # Get the values from the form if they are different
                elif request.form.get(key) != proj_dict[key]:
                    new_val = request.form.get(key)
                    proj_dict[key] = new_val

                else:  # Otherwise, continue iterating and change nothing
                    proj_dict[key] = proj_dict[key]

        # Add the new project to the database using function from queries.py
        edit_project(proj_dict)

        # Display a message on the home page to let the user know their
        #   project was successfully added to the database
        flash(f'Your project "{project}" has been edited successfully!')
        # Redirect user to the home page
        return redirect('/')

    # If the request method is 'GET' show the form to add a project
    return render_template('edit.html', name=project, details=proj_dict)


# Create a route for displaying all projects
@app.route('/all_projects')
@login_required  # Decorator to ensure user is logged in
def all_projects():
    """
    Functionality to view all the projects currently in the user's account
    """
    # # Check to make sure the user is already logged in
    # check_valid_login()

    # Get user's first name
    first = DB.engine.execute(text(
        'SELECT first FROM "user" WHERE id = :user_id'
    ), user_id=session.get("user_id")).one()

    # Query a list of all projects on the user's account
    projects = get_all(session.get("user_id"))

    # Create a list of all column names to display
    cols = ['Project Name', 'Mold Image', 'Brand of Resin',
            'Type of Resin', 'Amount of Resin', 'Color(s)',
            'Amount of Color(s)', 'Type of Color(s)', 'Glitter(s)',
            'Amount of Glitter(s)', 'Type of Glitter(s)',
            'Time Until Pour (HH:MM)', 'Pouring Time (HH:MM)',
            'Time until De-molding (HH:MM)', 'Starting Room Temp',
            'Ending Room Temp', 'De-molding Room Temp', 'Result Scale',
            'Result Image', 'Additional Notes']

    mold_type = [row['mold_img_type'] for row in projects]
    res_type = [row['result_img_type'] for row in projects]

    return render_template('all_projects.html', project=projects,
                           cols=cols, user=first[0],
                           mold_type=mold_type,
                           res_type=res_type)


# Create route to select just one project
@app.route('/select', methods=["GET", "POST"])
@login_required  # Decorator to ensure user is logged in
def select():
    """
    Functionality to display just one project in the users account
    """
    # # Check to make sure the user is already logged in
    # check_valid_login()

    # Create a list of project names for dropdown selection
    projects = get_all(session.get("user_id"))
    user_projects = [row[1] for row in projects]

    if request.method == "POST":
        # Redirect user to the edit page
        return redirect(f'/display/{request.form.get("project")}')

    # If the request method is 'GET' show the form to add a project
    return render_template('select.html', names=user_projects)


# Create route for display just one project
@app.route('/display/<project>', methods=["GET", "POST"])
@login_required  # Decorator to ensure user is logged in
def display(project):
    """
    Functionality to display just one project in the users account
    """
    # # Check to make sure the user is already logged in
    # check_valid_login()

    # Create a dictionary to hold all parameters needed
    proj_dict = {
        'id': None, 'name': None, 'mold_img': None, 'mold_img_type': None,
        'result_img': None, 'result_img_type': None, 'notes': None,
        'user_id': None, 'project_id': None, 'resin_brand': None,
        'resin_type': None, 'amount': None, 'unit': None,
        'colors': None, 'color_amts': None, 'color_types': None,
        'glitters': None, 'glitter_amts': None, 'glitter_types': None,
        'time_to_pour_hrs': None, 'time_to_pour_mins': None,
        'pouring_time_hrs': None, 'pouring_time_mins': None,
        'time_to_demold_hrs': None, 'time_to_demold_mins': None,
        'result_scale': None, 'start_temp': None, 'start_temp_unit': None,
        'end_temp': None, 'end_temp_unit': None, 'demold_temp': None,
        'demold_temp_unit': None
    }

    # Grab the project id from the database for the project name given
    projects = get_all(session.get("user_id"))
    project_id = [row[0] for row in projects if project in row[1]]

    # Get the details for the project name given
    project_details = get_single(project_id[0])

    # Iterate through the dictionary to add the values from the database for
    #   the project specified
    i = 0  # Create a counter to increment
    for k, _ in proj_dict.items():
        # Change the value in the dictionary to the value at the current location
        proj_dict[k] = project_details[i]
        i += 1  # Increment the index location value by 1

    return render_template('display.html', project=proj_dict)


# Create a route to create the database
@app.route('/rch_create_db_jmm', methods=['GET', 'POST'])
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

    # Display a message on the home page
    flash(f'The database has been created successfully!')
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
