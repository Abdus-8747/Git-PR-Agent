import os
import hmac
import hashlib
from dotenv import load_dotenv

# CRITICAL: Ensure environment variables are loaded before checking for the secret
load_dotenv()

def verify_signature(body: bytes, signature: str | None) -> bool:
    if not signature:
        return False

    secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    
    # Fail safely if the secret isn't configured, rather than using a dummy key
    if not secret:
        print("❌ Error: GITHUB_WEBHOOK_SECRET is not set in the .env file!")
        return False

    expected = (
        "sha256="
        + hmac.new(
            secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
    )
    
    print(f"Expected Signature: {expected}")
    print(f"Received Signature: {signature}")

    return hmac.compare_digest(
        expected,
        signature
    )