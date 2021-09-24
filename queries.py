from sqlalchemy import text

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
        DB.session.close()
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
    new_user = User(first=first, last=last, username=user,
                    password=hash_pass, email=email)
    DB.session.add(new_user)
    DB.session.commit()
    DB.session.close()


def get_user_id(username):
    """
        Get the row where the username is in the database

        :param
            username: str: user's username

        :return:
            int : row number where the username is in the database
    """
    user = DB.engine.execute(
        text("""
        SELECT *
        FROM "user"
        WHERE username = :username;
        """), username=username).all()
    DB.session.close()
    user_id = user[0][0]
    return user_id


def user_details(user_id):
    """
    Query to get current user details from the database

    :param
        - user_id : int : id number of the user currently logged in

    :return:
        list with all the details for given user only
    """
    # Query the database joining the two tables with all the details
    single = DB.engine.execute(text(
        """
        SELECT *
        FROM "user" 
        WHERE id = :id;
        """), id=user_id).all()

    # Close the session
    DB.session.close()

    # Turn the tuple into a list
    single_list = [i for i in single[0]]

    return single_list


def edit_user(user_dict):
    """
    Query to edit details in the current user's account with all the
        optional parameters available.

    :param
        - user_dict : *dict* : Dictionary with all of the following as its keys:

            - id         : *int* : currently logged in user id
            - first_name : *str* : first name of the user
            - last_name  : *str* : last name of the user
            - username   : *str* : username of the user - can not be changed
            - password   : *str* : hashed user's password
            - email      : *str* : user's email address

    :return:
        Edits only the given parameters in the database
    """
    user = User.query.filter_by(id = user_dict['id']).first()

    user.first_name = user_dict['first_name']
    user.last_name = user_dict['last_name']
    user.password = user_dict['password']
    user.email = user_dict['email']

    # Commit the changes to the database
    DB.session.commit()
    # Close the session
    DB.session.close()


