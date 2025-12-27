import smtplib

# Replace with YOUR actual credentials
username = "fidel.ehirim1@gmail.com"
password = "PASTE_YOUR_NEW_16_CHAR_PASSWORD_HERE"  # The one you just generated

print(f"Testing Gmail authentication...")
print(f"Username: {username}")
print(f"Password: {password[:4]}...{password[-4:]} ({len(password)} chars)")
print()

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    print("✓ Connected to smtp.gmail.com:587")
    
    server.starttls()
    print("✓ STARTTLS successful")
    
    server.login(username, password)
    print("✓ Authentication successful!")
    print()
    print("SUCCESS! Your credentials work.")
    print(f"Now update .flaskenv with: MAIL_PASSWORD={password}")
    
    server.quit()
    
except smtplib.SMTPAuthenticationError as e:
    print(f"✗ Authentication FAILED: {e}")
    print()
    print("Your App Password is INVALID. Please:")
    print("1. Go to https://myaccount.google.com/apppasswords")
    print("2. Generate a NEW App Password")
    print("3. Update this script and test again")
    
except Exception as e:
    print(f"✗ Connection error: {e}")
