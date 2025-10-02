import os
from flask import Flask, jsonify, render_template, request, redirect, session, url_for
from requests_oauthlib import OAuth2Session

app = Flask(__name__)

# Get this information by registering your app at https://developer.id.me
client_id              = '28bf5c72de76f94a5fb1d9454e347d4e'
client_secret          = '3e9f2e9716dba6ec74a2e42e90974828'
redirect_uri           = 'http://IP:5000/callback'
authorization_base_url = 'https://api.id.me/oauth/authorize'
token_url              = 'https://api.id.me/oauth/token'
attributes_url         = 'https://api.id.me/api/public/v3/attributes.json'

@app.route("/")

def demo():
    return render_template('index.html')

@app.route("/callback", methods=["GET"])
def callback():
    # Exchange your code for an access token
    idme  = OAuth2Session(client_id, redirect_uri=redirect_uri)
    token = idme.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)

    # Extract the access token from the token response
    access_token = token.get('access_token')
    refresh_token = token.get('refresh_token')
    token_type = token.get('token_type', 'Bearer')
    expires_in = token.get('expires_in')
    
    # Store tokens in session for later use
    session['oauth_token'] = token
    session['access_token'] = access_token
    session['refresh_token'] = refresh_token
    
    # Optional: Print token info for debugging (remove in production)
    print(f"Access Token: {access_token}")
    print(f"Token Type: {token_type}")
    print(f"Expires In: {expires_in} seconds")
    
    # You can also return the token info as JSON for API usage
    # return jsonify({
    #     'access_token': access_token,
    #     'token_type': token_type,
    #     'expires_in': expires_in
    # })

    return redirect(url_for('.profile'))

@app.route("/profile", methods=["GET"])
def profile():
    # Fetching the user's attributes using an OAuth 2 token.
    idme = OAuth2Session(client_id, token=session['oauth_token'])
    payload = idme.get(attributes_url).json()

    session['profile'] = 'true'
    return jsonify(payload)

@app.route("/token", methods=["GET"])
def get_token():
    # Return just the access token for API usage
    if 'access_token' not in session:
        return jsonify({'error': 'No access token found. Please authenticate first.'}), 401
    
    return jsonify({
        'access_token': session['access_token'],
        'token_type': 'Bearer',
        'expires_in': session.get('oauth_token', {}).get('expires_in')
    })

@app.route("/userinfo", methods=["GET"])
def get_userinfo():
    # Call ID.me userinfo endpoint with access token
    if 'access_token' not in session:
        return jsonify({'error': 'No access token found. Please authenticate first.'}), 401
    
    access_token = session['access_token']
    userinfo_url = 'https://api.id.me/api/public/v3/userinfo'
    
    try:
        # Make request to userinfo endpoint with access token
        import requests
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(userinfo_url, headers=headers)
        
        if response.status_code == 200:
            userinfo_data = response.json()
            # Store userinfo in session for later use
            session['userinfo'] = userinfo_data
            return jsonify(userinfo_data)
        else:
            return jsonify({
                'error': 'Failed to fetch user info',
                'status_code': response.status_code,
                'message': response.text
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'error': 'Error calling userinfo endpoint',
            'message': str(e)
        }), 500

if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['DEBUG'] = "1"
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app.secret_key = os.urandom(24)
    app.run(host='0.0.0.0',debug=True)
