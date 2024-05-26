import csv

def clean_ids(input_file):

    seen_ids = set()

    with open(input_file, 'r', newline='', encoding='utf-8') as read_file, \
            open('Trendyol_' + input_file, 'w', newline='', encoding='utf-8') as write_file:

        reader = csv.DictReader(read_file)
        writer = csv.DictWriter(write_file, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
    
            if row['Id'] not in seen_ids:
        
                writer.writerow(row)
                seen_ids.add(row['Id'])
            else:
                 print(f"Skipping row with ID {row['Id']}.")

    print("Process completed. New file has been created.")



