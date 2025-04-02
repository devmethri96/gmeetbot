from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json", SCOPES,
        redirect_uri="http://localhost:5000/oauth/callback"
    )

    print("🔗 Opening the authorization URL...")
    auth_url, _ = flow.authorization_url(prompt="consent")

    print("\n🔗 Please go to this URL and authorize access:")
    print(auth_url)

    auth_code = input("\nEnter the authorization code: ").strip()

    flow.fetch_token(code=auth_code)
    creds = flow.credentials

    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)

    print("✅ Token saved successfully in token.pickle")

if __name__ == "__main__":
    main()

