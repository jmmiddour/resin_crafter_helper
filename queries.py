import pandas
import pandas as pd
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash

from db_model import DB, User, Project, Details


def dup_user(name):
    """
    Look for a duplicate username in the data base

    :param
        name: str: preferred username

    :return:
        bool: True if username already in database; False if not found
    """
    if DB.session.query(User.id).filter(User.username == name).count() > 0:
        return True

    else:
        return False


def add_user(first, last, user, hash_pass, email):
    """
    Add a new user into the user's database table

    :param
        - first     : *str* : user's first name
        - last      : *str* : user's last name
        - user      : *str* : user's preferred username
        - hash_pass : *str* : hashed password for the user's protection
        - email     : *str* : user's email address

    :return:
        Adds new user to the database user table
    """
    new_user = User(first_name=first, last_name=last, username=user,
                    password=hash_pass, email=email)
    DB.session.add(new_user)
    DB.session.commit()


def get_user(username):
    """
        Get the row where the username is in the database

        :param
            username: str: user's username

        :return:
            int : row number where the username is in the database
        """
    user = User.query.filter(User.username == username).one()
    return user[0]


def dup_proj(proj_name, user_id):
    """
    Query to verify project name does not already exist

    :return:
        *bool* : True if project name already exists; False if not found
    """
    proj_rows = DB.engine.execute(
        text("""
        SELECT name
        FROM "project"
        WHERE user_id = :user_id;
        """), user_id=user_id).all()

    if proj_name in proj_rows:
        return True

    else:
        return False


def get_last_ten(user_id):
    """
    Functionality to query the 10 most recently added projects in a table
    :param
        - user_id : int : id of the user currently logged in to the application
    :return:
        Array with select project details for the 10 most recently added
    """
    rows = DB.engine.execute(
        text("""
            SELECT p.name, d.resin_brand, d.resin_type, d.amount, d.unit,
                d.colors, d.glitters, d.result_scale
            FROM "user" u
                JOIN "project" p ON p.user_id = u.id
                JOIN "details" d ON d.project_id = p.id
            WHERE u.id = :user_id
            ORDER BY p.id DESC
            LIMIT 10;
        """), user_id=user_id).all()

    return rows


def add_new_project(project_dict: dict):
    """
    Function to add a new project with all the optional parameters available
        for input into the database for recovery later.

    :param
        - project_dict : *dict* : Dictionary with all of the following as its keys:

            - user_id            : *int*         : currently logged in user id
            - name               : *str*         : name of project
            - mold_img           : *url*         : link to image of mold used
            - res_img            : *url*         : link to image of results
            - resin_brand        : *str*         : name of the brand of resin used
            - resin_type         : *str*         : type of resin used
            - amt                : *int*         : total amount of resin used
            - unit               : *str*         : unit of measurement for resin
            - colors             : *str or list* : color(s) separated by commas
            - color_amts         : *str or list* : color(s) amounts separated by commas
            - color_types        : *str or list* : color(s) types separated by commas
            - glitters           : *str or list* : glitter(s) separated by commas
            - glitter_amts       : *str or list* : glitter(s) amounts separated by commas
            - time_to_pour_mins  : *int*         : time from combining to pouring in minutes
            - notes              : *str*         : additional notes
            - pouring_time_mins  : *int*         : total time took for all pouring in minutes
            - time_to_demold_hrs : *float*       : time from finished pouring to de-molding in hours
            - result_scale       : *int*         : results scale 1-5 (1 being best result)
            - start_rm_temp_f    : *float*       : room temp at start of project in fahrenheit
            - end_rm_temp_f      : *float*       : room temp at end of project in fahrenheit

    :return:
        Adds all given parameters to the database
    """
    # Create new values to add to the project table based on given parameters
    new_project = Project(name=project_dict['name'],
                          mold_img=project_dict['mold_img'],
                          result_img=project_dict['res_img'],
                          notes=project_dict['notes'],
                          user_id=project_dict['user_id']
                          )
    # Add the new values to the project table
    DB.session.add(new_project)
    # Commit those changes so we can get the new project id number
    DB.session.commit()
    # Get the new project id number for the details table
    proj_id = DB.engine.execute(text(
        'SELECT id FROM "project" WHERE name = :name and user_id = :user_id'),
        name=project_dict['name'], user_id=project_dict['user_id']).one()
    # Create new values to add to the details table based on given parameters
    new_details = Details(project_id=proj_id[0],
                          resin_brand=project_dict['resin_brand'],
                          resin_type=project_dict['resin_type'],
                          amount=project_dict['amt'],
                          unit=project_dict['unit'],
                          colors=project_dict['colors'],
                          color_amts=project_dict['color_amts'],
                          color_types=project_dict['color_types'],
                          glitters=project_dict['glitters'],
                          glitter_amts=project_dict['glitter_amts'],
                          time_to_pour_mins=project_dict['time_to_pour_mins'],
                          pouring_time_mins=project_dict['pouring_time_mins'],
                          time_to_demold_hrs=project_dict['time_to_demold_hrs'],
                          result_scale=project_dict['result_scale'],
                          start_rm_temp_f=project_dict['start_rm_temp_f'],
                          end_rm_temp_f=project_dict['end_rm_temp_f'])
    # Add the new values to the details table
    DB.session.add(new_details)
    # Commit the changes to the database
    DB.session.commit()



