from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

# Load OAuth credentials
flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)

# Generate the authentication URL
auth_url, _ = flow.authorization_url(prompt="consent")
print(f"🔗 Open this URL in your browser and authorize access:\n{auth_url}")

# Get authorization code from user
code = input("Enter the authorization code: ").strip()

# Exchange authorization code for access token
flow.fetch_token(code=code)
creds = flow.credentials

# Save credentials to a token file
with open("token.pickle", "wb") as token_file:
    pickle.dump(creds, token_file)

print("✅ Token saved successfully in token.pickle")

