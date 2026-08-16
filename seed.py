import firebase_admin
from firebase_admin import credentials, firestore

# Load Firebase credentials
cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Mechanic seed data
mechanics_data = [
    {
        "name": "Hanamkonda Auto Garage",
        "address": "MG Road, Hanamkonda, Telangana",
        "latitude": 17.9959,
        "longitude": 79.5310,
        "phone": "+91 90000 12345"
    },
    {
        "name": "Sri Sai Motors",
        "address": "Kakaji Colony, Hanamkonda, Telangana",
        "latitude": 17.9965,
        "longitude": 79.5281,
        "phone": "+91 90123 45678"
    },
    {
        "name": "Raju Bike Works",
        "address": "Subedari, Hanamkonda, Telangana",
        "latitude": 17.9943,
        "longitude": 79.5295,
        "phone": "+91 91234 56789"
    },
    {
        "name": "Lucky Auto Repairs",
        "address": "NIT Warangal Road, Hanamkonda, Telangana",
        "latitude": 18.0007,
        "longitude": 79.5403,
        "phone": "+91 99887 65432"
    }
]

# Upload to Firestore
for mechanic in mechanics_data:
    db.collection('mechanics').add(mechanic)

print("✅ Hanamkonda mechanics added successfully with phone numbers.")
