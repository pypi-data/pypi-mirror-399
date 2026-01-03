"""
Qualys API diagnostics module.

Provides diagnostic functions to test Qualys API authentication
and module availability.
"""

import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, Tuple, Optional
from requests.auth import HTTPBasicAuth
import requests

from .url_utils import transform_to_gateway_url, transform_to_api_url, get_api_versions

logger = logging.getLogger("regscale")


def _fetch_vmdr_sample(username: str, password: str, base_url: str) -> Dict:
    """Fetch sample VM detection data (used by sync_qualys)."""
    try:
        url = f"{base_url}/api/2.0/fo/asset/host/vm/detection/"
        response = requests.get(
            url,
            auth=HTTPBasicAuth(username, password),
            params={"action": "list", "show_asset_id": "1", "truncation_limit": "5"},
            timeout=60,
        )

        if response.status_code == 200:
            # Parse XML to extract first few hosts
            hosts = []
            root = ET.fromstring(response.text)
            for host_elem in root.findall(".//HOST")[:3]:  # First 3 hosts
                host_data = {}
                for field in ["ID", "ASSET_ID", "IP", "DNS", "OS", "TRACKING_METHOD"]:
                    elem = host_elem.find(field)
                    if elem is not None and elem.text:
                        host_data[field] = elem.text
                hosts.append(host_data)

            return {"status": "success", "total_hosts_fetched": len(hosts), "sample_hosts": hosts}
        else:
            return {"status": "failed", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _fetch_container_sample(access_token: str, container_url: str, version: str = "v1.3") -> Dict:
    """Fetch sample container data (used by import_container_scans)."""
    try:
        list_url = f"{container_url}/csapi/{version}/containers"
        response = requests.get(
            list_url, headers={"Authorization": f"Bearer {access_token}"}, params={"pageSize": 5}, timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            containers = data.get("data", [])[:3]  # First 3 containers
            sample_containers = []
            for container in containers:
                sample_containers.append(
                    {
                        "containerId": container.get("containerId"),
                        "name": container.get("name"),
                        "imageId": container.get("imageId"),
                        "vulnerabilities": container.get("vulnerabilities", {}).get("total", 0),
                    }
                )
            return {
                "status": "success",
                "total_containers_fetched": len(sample_containers),
                "sample_containers": sample_containers,
            }
        else:
            return {"status": "failed", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _fetch_was_sample(username: str, password: str, base_url: str, version: str = "3.0") -> Dict:
    """Fetch sample WAS webapp data (used by import_was_scans)."""
    try:
        url = f"{base_url}/qps/rest/{version}/search/was/webapp"
        response = requests.post(
            url,
            auth=HTTPBasicAuth(username, password),
            headers={"Content-Type": "application/json"},
            json={"ServiceRequest": {"preferences": {"limitResults": 5}}},
            timeout=60,
        )

        if response.status_code == 200:
            data = response.json()
            webapps = data.get("ServiceResponse", {}).get("data", [])[:3]  # First 3 webapps
            sample_webapps = []
            for webapp in webapps:
                sample_webapps.append({"id": webapp.get("id"), "name": webapp.get("name"), "url": webapp.get("url")})
            return {"status": "success", "total_webapps_fetched": len(sample_webapps), "sample_webapps": sample_webapps}
        else:
            return {"status": "failed", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def test_vmdr_authentication(username: str, password: str, base_url: str, fetch_sample: bool = False) -> Dict:
    """
    Test VMDR/Total Cloud API authentication and optionally fetch sample data.

    :param str username: Qualys username
    :param str password: Qualys password
    :param str base_url: Qualys API base URL
    :param bool fetch_sample: If True, fetch sample vulnerability detection data
    :return: Test result dictionary
    :rtype: Dict
    """
    result = {"status": "unknown", "error": None, "status_code": None}

    try:
        test_url = f"{base_url}/api/2.0/fo/asset/host/"
        response = requests.get(
            test_url,
            auth=HTTPBasicAuth(username, password),
            params={"action": "list", "truncation_limit": "1"},
            timeout=30,
        )
        result["status_code"] = response.status_code

        if response.status_code == 200:
            result["status"] = "success"

            # If requested, fetch sample VM detection data (used by sync_qualys)
            if fetch_sample:
                result["sample_data"] = _fetch_vmdr_sample(username, password, base_url)
        else:
            result["status"] = "failed"
            result["error"] = f"HTTP {response.status_code}"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def _try_container_version_auth(username: str, password: str, container_url: str, version: str) -> tuple:
    """Try authenticating with a specific Container Security API version."""
    auth_url = f"{container_url}/csapi/{version}/auth"
    logger.debug("Container Security: Trying API version %s at %s", version, auth_url)

    try:
        response = requests.post(
            auth_url,
            headers={"X-Requested-With": "RegScale CLI"},
            data={"username": username, "password": password, "permissions": True, "token": True},
            timeout=30,
        )

        if response.status_code == 200:
            auth_data = response.json()
            if "access_token" in auth_data:
                return True, None, response.status_code, auth_data["access_token"]
            return False, "No access token in response", response.status_code, None

        if response.status_code == 401:
            return False, "Authentication failed - module may not be enabled", response.status_code, None
        if response.status_code == 404:
            return False, f"API version {version} not supported", response.status_code, None

        return False, f"HTTP {response.status_code}", response.status_code, None

    except Exception as e:
        return False, str(e), None, None


def test_container_authentication(username: str, password: str, base_url: str, fetch_sample: bool = False) -> Dict:
    """
    Test Container Security API authentication and optionally fetch sample data.

    Tries multiple API versions (v1.3, v1.2, v1.1, v1.0) with automatic fallback.

    :param str username: Qualys username
    :param str password: Qualys password
    :param str base_url: Qualys API base URL
    :param bool fetch_sample: If True, fetch sample container data
    :return: Test result dictionary
    :rtype: Dict
    """
    result = {"status": "unknown", "error": None, "status_code": None, "api_version": None}

    # Transform URL for Container API (uses gateway subdomain)
    container_url = transform_to_gateway_url(base_url)

    # Try API versions from newest to oldest
    api_versions = get_api_versions("container_security")
    last_error = None

    for version in api_versions:
        success, error, status_code, access_token = _try_container_version_auth(
            username, password, container_url, version
        )

        result["status_code"] = status_code
        result["api_version"] = version

        if success:
            result["status"] = "success"
            logger.info("Container Security: Successfully authenticated using API version %s", version)

            # If requested, fetch sample container data
            if fetch_sample:
                result["sample_data"] = _fetch_container_sample(access_token, container_url, version)
            return result

        last_error = error
        if status_code == 404:
            logger.debug("Container Security: API version %s not found (404), trying older version", version)

    # All versions failed
    result["status"] = "failed"
    result["error"] = last_error or "All API versions failed"
    return result


def test_was_authentication(username: str, password: str, base_url: str, fetch_sample: bool = False) -> Dict:
    """
    Test WAS (Web Application Scanning) API authentication and optionally fetch sample data.

    Tries multiple API versions (4.0, 3.0, 2.0) with automatic fallback.

    :param str username: Qualys username
    :param str password: Qualys password
    :param str base_url: Qualys API base URL
    :param bool fetch_sample: If True, fetch sample webapp data
    :return: Test result dictionary
    :rtype: Dict
    """
    result = {"status": "unknown", "error": None, "status_code": None, "api_version": None}

    # Try API versions from newest to oldest
    api_versions = get_api_versions("was")
    last_error = None

    for version in api_versions:
        try:
            test_url = f"{base_url}/qps/rest/{version}/search/was/webapp"
            logger.debug("WAS: Trying API version %s at %s", version, test_url)

            response = requests.post(
                test_url,
                auth=HTTPBasicAuth(username, password),
                headers={"Content-Type": "application/json"},
                json={"ServiceRequest": {"preferences": {"limitResults": 1}}},
                timeout=30,
            )
            result["status_code"] = response.status_code
            result["api_version"] = version

            if response.status_code == 200:
                result["status"] = "success"
                logger.info("WAS: Successfully authenticated using API version %s", version)

                # If requested, fetch sample WAS webapp data
                if fetch_sample:
                    result["sample_data"] = _fetch_was_sample(username, password, base_url, version)
                return result
            elif response.status_code == 404:
                # Could be API version not supported OR WAS module not enabled
                # Try next version before concluding module is disabled
                logger.debug("WAS: API version %s returned 404, trying older version", version)
                last_error = f"API version {version} not found (404)"
                continue
            elif response.status_code == 401:
                last_error = "Authentication failed"
                continue
            else:
                last_error = f"HTTP {response.status_code}"
                continue
        except Exception as e:
            last_error = str(e)
            continue

    # All versions failed - likely WAS module not enabled
    result["status"] = "failed"
    result["error"] = last_error or "WAS module may not be enabled (all API versions returned 404)"
    return result


def generate_summary(test_results: Dict) -> Tuple[list, list]:
    """
    Generate summary of available and unavailable modules.

    :param Dict test_results: Dictionary of test results
    :return: Tuple of (available modules, unavailable modules)
    :rtype: Tuple[list, list]
    """
    available = [name.upper() for name, test in test_results.items() if test["status"] == "success"]
    unavailable = [name.upper() for name, test in test_results.items() if test["status"] != "success"]
    return available, unavailable


def save_diagnostics_report(results: Dict, output_file: str) -> None:
    """
    Save diagnostics results to JSON file.

    :param Dict results: Diagnostics results dictionary
    :param str output_file: Output file path
    :raises IOError: If file cannot be written
    """
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)


def run_all_diagnostics(username: str, password: str, base_url: str, fetch_samples: bool = False) -> Dict:
    """
    Run all diagnostic tests and return results.

    :param str username: Qualys username
    :param str password: Qualys password
    :param str base_url: Qualys API base URL
    :param bool fetch_samples: If True, fetch sample data from each successful API
    :return: Complete diagnostics results
    :rtype: Dict
    """
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "config": {"username": username, "base_url": base_url},
        "tests": {},
    }

    # Run all tests with optional sample data fetching
    results["tests"]["vmdr"] = test_vmdr_authentication(username, password, base_url, fetch_samples)
    results["tests"]["container_security"] = test_container_authentication(username, password, base_url, fetch_samples)
    results["tests"]["was"] = test_was_authentication(username, password, base_url, fetch_samples)

    # Generate summary
    available, unavailable = generate_summary(results["tests"])
    results["summary"] = {"modules_available": available, "modules_unavailable": unavailable}

    return results
