from flask_sqlalchemy import SQLAlchemy

# from .app import app

# Initialize the SQLAlchemy
DB = SQLAlchemy()


# Create table class for the user data
class User(DB.Model):
    """
    user table column definitions:

        - *id*:
            auto populated id for each user registered through app
                - One-to-Many relationship to project table
        - *first*:
            the first name the user entered when registering
        - *last*:
            the last name the user entered when registering
        - *username*:
            name the user entered when registering as their username for login
                - each username must be unique
        - *password*:
            the password the user entered - hashed for user's privacy
        - *email*:
            the users registered email address for forgotten username/password
                - each email must be unique
    """
    id = DB.Column(DB.Integer(), primary_key=True)
    first = DB.Column(DB.String, nullable=False)
    last = DB.Column(DB.String, nullable=False)
    username = DB.Column(DB.String, unique=True, nullable=False)
    password = DB.Column(DB.String, nullable=False)
    email = DB.Column(DB.String, unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.first_name


# Create table class for project data
class Project(DB.Model):
    """
    project table column definitions:

        - *id*:
            auto populated for each new project created
                - One-to-One relationship to details table
        - *name*:
            name the user entered for the project
                - each project name must be unique to user
        - *mold_img*:
            BLOB data for image of mold used for project
        - *mold_img_type*:
            the type of image of mold used for project
        - *result_img*:
            BLOB data for image of the resulting project
        - *mold_img*:
            the type of image of the resulting project
        - *notes*:
            any additional notes user entered
        - *user_id*:
            links to the user who created the project
                - Many-to-One relationship to the user table
    """
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String, nullable=False)
    mold_img = DB.Column(DB.Text)
    mold_img_type = DB.Column(DB.String)
    result_img = DB.Column(DB.Text)
    result_img_type = DB.Column(DB.String)
    notes = DB.Column(DB.String)
    user_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'), nullable=False)
    user = DB.relationship('User', backref=DB.backref('project', lazy=True))

    def __repr__(self):
        return '<Project %r>' % self.name


# Create a table class for project detail data
class Details(DB.Model):
    """
    details table column definitions:

        - *project_id*:
            links to the rest of the details of the project
                - One-to-One relationship to the project table
        - *resin_brand*:
            the brand of resin the user used for the project
        - *resin_type*:
            the type of resin the user used for the project
        - *amount*:
            the amount of resin the user needed for the project
        - *unit*:
            the unit of measurement the user used to measure the amount of resin
        - *colors*:
            color(s) the user used for the project - separated by commas
        - *color_amts*:
            amount(s) of each color the user used - separated by commas
        - *color_types*:
            type(s) of colorant the user used - separated by commas
        - *glitters*:
            glitter(s) the user used in the project - separated by commas
        - *glitter_types*:
            type(s) of glitters the user used - separated by commas
        - *glitter_amts*:
            amount(s) of each glitter used - separated by commas
        - *time_to_pour_hrs*:
            the time from combining to pouring into mold in hours
        - *time_to_pour_mins*:
            the time from combining to pouring into mold in minutes
        - *pouring_time_hrs*:
            the time it took to pour all the resin in hours
        - *pouring_time_mins*:
            the time it took to pour all the resin in minutes
        - *time_to_demold_hrs*:
            time between pouring and de-molding in hours
        - *time_to_demold_mins*:
            time between pouring and de-molding in minutes
        - *result_scale*:
            scale of 1-5 (1 = best, 5 = worst) - how happy user is with results
        - *start_temp*:
            start of project room temperature
        - *start_temp_unit*:
            start of project temperature unit
        - *end_temp*:
            room temperature when finished pouring
        - *end_temp_unit*:
            unit of room temperature when finished pouring
        - *demold_rm_temp*:
            room temperature when de-molding
        - *demold_temp_unit*:
            unit of de-molding room temperature
    """
    project_id = DB.Column(DB.Integer, DB.ForeignKey('project.id'), primary_key=True, nullable=False)
    id = DB.relationship('Project', backref=DB.backref('details', lazy=True))
    resin_brand = DB.Column(DB.String)
    resin_type = DB.Column(DB.String)
    amount = DB.Column(DB.Integer)
    unit = DB.Column(DB.String)
    colors = DB.Column(DB.String)
    color_amts = DB.Column(DB.String)
    color_types = DB.Column(DB.String)
    glitters = DB.Column(DB.String)
    glitter_amts = DB.Column(DB.String)
    glitter_types = DB.Column(DB.String)
    time_to_pour_hrs = DB.Column(DB.Integer)
    time_to_pour_mins = DB.Column(DB.Integer)
    pouring_time_hrs = DB.Column(DB.Integer)
    pouring_time_mins = DB.Column(DB.Integer)
    time_to_demold_hrs = DB.Column(DB.Integer)
    time_to_demold_mins = DB.Column(DB.Integer)
    result_scale = DB.Column(DB.String)
    start_temp = DB.Column(DB.Integer)
    start_temp_unit = DB.Column(DB.String)
    end_temp = DB.Column(DB.Integer)
    end_temp_unit = DB.Column(DB.String)
    demold_temp = DB.Column(DB.Integer)
    demold_temp_unit = DB.Column(DB.String)

    def __repr__(self):
        return '<Details %r>' % self.project_id
