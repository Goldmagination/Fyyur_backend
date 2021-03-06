#----------------------------------------------------------------------------#
# Imports

#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
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

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    address = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    show = db.relationship('Show', backref='Venue', lazy=True)

    def __repr__(self):
        return f"<Venue {self.name}"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


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
    genres = db.Column(db.String(120))
    address = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    show = db.relationship('Show', backref='Artist', lazy=True)

    def __repr__(self):
        return f"<Artist {self.name}"


class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    starttime = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Show {self.artist_id}{self.venue_id}"


db.create_all()

# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    data = db.session.query(Venue).all()
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term')
    result = db.session.query(Venue).filter(
        Venue.name.ilike(f'%{search_term}%')).all()
    count = []
    for i in result:
        count.append(i.name)

    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {
        "count": len(count),
        "data": result,
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    Venue = Venue.query.get(venue_id)

    query_up_shows = db.session.query(Show).filter(
        Show.venue_id == venue_id).filter(Show.starttime > datetime.now()).all
    upcoming_shows = []
    for i in query_up_shows:
        upcoming_shows.append({
            "artist_id": i.artist_id,
            "artist_name": i.artist.name,
            "artist_image_link": i.artist.image_link,
            "start_time": i.start_time
        })

    query_p_shows = db.session.query(Show).filter(
        Show.venue_id == venue_id).filter(Show.starttime < datetime.now()).all
    previous_show = []
    for i in query_p_shows:
        previous_show.append({
            "artist_id": i.artist_id,
            "artist_name": i.artist.name,
            "artist_image_link": i.artist.image_link,
            "start_time": i.start_time
        })
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

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
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "previous_show": previous_show,
        "upcoming_shows": upcoming_shows, }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        id = request.form.get('id')
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        genres = request.form.get('genres')
        image_link = request.form.get('image_link')
        facebook_link = request.form.get('facebook_link')
        address = request.form.get('address')
        website = request.form.get('website')
        seeking_talent = True if 'seeking_talent' in request.form.get else False
        seeking_description = request.form.get('seeking_description')
        createvenue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link,
                            image_link=image_link, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)
        db.session.add(createvenue)
        db.session.commit()
        flash('Venue ' + request.form.get('name') + ' was successfully listed!')
    except:
        error = True
        flash('An error occurred. Venue ' +
              data.name + ' could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        abort(400)
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        return render_template('errors/404.html')
    finally:
        db.session.close()
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/venues.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = db.session.query(Artist).all()
    # TODO: replace with real data returned from querying the database
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.get.form('search_term')
    result = db.session.query(Artist).filter(
        Artist.name.ilike(f'%{search_term}%'))
    count = []
    for i in result:
        count.append(i.name)

    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {
        "count": len(count),
        "data": result,
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = db.session.query(Artist).filter(Artist.id == artist_id).one()
    query_up_shows = db.session.query(Show).filter(
        Show.artist_id == artist_id).filter(Show.starttime > datetime.now()).all
    upcoming_shows = []
    for i in query_up_shows:
        upcoming_shows.append({
            "venue_id": i.venue_id,
            "venue_name": i.venue.name,
            "venue_image_link": i.venue.image_link,
            "start_time": i.start_time
        })

    query_p_shows = db.session.query(Show).filter(
        Show.artist_id == artist_id).filter(Show.starttime < datetime.now()).all
    previous_show = []
    for i in query_p_shows:
        previous_show.append({
            "venue_id": i.venue_id,
            "venue_name": i.venue.name,
            "venue_image_link": i.venue.image_link,
            "start_time": i.start_time
        })
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data1 = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artost.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "previous_show": previous_show,
        "upcoming_shows": upcoming_shows, }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = db.session.query(Artist).filter(artist_id).all()
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    try:
        artist.name = request.form.get('name')
        artist.genres = request.form.get('genres')
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        artist.website = request.form.get('website')
        artist.facebook_link = request.form.get('facebook_link')
        artist.seeking_venue = True if 'seeking_venue' in request.form.get else False
        artist.seeking_description = request.form.get('seeking_description')
        artist.image_link = request.form.get('image_link')
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = db.session.query(Venue).filter(venue_id).all()
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    try:
        venue.name = request.form.get('name')
        venue.genres = request.form.get('genres')
        venue.address = request.form.get('address')
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.phone = request.form.get('phone')
        venue.website = request.form.get('website')
        venue.facebook_link = request.form.get('facebook_link')
        venue.seeking_talent = True if 'seeking_talent' in request.form.get else False
        venue.seeking_description = request.form.get('seeking_description')
        venue.image_link = request.form.get('image_link')
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    try:
        name = request.form.get('name')
        genres = request.form.get('genres')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        address = request.form.get('address')
        website = request.form.get('website')
        facebook_link = request.form.get('facebook_link')
        seeking_venue = True if 'seeking_venue' in request.form.get else False
        seeking_description = request.form.get('seeking_description')
        image_link = request.form.get('image_link')
        createartist = Artist(name=name, genres=genres, city=city, state=state, phone=phone, address=address, website=website,
                              facebook_link=facebook_link, seeking_venue=seeking_venue, seeking_description=seeking_description, image_link=image_link)
        db.session.add(createartist)
        db.session.commit()
        flash('Artist ' + request.form.get('name') + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        # called upon submitting the new artist listing form
        # TODO: insert form data as a new Venue record in the db, instead
        # TODO: modify data to be the data object returned from db insertion
        # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    query = db.session.query(Show).join(Artist).join(Venue).all()
    data = []
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    for i in query:
        data.append({
            "venue_id": i.venue_id,
            "venue_name": i.venue_name,
            "artist_id": i.artist_id,
            "artist_name": i.artist_name,
            "artist_image_link": i.artist_image_link,
            "start_time": i.start.time})
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        artist_id = request.form.get('artist_id')
        venue_id = request.form.get('venue_id')
        start_time = request.form.get('start_time')
        createshows = Show(artist_id=artist_id,
                           venue_id=venue_id, start_time=start_time)
        db.session.add(createshows)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
