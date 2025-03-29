from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import tweepy
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

class TwitterAPI:
    def __init__(self):
        self.client_id = os.getenv('TWITTER_CLIENT_ID')
        self.client_secret = os.getenv('TWITTER_CLIENT_SECRET')
        self.oauth2_user_handler = None
        self.client = None

    def get_auth_url(self):
        """Get Twitter OAuth2 authorization URL"""
        self.oauth2_user_handler = tweepy.OAuth2UserHandler(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri="https://shopgaho.com/callback",
            scope=["tweet.read", "users.read", "follows.read"]
        )
        return self.oauth2_user_handler.get_authorization_url()

    def handle_callback(self, code):
        """Handle OAuth2 callback and get access token"""
        try:
            access_token = self.oauth2_user_handler.fetch_token(code)
            self.client = tweepy.Client(access_token["access_token"])
            return True
        except Exception as e:
            print(f"Error getting access token: {str(e)}")
            return False

    def search_followers(self, username, keywords):
        """Search followers' bios for keywords"""
        if not self.client:
            return {"error": "Not authenticated"}, 401
            
        try:
            # Get user ID
            user = self.client.get_user(username=username)
            if not user.data:
                return {'error': 'User not found'}, 404
            
            # Get followers
            followers = self.client.get_users_followers(
                user.data.id,
                max_results=100,
                user_fields=['description']
            )
            
            if not followers.data:
                return {'error': 'No followers found'}, 404
            
            # Search bios
            matches = []
            for follower in followers.data:
                if follower.description:
                    matched_keywords = [
                        keyword.strip() 
                        for keyword in keywords 
                        if keyword.strip().lower() in follower.description.lower()
                    ]
                    if matched_keywords:
                        matches.append({
                            'username': follower.username,
                            'bio': follower.description,
                            'matched_keywords': matched_keywords
                        })
            
            return matches, 200
            
        except tweepy.TweepyException as e:
            return {'error': str(e)}, 500

# Create a global rate limiter
rate_limiter = {
    'last_request': 0,
    'requests_made': 0,
    'limit': 10,
    'window': 60  # 1 minute window
}

# Create a global Twitter API instance
twitter_api = TwitterAPI()

@app.route('/')
def home():
    """Render the home page"""
    return render_template('index.html')

@app.route('/auth')
def auth():
    """Start Twitter OAuth2 flow"""
    auth_url = twitter_api.get_auth_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Handle Twitter OAuth2 callback"""
    code = request.args.get('code')
    if not code:
        return redirect(url_for('home'))
    
    if twitter_api.handle_callback(code):
        session['authenticated'] = True
        return redirect(url_for('home'))
    else:
        return "Authentication failed", 400

@app.route('/search', methods=['POST'])
def search():
    """Search followers' bios"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    username = data.get('username')
    keywords = data.get('keywords', '').split(',')
    
    if not username or not keywords:
        return jsonify({'error': 'Missing username or keywords'}), 400
    
    # Check rate limit
    current_time = time.time()
    if current_time - rate_limiter['last_request'] > rate_limiter['window']:
        rate_limiter['requests_made'] = 0
        rate_limiter['last_request'] = current_time
    
    if rate_limiter['requests_made'] >= rate_limiter['limit']:
        return jsonify({'error': 'Rate limit reached'}), 429
    
    rate_limiter['requests_made'] += 1
    
    # Remove @ symbol if present
    username = username.lstrip('@')
    
    # Search followers
    matches, status_code = twitter_api.search_followers(username, keywords)
    
    if status_code == 200:
        return jsonify({
            'matches': matches,
            'total_matches': len(matches)
        })
    else:
        return jsonify(matches), status_code

@app.route('/logout')
def logout():
    """Clear session and log out"""
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 