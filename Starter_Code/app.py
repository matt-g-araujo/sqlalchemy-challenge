# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement_table = Base.classes.measurement
station_table = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
        
    )

@app.route("/api/v1.0/precipitation")

def precipitation():
    session = Session(engine)

    first_date = session.query(measurement_table.date).order_by(measurement_table.date.desc()).first()[0]
    last_date = dt.datetime.strptime(first_date, '%Y-%m-%d').date() - dt.timedelta(days=365)
    new_data = session.query(measurement_table.date,measurement_table.prcp).filter(measurement_table.date >= last_date).all()
    new_dict = {k:v for (k,v) in new_data}
    return jsonify ({'Date':'Precipitation in Inches'},new_dict)



def precipitation():
    session = Session(engine)
    most_recent_date_s = session.query(Measurement.date).order_by(desc(Measurement.date)).first()[0]
    most_recent_date = pd.to_datetime(most_recent_date_s)

    # Calculate the date one year from the last date in data set.
    one_year_ago_date = most_recent_date - pd.DateOffset(years=1)
    one_year_ago_date_str = one_year_ago_date.strftime('%Y-%m-%d')

    # query the last 12 months of precipitation data
    prcp_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago_date_str).all()

    # convert the query results to a dictionary using date as the key and prcp as the value
    prcp_dict = {}
    for result in prcp_results:
        prcp_dict[result.date] = result.prcp

    # close the session
    session.close()

    # return the JSON representation of the dictionary
    return jsonify(prcp_dict)






@app.route("/api/v1.0/stations")

def stations():
    session = Session(engine)
    station_all = session.query(station_table.station).all()
    return jsonify (list(np.ravel(station_all)))

@app.route("/api/v1.0/tobs")

def tobs():
    session = Session(engine)
    most_active = session.query(measurement_table.station,func.count(measurement_table.station)).\
    group_by(measurement_table.station).\
    order_by(func.count(measurement_table.station).desc()).all()
    recent_date = session.query(measurement_table.date).order_by(measurement_table.date.desc()).first()
    prev_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d').date() - dt.timedelta(days=365)
    station_data = session.query(measurement_table.tobs,measurement_table.station).\
        filter(measurement_table.station == most_active[0][0]).\
        filter(measurement_table.date >= prev_date).all() 
    return jsonify (('Most Active Station TOBs Data'),list(np.ravel(station_data)))

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")

def date_temp(start = None, end = None):
    session = Session(engine)
    start = dt.datetime.strptime(start, '%Y-%m-%d').date()
    if not end:
        lowest_temp = session.query(func.min(measurement_table.tobs)).\
            filter(measurement_table.date >= start).scalar() 
            
        highest_temp = session.query(func.max(measurement_table.tobs)).\
            filter(measurement_table.date >= start).scalar()
        avg_temp = session.query(func.round(func.avg(measurement_table.tobs)),2).\
            filter(measurement_table.date >= start).scalar()
        
        return jsonify({'Lowest Temp':lowest_temp, 
                        'Highest Temp': highest_temp, 
                        'Avg Temp' :avg_temp})
    end = dt.datetime.strptime(end, '%Y-%m-%d').date()
    lowest_temp = session.query(func.min(measurement_table.tobs)).\
        filter(measurement_table.date >= start).filter(measurement_table.date <= end).scalar()
    highest_temp = session.query(func.max(measurement_table.tobs)).\
        filter(measurement_table.date >= start).filter(measurement_table.date <= end).scalar()
    avg_temp = session.query(func.round(func.avg(measurement_table.tobs)),2).\
        filter(measurement_table.date >= start).filter(measurement_table.date <= end).scalar()
    return jsonify({'Lowest Temperature':lowest_temp, 
                        'Highest Temperature': highest_temp, 
                        'Avg Temperature' :avg_temp})

#start the app
if __name__ == "__main__":
    app.run(debug=True)


