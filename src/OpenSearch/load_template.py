from opensearchpy import OpenSearch, RequestsHttpConnection, NotFoundError
from typing import Dict, Any, Optional, List
import json
import logging
from pathlib import Path


class OpenSearchTemplateManager:
    def __init__(
            self,
            hosts: list[str],
            http_auth: tuple[str, str],
            use_ssl: bool = True,
            verify_certs: bool = True,
            logger: Optional[logging.Logger] = None
    ):
        self.client = OpenSearch(
            hosts=hosts,
            http_auth=http_auth,
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            connection_class=RequestsHttpConnection
        )
        self.logger = logger or logging.getLogger(__name__)

    def load_templates(self, templates_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Loads multiple templates from a dictionary. Updates existing templates if they exist.

        Args:
            templates_dict: Dictionary containing multiple templates

        Returns:
            List of creation/update responses
        """
        responses = []
        for template_id, template_info in templates_dict["templates"].items():
            try:
                # Try to delete existing template first
                try:
                    self.client.delete_script(id=template_id)
                    self.logger.info(f"Deleted existing template: {template_id}")
                except NotFoundError:
                    self.logger.info(f"No existing template found for: {template_id}")

                # Create new template
                response = self.client.put_script(
                    id=template_id,
                    body={
                        "script": {
                            "lang": "mustache",
                            "source": json.dumps(template_info["template"]),
                            "params": self._extract_params(template_info["template"])
                        }
                    }
                )
                self.logger.info(f"Successfully created template: {template_id}")
                responses.append({template_id: response})
            except Exception as e:
                self.logger.error(f"Failed to create template {template_id}: {str(e)}")
                raise

        return responses

    def _extract_params(self, template_body: Dict[str, Any]) -> Dict[str, Any]:
        params = {}
        template_str = json.dumps(template_body)
        import re
        param_pattern = r'\{\{(\w+)\}\}'
        for param in re.findall(param_pattern, template_str):
            params[param] = None
        return params


# Usage
if __name__ == "__main__":
    # Initialize manager
    manager = OpenSearchTemplateManager(
        hosts=["https://search-mfcodeblooded-public-2pyd6s6pv5mkpug4ostdgfqltu.aos.us-east-1.on.aws"],
        http_auth=("admin", "Mfcodeblooded@123")
    )

    # Load templates from dictionary
    templates = {
        "templates":
{
  "classification_search": {
    "description": "Search by classification with optional filters",
    "template": {
      "from": "{{from}}",
      "size": "{{size}}",
      "query": {
        "bool": {
          "must": [
            {
              "term": {
                "Classification.keyword": "{{classification}}"
              }
            }
          ],
          "should": [
            {
              "multi_match": {
                "query": "{{query_string}}",
                "fields": ["First^2", "Last^2", "Cross-Reference"],
                "operator": "and",
                "fuzziness": "AUTO"
              }
            }
          ],
          "minimum_should_match": 0
        }
      },
      "sort": [
        {"Creation_Date": {"order": "desc"}}
      ],
      "aggs": {
        "by_exclusion_type": {
          "terms": {
            "field": "Exclusion Type.keyword",
            "size": 10
          }
        },
        "by_excluding_agency": {
          "terms": {
            "field": "Excluding Agency.keyword",
            "size": 10
          }
        }
      }
    }
  }
}
    }

    try:
        responses = manager.load_templates(templates)
        print("Templates created successfully:", responses)
    except Exception as e:
        print(f"Failed to create templates: {str(e)}")