# Blue Button 2.0 Sandbox Registration Guide

1. Go to: [https://bluebutton.cms.gov/developers/](https://bluebutton.cms.gov/developers/)
2. Click 'Sign up for sandbox access'
3. Register a new application:
   - Name: `fhir-cms-interop-toolkit`
   - Redirect URI: `http://localhost:8000/callback`
   - Scopes: `patient/Patient.read patient/ExplanationOfBenefit.read patient/Coverage.read`
4. Save `BB2_CLIENT_ID` and `BB2_CLIENT_SECRET` to your `.env` file.

## Troubleshooting

- `invalid_client`: Check your credentials in `.env`.
- `redirect_uri_mismatch`: Ensure `CALLBACK_URL` in `.env` matches your registration.
- `403 Forbidden`: Token may have expired or scopes are missing. Delete `modules/bb2_sandbox/data/.token_cache.json` and re-authenticate.
