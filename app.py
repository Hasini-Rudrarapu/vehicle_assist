from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, session
import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = '123456'

# Load Google Maps API Key securely
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', 'YOUR_DEFAULT_API_KEY_HERE')

# Initialize Firebase Admin SDK
cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred, {'projectId': 'vehicle-breakdown-38d5c'})
db = firestore.client()

# Enable CORS (optional if using frontend on a different domain/port)
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

# ---------------- ROUTES ---------------- #

@app.route('/')
@app.route('/login')
def login_page():
    return render_template('index.html')

@app.route('/sessionLogin', methods=['POST'])
def session_login():
    id_token = request.json.get('idToken')
    expires_in = 60 * 60 * 24 * 5  # 5 days
    try:
        auth.verify_id_token(id_token)
        session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)

        response = jsonify({'status': 'success'})
        response.set_cookie(
            'session',
            session_cookie,
            max_age=expires_in,
            httponly=True,
            secure=not app.debug  # Use secure=True in production
        )
        return response
    except Exception as e:
        print(f"Error during session login: {e}")
        return jsonify({'error': 'Failed to create session cookie'}), 401

@app.route('/logout')
def logout():
    response = redirect(url_for('login_page'))
    response.set_cookie('session', '', expires=0)
    return response

@app.route('/mechanics')
def mechanic_list():
    session_cookie = request.cookies.get('session')
    if not session_cookie:
        return redirect(url_for('login_page'))

    try:
        decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
    except Exception:
        return redirect(url_for('login_page'))

    user_lat = float(request.args.get('lat', 37.7749))  # Default: San Francisco
    user_lng = float(request.args.get('lng', -122.4194))

    mechanics_ref = db.collection('mechanics')
    mechanics = []
    for doc in mechanics_ref.stream():
        data = doc.to_dict()
        data['id'] = doc.id  # Add ID for form
        mechanics.append(data)

    return render_template(
        'mechanic_list.html',
        mechanics=mechanics,
        user_lat=user_lat,
        user_lng=user_lng,
        google_maps_api_key=GOOGLE_MAPS_API_KEY
    )

from flask import flash, redirect, url_for

@app.route('/request_help', methods=['GET', 'POST'])
def request_help():
    if request.method == 'POST':
        mechanic_id = request.form['mechanic_id']
        breakdown_type = request.form['breakdown_type']
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        # Save help request to database here (your logic)

        # Show message after request
        flash(f"✅ Help requested for '{breakdown_type}' successfully! A mechanic is on the way.", "success")
        return redirect(url_for('request_status'))  # create this route to show confirmation

    # On GET, show form
    mechanics = get_available_mechanics()  # your logic
    return render_template('request_help.html', mechanics=mechanics, google_maps_api_key=GOOGLE_MAPS_API_KEY)

@app.route('/wait_for_mechanic')
def wait_for_mechanic():
    session_cookie = request.cookies.get('session')
    if not session_cookie:
        return redirect(url_for('login_page'))

    try:
        decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
    except Exception:
        return redirect(url_for('login_page'))

    user_id = decoded_claims.get('uid')
    request_doc = db.collection('help_requests').document(user_id).get()

    if not request_doc.exists:
        return "No help request found."

    request_data = request_doc.to_dict()
    mechanic_id = request_data['mechanic_id']
    status = request_data.get('status', 'pending')

    if status == 'accepted':
        mechanic_doc = db.collection('mechanics').document(mechanic_id).get()
        if mechanic_doc.exists:
            mechanic = mechanic_doc.to_dict()
            cost = 200
            return render_template('request_help.html', mechanic=mechanic, cost=cost, google_maps_api_key=GOOGLE_MAPS_API_KEY)
    elif status == 'busy':
        return "<script>alert('❌ Mechanic is currently busy or unavailable. Please try again later.'); window.location='/mechanics';</script>"

    return "<script>alert('⏳ Waiting for mechanic confirmation...'); setTimeout(() => window.location.reload(), 3000);</script>"

@app.route('/live_tracking/<mechanic_id>')
def live_tracking(mechanic_id):
    session_cookie = request.cookies.get('session')
    if not session_cookie:
        return redirect(url_for('login_page'))

    try:
        decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
    except Exception:
        return redirect(url_for('login_page'))

    mechanic_ref = db.collection('mechanics').document(mechanic_id)
    mechanic = mechanic_ref.get()
    mechanic_data = mechanic.to_dict() if mechanic.exists else {}

    cost_estimate = 50
    return render_template(
        'live_tracking.html',
        mechanic=mechanic_data,
        cost=cost_estimate,
        google_maps_api_key=GOOGLE_MAPS_API_KEY
    )

@app.route('/getEmailByUsername', methods=['POST'])
def get_email_by_username():
    data = request.get_json()
    username = data.get('username', '').strip().lower()
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    users_ref = db.collection('users')
    for doc in users_ref.stream():
        user_data = doc.to_dict()
        db_username = user_data.get('username', '').strip().lower()
        if db_username == username:
            return jsonify({'email': user_data.get('email')})
    return jsonify({'error': 'Username not found'}), 404

@app.route('/listUsernames', methods=['GET'])
def list_usernames():
    users_ref = db.collection('User')
    usernames = [doc.to_dict().get('Name') for doc in users_ref.stream() if doc.to_dict().get('Name')]
    return jsonify({'usernames': usernames})
@app.route('/request_status')
def request_status():
    return render_template('status.html')
@app.route('/select_breakdown', methods=['GET', 'POST'])
def select_breakdown():
    return render_template('select_breakdown.html')



# ---------------- MAIN ---------------- #

if __name__ == '__main__':
    app.run(debug=True)
