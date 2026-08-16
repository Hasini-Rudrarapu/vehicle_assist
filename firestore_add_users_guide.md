# Guide to Add User Data to Firestore for Testing

To enable username-based login, you need to add user documents to your Firestore database with the following fields:

- `username`: The username string used for login.
- `email`: The email address associated with the user (used for Firebase Authentication).
- Other optional fields as needed.

## Steps to Add Users in Firestore Console

1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Select your project: **vehicle-breakdown-38d5c**.
3. In the left sidebar, click on **Firestore Database**.
4. If you haven't set up Firestore yet, follow the prompts to create a Firestore database.
5. Click on **Start Collection**.
6. Enter the collection name as `users`.
7. Add a document with an auto-generated ID or a custom ID.
8. Add fields:
   - `username` (string): e.g., "Hasini"
   - `email` (string): e.g., "hasini@example.com"
9. Save the document.
10. Repeat for other users as needed.

## Testing

- Use the usernames you added in the Firestore `users` collection to log in.
- Use the corresponding email's password for Firebase Authentication.

## Notes

- Make sure the emails you use are registered users in Firebase Authentication.
- You can add users via Firebase Authentication console or programmatically.

If you want, I can help you create a script to add users programmatically.

Let me know if you need further assistance.
