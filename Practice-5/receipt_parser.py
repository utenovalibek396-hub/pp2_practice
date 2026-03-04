import re
import json

# 1
with open(r'C:\Users\User\Documents\PP_2\work\work\Practice-5\raw.txt', 'r', encoding='utf-8') as file:
    text = file.read()
# #with open(...) as file: – Open the file safely.
# r'...' – Raw string path, backslashes are literal.
# 'r' – Open in read-only mode.
# encoding='utf-8' – Use UTF-8 encoding for text.
# text = file.read() – Read entire file into text.

# 2
prices = [float(p.replace(" ", "").replace(",", ".")) for p in re.findall(r'Стоимость\s+([\d\s]+,\d{2})', text)]
# re.findall(r'Стоимость\s+([\d\s]+,\d{2})', text) – Find all price patterns like 1 152,00 after the word “Стоимость” in text.
# for p in ... – Loop through each matched price string.
# p.replace(" ", "").replace(",", ".") – Remove spaces and replace comma with a dot to convert to a standard decimal format.
# float(...) – Convert the cleaned string to a floating-point number.
# prices = [...] – Store all converted numbers in the list prices.

# 3
lines = text.split('\n')
products = []

for i, line in enumerate(lines):
    if re.search(r'\d+,\d{2}', line) and 'x' in line:
        product_line = lines[i-1].strip()
        products.append(product_line)
# lines = text.split('\n') – Split the text into a list of lines.
# products = [] – Create an empty list to store product names.
# for i, line in enumerate(lines): – Loop through each line with its index.
# if re.search(r'\d+,\d{2}', line) and 'x' in line: – Check if the line has a price pattern and contains 'x' (quantity).
# product_line = lines[i-1].strip() – Take the previous line (assumed product name) and remove spaces.
# products.append(product_line) – Add the product name to the products list.

# 4
total_amount = sum(prices)
# sum(prices) – Adds up all numbers in the prices list.

# 5
date_match = re.search(r'\b\d{2}\.\d{2}\.\d{4}\b', text)
time_match = re.search(r'\b\d{2}:\d{2}:\d{2}\b', text)
date = date_match.group(0) if date_match else None
time = time_match.group(0) if time_match else None
# re.search(r'\b\d{2}\.\d{2}\.\d{4}\b', text) – Look for a date in dd.mm.yyyy format in the text.
# re.search(r'\b\d{2}:\d{2}:\d{2}\b', text) – Look for a time in hh:mm:ss format.
# date = date_match.group(0) if date_match else None – Extract the matched date, or None if not found.
# time = time_match.group(0) if time_match else None – Extract the matched time, or None if not found.

# 6
payment_match = re.search(r'\b(Банковская карта|CASH|CARD|CREDIT|DEBIT)\b', text, re.IGNORECASE)
payment_method = payment_match.group(0) if payment_match else None
# re.search() – Search for payment words like “CASH”, “CARD”, or “Банковская карта” in the text, ignoring case.
# payment_method = payment_match.group(0) if payment_match else None – Extract the matched payment method, or None if nothing is found.

# 7
receipt_data = {
    "products": products,
    "prices": prices,
    "total": total_amount,
    "date": date,
    "time": time,
    "payment_method": payment_method
}
# receipt_data = { ... } – Create a dictionary to store all receipt information.

# 8
with open('parsed_receipt.json', 'w', encoding='utf-8') as json_file:
    json.dump(receipt_data, json_file, ensure_ascii=False, indent=4)
#–Open a new JSON file for writing ('w') with UTF-8 encoding.
# json.dump()– Write the receipt_data dictionary to the file in pretty JSON format, keeping non-ASCII characters readable.

# 9
print(json.dumps(receipt_data, ensure_ascii=False, indent=4))
#print