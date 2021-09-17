"""
All functionality for adding, deleting, editing, and viewing projects
"""
from flask import Flask, render_template, request, session, redirect

from db_model import DB, User, Project, Details
from queries import no_dup, add_user, get_user


