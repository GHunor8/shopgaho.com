# X (Twitter) Follower Search Tool

This tool allows you to search through Twitter followers' bios for specific keywords.

## Setup Instructions

1. Twitter Developer Account Setup:
   - Go to https://developer.twitter.com/
   - Create a developer account if you don't have one
   - Create a new project and app
   - Enable OAuth 2.0 in your app settings
   - Set the callback URL to your Squarespace domain (e.g., https://yourdomain.com/callback)
   - Add required scopes: tweet.read, users.read, follows.read
   - Save your Client ID and Client Secret

2. Environment Setup:
   - Create a `.env` file with your Twitter credentials:
     ```
     TWITTER_CLIENT_ID=your_client_id
     TWITTER_CLIENT_SECRET=your_client_secret
     ```

3. Squarespace Deployment:
   - Log in to your Squarespace account
   - Go to Settings > Advanced > Code Injection
   - Add the following code to the Header section:
     ```html
     <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
     ```
   - Create a new page for the tool
   - Add a Code Block to the page
   - Copy the contents of `index.html` into the Code Block
   - Update the API endpoint URLs in the JavaScript code to match your server URL

4. Server Setup:
   - Deploy the Flask application to a hosting service (e.g., Heroku, DigitalOcean, AWS)
   - Set up SSL/HTTPS on your server
   - Update the callback URL in your Twitter Developer Portal to match your server URL
   - Install dependencies: `pip install -r requirements.txt`
   - Run the application: `gunicorn app:app`

## Files Structure
```
x automation tool/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
├── templates/         # HTML templates
│   └── index.html     # Main page template
└── README.md          # This file
```

## Security Notes
- Always use HTTPS in production
- Keep your .env file secure and never commit it to version control
- Regularly rotate your Twitter API credentials
- Monitor your API usage to stay within rate limits

## Support
For issues or questions, please contact your system administrator. 