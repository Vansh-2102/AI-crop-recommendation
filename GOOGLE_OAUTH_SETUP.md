# Google OAuth Setup Guide

This guide will help you set up Google OAuth authentication for the AI Crop Recommendation Platform.

## Prerequisites

1. A Google Cloud Platform account
2. Access to Google Cloud Console

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note down your project ID

## Step 2: Enable Google+ API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google+ API" and enable it
3. Also enable "Google Identity and Access Management (IAM) API"

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Configure the OAuth consent screen:
   - Choose "External" for user type
   - Fill in the required fields:
     - App name: "AI Crop Recommendation Platform"
     - User support email: Your email
     - Developer contact information: Your email
4. Create OAuth 2.0 Client ID:
   - Application type: "Web application"
   - Name: "Crop AI Web Client"
   - Authorized JavaScript origins:
     - `http://localhost:3000` (for development)
     - `http://localhost:5000` (for backend)
   - Authorized redirect URIs:
     - `http://localhost:5000/api/auth/google/callback`
     - `http://localhost:3000/auth/callback` (if using frontend callback)

## Step 4: Configure Environment Variables

1. Copy your Client ID and Client Secret from the Google Cloud Console
2. Update your `.env` file:

```env
GOOGLE_CLIENT_ID=your-actual-google-client-id
GOOGLE_CLIENT_SECRET=your-actual-google-client-secret
```

## Step 5: Update Database Schema

The database schema has been updated to support Google OAuth. Run the following to update your database:

```bash
# Activate virtual environment
venv\Scripts\activate

# Start the application (this will create new tables automatically)
python app.py
```

## Step 6: Test Google OAuth

1. Start the backend server:
   ```bash
   python app.py
   ```

2. Test the Google OAuth endpoints:
   - **Initiate Google Login**: `GET http://localhost:5000/api/auth/google/login`
   - **Verify Google Token**: `POST http://localhost:5000/api/auth/google/verify`

## New API Endpoints

### Google OAuth Endpoints

- `GET /api/auth/google/login` - Initiate Google OAuth login
- `GET /api/auth/google/callback` - Handle Google OAuth callback
- `POST /api/auth/google/verify` - Verify Google ID token (for frontend)

### Example Usage

#### Frontend Integration
```javascript
// Redirect to Google OAuth
window.location.href = 'http://localhost:5000/api/auth/google/login';

// Or verify Google ID token
const response = await fetch('/api/auth/google/verify', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    token: googleIdToken
  })
});
```

## Database Changes

The User model now includes:
- `google_id` - Google user ID
- `profile_picture` - User's Google profile picture URL
- `auth_provider` - Authentication provider ('local' or 'google')
- `password_hash` - Now nullable for Google OAuth users

## Security Notes

1. Keep your Google Client Secret secure and never commit it to version control
2. Use HTTPS in production
3. Regularly rotate your OAuth credentials
4. Monitor OAuth usage in Google Cloud Console

## Troubleshooting

### Common Issues

1. **"redirect_uri_mismatch"**: Ensure your redirect URIs in Google Cloud Console match exactly
2. **"invalid_client"**: Check your Client ID and Secret
3. **"access_denied"**: User denied permission or OAuth consent screen not configured

### Testing

You can test the Google OAuth flow by:
1. Visiting `http://localhost:5000/api/auth/google/login`
2. Completing the Google sign-in process
3. Checking if you're redirected back with a JWT token

## Production Deployment

For production:
1. Update authorized origins and redirect URIs in Google Cloud Console
2. Use environment variables for credentials
3. Enable HTTPS
4. Configure proper CORS settings
5. Set up proper error handling and logging

