from typing import Dict, Any
from fuzzywuzzy import fuzz
from datetime import datetime
import re


class DataComparator:
    def __init__(self, fuzzy_threshold: int = 85):
        """
        Initialize the DataComparator with configurable settings.

        Args:
            fuzzy_threshold (int): Minimum score for fuzzy text matching (0-100)
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.date_fields = ['Creation_Date', 'Active Date', 'Termination Date']
        self.exact_match_fields = [
            'Classification',
            'First',
            'Last',
            'Excluding Agency',
            'Exclusion Type',
            'Record Status'
        ]
        self.fuzzy_match_fields = [
            'Cross-Reference',
            'Additional Comments',
            'Address 1',
            'Address 2'
        ]

    def compare_records(self, csv_record: Dict[str, Any], opensearch_record: Dict[str, Any]) -> bool:
        """
        Compare all fields between CSV and OpenSearch records.

        Args:
            csv_record: Record from CSV file
            opensearch_record: Record from OpenSearch

        Returns:
            bool: True if records match according to comparison rules
        """
        if not csv_record or not opensearch_record:
            return False

        # Compare exact match fields
        for field in self.exact_match_fields:
            if not self.compare_field_exact(csv_record.get(field), opensearch_record.get(field)):
                print(f"Exact match failed for field {field}")
                print(f"CSV value: {csv_record.get(field)}")
                print(f"OpenSearch value: {opensearch_record.get(field)}")
                return False

        # Compare fuzzy match fields
        for field in self.fuzzy_match_fields:
            if not self.compare_field_fuzzy(csv_record.get(field), opensearch_record.get(field)):
                print(f"Fuzzy match failed for field {field}")
                print(f"CSV value: {csv_record.get(field)}")
                print(f"OpenSearch value: {opensearch_record.get(field)}")
                return False

        # Compare date fields
        for field in self.date_fields:
            if not self.compare_dates(csv_record.get(field), opensearch_record.get(field)):
                print(f"Date comparison failed for field {field}")
                print(f"CSV value: {csv_record.get(field)}")
                print(f"OpenSearch value: {opensearch_record.get(field)}")
                return False

        return True

    def compare_field_exact(self, csv_value: Any, opensearch_value: Any) -> bool:
        """
        Perform exact comparison between two field values.

        Args:
            csv_value: Value from CSV record
            opensearch_value: Value from OpenSearch record

        Returns:
            bool: True if values match exactly (case-insensitive)
        """
        # Handle None/empty values
        if csv_value is None and opensearch_value is None:
            return True
        if csv_value is None or opensearch_value is None:
            return False

        # Convert to strings and clean
        csv_str = str(csv_value).strip().lower()
        opensearch_str = str(opensearch_value).strip().lower()

        return csv_str == opensearch_str

    def compare_field_fuzzy(self, csv_value: Any, opensearch_value: Any) -> bool:
        """
        Perform fuzzy comparison between two field values.

        Args:
            csv_value: Value from CSV record
            opensearch_value: Value from OpenSearch record

        Returns:
            bool: True if fuzzy match score exceeds threshold
        """
        # Handle None/empty values
        if csv_value is None and opensearch_value is None:
            return True
        if csv_value is None or opensearch_value is None:
            return False

        # Convert to strings and clean
        csv_str = str(csv_value).strip()
        opensearch_str = str(opensearch_value).strip()

        # If strings are exactly equal, return True
        if csv_str.lower() == opensearch_str.lower():
            return True

        # Calculate fuzzy match score
        ratio = fuzz.ratio(csv_str.lower(), opensearch_str.lower())
        token_sort_ratio = fuzz.token_sort_ratio(csv_str.lower(), opensearch_str.lower())

        # Use the higher of the two scores
        max_score = max(ratio, token_sort_ratio)

        return max_score >= self.fuzzy_threshold

    def compare_dates(self, csv_date: str, opensearch_date: str) -> bool:
        """
        Compare dates accounting for different formats.

        Args:
            csv_date: Date string from CSV
            opensearch_date: Date string from OpenSearch

        Returns:
            bool: True if dates match
        """
        if csv_date is None and opensearch_date is None:
            return True
        if csv_date is None or opensearch_date is None:
            return False

        try:
            # Clean date strings
            csv_date = self._clean_date(csv_date)
            opensearch_date = self._clean_date(opensearch_date)

            # Parse dates
            csv_dt = self._parse_date(csv_date)
            opensearch_dt = self._parse_date(opensearch_date)

            return csv_dt == opensearch_dt
        except ValueError:
            return False

    def _clean_date(self, date_str: str) -> str:
        """
        Clean date string by removing extra whitespace and standardizing format.
        """
        if not date_str:
            return ""
        return re.sub(r'\s+', ' ', date_str).strip()

    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse date string using multiple format attempts.

        Args:
            date_str: Date string to parse

        Returns:
            datetime: Parsed datetime object

        Raises:
            ValueError: If date string cannot be parsed
        """
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%y',
            '%m/%d/%Y',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%dT%H:%M:%SZ'
        ]

        for date_format in date_formats:
            try:
                return datetime.strptime(date_str, date_format)
            except ValueError:
                continue

        raise ValueError(f"Unable to parse date string: {date_str}")

    def get_comparison_report(self, csv_record: Dict[str, Any], opensearch_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a detailed comparison report between two records.

        Args:
            csv_record: Record from CSV file
            opensearch_record: Record from OpenSearch

        Returns:
            Dict containing comparison results for each field
        """
        report = {
            'exact_matches': {},
            'fuzzy_matches': {},
            'date_matches': {},
            'mismatches': []
        }

        # Check exact match fields
        for field in self.exact_match_fields:
            matches = self.compare_field_exact(csv_record.get(field), opensearch_record.get(field))
            if matches:
                report['exact_matches'][field] = True
            else:
                report['mismatches'].append({
                    'field': field,
                    'csv_value': csv_record.get(field),
                    'opensearch_value': opensearch_record.get(field),
                    'comparison_type': 'exact'
                })

        # Check fuzzy match fields
        for field in self.fuzzy_match_fields:
            matches = self.compare_field_fuzzy(csv_record.get(field), opensearch_record.get(field))
            if matches:
                report['fuzzy_matches'][field] = True
            else:
                report['mismatches'].append({
                    'field': field,
                    'csv_value': csv_record.get(field),
                    'opensearch_value': opensearch_record.get(field),
                    'comparison_type': 'fuzzy'
                })

        # Check date fields
        for field in self.date_fields:
            matches = self.compare_dates(csv_record.get(field), opensearch_record.get(field))
            if matches:
                report['date_matches'][field] = True
            else:
                report['mismatches'].append({
                    'field': field,
                    'csv_value': csv_record.get(field),
                    'opensearch_value': opensearch_record.get(field),
                    'comparison_type': 'date'
                })

        return report