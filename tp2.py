from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json", SCOPES
    )

    auth_url, _ = flow.authorization_url(prompt="consent")

    print("\n🔗 Please open this URL in a browser and authorize access:")
    print(auth_url)

    auth_code = input("\nPaste the authorization code here: ").strip()

    flow.fetch_token(code=auth_code)
    creds = flow.credentials

    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)

    print("✅ Token saved successfully in token.pickle")

if __name__ == "__main__":
    main()

