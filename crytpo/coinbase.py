import os
import jwt
from cryptography.hazmat.primitives import serialization
import time
import requests
import pandas as pd
import secrets

Env = os.environ


def build_jwt(path):
    private_key_bytes = "-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIHeuyqBwwMEKneZUUVoNvGJCvS3G+ux+mprsmOZjJhNvoAoGCCqGSM49\nAwEHoUQDQgAEF9Rrboe4VVEHCMAfQbsmeyzuq4QPjin8rZ6e1IQdFVwIQ4V80cPT\nRYI8wcMRVauw9xWn7EWJNb6rp/lEA0kwSg==\n-----END EC PRIVATE KEY-----\n".encode(
        "utf-8"
    )
    private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
    jwt_payload = {
        "sub": Env["KEY_NAME"],
        "iss": "cdp",
        "nbf": int(time.time()),
        "exp": int(time.time()) + 120,
        "uri": f"GET api.coinbase.com{path}",
    }
    jwt_token = jwt.encode(
        jwt_payload,
        private_key,
        algorithm="ES256",
        headers={"kid": Env["KEY_NAME"], "nonce": secrets.token_hex()},
    )
    return jwt_token


def main():
    jwt_token = build_jwt("/api/v3/brokerage/products")

    res = requests.get(
        "https://api.coinbase.com/api/v3/brokerage/products",
        headers={"Authorization": f"Bearer {jwt_token}"},
    )
    res_json = res.json()

    df = pd.DataFrame(res_json["products"])
    df["volume_norm"] = df["price"].astype(float) * df["volume_24h"].astype(float)
    print(
        df[
            (df["quote_currency_id"] == "USDC")
            & (df["volume_norm"].astype(float) > 1000000)
        ].sort_values("volume_norm", ascending=False)
    )


if __name__ == "__main__":
    main()
