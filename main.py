from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_bcrypt import Bcrypt
from joblib import load
from collections import defaultdict
import re
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import AdaBoostRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import json
from models import db, Users, Trees, Ubers

app = Flask(__name__)

# Configure the database URI
app.config['SECRET_KEY'] = 'nissijeapaglinawan-ml-web-app'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/itd105-webapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

bcrypt = Bcrypt(app)

# Initialize SQLAlchemy
db.init_app(app)

with app.app_context():
    db.create_all()

# Load the tree trained model
treeModel = load('templates/model-pkl/tree_logreg_model.pkl')

@app.route('/')
def home():
    return render_template('dashboard.html', result=None, user_input=None)

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        fullname = request.form['name']
        password = request.form['password']
        email = request.form['email']

        user_exists = Users.query.filter_by(email=email).first() is not None

        if user_exists:
            message = 'Email already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address !'
        elif not fullname or not password or not email:
            message = 'Please fill out the form !'
        else:
            hashed_password = bcrypt.generate_password_hash(password)
            new_user = Users(name=fullname, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            message = 'You have successfully registered !'
    elif request.method == 'POST':
        message = 'Please fill out the form !'
    return render_template('register.html', message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == '' or password == '':
            message = 'Please enter email and password !'
        else:
            user = Users.query.filter_by(email=email).first()
            print(user)

            if user is None:
                message = 'Please enter correct email / password !'
            else:
                if not bcrypt.check_password_hash(user.password, password):
                    message = 'Please enter correct email and password !'
                else:
                    session['loggedin'] = True
                    session['userid'] = user.id
                    session['name'] = user.name
                    session['email'] = user.email
                    message = 'Logged in successfully !'
                    return redirect(url_for('dashboard'))

    return render_template('login.html', message=message)

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:
        trees = Trees.query.all()
        ubers = Ubers.query.all()

        # Calculate total tree count
        total_tree_count = len(trees)

        # Calculate total tree count
        total_uber_count = len(ubers)

        return render_template("dashboard.html", trees=trees, ubers=ubers, total_tree_count=total_tree_count,total_uber_count=total_uber_count)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/read_csv')
def read_csv():
    if 'loggedin' in session:
        return render_template('read_csv.html', result=None, user_input=None)
    return redirect(url_for('login'))



#### CLASSIFICATION MODEL ###
@app.route("/trees", methods=['GET', 'POST'])
def trees():
    if 'loggedin' in session:
        trees = Trees.query.all()

        return render_template("trees.html", trees=trees)
    return redirect(url_for('login'))

@app.route('/predict_trees')
def predict_trees():
    if 'loggedin' in session:
        return render_template('predict_trees.html', result=None, user_input=None)
    return redirect(url_for('login'))

@app.route('/save_tree', methods=['POST'])
def save_tree():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST':
            No = request.form['No']
            Plot = request.form['Plot']
            Subplot = request.form['Subplot']
            Species = request.form['Species']
            Light_ISF = request.form['Light_ISF']
            Light_Cat = request.form['Light_Cat']
            Core = request.form['Core']
            Soil = request.form['Soil']
            Adult = request.form['Adult']
            Sterile = request.form['Sterile']
            Conspecific = request.form.get('Conspecific', '')  # Add this line
            Myco = request.form.get('Myco', '')  # Add this line
            SoilMyco = request.form.get('SoilMyco', '')  # Add this line
            PlantDate = request.form.get('PlantDate', '')  # Add this line
            AMF = request.form.get('AMF', '')  # Add this line
            EMF = request.form.get('EMF', '')  # Add this line
            Phenolics = request.form.get('Phenolics', '')  # Add this line
            Lignin = request.form['Lignin']
            NSC = request.form['NSC']
            Census = request.form['Census']
            Time = request.form['Time']
            Harvest = request.form['Harvest']
            Alive = request.form['Alive']
            Event = request.form['Event']

            action = request.form['action']

            if action == 'updateTree':
                treeid = request.form['treeid']
                tree = Trees.query.get(treeid)

                tree.No = No
                tree.Plot = Plot
                tree.Subplot = Subplot
                tree.Species = Species
                tree.Light_ISF = Light_ISF
                tree.Light_Cat = Light_Cat
                tree.Core = Core
                tree.Soil = Soil
                tree.Adult = Adult
                tree.Sterile = Sterile
                tree.Conspecific = Conspecific
                tree.Myco = Myco
                tree.SoilMyco = SoilMyco
                tree.PlantDate = PlantDate
                tree.AMF = AMF
                tree.EMF = EMF
                tree.Phenolics = Phenolics
                tree.Lignin = Lignin
                tree.NSC = NSC
                tree.Census = Census
                tree.Time = Time
                tree.Harvest = Harvest
                tree.Alive = Alive
                tree.Event = Event

                db.session.commit()
                print("UPDATE tree")
            else:
                # Assuming 'uploadFile' is not relevant for the tree table, remove if not needed.
                tree = Trees(

                    No=No,
                    Plot=Plot,
                    Subplot=Subplot,
                    Species=Species,
                    Light_ISF=Light_ISF,
                    Light_Cat=Light_Cat,
                    Core=Core,
                    Soil=Soil,
                    Adult=Adult,
                    Sterile=Sterile,
                    Conspecific=Conspecific,
                    Myco=Myco,
                    SoilMyco=SoilMyco,
                    PlantDate=PlantDate,
                    AMF=AMF,
                    EMF=EMF,
                    Phenolics=Phenolics,
                    Lignin=Lignin,
                    NSC=NSC,
                    Census=Census,
                    Time=Time,
                    Harvest=Harvest,
                    Alive=Alive,
                    Event=Event
                )
                db.session.add(tree)
                db.session.commit()
                print("INSERT INTO trees")
            return redirect(url_for('trees'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("trees.html", msg=msg)
    return redirect(url_for('login'))


@app.route("/edit_tree", methods=['GET', 'POST'])
def edit_tree():
    msg = ''
    if 'loggedin' in session:
        treeid = request.args.get('treeid')
        print(treeid)
        tree = Trees.query.get(treeid)

        return render_template("edit_trees.html", tree=tree)
    return redirect(url_for('login'))

@app.route("/delete_tree", methods=['GET'])
def delete_tree():
    if 'loggedin' in session:
        treeid = request.args.get('treeid')
        tree = Trees.query.get(treeid)

        db.session.delete(tree)
        db.session.commit()

        return redirect(url_for('trees'))

    return redirect(url_for('login'))

@app.route('/predictTree', methods=['POST'])
def predictTree():
    if request.method == 'POST':
        features = {
            'No': float(request.form['No']),
            'Plot': float(request.form['Plot']),
            'Subplot': request.form['Subplot'],
            'Species': request.form['Species'],
            'Light_ISF': float(request.form['Light_ISF']),
            'Light_Cat': request.form['Light_Cat'],
            'Core': float(request.form['Core']),
            'Soil': request.form['Soil'],
            'Adult': float(request.form['Adult']),
            'Sterile': request.form['Sterile'],
            'Conspecific': request.form['Conspecific'],
            'Myco': request.form['Myco'],
            'SoilMyco': request.form['SoilMyco'],
            'PlantDate': request.form['PlantDate'],
            'AMF': request.form['AMF'],
            'EMF': request.form['EMF'],
            'Phenolics': request.form['Phenolics'],
            'Lignin': float(request.form['Lignin']),
            'NSC': float(request.form['NSC']),
            'Census': float(request.form['Census']),
            'Time': float(request.form['Time']),
            'Harvest': float(request.form['Harvest']),
            'Alive': float(request.form['Alive']),
        }

        # Make prediction using the loaded model
        prediction = treeModel.predict(pd.DataFrame([features]))[0]
        result = "SURVIVE" if prediction == 1 else "DEAD"

        return render_template('predict_trees.html', result=result, user_input=features)

@app.route('/tree_save_to_db', methods=['POST'])
def tree_save_to_db():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        Event = int(request.form['Event'])

        try:
            user_input_dict = json.loads(user_input)

            if isinstance(user_input_dict, dict):
                new_tree = Trees(**user_input_dict, Event=Event)
                db.session.add(new_tree)
                db.session.commit()

                return jsonify({'status': 'success'}), 200
            else:
                return jsonify({'status': 'error', 'message': 'Invalid user input format'}), 500
        except json.JSONDecodeError as e:
            return jsonify({'status': 'error', 'message': 'Error decoding JSON: {}'.format(str(e))}), 500
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/chart_trees')
def chart_trees():
    # Fetch actual data from the database
    trees_data = Trees.query.all()

    # Preprocess data to aggregate similar labels (Species)
    aggregated_data = defaultdict(float)
    for tree in trees_data:
        # Assuming Species is a string, modify this if it's another type
        label = str(tree.Species)
        # Aggregate Adult counts for each unique Species
        aggregated_data[label] += float(tree.Adult)

    # Prepare data for the bar chart
    bar_chart_data = {
        'labels': list(aggregated_data.keys()),
        'datasets': [{
            'label': 'Adult',
            'data': list(aggregated_data.values()),
            'backgroundColor': 'rgba(54, 162, 235, 0.2)',
            'borderColor': 'rgba(54, 162, 235, 1)',
            'borderWidth': 1
        }]
    }

    # Preprocess data to aggregate similar labels (Species)
    aggregated_data = defaultdict(float)
    for tree in trees_data:
        # Assuming Species is a string, modify this if it's another type
        label = str(tree.Species)
        # Aggregate Harvest counts for each unique Species
        aggregated_data[label] += float(tree.Harvest)

    # Prepare data for the area chart
    area_chart_data = {
        'labels': list(aggregated_data.keys()),
        'datasets': [{
            'label': 'Total Harvest',
            'data': list(aggregated_data.values()),
            'borderColor': '#3498DB',
            'borderWidth': 1,
        }]
    }

    # Preprocess data to aggregate similar labels (Species) for Alive count
    alive_data = defaultdict(float)
    for tree in trees_data:
        label = str(tree.Species)
        alive_data[label] += float(tree.Alive)

    # Prepare data for the line chart
    line_chart_data = {
        'labels': list(alive_data.keys()),
        'datasets': [{
            'label': 'Total Alive',
            'data': list(alive_data.values()),
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1,
            'fill': False,  # Do not fill the area under the line
            'tension': 0.1,  # Set tension for a smooth curve
        }]
    }

    # Preprocess data to aggregate values for unique Soil types
    aggregated_data = defaultdict(float)
    for tree in trees_data:
        # Assuming Soil is a string, modify this if it's another type
        label = str(tree.Soil)
        # Aggregate Event values for each unique Soil type
        aggregated_data[label] += float(tree.Harvest)

    # Prepare data for the pie chart
    pie_chart_data = {
        'labels': list(aggregated_data.keys()),
        'datasets': [{
            'data': list(aggregated_data.values()),
            'backgroundColor': ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)'],
            'borderColor': ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)'],
            'borderWidth': 1
        }]
    }

    # Preprocess data to aggregate values for unique Soil types
    aggregated_data = defaultdict(float)
    for tree in trees_data:
        # Assuming Soil is a string, modify this if it's another type
        label = str(tree.Soil)
        # Aggregate Alive values for each unique Soil type
        aggregated_data[label] += float(tree.Alive)

    # Prepare data for the donut chart
    donut_chart_data = {
        'labels': list(aggregated_data.keys()),
        'datasets': [{
            'data': list(aggregated_data.values()),
            'backgroundColor': ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)'],
            'borderColor': ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)'],
            'borderWidth': 1
        }]
    }

    # Preprocess data to aggregate values for unique Events
    events_data = defaultdict(lambda: {'Total Harvest': 0, 'Total Alive': 0})
    for tree in trees_data:
        label = str(tree.Species)
        events_data[label]['Total Harvest'] += float(tree.Harvest)
        events_data[label]['Total Alive'] += float(tree.Alive)

    # Prepare data for the scatter chart
    scatter_chart_data = {
        'labels': list(events_data.keys()),
        'datasets': [{
            'label': 'Total Harvest',
            'data': [{'x': label, 'y': data['Total Harvest']} for label, data in events_data.items()],
            'backgroundColor': 'rgba(255, 99, 132, 0.2)',
            'borderColor': 'rgba(255, 99, 132, 1)',
            'borderWidth': 1
        }, {
            'label': 'Total Alive',
            'data': [{'x': label, 'y': data['Total Alive']} for label, data in events_data.items()],
            'backgroundColor': 'rgba(54, 162, 235, 0.2)',
            'borderColor': 'rgba(54, 162, 235, 1)',
            'borderWidth': 1
        }]
    }

    # Process data for radarChart1
    radar_chart1_data = {'labels': ['Alive', 'Dead'], 'datasets': []}

    alive_count = sum(tree.Alive for tree in trees_data if tree.Event == 0)
    dead_count = sum(tree.Harvest for tree in trees_data if tree.Event == 1)

    radar_chart1_data['datasets'].append({
        'label': 'Total Harvest Count',
        'data': [alive_count, dead_count],
        'backgroundColor': 'rgba(255, 99, 132, 0.2)',
        'borderColor': 'rgba(255, 99, 132, 1)',
        'borderWidth': 1
    })

    # Process data for radarChart2
    radar_chart2_data = {'labels': ['Alive', 'Dead'], 'datasets': []}

    alive_count = sum(tree.Alive for tree in trees_data if tree.Event == 0)
    dead_count = sum(tree.Alive for tree in trees_data if tree.Event == 1)

    radar_chart2_data['datasets'].append({
        'label': 'Total Alive Count',
        'data': [alive_count, dead_count],
        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
        'borderColor': 'rgba(54, 162, 235, 1)',
        'borderWidth': 1
    })

    return render_template('chart_trees.html', bar_chart_data=bar_chart_data, area_chart_data=area_chart_data, line_chart_data=line_chart_data, pie_chart_data=pie_chart_data,  donut_chart_data=donut_chart_data, scatter_chart_data=scatter_chart_data, radar_chart1_data=radar_chart1_data, radar_chart2_data=radar_chart2_data)


