from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), index=True, unique=True)
    email = db.Column(db.String(150), index=True, unique=True)
    password = db.Column(db.String(255), index=True, unique=True)

class Trees(db.Model):
    __tablename__ = "trees"
    id = db.Column(db.Integer, primary_key=True)
    No = db.Column(db.Float, index=True, unique=True)
    Plot = db.Column(db.Float)
    Subplot = db.Column(db.String(255))
    Species = db.Column(db.String(255))
    Light_ISF = db.Column(db.Float)
    Light_Cat = db.Column(db.String(255))
    Core = db.Column(db.Float)
    Soil = db.Column(db.String(255))
    Adult = db.Column(db.Float)
    Sterile = db.Column(db.String(255))
    Conspecific = db.Column(db.String(255))
    Myco = db.Column(db.String(255))
    SoilMyco = db.Column(db.String(255))
    PlantDate = db.Column(db.String(255))
    AMF = db.Column(db.String(255))
    EMF = db.Column(db.String(255))
    Phenolics = db.Column(db.String(255))
    Lignin = db.Column(db.Float)
    NSC = db.Column(db.Float)
    Census = db.Column(db.Float)
    Time = db.Column(db.Float)
    Harvest = db.Column(db.Float)
    Alive = db.Column(db.Float)
    Event = db.Column(db.Integer, nullable=False)

class Ubers(db.Model):
    __tablename__ = "ubers"
    id = db.Column(db.Integer, primary_key=True)
    fare_amount = db.Column(db.Float, nullable=False)
    pickup_longitude = db.Column(db.String(255))
    pickup_latitude = db.Column(db.String(255))
    dropoff_longitude = db.Column(db.String(255))
    dropoff_latitude = db.Column(db.String(255))
    passenger_count = db.Column(db.Integer)
    distance = db.Column(db.Float)