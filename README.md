# The Resin Crafter's Helper

A web-based application to help the resin crafter organize all project notes in one place.

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
All dependencies are housed within the `Pipfile` in this repository. All you need to do is just install the pip environment on your machine using the command `pipenv install --python 3.8 --dev` and then enter into your `pipenv shell`.

## Deploying Locally
Being that this application is a web-based Flask application, it can be deployed locally.

This application can simply be deployed locally using the `python app.py` command since I included the run functionally in the `app.py` file. This will also run it in the `developer` mode. If you would like to take it out of the `developer` mode, you can remove `debug=True` parameter from the `app.run()` code at the end of the file.

## Final Deployment

