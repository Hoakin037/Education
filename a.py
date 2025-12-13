from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

print(password_hash.hash("12345678"))
print(password_hash.verify("12345678", password_hash.hash("12345678")))