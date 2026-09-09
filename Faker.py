import json
import os
from faker import Faker
from anonymate.anonymizer import Anonymizer
from cryptography.fernet import Fernet

KEY_FILE = "encryption.key"


if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "rb") as f:
        encryption_key = f.read()
else:
    encryption_key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(encryption_key)


anonymizer = Anonymizer(encryption_key=encryption_key)
fake = Faker()

length = int(input("Enter the number of fake data to be generated: "))

data = []

for _ in range(length):
    data.append(fake.profile())

print("Unencrypted data: ")
print(data)

data_str = json.dumps(data, default=str)

secure_data = anonymizer.encrypt_text(data_str)
print("Encrypted data: ")
print(secure_data)

def write_to_file(question: str) -> bool:
    while True:
        write_decision = input(f"{question} (y/n): ").strip().lower()
        if write_decision == ('y', 'yes'):
            return True
        elif write_decision == ('n', 'no'):
            return False
        print("Please respond with 'y' or 'n': ")

write_bool = write_to_file("Do you want to write to this file? (y/n): ?")

if write_bool == True:
    custom_name = input("Enter the name of the file: ")
    file_name = (f"{custom_name}.txt")
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(secure_data)
    print(f"File has been written to {file_name}")

else:
    print("Data not saved. All data will be lost when application is closed.")
