from __future__ import annotations
import datetime
import json
from decimal import Decimal
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
from faker import Faker

# ---------------------------------------------------------------------------
# 1. Source data
# ---------------------------------------------------------------------------
profiles = [
    {
        "job": "Agricultural engineer",
        "company": "Phillips-Johnson",
        "ssn": "055-51-3629",
        "residence": "1107 Brian Coves\nSouth Jessica, UT 66862",
        "current_location": (Decimal("-81.6575675"), Decimal("111.794874")),
        "blood_group": "B+",
        "website": [
            "https://hurley.com/",
            "http://www.baker.info/",
            "http://silva-jones.com/",
            "https://www.mathews.com/",
        ],
        "username": "nnelson",
        "name": "Oscar Newman",
        "sex": "M",
        "address": "2574 Scott Manors\nPort Aprilfort, MI 13337",
        "mail": "wgraham@hotmail.com",
        "birthdate": datetime.date(1927, 1, 19),
    },
    {
        "job": "Engineer, civil (consulting)",
        "company": "Guzman Inc",
        "ssn": "457-09-3674",
        "residence": "8014 Lambert Ways Apt. 285\nSouth Briannaside, KS 13217",
        "current_location": (Decimal("61.686331"), Decimal("-42.036583")),
        "blood_group": "A-",
        "website": [
            "http://gregory-martin.org/",
            "http://tanner.org/",
            "https://www.carr.org/",
        ],
        "username": "lking",
        "name": "Jeremy Wilson",
        "sex": "M",
        "address": "9375 Thomas Alley Suite 536\nNorth Darren, AZ 22956",
        "mail": "hdeleon@hotmail.com",
        "birthdate": datetime.date(1996, 10, 12),
    },
    {
        "job": "Information officer",
        "company": "Green Inc",
        "ssn": "230-42-2169",
        "residence": "Unit 6625 Box 0858\nDPO AE 52466",
        "current_location": (Decimal("-78.802646"), Decimal("-47.996111")),
        "blood_group": "A-",
        "website": ["https://www.watkins.com/", "http://johnson.org/"],
        "username": "timothycastro",
        "name": "Kenneth Rhodes",
        "sex": "M",
        "address": "7994 Pearson Square\nHannahmouth, FM 16699",
        "mail": "sonya72@hotmail.com",
        "birthdate": datetime.date(2003, 6, 15),
    },
    {
        "job": "Contracting civil engineer",
        "company": "Smith-Williamson",
        "ssn": "796-76-1297",
        "residence": "0041 Brittany Mountains\nNorth Harryshire, MN 69202",
        "current_location": (Decimal("66.422320"), Decimal("107.124001")),
        "blood_group": "AB+",
        "website": ["http://www.nolan.com/"],
        "username": "debraphillips",
        "name": "Nicole Richardson",
        "sex": "F",
        "address": "303 Wong Trafficway Suite 883\nLake Kiara, MN 78039",
        "mail": "andrew33@gmail.com",
        "birthdate": datetime.date(2003, 9, 7),
    },
    {
        "job": "Engineer, technical sales",
        "company": "Moody-Meza",
        "ssn": "574-63-6422",
        "residence": "74438 Moore Fall\nSouth Andrew, GA 64257",
        "current_location": (Decimal("38.089195"), Decimal("35.459581")),
        "blood_group": "A+",
        "website": ["https://brooks-moore.com/"],
        "username": "xlewis",
        "name": "Gary Gamble",
        "sex": "M",
        "address": "9929 Henderson Branch Suite 961\nLake Mary, AL 36478",
        "mail": "ambercordova@yahoo.com",
        "birthdate": datetime.date(1968, 8, 19),
    },
]


