#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Join Tables
venue_genres = db.Table('venue_genres',
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True)
)

artist_genres = db.Table('artist_genres',
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True)
)

class Show(db.Model): 
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    start_time = db.Column(db.DateTime)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    genres = db.relationship('Genre', secondary=venue_genres, backref=db.backref('venues', lazy=True))
    shows = db.relationship('Show', backref='venue', lazy=True)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    genres = db.relationship('Genre', secondary=artist_genres, backref=db.backref('artists', lazy=True))
    shows = db.relationship('Show', backref='artist', lazy=True)

class Genre(db.Model):
    __tablename__ = 'Genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  
  venues = Venue.query.all()
  cities = []
  states = []
  for venue in venues:
    if venue.city not in cities:
      cities.append(venue.city)
    if venue.state not in states:
      states.append(venue.state)

  showsUpcomeing = Show.query.filter(Show.start_time > '2020-01-25').all()
  showsPast = Show.query.filter(Show.start_time < '2020-01-25').all()

  data2 = []
  index = 0
  for city in cities:
    
    data2.append({
      "city": city,
      "state": Venue.query.filter_by(city=city).first().state
    })
    #get all venues for this city
    venues = Venue.query.filter_by(city=city).all()
    data2[index]["venues"] = []
    for venue in venues:
      data2[index]["venues"].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows" : len(Show.query.filter(Show.venue_id == venue.id, Show.start_time > '2020-01-25').all())
      })

    index = index + 1
  
  print(data2)
  
  return render_template('pages/venues.html', areas=data2)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  search_term = request.form.get('search_term', '')
  print(search_term)

  venues = Venue.query.filter(func.lower(Venue.name).contains(func.lower(search_term))).all()
  #venues = Venue.query.filter(Venue.name.lower().contains(search_term.lower())).all()
  print(venues)

  response = {
    'count' : len(venues)
  } 
  response['data'] = []

  for venue in venues:
    response['data'].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(Show.query.filter(Show.venue_id == venue.id, Show.start_time > '2020-01-25').all())
    })

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.filter_by(id=venue_id).first()

  data = {
    "id": venue.id,
    "name": venue.name,
    "city": venue.city,
    "state": venue.state,
    "address": venue.address,
    "phone": venue.phone,
    "image_link": venue.image_link,
    "facebook_link": venue.facebook_link,
    "website": venue.website,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description
  }

  genres = Genre.query.filter(Genre.venues.any(id=venue.id)).all()
  data["genres"] = []
  for genre in genres:
    data["genres"].append(genre.name)

  pastShows = Show.query.filter(Show.venue_id == venue.id, Show.start_time < '2020-01-25').all()
  upcoming_shows = Show.query.filter(Show.venue_id == venue.id, Show.start_time > '2020-01-25').all()
  
  data["past_shows"] = []
  for show in pastShows:
    artist = Artist.query.filter_by(id=show.artist_id).first()
    data["past_shows"].append({
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.isoformat()
    })

  data["upcoming_shows"] = []
  for show in upcoming_shows:
    artist = Artist.query.filter_by(id=show.artist_id).first()
    data["upcoming_shows"].append({
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.isoformat()
    })

    data["past_shows_count"] = len(pastShows),
    data["upcoming_shows_count"] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  #create the genre array first
  mylist = request.form.lists()

  genres = []
  for key, value in mylist:
    if(key == 'genres'):
      for genre in value:
        print(genre)
        out = Genre.query.filter_by(name=genre).first()
        print(out)
        if out is not None:
          genres.append(out) 
    
  print(genres)

  formDict = request.form

  error = False
  try:
    newVenue = Venue(
      name=formDict['name'], 
      city=formDict['city'], 
      state=formDict['state'], 
      address=formDict['address'],
      phone=formDict['phone'],
      facebook_link=formDict['facebook_link'])
    
    #use the prior created genres list
    newVenue.genres = genres

    db.session.add(newVenue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  if error:
    abort(400)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data=[]
  artists = Artist.query.all()
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term', '')

  artists = Artist.query.filter(func.lower(Artist.name).contains(func.lower(search_term))).all()

  response = {
    "count": len(artists)
  }
  
  response['data'] = []
  for artist in artists:
    response['data'].append({
      "id": artist.id,
      "name": artist.name
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  
  artist = Artist.query.filter_by(id=artist_id).first()

  data = {
    "id": artist.id,
    "name": artist.name,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }

  genres = Genre.query.filter(Genre.artists.any(id=artist.id)).all()
  data["genres"] = []
  for genre in genres:
    data["genres"].append(genre.name)

  pastShows = Show.query.filter(Show.artist_id == artist.id, Show.start_time < '2020-01-25').all()
  upcoming_shows = Show.query.filter(Show.artist_id == artist.id, Show.start_time > '2020-01-25').all()
  
  data["past_shows"] = []
  for show in pastShows:
    venue = Venue.query.filter_by(id=show.venue_id).first()
    data["past_shows"].append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.isoformat()
    })

  data["upcoming_shows"] = []
  for show in upcoming_shows:
    venue = Venue.query.filter_by(id=show.venue_id).first()
    data["upcoming_shows"].append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.isoformat()
    })

    data["past_shows_count"] = len(pastShows),
    data["upcoming_shows_count"] = len(upcoming_shows)
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist = Artist.query.filter_by(id=artist_id).first()

  form.name.data = artist.name
  form.city.data = artist.city
  form.phone.data = artist.phone
  form.facebook_link.data = artist.facebook_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  print(request.form)

  formDict = request.form
  artist = Artist.query.filter_by(id=artist_id).first()
  try:
    artist.name = formDict['name']
    artist.city = formDict['city']
    artist.phone = formDict['phone']
    artist.facebook_link = formDict['facebook_link']
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))    

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = Venue.query.filter_by(id=venue_id).first()

  form.name.data = venue.name
  form.city.data = venue.city
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.facebook_link.data = venue.facebook_link

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  formDict = request.form
  venue = Venue.query.filter_by(id=venue_id).first()

  try:
    venue.name = formDict['name']
    venue.city = formDict['city']
    venue.address = formDict['address']
    venue.phone = formDict['phone']
    venue.facebook_link = formDict['facebook_link']
    db.session.commit()
  except:
    db.session.rollback()
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

  #create the genre array first
  formList = request.form.lists()

  genres = []
  for key, value in formList:
    if(key == 'genres'):
      for genre in value:
        out = Genre.query.filter_by(name=genre).first()
        if out is not None:
          genres.append(out)

  formDict = request.form
  error = False
  try:
    newArtist = Artist(
      name=formDict['name'],
      city=formDict['city'], 
      state=formDict['state'], 
      phone=formDict['phone'],
      facebook_link=formDict['facebook_link']
    ) 
  
    #use the previously created genres list
    newArtist.genres = genres

    db.session.add(newArtist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  if error:
    #abort(400)
    print("error")
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows

  shows = Show.query.all()

  data = []
  for show in shows:
    venue = Venue.query.filter_by(id=show.venue_id).first()
    artist = Artist.query.filter_by(id=show.artist_id).first()
    data.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.isoformat()
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form

  formDict = request.form

  error = False
  try:
    newShow = Show(
      start_time = formDict['start_time']
    )
    newShow.venue = Venue.query.filter_by(id=formDict['venue_id']).first()
    newShow.artist = Artist.query.filter_by(id=formDict['artist_id']).first()

    db.session.add(newShow)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  
  if error:
    print('error')
  else:
    flash('Show was successfully listed!')

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
