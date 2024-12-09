Feature: Data Accuracy Verification
  As a data quality engineer
  I want to verify that the OpenSearch data matches the source CSV
  So that I can ensure data integrity

  Background:
    Given I have access to the source CSV file
    And I have access to the OpenSearch API

  Scenario: Verify individual record accuracy
    Given I read a record from CSV with Classification "Individual"
    When I search for this record in OpenSearch