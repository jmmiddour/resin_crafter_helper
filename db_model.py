
from flask_sqlalchemy import SQLAlchemy

# from .app import app

# Initialize the SQLAlchemy
DB = SQLAlchemy()


# Create table class for the user data
class User(DB.Model):
    """
    user table column definitions:

        - *id*: auto populated id for each user registered through app
        - *first_name*: the first name the user entered when registering
        - *last_name*: the last name the user entered when registering
        - *username*: name the user entered when registering as their username for login
        - *password*: the hashed password the user entered
        - *email*: the users registered email address for forgotten username/password
    """
    id = DB.Column(DB.Integer(), primary_key=True)
    first_name = DB.Column(DB.String(80), nullable=False)
    last_name = DB.Column(DB.String(80), nullable=False)
    username = DB.Column(DB.String(80), unique=True, nullable=False)
    password = DB.Column(DB.String(), unique=True, nullable=False)
    email = DB.Column(DB.String(300), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.first_name


# Create table class for project data
class Project(DB.Model):
    """
    project table column definitions:

        - *id*: auto populated for each new project created
        - *name*: name the user entered for the project
        - *mold_img*: link to user's image of mold used for project
        - *result_img*: link to user's image of the resulting project
        - *notes*: any additional notes user entered
        - *user_id*: many-to-one relationship to the user table - links to the user who created the project
    """
    id = DB.Column(DB.Integer(), primary_key=True)
    name = DB.Column(DB.String(), nullable=False)
    mold_img = DB.Column(DB.String())
    result_img = DB.Column(DB.String())
    notes = DB.Column(DB.String())
    user_id = DB.Column(DB.Integer(), DB.ForeignKey('user.id'), nullable=False)
    user = DB.relationship('User', backref=DB.backref('project', lazy=True))

    def __repr__(self):
        return '<Project %r>' % self.name


# Create a table class for project detail data
class Details(DB.Model):
    """
    details table column definitions:

        - *project_id*: one-to-one relationship to the project table - links to the rest of the details of the project
        - *resin_brand*: the brand of resin the user used for the project
        - *resin_type*: the type of resin the user used for the project
        - *amount*: the amount of resin the user needed for the project
        - *unit*: the unit of measurement the user used to measure the amount of resin
        - *colors*: list of the colors the user used for the project
        - *color_amts*: list of the amounts of each color the user used
        - *color_types*: list of the type(s) of colorant the user used
        - *glitters*: list of the glitters the user used in the project
        - *glitter_amts*: list of the amounts of each glitter used
        - *time_to_pour_mins*: the time from combining to pouring into mold in minutes
        - *pouring_time_mins*: the time it took to pour all the resin in minutes
        - *time_to_demold_hrs*: time between pouring and de-molding in hours
        - *result_scale*: scale of 1-5 (5 = best, 1 = worst) on how happy user is with results
        - *start_rm_temp_f*: start of project room temp in fahrenheit
        - *end_rm_temp_f*: room temp when finished pouring in fahrenheit
    """
    project_id = DB.Column(DB.Integer, DB.ForeignKey('project.id'), primary_key=True, nullable=False)
    id = DB.relationship('Project', backref=DB.backref('details', lazy=True))
    resin_brand = DB.Column(DB.String())
    resin_type = DB.Column(DB.String())
    amount = DB.Column(DB.String())
    unit = DB.Column(DB.String())
    colors = DB.Column(DB.String())
    color_amts = DB.Column(DB.String())
    color_types = DB.Column(DB.String())
    glitters = DB.Column(DB.String())
    glitter_amts = DB.Column(DB.String())
    time_to_pour_mins = DB.Column(DB.String())
    pouring_time_mins = DB.Column(DB.String())
    time_to_demold_hrs = DB.Column(DB.String())
    result_scale = DB.Column(DB.String())
    start_rm_temp_f = DB.Column(DB.String())
    end_rm_temp_f = DB.Column(DB.String())

    def __repr__(self):
        return '<Details %r>' % self.project_id
