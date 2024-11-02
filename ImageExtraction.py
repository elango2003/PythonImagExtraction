import pytesseract
from PIL import Image
import re
import json

# Path to Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load the image and extract text
image_path = r'C:\Users\AkashElango\anaconda3\envs\Imageextraction\Raw Data.jpeg'
img = Image.open(image_path)
text = pytesseract.image_to_string(img)
print("Extracted Text:",text)

# Split the text by newlines and group lines for each record
lines = text.splitlines()
records = []
current_record = []

# Organize lines into blocks for each record
for line in lines:
    if line.strip():  # Add non-empty lines to the current record
        current_record.append(line.strip())
    else:
        if current_record:  # Append complete record and reset
            records.append(current_record)
            current_record = []

if current_record:  # Append the last record if it exists
    records.append(current_record)

# Function to parse each block of lines into a structured format
def parse_record_block(lines_block):
    record = {}
    try:
        # First line (RecordNo, KYCID, Name, Guardian, Gender, etc.)
        first_line_parts = lines_block[0].split()
        record['RecordNo'] = first_line_parts[0] if len(first_line_parts) > 0 else ""
        record['KYCID'] = first_line_parts[1] if len(first_line_parts) > 1 else ""
        record['Name'] = ' '.join(first_line_parts[2:4]) if len(first_line_parts) > 3 else ""
        record['GuardianName'] = ' '.join(first_line_parts[4:6]) if len(first_line_parts) > 5 else ""
        record['Gender'] = first_line_parts[6] if len(first_line_parts) > 6 else "Unknown"
        record['MaritalStatus'] = first_line_parts[7] if len(first_line_parts) > 7 else "Unknown"
        record['Dob'] = first_line_parts[8] if len(first_line_parts) > 8 else "Unknown"
        
        # Second line (Address and Location)
        address_line = lines_block[1] if len(lines_block) > 1 else ""
        record['Address'] = address_line.split('Not Available')[0].strip() if 'Not Available' in address_line else address_line.strip()
        record['City'] = 'SAN ANTONIA' if 'SAN ANTONIA' in address_line else 'PRATIVILLE' if 'PRATIVILLE' in address_line else "Unknown"
        zip_match = re.search(r"\b\d{5}\b", address_line)
        record['Zip'] = zip_match.group() if zip_match else ""
        record['CityOfBirth'] = 'SAMKE ADDRESS' if 'SAMKE' in address_line else 'Not Available'
        record['Nationality'] = 'United States Of America'

        # Third line (Residential Status, Occupation, Account Type, Income)
        occupation_line = lines_block[2] if len(lines_block) > 2 else ""
        occupation_parts = occupation_line.split()
        record['ResidentialStatus'] = occupation_parts[0] if len(occupation_parts) > 0 else "Unknown"
        record['Occupation'] = occupation_parts[1] if len(occupation_parts) > 1 else "Unknown"
        record['AccountType'] = occupation_parts[2] if len(occupation_parts) > 2 else "Unknown"
        income_match = re.search(r"[\d,.]+", occupation_line)
        record['AnnualIncome'] = income_match.group() if income_match else "0"

        # Fourth line (Related Person Information)
        related_info_line = lines_block[3] if len(lines_block) > 3 else ""
        if '|' in related_info_line:
            record['RelatedPersonName'] = related_info_line.split('|')[1].strip()
        else:
            related_info_parts = related_info_line.split()
            record['RelatedPersonName'] = related_info_parts[-3] if len(related_info_parts) >= 3 else ""
        record['RelatedPersonRelation'] = 'Grand Fathr' if 'Grand Fathr' in related_info_line else 'Step Father'
        record['AnyPolicy'] = 'YES' if 'YES' in related_info_line else 'NO'
        record['Passport'] = 'YES' if 'YES' in related_info_line else 'NO'
        passport_expiry_match = re.search(r"\d{2}/\d{4}", related_info_line)
        record['PassportExpiry'] = passport_expiry_match.group() if passport_expiry_match else ""

        return record
    except Exception as e:
        print(f"Error parsing record block: {e}")
        return None

# Parse each record block
parsed_records = []
for block in records:
    parsed_record = parse_record_block(block)
    if parsed_record:
        parsed_records.append(parsed_record)

# Display the parsed records
for record in parsed_records:
    print(record)

# Optionally, save to JSON
with open("parsed_records.json", "w") as f:
    json.dump(parsed_records, f, indent=4)
