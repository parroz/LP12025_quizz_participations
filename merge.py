import pandas as pd
import sys
import os

def merge_cleaned_csv_files(db_file, input_files, output_csv, output_html):
    # Load student database
    db_df = pd.read_csv(db_file)
    
    unique_students = {}
    
    for file in input_files:
        try:
            df = pd.read_csv(file, on_bad_lines='skip', dtype=str)
            if "Student Number" in df.columns:
                for student_id in df["Student Number"].dropna().astype(str).tolist():
                    if student_id not in unique_students:
                        matched_row = db_df.loc[db_df['ID'].astype(str) == student_id]
                        student_name = matched_row['Nome'].values[0] if not matched_row.empty else "Unknown"
                        unique_students[student_id] = student_name
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    merged_df = pd.DataFrame({
        "Student Number": sorted(unique_students.keys()),
        "Student Name": [unique_students[num] for num in sorted(unique_students.keys())]
    })
    
    merged_df.to_csv(output_csv, index=False)
    
    # Generate and save HTML file
    html_content = """
    <html>
    <head>
        <title>Merged Participants List</title>
        <style>
            body { font-family: Arial, sans-serif; }
            table { border-collapse: collapse; width: 50%; margin: 20px auto; }
            th, td { border: 1px solid black; padding: 10px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h2 style="text-align:center;">Merged Participants List</h2>
        <table>
            <tr><th>Student Number</th><th>Student Name</th></tr>
    """
    
    for num, name in unique_students.items():
        html_content += f"<tr><td>{num}</td><td>{name}</td></tr>"
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Merged {len(input_files)} files into {output_csv} and {output_html}")
    print(f"Total unique student IDs: {len(unique_students)}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python merge_script.py <db.csv> <output_file.csv> <output_file.html> <input1.csv> <input2.csv> ...")
        sys.exit(1)
    
    db_file = sys.argv[1]
    output_csv = sys.argv[2]
    output_html = sys.argv[3]
    input_files = sys.argv[4:]
    merge_cleaned_csv_files(db_file, input_files, output_csv, output_html)

