import os
import json
from datetime import datetime, timedelta
from typing import Dict, List
import requests


class SendScans:
  def __init__(self, defectdojo_host: str, defectdojo_user: str, defectdojo_password: str):
      self.defectdojo_host = 'https://demo.defectdojo.org'
      self.defectdojo_user = 'admin'
      self.defectdojo_password = '1Defectdojo@demo#appsec'
      self.defectdojo_api_key = '548afd6fab3bea9794a41b31da0e9404f733e222'
      self.product_id = None
      self.engagement_id = None
      self.start_date = None
      self.end_date = None

  def __get_defectdojo_api_key(self) -> str:
      try:
          url = f"{self.defectdojo_host}/api/v2/api-token-auth/"
          payload = json.dumps({"username": self.defectdojo_user, "password": self.defectdojo_password})
          headers = {"Accept": "application/json", "Content-Type": "application/json"}
          response = requests.request("POST", url, headers=headers, data=payload)
          response.raise_for_status()
          return response.json()["token"]
      except requests.exceptions.HTTPError as e:
          print(f"Failed to get API key: {e}")
          raise e


  def create_product(self, product_name: str, product_description: str, product_type: int) -> None:

          url = f"{self.defectdojo_host}/api/v2/products/"
          payload = json.dumps({"name": product_name, "description": product_description, "prod_type": product_type})
          headers = {"Accept": "application/json", "Authorization": f"Token {self.defectdojo_api_key}", "Content-Type": "application/json"}
          try:
              response = requests.request("POST", url, headers=headers, data=payload)
              response.raise_for_status()
              self.product_id = response.json()["id"]
              print(f"Created product {self.product_id}")
          except requests.exceptions.HTTPError as e:
              print(f"Failed to create product: {e}")
              print("Response status code:", e.response.status_code)
              print("Response text:", e.response.text)
              raise e


  def create_product(self, product_name: str, product_description: str, product_type: int) -> None:

            url = f"{self.defectdojo_host}/api/v2/products/"
            payload = json.dumps({"name": product_name, "description": product_description, "prod_type": product_type})
            headers = {"Accept": "application/json", "Authorization": f"Token {self.defectdojo_api_key}", "Content-Type": "application/json"}
            try:
                response = requests.request("POST", url, headers=headers, data=payload)
                response.raise_for_status()
                self.product_id = response.json()["id"]
                print(f"Created product {self.product_id}")
            except requests.exceptions.HTTPError as e:
                print(f"Failed to create product: {e}")
                print("Request headers:", response.request.headers)
                print("Request body:", response.request.body)
                print("Response status code:", response.status_code)
                print("Response text:", response.text)
                raise e


  def create_engagement(
      self,
      pipeline_id: str,
      commit_hash: str,
      branch_or_tag: str,
      version: str,
      repo_uri: str,
      scm_server: int,
      build_server: int,
      engagement_duration_days: int,
  ) -> None:
      url = f"{self.defectdojo_host}/api/v2/engagements/"
      self.start_date = datetime.now().strftime("%Y-%m-%d")
      self.end_date = (datetime.now() + timedelta(days=engagement_duration_days)).strftime("%Y-%m-%d")
      payload = json.dumps(
          {
              "product": self.product_id,
              "name": f"Gitlab CI #{pipeline_id}",
              "version": version,
              "target_start": self.start_date,
              "target_end": self.end_date,
              "status": "In Progress",
              "engagement_type": "CI/CD",
              "active": True,
              "build_id": f"#{pipeline_id}",
              "commit_hash": commit_hash,
              "branch_tag": branch_or_tag,
              "source_code_management_uri": repo_uri,
              "source_code_management_server": scm_server,
              "build_server": build_server,
              "deduplication_on_engagement": False,
          }
      )
      headers = {"Accept": "application/json", "Authorization": f"Token {self.defectdojo_api_key}", "Content-Type": "application/json"}
      try:
          response = requests.request("POST", url, headers=headers, data=payload)
          response.raise_for_status()
          self.engagement_id = response.json()["id"]
          print(f"Created engagement {self.engagement_id}")
      except requests.exceptions.HTTPError as e:
          print(f"Failed to create engagement: {e}")
          raise e

  def upload_scans(self, scans: List[Dict[str, str]]) -> None:
      for scan in scans:
          url = f"{self.defectdojo_host}/api/v2/import-scan/"
          payload = {
              "scan_date": self.start_date,
              "engagement": self.engagement_id,
              "scan_type": scan["scan_type"],
              "active": "true",
              "verified": "false",
              #"close_old_findings": "true",
              "skip_duplicates": "true",
              "minimum_severity": "Info",
          }
          try:
              file = {"file": open(scan["scan_file"], "rb")}
          except Exception as e:
              print(f"Failed to open scan file {scan['scan_file']}: {e}")
              continue
          headers = {"Accept": "application/json", "Authorization": f"Token {self.defectdojo_api_key}"}
          try:
              response = requests.request("POST", url, headers=headers, data=payload, files=file)
              response.raise_for_status()
              print(f"Uploaded scan {scan['scan_file']}")
          except requests.exceptions.HTTPError as e:
              print(f"Failed to upload scan {scan['scan_file']}: {e}")
              print("Response content:", response.text)

def main():
  DEFECTDOJO_HOST = os.getenv("DEFECTDOJO_HOST")
  DEFECTDOJO_USER = os.getenv("DEFECTDOJO_USER")
  DEFECTDOJO_PASSWORD = os.getenv("DEFECTDOJO_PASSWORD")
  send_scans = SendScans(DEFECTDOJO_HOST, DEFECTDOJO_USER, DEFECTDOJO_PASSWORD)
  PRODUCT = 'juice-shop-test10'
  send_scans.create_product(PRODUCT, PRODUCT, 1)  # 1 - Research and Development, product type
  PIPELINE_ID = os.getenv("CI_PIPELINE_ID")
  VERSION = os.getenv("VERSION")
  VERSION = os.getenv("VERSION")
  if VERSION is None:
    VERSION = os.getenv("CI_COMMIT_SHORT_SHA")
  COMMIT_HASH = os.getenv("CI_COMMIT_SHA")
  BRANCH_OR_TAG = os.getenv("CI_COMMIT_REF_NAME")
  REPO_URI = os.getenv("CI_PROJECT_URL")
  SCM_SERVER = 1
  BUILD_SERVER = 2
  ENGAGEMENT_DURATION_DAYS = 100  # Medium Finding SLA Days + 10
  send_scans.create_engagement(PIPELINE_ID, COMMIT_HASH, BRANCH_OR_TAG, VERSION, REPO_URI, SCM_SERVER, BUILD_SERVER, ENGAGEMENT_DURATION_DAYS)
  scans = [
      {"scan_type": "ZAP Scan", "scan_file": "report.json"},

  ]
  send_scans.upload_scans(scans)

if __name__ == "__main__":
  main()

