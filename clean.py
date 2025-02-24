import pandas as pd
import re
import unicodedata
import sys
import os

def extract_student_number(input_str):
    """Extracts student number from input string if present."""
    match = re.search(r'(\d{7,8})', str(input_str))  # Look for a 7 or 8-digit number
    return match.group(1) if match else None

def clean_name(name):
    """Removes special characters, emojis, and extra spaces from names."""
    name = ''.join(c for c in unicodedata.normalize('NFKD', name) if unicodedata.category(c) != 'Mn')
    name = re.sub(r'[^a-zA-Z\s]', '', name)  # Remove non-alphabetic characters
    return name.strip().lower()

def match_by_name(input_name, db_df):
    """Matches student name against the database to find the corresponding student number."""
    input_name_cleaned = clean_name(input_name)
    
    matched = db_df[db_df['Nome'].apply(lambda x: clean_name(str(x))).str.contains(re.escape(input_name_cleaned), na=False)]
    
    if len(matched) == 1:
        return matched.iloc[0]['ID'], matched.iloc[0]['Nome']  # Return unique match's student number and name
    
    # If no exact match, try matching just the first name
    first_name = input_name_cleaned.split()[0]
    matched = db_df[db_df['Nome'].apply(lambda x: clean_name(str(x))).str.contains(first_name, na=False)]
    
    if len(matched) == 1:
        return matched.iloc[0]['ID'], matched.iloc[0]['Nome']
    
    return None, None

def match_by_partial_name(input_name, db_df):
    """Matches names by checking if all parts of the input name appear in any order in the database."""
    name_parts = [re.escape(clean_name(part)) for part in str(input_name).strip().lower().split()]
    
    # Create a regex pattern that requires all parts to be present, regardless of order
    pattern = '(?=.*' + ')(?=.*'.join(name_parts) + ')'
    possible_matches = db_df[db_df['Nome'].apply(lambda x: clean_name(str(x))).str.contains(pattern, regex=True, na=False)]
    
    if len(possible_matches) == 1:
        return possible_matches.iloc[0]['ID'], possible_matches.iloc[0]['Nome']
    return None, None

def process_socrative_export(db_path, socrative_path):
    # Generate output file names based on input file name
    base_name = os.path.splitext(os.path.basename(socrative_path))[0]
    output_csv = f"{base_name}.csv"
    output_html = f"{base_name}.html"
    
    # Load the student database
    db_df = pd.read_csv(db_path)
    
    # Load the Socrative export file
    socrative_df = pd.read_excel(socrative_path, sheet_name=0)
    
    # Extract student identifiers from column A, starting from row 6 (index 5)
    student_inputs = socrative_df.iloc[5:, 0].dropna().astype(str).tolist()
    
    # Normalize student inputs
    normalized_numbers = {}
    unmatched_entries = []
    
    for inp in student_inputs:
        student_number = extract_student_number(inp)
        if student_number:
            matched_row = db_df.loc[db_df['ID'].astype(str) == student_number]
            matched_name = matched_row['Nome'].values[0] if not matched_row.empty else None
            normalized_numbers[student_number] = (matched_name, inp)
        else:
            matched_number, matched_name = match_by_name(inp, db_df)
            if not matched_number:
                matched_number, matched_name = match_by_partial_name(inp, db_df)
            if matched_number:
                normalized_numbers[matched_number] = (matched_name, inp)
            else:
                unmatched_entries.append(inp)
    
    # Create DataFrame with matched student numbers
    matched_students_df = pd.DataFrame({
        "Student Number": list(normalized_numbers.keys()),
        "Student Name": [normalized_numbers[num][0] for num in normalized_numbers.keys()],
        "Original Input": [normalized_numbers[num][1] for num in normalized_numbers.keys()]
    })
    
    # Save to CSV
    matched_students_df.to_csv(output_csv, index=False)
    
    # Generate and save HTML file
    html_content = """
    <html>
    <head>
        <title>Participants List</title>
        <style>
            body { font-family: Arial, sans-serif; }
            table { border-collapse: collapse; width: 50%; margin: 20px auto; }
            th, td { border: 1px solid black; padding: 10px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h2 style="text-align:center;">Participants List</h2>
        <table>
            <tr><th>Student Number</th><th>Student Name</th><th>Original Input</th></tr>
    """
    
    for num, (name, original) in normalized_numbers.items():
        html_content += f"<tr><td>{num}</td><td>{name}</td><td>{original}</td></tr>"
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Print unmatched entries to the command line
    print(f"Total responses in Socrative export: {len(student_inputs)}")
    print(f"Total matched responses: {len(normalized_numbers)}")
    print(f"Total unmatched responses: {len(unmatched_entries)}")
    if unmatched_entries:
        print("Unmatched entries:")
        for entry in unmatched_entries:
            print(f" - {entry}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <db.csv> <socrative_export.xlsx>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    socrative_path = sys.argv[2]
    process_socrative_export(db_path, socrative_path)