# ---------------------------------------------------------------------------
# 2. AnonyMate: symmetric-encryption anonymizer
# ---------------------------------------------------------------------------
class AnonyMate:

    def __init__(self, key: Optional[bytes] = None):
        self.key: bytes = key or Fernet.generate_key()
        self._cipher = Fernet(self.key)

    def encrypt_value(self, value) -> str:
        serialized = json.dumps(value, default=str).encode("utf-8")
        return self._cipher.encrypt(serialized).decode("utf-8")

    def decrypt_value(self, token: str):
        raw = self._cipher.decrypt(token.encode("utf-8"))
        return json.loads(raw)

    def anonymize_profile(self, profile: dict) -> dict:
        return {field: self.encrypt_value(val) for field, val in profile.items()}

    def anonymize_profiles(self, profile_list: list[dict]) -> list[dict]:
        return [self.anonymize_profile(p) for p in profile_list]


# ---------------------------------------------------------------------------
# 3. Query tool — restricted to Name, DoB, Sex, Blood Type
# ---------------------------------------------------------------------------
QUERYABLE_FIELDS = {
    "1": "name",
    "2": "birthdate",
    "3": "sex",
    "4": "blood_group",
}
FIELD_LABELS = {
    "name": "Name",
    "birthdate": "DoB",
    "sex": "Sex",
    "blood_group": "Blood Type",
}


def find_profile(encrypted_profiles: list[dict], anonymizer: AnonyMate, identifier: str) -> Optional[int]:
    """Locate a profile index by username or full name (case-insensitive)."""
    needle = identifier.strip().lower()
    for idx, enc_profile in enumerate(encrypted_profiles):
        username = anonymizer.decrypt_value(enc_profile["username"]).lower()
        name = anonymizer.decrypt_value(enc_profile["name"]).lower()
        if needle in (username, name):
            return idx
    return None


def query_field(encrypted_profiles: list[dict], anonymizer: AnonyMate, idx: int, field_key: str):
    field = QUERYABLE_FIELDS.get(field_key)
    if field is None:
        return None
    value = anonymizer.decrypt_value(encrypted_profiles[idx][field])
    return FIELD_LABELS[field], value


# ---------------------------------------------------------------------------
# 4. CLI
# ---------------------------------------------------------------------------
def main():
    anonymizer: Optional[AnonyMate] = None
    encrypted_profiles: Optional[list[dict]] = None

    print("=== Profile Privacy Tool ===")
    while True:
        print("\nOptions:")
        print("  [E] Encrypt profile data")
        print("  [Q] Query a profile (Name / DoB / Sex / Blood Type)")
        print("  [X] Exit")
        choice = input("Select an option: ").strip().upper()

        if choice == "E":
            anonymizer = AnonyMate()
            encrypted_profiles = anonymizer.anonymize_profiles(profiles)
            print(f"Encrypted {len(encrypted_profiles)} profiles with symmetric (Fernet) encryption.")
            print(
                "Session key (needed to decrypt later — store it securely, "
                "never alongside the ciphertext): "
                f"{anonymizer.key.decode()}"
            )

        elif choice == "Q":
            if encrypted_profiles is None or anonymizer is None:
                print("Data isn't encrypted yet. Choose [E] first.")
                continue
            identifier = input("Enter username or full name to look up: ")
            idx = find_profile(encrypted_profiles, anonymizer, identifier)
            if idx is None:
                print("Profile not found.")
                continue
            print("Which field?")
            for key, field in QUERYABLE_FIELDS.items():
                print(f"  [{key}] {FIELD_LABELS[field]}")
            field_key = input("Enter choice (1-4): ").strip()
            try:
                result = query_field(encrypted_profiles, anonymizer, idx, field_key)
            except InvalidToken:
                print("Decryption failed — key mismatch or corrupted data.")
                continue
            if result is None:
                print("Invalid field selection.")
            else:
                label, value = result
                print(f"{label}: {value}")

        elif choice == "X":
            print("Goodbye.")
            break
        else:
            print("Unrecognized option.")


if __name__ == "__main__":
    main()
