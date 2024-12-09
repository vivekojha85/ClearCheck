import csv
from typing import Dict, Optional, List

class CSVReader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = []
        self._load_data()

    def _load_data(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.data = list(reader)

    def is_accessible(self) -> bool:
        try:
            with open(self.file_path, 'r'):
                return True
        except:
            return False

    def get_record_by_classification(self, classification: str) -> Optional[Dict]:
        for record in self.data:
            if record['Classification'] == classification:
                return record
        return None

    def get_record_by_field(self, field: str, value: str) -> Optional[Dict]:
        for record in self.data:
            if record.get(field) == value:
                return record
        return None

    def get_all_records(self) -> List[Dict]:
        return self.data

    def get_record_count(self) -> int:
        return len(self.data)

    def get_latest_record(self) -> Optional[Dict]:
        if not self.data:
            return None
        return max(self.data, key=lambda x: x.get('Creation_Date', ''))