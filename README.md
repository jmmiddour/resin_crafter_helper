# The Resin Crafter's Helper

A web-based application to help the resin crafter organize all project notes in one place.

[Video Demonstration of working Application](https://youtu.be/86l4B5phzJM)

## The Problem
As a resin crafter myself, I find myself in need of a way to organize my notes all in one place. When I experiment with different projects I like to take notes as to what I did. This way when I get a desired outcome I have a better chance to recreate it. I have talked to other resin crafters who have expressed their interested in having an application available like this as well.

## How this application helps...
When you are experimenting with a specific outcome in mind, the best way to be able to recreate your work is to note everything from the type of resin, to the color used, and everything in between. This web-based application is a great way to keep all those notes in one place and can be accessed from any computer with an internet connection. There are several fields that can be filled in for each project. You can even add a picture of the mold you are using and the resulting image.

Some fields that are available for each project include:
- Name of the project
- Add a link to an image of the mold used and resulting project
- Resin brand
- Resin type
- Color(s) added and the type of colorant
- Prep time
- Working time
- Set time
- etc.

There is even a field where you can add additional notes.

## Dependencies
All dependencies are housed within the `Pipfile` in this repository. All you need to do is just install the pip environment on your machine using the command `pipenv install --python 3.8 --dev` and then enter into your `pipenv shell`. There is also a `requirements.txt` file in this repository, so you could also install the dependencies with it.

## Deploying Locally
Being that this application is a web-based Flask application, it can be deployed locally.

I have made it super easy to deploy this application locally. All you have to do is run `python app.py` in your terminal. This will also run the Flask application in debug or "developer" mode. If you would like to take it out of "developer" mode, all you have to do is remove the parameter `debug=True` in the `app.run()` code at the end of the file.

## Final Deployment
This application has been deployed on Heroku, which gives anyone with internet access, access to the fully functioning application. 

You can access this application at: [https://resin-crafters.herokuapp.com/](https://resin-crafters.herokuapp.com/)

Register for an account and login to start enjoying all the functionality from any computer anywhere with just an internet connection.

## Future Features...
1. This application was designed with user security in mind, therefore all user passwords are hashed before being stored in the database. This makes that the developer(s) that work on this project will not be able to access any user password in the situation that a user forgets their password. In the future, I would like to implement the ability for a user to receive an email with a way to reset their password in the case of a forgotten password. This is the reason for asking for a user's email address when registering for an account.

2. I would like to include a feature where the user would be able to publicly share their projects with other users. 

3. Would also like to implement a feature where a user can share their project on their social media accounts.

4. With the implementation of users being able to share their projects with each other, would also like to implement a search feature. With the search feature the user would be able to search all publicly shared projects based on keywords.

5. A resource page where users can link to different resources that can be shared with other users. This would be a great way for resin crafters to share their knowledge with other resin crafters.

6. As more data is added to the database, would like to be able to use that data, anonymously to see if I could implement a model to help users better determine what factors to change to get the desired results. This would take a lot of accurate data to train a model, so this would be something that may take a while to be able to implement.

7. Looking forward to any suggestions from users on what features they would like to see.

## Developer's Contact Information
| [Joanne Middour](https://github.com/jmmiddour) | |
| :---: | :---: | 
| [<img src="https://avatars.githubusercontent.com/u/64432505?s=400&u=fad1eeb4a6b675f1fb6f0461fe1a231a68d6ad98&v=4" width = "180" />](https://github.com/jmmiddour) | [<img src="https://github.com/favicon.ico" width="30"> ](https://github.com/jmmiddour) <br><br> [<img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="30">](https://www.linkedin.com/in/joanne-middour/) <br><br> [<img src="https://raw.githubusercontent.com/jmmiddour/jmmiddour.github.io/master/assets/img/favicon.jpg" width="30">](https://joannemiddour.com/) |