#### REGRESSION MODEL ###
# Load the uber trained model
uberModel = load('templates/model-pkl/uber_xgb_model.pkl')

@app.route("/ubers", methods=['GET', 'POST'])
def ubers():
    if 'loggedin' in session:
        ubers = Ubers.query.all()

        return render_template("ubers.html", ubers=ubers)
    return redirect(url_for('login'))

@app.route('/save_uber', methods=['POST'])
def save_uber():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST':
            fare_amount = request.form['fare_amount']
            pickup_longitude = request.form['pickup_longitude']
            pickup_latitude = request.form['pickup_latitude']
            dropoff_longitude = request.form['dropoff_longitude']
            dropoff_latitude = request.form['dropoff_latitude']
            passenger_count = request.form['passenger_count']
            distance = request.form['distance']

            action = request.form['action']

            if action == 'updateUber':
                uberid = request.form['uberid']
                uber = Trees.query.get(uberid)

                uber.fare_amount = fare_amount
                uber.pickup_longitude = pickup_longitude
                uber.pickup_latitude = pickup_latitude
                uber.dropoff_longitude = dropoff_longitude
                uber.dropoff_latitude = dropoff_latitude
                uber.passenger_count = passenger_count
                uber.distance = distance

                db.session.commit()
                print("UPDATE uber")
            else:
                # Assuming 'uploadFile' is not relevant for the uber table, remove if not needed.
                uber = Ubers(

                    fare_amount=fare_amount,
                    pickup_longitude=pickup_longitude,
                    pickup_latitude=pickup_latitude,
                    dropoff_longitude=dropoff_longitude,
                    dropoff_latitude=dropoff_latitude,
                    passenger_count=passenger_count,
                    distance=distance,
                )
                db.session.add(uber)
                db.session.commit()
                print("INSERT INTO ubers")
            return redirect(url_for('ubers'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("ubers.html", msg=msg)
    return redirect(url_for('login'))

@app.route("/edit_uber", methods=['GET', 'POST'])
def edit_uber():
    msg = ''
    if 'loggedin' in session:
        uberid = request.args.get('uberid')
        print(uberid)
        uber = Ubers.query.get(uberid)

        return render_template("edit_ubers.html", uber=uber)
    return redirect(url_for('login'))

@app.route("/delete_uber", methods=['GET'])
def delete_uber():
    if 'loggedin' in session:
        uberid = request.args.get('uberid')
        uber = Ubers.query.get(uberid)

        db.session.delete(uber)
        db.session.commit()

        return redirect(url_for('ubers'))

    return redirect(url_for('login'))

@app.route('/predict_ubers')
def predict_ubers():
    if 'loggedin' in session:
        return render_template('predict_ubers.html', result=None, user_input=None)
    return redirect(url_for('login'))

@app.route('/predictUber', methods=['POST'])
def predictUber():
    if 'loggedin' in session:
        if request.method == 'POST':
            # Retrieve user input from the form
            user_input = {
                'pickup_longitude': float(request.form['pickup_longitude']),
                'pickup_latitude': float(request.form['pickup_latitude']),
                'dropoff_longitude': float(request.form['dropoff_longitude']),
                'dropoff_latitude': float(request.form['dropoff_latitude']),
                'passenger_count': int(request.form['passenger_count']),
                'distance': float(request.form['distance']),
            }

            # Make prediction using the loaded model
            fare_prediction = uberModel.predict(pd.DataFrame([user_input]))[0]

            return render_template('predict_ubers.html', prediction=fare_prediction, user_input=user_input)

        return render_template('predict_ubers.html', result=None, user_input=None)
    return redirect(url_for('login'))

@app.route('/uber_save_to_db', methods=['POST'])
def uber_save_to_db():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        fare_amount = float(request.form['fare_amount'])

        try:
            user_input_dict = json.loads(user_input)

            if isinstance(user_input_dict, dict):
                new_uber = Ubers(**user_input_dict, fare_amount=fare_amount)
                db.session.add(new_uber)
                db.session.commit()

                return jsonify({'status': 'success'}), 200
            else:
                return jsonify({'status': 'error', 'message': 'Invalid user input format'}), 500
        except json.JSONDecodeError as e:
            return jsonify({'status': 'error', 'message': 'Error decoding JSON: {}'.format(str(e))}), 500
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/chart_ubers')
def chart_ubers():
    # Fetch actual data from the database
    uber_data = Ubers.query.all()

    # Preprocess data to aggregate fare_amount for each passenger_count
    aggregated_data = defaultdict(float)
    for uber in uber_data:
        passenger_count = uber.passenger_count
        fare_amount = float(uber.fare_amount)
        aggregated_data[passenger_count] += fare_amount

    # Prepare data for the bar chart
    bar_chart_data = {
        'labels': list(aggregated_data.keys()),
        'datasets': [{
            'label': 'Fare Amount',
            'data': list(aggregated_data.values()),
            'backgroundColor': 'rgba(54, 162, 235, 0.2)',
            'borderColor': 'rgba(54, 162, 235, 1)',
            'borderWidth': 1
        }]
    }

    # Preprocess data for the area chart
    area_chart_data = {
        'labels': [uber.distance for uber in uber_data],
        'datasets': [{
            'label': 'Fare Amount',
            'data': [uber.fare_amount for uber in uber_data],
            'borderColor': '#3498DB',
            'borderWidth': 1,
            'backgroundColor': 'rgba(45, 85, 255)',
            'fill': True,  # Fill the area under the line
            'tension': 0.1,  # Set tension for a smooth curve
        }]
    }

    # Preprocess data to aggregate values for unique passenger_count
    aggregated_data = defaultdict(float)
    for uber in uber_data:
        # Assuming passenger_count is an integer
        label = uber.passenger_count
        # Aggregate distance values for each unique passenger_count
        aggregated_data[label] += float(uber.distance)

    # Prepare data for the line chart
    line_chart_data = {
        'labels': list(aggregated_data.keys()),
        'datasets': [{
            'label': 'Distance',
            'data': list(aggregated_data.values()),
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1,
            'fill': False,  # Do not fill the area under the line
            'tension': 0.1,  # Set tension for a smooth curve
            'pointRadius': 6,  # Adjust the point radius as needed
            'pointHoverRadius': 8  # Adjust the hover radius as needed
        }]
    }

    # Preprocess data to aggregate values for unique Soil types
    aggregated_data = defaultdict(float)
    for uber in uber_data:
        # Assuming Soil is a string, modify this if it's another type
        label = str(uber.passenger_count)
        # Aggregate Event values for each unique Soil type
        aggregated_data[label] += float(uber.fare_amount)

    # Prepare data for the pie chart
    pie_chart_data = {
        'labels': list(aggregated_data.keys()),
        'datasets': [{
            'data': list(aggregated_data.values()),
            'backgroundColor': ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)'],
            'borderColor': ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)'],
            'borderWidth': 1
        }]
    }

    # Preprocess data to aggregate values for unique Soil types
    aggregated_data = defaultdict(float)
    for uber in uber_data:
        # Assuming Soil is a string, modify this if it's another type
        label = str(uber.passenger_count)
        # Aggregate Event values for each unique Soil type
        aggregated_data[label] += float(uber.fare_amount)

    # Prepare data for the pie chart
    donut_chart_data = {
        'labels': list(aggregated_data.keys()),
        'datasets': [{
            'data': list(aggregated_data.values()),
            'backgroundColor': ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)'],
            'borderColor': ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)'],
            'borderWidth': 1
        }]
    }

    # Preprocess data to aggregate values for unique passenger_count
    aggregated_data = defaultdict(list)

    for uber in uber_data:
        # Assuming passenger_count is an integer, modify this if it's another type
        label = uber.passenger_count
        # Aggregate data for each unique passenger_count
        aggregated_data[label].append({
            'x': uber.passenger_count,
            'y_distance': uber.distance,
            'y_fare_amount': uber.fare_amount
        })

    # Prepare data for the scatter chart
    scatter_chart_data = {
        'labels': list(aggregated_data.keys()),
        'datasets': [
            {
                'label': 'Distance',
                'data': [{'x': data['x'], 'y': data['y_distance']} for data in aggregated_data[label]],
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1,
                'pointRadius': 6,
                'pointHoverRadius': 8
            },
            {
                'label': 'Fare Amount',
                'data': [{'x': data['x'], 'y': data['y_fare_amount']} for data in aggregated_data[label]],
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1,
                'pointRadius': 6,
                'pointHoverRadius': 8
            }
        ]
    }

    return render_template('chart_ubers.html', bar_chart_data=bar_chart_data, area_chart_data=area_chart_data,
                           line_chart_data=line_chart_data, pie_chart_data=pie_chart_data,
                           donut_chart_data=donut_chart_data, scatter_chart_data=scatter_chart_data)