def dup_proj(proj_name, user_id):
    """
    Query to verify project name does not already exist

    :param
        - proj_name : *str* : the preferred project name to be checked
        - user_id   : *int* : the user id of the user currently logged in

    :return:
        *bool* : True if project name already exists; False if not found
    """
    # Get all project names by the user
    proj_names = DB.session.query(Project.name).filter(
        Project.user_id == user_id).all()

    DB.session.close()

    # Pull out all the names from the tuples and put them in a list
    name = [True for i in proj_names if proj_name in i]

    # Check if the project name is already used my the user
    return True in name


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
            FROM "project" p
                JOIN "details" d ON d.project_id = p.id
            WHERE p.user_id = :user_id
            ORDER BY p.id DESC
            LIMIT 10;
        """), user_id=user_id).all()

    DB.session.close()

    return rows


def add_new_project(project_dict: dict):
    """
    Function to add a new project with all the optional parameters available
        for input into the database for recovery later.

    :param
        - project_dict : *dict* : Dictionary with all of the following as its keys:

            - user_id            : *int*         :
                - currently logged in user id
            - name               : *str*         :
                - name of project
            - mold_img           : *url*         :
                - link to image of mold used
            - resin_brand        : *str*         :
                - name of the brand of resin used
            - resin_type         : *str*         :
                - type of resin used
            - amt                : *int*         :
                - total amount of resin used
            - unit               : *str*         :
                - unit of measurement for resin
            - colors             : *str or list* :
                - color(s) separated by commas
            - color_amts         : *str or list* :
                - color amount(s) separated by commas
            - color_types        : *str or list* :
                - color type(s) separated by commas
            - glitters           : *str or list* :
                - glitter(s) separated by commas
            - glitter_amts       : *str or list* :
                - glitter amount(s) separated by commas
            - glitter_types      : *str or list* :
                - glitter type(s) separated by commas
            - time_to_pour_hrs   : *int*         :
                - time from combining to pouring in hours
            - time_to_pour_mins  : *int*         :
                - time from combining to pouring in minutes
            - pouring_time_hrs   : *int*         :
                - total time took for all pouring in hours
            - pouring_time_mins  : *int*         :
                - total time took for all pouring in minutes
            - time_to_demold_hrs : *float*       :
                - time from finished pouring to de-molding in hours
            - time_to_demold_mins: *float*       :
                - time from finished pouring to de-molding in minutes
            - start_temp         : *float*       :
                - room temp at start of project
            - start_temp_unit    : *float*       :
                - unit of room temp at start of project
            - end_temp           : *float*       :
                - room temp at end of project
            - end_temp_unit      : *float*       :
                - unit of room temp at end of project
            - demold_temp        : *float*       :
                - room temp at de-molding of project
            - demold_temp_unit   : *float*       :
                - unit of room temp at de-molding of project
            - result_scale       : *int*         :
                - results scale 1-5 (1 being best result)
            - res_img            : *url*         :
                - link to image of results
            - notes              : *str*         :
                - additional notes
            - mold_img_type      : *str*         :
                - type of mold image uploaded, taken from data when uploaded
            - res_img_type       : *str*         :
                - type of result image uploaded, taken from data when uploaded

    :return:
        Adds all given parameters to the database
    """
    # Create new values to add to the project table based on given parameters
    new_project = Project(name=project_dict['name'],
                          mold_img=project_dict['mold_img'],
                          mold_img_type=project_dict['mold_img_type'],
                          result_img=project_dict['res_img'],
                          res_img_type=project_dict['res_img_type'],
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
                          glitter_types=project_dict['glitter_types'],
                          glitter_amts=project_dict['glitter_amts'],
                          time_to_pour_hrs=project_dict['time_to_pour_hrs'],
                          time_to_pour_mins=project_dict['time_to_pour_mins'],
                          pouring_time_hrs=project_dict['pouring_time_hrs'],
                          pouring_time_mins=project_dict['pouring_time_mins'],
                          time_to_demold_hrs=project_dict['time_to_demold_hrs'],
                          time_to_demold_mins=project_dict['time_to_demold_mins'],
                          result_scale=project_dict['result_scale'],
                          start_temp=project_dict['start_temp'],
                          start_temp_unit=project_dict['start_temp_unit'],
                          end_temp=project_dict['end_temp'],
                          end_temp_unit=project_dict['end_temp_unit'],
                          demold_temp=project_dict['demold_temp'],
                          demold_temp_unit=project_dict['demold_temp_unit'])
    # Add the new values to the details table
    DB.session.add(new_details)
    # Commit the changes to the database
    DB.session.commit()
    DB.session.close()


def get_all(user_id):
    """
    Functionality to run the query to get all projects for user specified

    :param
        - user_id : int : user id of currently signed in user

    :return:
        Array with all products in user account and details
    """
    all_projects = DB.engine.execute(text(
        """
        SELECT *
        FROM "project" p
            JOIN "details" d ON d.project_id = p.id
        WHERE p.user_id = :user_id;
        """), user_id=user_id).all()

    DB.session.close()

    return all_projects


def del_rec(proj_name, user_id):
    """
    Queries the database to remove a single record with the provide project id

    :param
        - proj_name : str : the name of the project record to be removed
        - user_id   : int : id of the user who added the project record

    :return:
        Database with the record removed that had the given id.
    """
    # Get the project id from the parameters given
    proj_id = DB.engine.execute(
        text("""
        SELECT id
        FROM "project"
        WHERE name = :name AND user_id = :user;
        """), name=proj_name, user=user_id).one()

    # Remove the project record from both tables
    DB.engine.execute(
        text("""
            DELETE FROM "details"
            WHERE project_id = :id;
            
            DELETE FROM "project"
            WHERE id = :id;
            """), id=proj_id[0])

    # Commit the changes to the database
    DB.session.commit()
    # Close the database session
    DB.session.close()

    return


def get_single(proj_id):
    """
    Query to get just one single project and all its details from the database

    :param
        - proj_id : int : id number of the project needed

    :return:
        list with all the details for given project only
    """
    # Query the database joining the two tables with all the details
    single = DB.engine.execute(text(
        """
        SELECT *
        FROM "project" p
            JOIN "details" d ON d.project_id = p.id
        WHERE p.id = :id;
        """), id=proj_id).all()

    # Close the session
    DB.session.close()

    # Turn the tuple into a list
    single_list = [i for i in single[0]]

    return single_list


def edit_project(project_dict):
    """
    Function to edit a project in the current user's account with all the
        optional parameters available.

    :param
        - project_dict : *dict* : Dictionary with all of the following as its keys:

            - user_id            : *int*         :
                - currently logged in user id
            - name               : *str*         :
                - name of project
            - mold_img           : *url*         :
                - link to image of mold used
            - resin_brand        : *str*         :
                - name of the brand of resin used
            - resin_type         : *str*         :
                - type of resin used
            - amt                : *int*         :
                - total amount of resin used
            - unit               : *str*         :
                - unit of measurement for resin
            - colors             : *str or list* :
                - color(s) separated by commas
            - color_amts         : *str or list* :
                - color amount(s) separated by commas
            - color_types        : *str or list* :
                - color type(s) separated by commas
            - glitters           : *str or list* :
                - glitter(s) separated by commas
            - glitter_amts       : *str or list* :
                - glitter amount(s) separated by commas
            - glitter_types      : *str or list* :
                - glitter type(s) separated by commas
            - time_to_pour_hrs   : *int*         :
                - time from combining to pouring in hours
            - time_to_pour_mins  : *int*         :
                - time from combining to pouring in minutes
            - pouring_time_hrs   : *int*         :
                - total time took for all pouring in hours
            - pouring_time_mins  : *int*         :
                - total time took for all pouring in minutes
            - time_to_demold_hrs : *float*       :
                - time from finished pouring to de-molding in hours
            - time_to_demold_mins: *float*       :
                - time from finished pouring to de-molding in minutes
            - start_temp         : *float*       :
                - room temp at start of project
            - start_temp_unit    : *float*       :
                - unit of room temp at start of project
            - end_temp           : *float*       :
                - room temp at end of project
            - end_temp_unit      : *float*       :
                - unit of room temp at end of project
            - demold_temp        : *float*       :
                - room temp at de-molding of project
            - demold_temp_unit   : *float*       :
                - unit of room temp at de-molding of project
            - result_scale       : *int*         :
                - results scale 1-5 (1 being best result)
            - res_img            : *url*         :
                - link to image of results
            - notes              : *str*         :
                - additional notes
            - mold_img_type      : *str*         :
                - type of mold image uploaded, taken from data when uploaded
            - res_img_type       : *str*         :
                - type of result image uploaded, taken from data when uploaded

    :return:
        Edits only the given parameters in the database
    """
    details = Details.query.filter_by(project_id = project_dict['id']).first()

    details.resin_brand = project_dict['resin_brand']
    details.resin_type = project_dict['resin_type']
    details.amount = project_dict['amount']
    details.unit = project_dict['unit']
    details.colors = project_dict['colors']
    details.color_amts = project_dict['color_amts']
    details.color_types = project_dict['color_types']
    details.glitters = project_dict['glitters']
    details.glitter_types = project_dict['glitter_types']
    details.glitter_amts = project_dict['glitter_amts']
    details.time_to_pour_hrs = project_dict['time_to_pour_hrs']
    details.time_to_pour_mins = project_dict['time_to_pour_mins']
    details.pouring_time_hrs = project_dict['pouring_time_hrs']
    details.pouring_time_mins = project_dict['pouring_time_mins']
    details.time_to_demold_hrs = project_dict['time_to_demold_hrs']
    details.time_to_demold_mins = project_dict['time_to_demold_mins']
    details.result_scale = project_dict['result_scale']
    details.start_temp = project_dict['start_temp']
    details.start_temp_unit = project_dict['start_temp_unit']
    details.end_temp = project_dict['end_temp']
    details.end_temp_unit = project_dict['end_temp_unit']
    details.demold_temp = project_dict['demold_temp']
    details.demold_temp_unit = project_dict['demold_temp_unit']

    project = Project.query.filter_by(id = project_dict['id']).first()

    project.mold_img = project_dict['mold_img']
    project.mold_img_type = project_dict['mold_img_type']
    project.result_img = project_dict['result_img']
    project.result_img_type = project_dict['result_img_type']
    project.notes = project_dict['notes']

    DB.session.commit()

    # for k, v in project_dict.items():
    #     if k in d_to_change:
    #         details.k = project_dict[k]
    #         print(f'k in loop: {k}\n details in loop: {details}\n  details.k in loop: {details.k}')
    #         # DB.session.update(details.k)
    #         DB.session.commit()
    #
    #     if k in p_to_change:
    #         project.k = project_dict[k]
    #         # DB.session.update(project.k)
    #         DB.session.commit()
    #
    # pprint(project_dict)

    # Add the new values to the details table
    # DB.session.add(details)

    # # Update values in the project table based on given parameters
    # edit_proj = DB.engine.execute(
    #     text(
    #         """
    #         UPDATE "project"
    #         SET mold_img = :mold_img, result_img = :res_img, notes = :notes
    #         WHERE id = :id;
    #         """
    #     ), mold_img=project_dict['mold_img'], res_img=project_dict['result_img'],
    #     notes=project_dict['notes'], id=project_dict['id']
    # )
    #
    # Add the new values to the project table
    # DB.session.add(project)

    # # Commit the changes to the database
    # DB.session.commit()
    # Close the session
    DB.session.close()
