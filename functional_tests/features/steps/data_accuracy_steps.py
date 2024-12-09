import os
from behave import given, when, then
from utilities.csv_reader import CSVReader
from utilities.api_client import OpenSearchClient
from utilities.data_comparator import DataComparator


@given('I have access to the source CSV file')
def step_impl(context):
    # Get the absolute path to the functional_tests directory (two levels up from steps)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    csv_path = os.path.join(base_dir, 'test_data', 'sample_data.csv')
    
    # Debug information
    print(f"Current working directory: {os.getcwd()}")
    print(f"Base directory: {base_dir}")
    print(f"Looking for CSV file at: {csv_path}")
    print(f"Directory exists: {os.path.exists(os.path.dirname(csv_path))}")
    print(f"File exists: {os.path.exists(csv_path)}")
    
    if not os.path.exists(csv_path):
        # List contents of the directory for debugging
        parent_dir = os.path.dirname(csv_path)
        if os.path.exists(parent_dir):
            print(f"Contents of {parent_dir}:")
            print(os.listdir(parent_dir))
        raise FileNotFoundError(f"CSV file not found at: {csv_path}")
    
    context.csv_path = csv_path
    context.csv_reader = CSVReader(csv_path)
    assert context.csv_reader.is_accessible(), f"CSV file not accessible at: {csv_path}"


@given('I have access to the OpenSearch API')
def step_impl(context):
    context.api_client = OpenSearchClient(
        host="search-mfcodeblooded-public-2pyd6s6pv5mkpug4ostdgfqltu.aos.us-east-1.on.aws",
        auth=("admin", "Mfcodeblooded@123")
    )
    assert context.api_client.is_accessible(), "OpenSearch API not accessible"


@given('I read a record from CSV with Classification "{classification}"')
def step_impl(context, classification):
    context.csv_record = context.csv_reader.get_record_by_classification(classification)
    assert context.csv_record is not None, f"No record found with Classification: {classification}"


@when('I search for this record in OpenSearch')
def step_impl(context):
    # Use the CSV record to build a query string, for example combining first and last names
    query_string = f"{context.csv_record['First']} {context.csv_record['Last']}".strip()
    if not query_string:
        # Fallback if record doesn't have first/last, adapt as needed
        query_string = context.csv_record['Classification']

    search_params = {
        "id": "basic_person_search",
        "params": {
            "query_string": query_string,
            "from": 0,
            "size": 10
        }
    }
    response = context.api_client.search_template(search_params)
    hits = response.get('hits', {}).get('hits', [])
    assert hits, f"No matching record found in OpenSearch for query_string: {query_string}"
    context.opensearch_record = hits[0].get('_source', {})
    assert context.opensearch_record, "No _source found in the returned OpenSearch record"


@given('I read a record from CSV with "{field_name}" equal to "{field_value}"')
def step_impl(context, field_name, field_value):
    context.field_name = field_name
    context.field_value = field_value
    context.csv_record = context.csv_reader.get_record_by_field(field_name, field_value)
    assert context.csv_record is not None, f"No record found with {field_name}: {field_value}"


@when('I search for this record in OpenSearch using the same field')
def step_impl(context):
    # Build the query string from the field name and value
    query_string = context.field_value
    search_params = {
        "id": "basic_person_search",
        "params": {
            "query_string": query_string,
            "from": 0,
            "size": 10
        }
    }
    response = context.api_client.search_template(search_params)
    hits = response.get('hits', {}).get('hits', [])
    assert hits, f"No matching record found in OpenSearch for {context.field_name}: {context.field_value}"
    context.opensearch_record = hits[0].get('_source', {})
    assert context.opensearch_record, "No _source found in the returned OpenSearch record"


@then('the OpenSearch data should match the CSV data')
def step_impl(context):
    comparator = DataComparator()
    assert comparator.compare_records(context.csv_record, context.opensearch_record), \
        "Records don't match between CSV and OpenSearch"

