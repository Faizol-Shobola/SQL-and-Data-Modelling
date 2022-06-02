#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  address = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  description = db.Column(db.String(500), default='')
  seeking_talent = db.Column(db.Boolean(), default=False, nullable=False)
  website = db.Column(db.String(120))
  show = db.relationship('Show', backref='venue', lazy=True)

  # TODO: implement any missing fields, as a database migration using Flask-Migrate

  def __init__(self, name, city, state, address, phone, genres, image_link, facebook_link, description, seeking_talent, website):
    self.name = name 
    self.city = city
    self.state = state
    self.address = address
    self.phone = phone
    self.genres = genres
    self.image_link = image_link
    self.facebook_link = facebook_link
    self.description = description
    self.seeking_talent = seeking_talent
    self.website = website



class Artist(db.Model):
  __tablename__ = 'artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean(), default=False, nullable=False)
  seeking_description = db.Column(db.String(120), default='')
  website = db.Column(db.String(120))
  show = db.relationship('Show', backref='artist', lazy=True)

  # TODO: implement any missing fields, as a database migration using Flask-Migrate

  def __init__(self, name, city, state, phone, genres, image_link, facebook_link, seeking_venue, description, website):
    self.name = name 
    self.city = city
    self.state = state
    self.phone = phone
    self.genres = genres
    self.image_link = image_link
    self.facebook_link = facebook_link
    self.seeking_venue = seeking_venue
    self.seeking_description = description
    self.website = website


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  start_time = db.Column(db.DateTime(), nullable=False)

  def __init__(self, venue_id, artist_id, start_time):
    self.venue_id = venue_id
    self.artist_id = artist_id
    self.start_time = start_time

