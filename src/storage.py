import csv

class Storage:
    def save(self, records, file_path):
        fieldnames = ["title", "post_date", "link", "company", "salary", "location", "description"]
        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames) 
            writer.writeheader()
            writer.writerows(records)