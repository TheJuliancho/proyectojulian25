from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app import db

bp = Blueprint('user', __name__)

