# The Alarm API backend

# Authentication

1. Run `openssl genpkey -algorithm RSA -out private_api_key.pem` and `openssl rsa -in private_api_key.pem -pubout -out public_api_key.pem`
to generate a private and public key pair for JWT signing and verification.
2. Add the absolute path between to the private/public key file to the .env file
3. Run `python backend/src/auth/utils.py` which generates a JWT token for you. This token will be used for authentication.
4. The private key is used for token signing (encoding), the public key is used for decoding. Therefore, the public key needs to be present on the API Server for JWT token validation.
The private key can be stored somewhere save. 