### TRAIN REGRESSION DATA ###
# # Load the XGBoost model
# with open('templates/model-pkl/uber_xgb_model.pkl', 'rb') as model_file:
#     xgb_model = pickle.load(model_file)
#
# @app.route('/train_uber')
# def index():
#     return render_template('train_uber.html')
#
# @app.route('/trainUber', methods=['POST'])
# def train_model():
#     try:
#         # Get the uploaded file
#         file = request.files['file']
#
#         # Load the new data
#         new_data = pd.read_csv(file)
#
#         # Assume the same features and target as in the initial model
#         features = ['pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude', 'passenger_count', 'distance']
#         target = 'fare_amount'
#
#         # Split the new data into features and target
#         X_new = new_data[features]
#         y_new = new_data[target]
#
#         # Standardize the features
#         scaler = StandardScaler()
#         X_new_scaled = scaler.fit_transform(X_new)
#
#         # Retrain the model on the new data
#         xgb_model.fit(X_new_scaled, y_new)
#
#         # Save the updated model
#         with open('templates/model-pkl/uber_xgb_model-updated.pkl', 'wb') as model_file:
#             pickle.dump(xgb_model, model_file)
#
#         # Send a success message
#         return jsonify({'status': 'success', 'message': 'Model trained successfully!'})
#     except Exception as e:
#         # Send an error message
#         return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    # Create the "trees" table if it doesn't exist
    with app.app_context():
        db.create_all()

    app.run(debug=True)

# if __name__ == '__main__':
#     app.run(debug=True)

