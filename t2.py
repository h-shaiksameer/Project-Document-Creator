import json

# Replace this with your original Firebase credentials JSON
original_credentials = {
    "type": "service_account",
    "project_id": "project-document-creator",
    "private_key_id": "4c885f18bbe5a1182f8ae2f2dea4ef82426225f1",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC/5ORUBn75jqaK
...rest_of_your_private_key...
-----END PRIVATE KEY-----""",
    "client_email": "firebase-adminsdk-ofoau@project-document-creator.iam.gserviceaccount.com",
    "client_id": "101920650321770320023",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-ofoau@project-document-creator.iam.gserviceaccount.com"
}

# Properly escape the private key for the .env file
original_credentials["private_key"] = original_credentials["private_key"].replace("\n", "\\n")

# Convert the entire JSON object to a string
encoded_credentials = json.dumps(original_credentials)
print(encoded_credentials)
