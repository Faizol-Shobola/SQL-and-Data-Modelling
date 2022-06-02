#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.mime import image
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # list for storing venue data
    data = []

    # get all the venues and create a set from the cities
    venues = Venue.query.all()
    venue_cities = set()
    for venue in venues:
        # add city/state tuples
        venue_cities.add((venue.city, venue.state))

    # for each unique city/state, add venues
    for location in venue_cities:
      data.append({
          "city": location[0],
          "state": location[1],
          "venues": []
      })

    for venue in venues:
      for result in data:
        if venue.city == result['city'] and venue.state == result['state']:
          result['venues'].append({
            "id": venue.id,
            "name": venue.name
          })

    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  # get search term from user input
    search_term = request.form.get('search_term', '')

    # find all artists matching search term
    # including partial match and case-insensitive
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

    response = {
        "count": len(venues),
        "data": []
    }

    # for all matching venues
    # and add data to reponse
    for venue in venues:

      response['data'].append({
          "id": venue.id,
          "name": venue.name,
      })
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  # get all venues
    venue = Venue.query.get(venue_id)

    # get all shows for given venue
    shows = Show.query.filter_by(venue_id=venue_id).all()

    # returns upcoming shows
    def upcoming_shows():
        upcoming = []

        # if show is in future, add show details to upcoming
        for show in shows:
            if show.start_time > datetime.now():
                upcoming.append({
                    "artist_id": show.artist_id,
                    "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                    "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
        return upcoming

    # returns past shows
    def past_shows():
        past = []

        # if show is in past, add show details to past
        for show in shows:
            if show.start_time < datetime.now():
              past.append({
                "artist_id": show.artist_id,
                "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                "start_time": format_datetime(str(show.start_time))
              })
        return past

    # data for given venue
    data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.description,
      "image_link": venue.image_link,
      "past_shows": past_shows(),
      "upcoming_shows": upcoming_shows(),
      "past_shows_count": len(past_shows()),
      "upcoming_shows_count": len(upcoming_shows())
    }
  
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  venueForm = VenueForm(request.form)
  try:
    if venueForm.validate():
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      address = request.form['address']
      phone = request.form['phone'] 
      genres = request.form.getlist('genres')
      image_link = request.form['image_link']
      facebook_link = request.form['facebook_link']
      description = request.form['seeking_description'] 
      #If checbox is clicked
      if 'seeking_talent' in request.form:
          response = True
      else:
          response = False
      seeking_talent =  response
      website = request.form['website_link'] 


    # TODO: modify data to be the data object returned from db insertion
      createVenue = Venue(name, city, state, address, phone, genres, image_link, facebook_link, description, seeking_talent, website)
      db.session.add(createVenue)
      db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  
  except: 
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  finally:
    db.session.close()
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  # get search term from user input
    search_term = request.form.get('search_term', '')

    # find all artists matching search term
    # including partial match and case-insensitive
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

    response = {
        "count": len(artists),
        "data": []
    }

    # for all matching artists
    # and add data to reponse
    for artist in artists:

      response['data'].append({
          "id": artist.id,
          "name": artist.name,
      })

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  # get artist by id
    artist = Artist.query.get(artist_id)

    # get all shows matching artist id
    shows = Show.query.filter_by(artist_id=artist_id).all()

    # returns upcoming shows
    def upcoming_shows():
        upcoming = []

        # if the show is upcoming, add to upcoming
        for show in shows:
            if show.start_time > datetime.now():
                upcoming.append({
                    "venue_id": show.venue_id,
                    "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
                    "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
        return upcoming

    # returns past shows
    def past_shows():
        past = []

        # if show is in past, add to past
        for show in shows:
            if show.start_time < datetime.now():
                past.append({
                    "venue_id": show.venue_id,
                    "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
                    "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
        return past

    # data for given artist
    data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows(),
      "upcoming_shows": upcoming_shows(),
      "past_shows_count": len(past_shows()),
      "upcoming_shows_count": len(upcoming_shows()),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  # get artist by id
  artist = Artist.query.get(artist_id)

  # artist data
  artist = {
      "id": artist.id,
      "name": artist.name,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "genres": artist.genres,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "image_link": artist.image_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description
  }

  # set placeholders in form SelectField dropdown menus to current data
  form.name.process_data(artist['name'])
  form.city.process_data(artist['city'])
  form.state.process_data(artist['state'])
  form.phone.process_data(artist['phone'])
  form.genres.process_data(artist['genres'])
  form.website_link.process_data(artist['website'])
  form.facebook_link.process_data(artist['facebook_link'])
  form.image_link.process_data(artist['image_link'])
  form.seeking_venue.process_data(artist['seeking_venue'])
  form.seeking_description.process_data(artist['seeking_description'])

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artistForm = ArtistForm(request.form)
  try:
    artist = Artist.query.get(artist_id)

    if artistForm.validate():
      artist.name = request.form['name']
      artist.city = request.form['city']
      artist.state = request.form['state']
      artist.phone = request.form['phone'] 
      artist.genres = request.form.getlist('genres')
      artist.image_link = request.form['image_link']
      artist.facebook_link = request.form['facebook_link']
      #If checbox is clicked
      if 'seeking_venue' in request.form:
          response = True
      else:
          response = False
      artist.seeking_venue = response 
      artist.seeking_description = request.form['seeking_description'] 
      artist.website = request.form['website_link'] 

      db.session.commit()

      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully Updated!')

  # TODO: on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be Updated.')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # get artist by id
  venue = Venue.query.get(venue_id)

  # artist data
  venue = {
      "id": venue.id,
      "name": venue.name,
      "city": venue.city,
      "state": venue.state,
      "address": venue.address,
      "phone": venue.phone,
      "genres": venue.genres,
      "facebook_link": venue.facebook_link,
      "image_link": venue.image_link,
      "website": venue.website,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.description
  }

  # set placeholders in form SelectField dropdown menus to current data
  form.name.process_data(venue['name'])
  form.city.process_data(venue['city'])
  form.state.process_data(venue['state'])
  form.address.process_data(venue['address'])
  form.phone.process_data(venue['phone'])
  form.genres.process_data(venue['genres'])
  form.facebook_link.process_data(venue['facebook_link'])
  form.image_link.process_data(venue['image_link'])
  form.website_link.process_data(venue['website'])
  form.seeking_talent.process_data(venue['seeking_talent'])
  form.seeking_description.process_data(venue['seeking_description'])
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venueForm = VenueForm(request.form)
  try:
    venue = Venue.query.get(venue_id)
    if venueForm.validate():
      venue.name = request.form['name']
      venue.city = request.form['city']
      venue.state = request.form['state']
      venue.address = request.form['address']
      venue.phone = request.form['phone'] 
      venue.genres = request.form.getlist('genres')
      venue.image_link = request.form['image_link']
      venue.facebook_link = request.form['facebook_link']
      venue.description = request.form['seeking_description'] 
      #If checbox is clicked
      if 'seeking_talent' in request.form:
          response = True
      else:
          response = False
      venue.seeking_talent =  response
      venue.website = request.form['website_link'] 

      db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully Updated!')
  # TODO: on unsuccessful db insert, flash an error instead.
  
  except: 
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be Updated.')

  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # called upon submitting the new artist listing form
  artistForm = ArtistForm(request.form)
  try:
    if  artistForm.validate():
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone'] 
      genres = request.form.getlist('genres')
      image_link = request.form['image_link']
      facebook_link = request.form['facebook_link']
      #If checbox is clicked
      if 'seeking_venue' in request.form:
          response = True
      else:
          response = False
      seeking_venue = response 
      description = request.form['seeking_description'] 
      website = request.form['website_link'] 

      # TODO: modify data to be the data object returned from db insertion
      createArtist = Artist(name, city, state, phone, genres, image_link, facebook_link, seeking_venue, description, website)
      db.session.add(createArtist)
      db.session.commit()


      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.

  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # TODO: replace with real venues data.
  data = []
  allShows = Show.query.all()

  # displays list of shows at /shows
  for show in allShows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
      "artist_id": show.artist_id,
      "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
      "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
      "start_time": format_datetime(str(show.start_time))
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  showForm = ShowForm(request.form)
  # TODO: insert form data as a new Show record in the db, instead
  # called to create new shows in the db, upon submitting new show listing form
  if showForm.validate():
    venue_id = request.form['venue_id']
    artist_id = request.form['artist_id']
    start_time = request.form['start_time']

    # create new show with user data
    createShow = Show(venue_id, artist_id, start_time)
    db.session.add(createShow)
    db.session.commit()
    db.session.close()


    # on successful db insert, flash success
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  else: 
     flash('An error occurred. Show could not be listed.')
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
