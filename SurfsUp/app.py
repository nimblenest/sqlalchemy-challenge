# Import the dependencies
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

# Database Setup
engine = create_engine("sqlite:///C:/Users/lukeb/sqlalchemy-challenge/SurfsUp/Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Define routes

@app.route('/')
def home():
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"<a href='/api/v1.0/start_date'>/api/v1.0/start_date</a><br/>"
        f"<a href='/api/v1.0/start_date/end_date'>/api/v1.0/start_date/end_date</a>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date one year from the last date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)
    
    # Query precipitation data for the last 12 months
    precipitation_data = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= one_year_ago)\
        .all()
    
    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations():
    # Query and return a list of stations
    station_data = session.query(Station.station).all()
    stations_list = [station[0] for station in station_data]
    
    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
    # Get the most active station ID
    most_active_station_id = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc())\
        .first()[0]
    
    # Calculate the date one year from the last date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)
    
    # Query temperature observation data for the last 12 months for the most active station
    tobs_data = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station_id, Measurement.date >= one_year_ago)\
        .all()
    
    # Convert the query results to a list of dictionaries
    tobs_list = [{'Date': date, 'Temperature': tobs} for date, tobs in tobs_data]
    
    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>')
def temperature_start(start):
    # Query the minimum, average, and maximum temperatures for dates greater than or equal to the start date
    temperature_stats = session.query(func.min(Measurement.tobs),
                                      func.avg(Measurement.tobs),
                                      func.max(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .all()
    
    # Convert the query results to a dictionary
    temperature_dict = {'Min Temperature': temperature_stats[0][0],
                        'Avg Temperature': temperature_stats[0][1],
                        'Max Temperature': temperature_stats[0][2]}
    
    return jsonify(temperature_dict)

@app.route('/api/v1.0/<start>/<end>')
def temperature_start_end(start, end):
    # Query the minimum, average, and maximum temperatures for dates between the start and end dates
    temperature_stats = session.query(func.min(Measurement.tobs),
                                      func.avg(Measurement.tobs),
                                      func.max(Measurement.tobs))\
        .filter(Measurement.date >= start, Measurement.date <= end)\
        .all()
    
    # Convert the query results to a dictionary
    temperature_dict = {'Min Temperature': temperature_stats[0][0],
                        'Avg Temperature': temperature_stats[0][1],
                        'Max Temperature': temperature_stats[0][2]}
    
    return jsonify(temperature_dict)

if __name__ == '__main__':
    app.run(debug=True)

