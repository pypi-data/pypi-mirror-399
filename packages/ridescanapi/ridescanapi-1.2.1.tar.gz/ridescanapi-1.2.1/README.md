Here are the updated files.
```python
import requests
import logging
import os
import mimetypes
from contextlib import ExitStack
from typing import Optional, List, Dict, Any, Union
from .exceptions import (
    RideScanError, AuthenticationError, ValidationError, 
    ResourceNotFoundError, ConflictError, ServerError
)

# Set up a library-specific logger to keep our SDK logs distinct from user app logs
logger = logging.getLogger("ridescanapi")

class RideScanClient:
    """
    Official Python SDK for the RideScan Safety Layer API.
    
    This client handles authentication, request formatting, error handling, 
    and resource management for Robots, Missions, Files, and Models.
    """

    def __init__(self, api_key: str, base_url: str = "http://localhost:8000/api", timeout: int = 300):
        """
        Initialize the RideScan client.

        Args:
            api_key (str): The unique API key for authentication (starts with 'rsk_').
            base_url (str): The root URL of the API. Defaults to localhost for development.
            timeout (int): Request timeout in seconds. Defaults to 300s to accommodate large file uploads.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        
        self.session.headers.update({
            "X-API-KEY": api_key,
            "User-Agent": "ridescan-python-sdk/1.1.0"
        })

    def __enter__(self):
        """Enables usage of the client as a context manager (with statement)."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensures the network session is closed properly when exiting the context."""
        self.session.close()

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Internal utility to parse API responses and raise specific exceptions.
        """
        try:
            # Raise HTTPError for 4xx/5xx status codes first
            response.raise_for_status()
            
            # 204 No Content has no JSON body
            if response.status_code != 204: 
                return response.json()
            return {}

        except requests.exceptions.HTTPError:
            try:
                payload = response.json()
                if "api_response" in payload:
                    msg = payload.get("message")
                    code = "UNKNOWN"
                    details = payload.get("errors")
                else:
                    error_body = payload.get("error", {})
                    if isinstance(error_body, str):
                        msg = error_body
                        code = "UNKNOWN"
                        details = None
                    else:
                        code = error_body.get("code", "UNKNOWN")
                        msg = error_body.get("message", str(response.reason))
                        details = error_body.get("details")

                if code.startswith("RS-AUTH") or response.status_code == 401:
                    raise AuthenticationError(msg, code, details)
                elif code.startswith("RS-VAL") or response.status_code == 400:
                    raise ValidationError(msg, code, details)
                elif response.status_code == 404:
                    raise ResourceNotFoundError(msg, code, details)
                elif response.status_code == 409:
                    raise ConflictError(msg, code, details)
                elif response.status_code >= 500:
                    raise ServerError(msg, code, details)
                else:
                    raise RideScanError(msg, code, details)

            except ValueError:
                raise RideScanError(f"HTTP {response.status_code}: {response.text[:100]}")

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Internal method to execute HTTP requests with unified error handling."""
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"Request: {method} {url}")
        
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            return self._handle_response(response)
        except requests.exceptions.ConnectionError:
            raise RideScanError("Failed to connect to RideScan API. Is the server running?")
        except requests.exceptions.Timeout:
            raise RideScanError(f"Request timed out after {self.timeout}s")

    # ==========================
    # ROBOT RESOURCES
    # ==========================
    
    def create_robot(self, name: str, robot_type: str) -> Dict[str, Any]:
        """
        Register a new robot in the system.

        Args:
            name (str): A unique friendly name for the robot.
            robot_type (str): The type identifier (e.g., 'SPOT', 'UR6').

        Returns:
            dict: The created robot object containing 'robot_id'.
        """
        payload = {"params": {"robot_name": name, "robot_type": robot_type}}
        return self._request("POST", "/robot/create", json=payload)

    def get_robots(self, robot_id: Optional[str] = None, name: Optional[str] = None, robot_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for robots matching the provided criteria.

        Args:
            robot_id (str, optional): Search by specific Robot UUID.
            name (str, optional): Search by robot name.
            robot_type (str, optional): Filter by robot type.

        Returns:
            list: A list of matching robot dictionaries.
        """
        criteria = {}
        if robot_id: criteria["robot_id"] = robot_id
        if name: criteria["robot_name"] = name
        if robot_type: criteria["robot_type"] = robot_type
        
        response = self._request("GET", "/getrobot", json={"criteria": criteria})
        return response.get("robot_list", [])

    def edit_robot(self, robot_id: str, new_name: Optional[str] = None, new_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing robot's details.

        Args:
            robot_id (str): The public UUID of the robot to update.
            new_name (str, optional): The new name to assign.
            new_type (str, optional): The new robot type.

        Returns:
            dict: The updated robot object.
        """
        params = {}
        if new_name: params["robot_name"] = new_name
        if new_type: params["robot_type"] = new_type
        
        if not params: 
            raise ValidationError("Must provide at least new_name or new_type")
        
        return self._request("PATCH", "/editrobot", json={"criteria": {"robot_id": robot_id}, "params": params})

    def delete_robot(self, robot_id: str) -> Dict[str, Any]:
        """
        Permanently delete a robot and its associated resources.

        Args:
            robot_id (str): The public UUID of the robot to delete.
        """
        return self._request("DELETE", "/deleterobot", json={"criteria": {"robot_id": robot_id}})

    # ==========================
    # MISSION RESOURCES
    # ==========================

    def create_mission(self, robot_id: str, mission_name: str) -> Dict[str, Any]:
        """
        Create a new mission linked to a specific robot.

        Args:
            robot_id (str): The public UUID of the robot performing the mission.
            mission_name (str): A descriptive name for this mission.

        Returns:
            dict: The created mission object containing 'mission_id'.
        """
        return self._request("POST", "/createmission", json={"params": {"robot_id": robot_id, "mission_name": mission_name}})

    def get_missions(self, robot_id: Optional[str] = None, mission_id: Optional[str] = None, mission_name: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for missions matching the provided criteria.

        Args:
            robot_id (str, optional): Filter missions by robot UUID.
            mission_id (str, optional): Filter by specific mission UUID.
            mission_name (str, optional): Search by mission name.
            start_time (str, optional): Filter by start timestamp (ISO format).
            end_time (str, optional): Filter by end timestamp (ISO format).

        Returns:
            list: A list of matching mission dictionaries.
        """
        criteria = {}
        if robot_id: criteria["robot_id"] = robot_id
        if mission_id: criteria["mission_id"] = mission_id
        if mission_name: criteria["mission_name"] = mission_name
        if start_time: criteria["start_time"] = start_time
        if end_time: criteria["end_time"] = end_time
        
        response = self._request("GET", "/getmission", json={"criteria": criteria})
        return response.get("mission_list", [])

    def edit_mission(self, robot_id: str, mission_id: str, new_name: str) -> Dict[str, Any]:
        """
        Rename an existing mission.

        Args:
            robot_id (str): The UUID of the robot linked to the mission.
            mission_id (str): The UUID of the mission to update.
            new_name (str): The new name for the mission.
        """
        return self._request("PATCH", "/editmission", json={"criteria": {"robot_id": robot_id, "mission_id": mission_id}, "params": {"mission_name": new_name}})

    def delete_mission(self, robot_id: str, mission_id: str) -> Dict[str, Any]:
        """
        Permanently delete a mission.

        Args:
            robot_id (str): The UUID of the robot linked to the mission.
            mission_id (str): The UUID of the mission to delete.
        """
        return self._request("DELETE", "/deletemission", json={"criteria": {"robot_id": robot_id, "mission_id": mission_id}})

    # ==========================
    # FILE RESOURCES
    # ==========================

    def upload_files(self, 
                     robot_id: str, 
                     mission_id: str, 
                     file_paths: List[str], 
                     file_type: str = "calib_file") -> Dict[str, Any]:
        """
        Bulk upload files (e.g., .bag, .csv) for a mission.

        Args:
            robot_id (str): The public UUID of the robot.
            mission_id (str): The public UUID of the mission.
            file_paths (List[str]): List of absolute local file paths to upload.
            file_type (str): 'calib_file' (training) or 'process_file' (inference).

        Returns:
            dict: Summary of uploaded files.
        """
        if not file_paths:
            raise ValidationError("file_paths list cannot be empty")

        url = f"{self.base_url}/upload/bulk"
        data = {
            "robot_pid": robot_id,
            "mission_pid": mission_id,
            "file_type": file_type
        }

        with ExitStack() as stack:
            files_to_send = []
            for path in file_paths:
                if not os.path.exists(path):
                    raise ValidationError(f"File not found: {path}")
                
                filename = os.path.basename(path)
                mime_type, _ = mimetypes.guess_type(path)
                if not mime_type:
                    mime_type = "application/octet-stream"

                # Open file and add to stack context
                file_obj = stack.enter_context(open(path, "rb"))
                files_to_send.append(("files", (filename, file_obj, mime_type)))

            response = self.session.post(url, data=data, files=files_to_send, timeout=self.timeout)
            return self._handle_response(response)

    def list_files(self, robot_id: str, mission_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve a list of all files uploaded to a specific mission.

        Args:
            robot_id (str): The public UUID of the robot.
            mission_id (str): The public UUID of the mission.

        Returns:
            list: A list of file objects containing 'unique_filename', 'original_filename', etc.
        """
        params = {
            "robot_id": robot_id,
            "mission_id": mission_id
        }
        response = self._request("GET", "/files/list", params=params)
        
        # Backend wraps list in data -> files
        if "data" in response and "files" in response["data"]:
            return response["data"]["files"]
        return []

    def delete_file(self, robot_id: str, mission_id: str, unique_filename: str) -> Dict[str, Any]:
        """
        Delete a specific uploaded file from storage and database.

        Args:
            robot_id (str): The public UUID of the robot.
            mission_id (str): The public UUID of the mission.
            unique_filename (str): The unique identifier returned by list_files.
        """
        payload = {
            "robot_pid": robot_id,
            "mission_pid": mission_id,
            "filename": unique_filename
        }
        return self._request("DELETE", "/blob/delete", json=payload)

    # ==========================
    # MODEL RESOURCES
    # ==========================

    def calibrate_model(self, 
                       robot_id: str, 
                       mission_id: str, 
                       epochs: int = 100, 
                       robot_type: Union[str, int] = "SPOT",
                       retrain: bool = False,
                       batch_size: int = 128,
                       file_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Trigger the calibration process to train a model based on uploaded files.

        Args:
            robot_id (str): The public UUID of the robot.
            mission_id (str): The public UUID of the mission.
            epochs (int): Number of training epochs (default: 100).
            robot_type (str|int): Type identifier for the robot (default: "SPOT").
                                  Supported values: "SPOT" (0), "UR6" (1).
            retrain (bool): Whether to force retraining if a model already exists (default: False).
            batch_size (int): Batch size for training (default: 128).
            file_names (List[str], optional): Specific unique filenames to use. 
                                              If None, all mission files are used.

        Returns:
            dict: Confirmation that the training task was queued.
        """
        # Map our friendly argument names to the backend's expected keys
        payload = {
            "robot_id": robot_id,
            "mission_id": mission_id,
            "epochs1": epochs,  # Backend expects 'epochs1'
            "robot_type": robot_type,
            "retrain": retrain,
            "batch_size": batch_size
        }
        
        if file_names:
            payload["blob_names"] = file_names

        return self._request("POST", "/calibrate", json=payload)

    def run_inference(self, 
                      robot_id: str, 
                      mission_id: str, 
                      file_names: Optional[List[str]] = None, 
                      device: str = "cpu") -> Dict[str, Any]:
        """
        Execute the inference process (risk scoring) on uploaded files.

        Args:
            robot_id (str): The public UUID of the robot.
            mission_id (str): The public UUID of the mission.
            file_names (List[str], optional): Specific unique filenames to process.
                                              If None, all files are processed.
            device (str): Computation device, 'cpu' or 'cuda' (default: 'cpu').

        Returns:
            dict: The inference results or status.
        """
        payload = {
            "robot_id": robot_id,
            "mission_id": mission_id,
            "device": device
        }
        
        if file_names:
            payload["blob_names"] = file_names

        return self._request("POST", "/process", json=payload)

    def get_model_status(self, mission_id: str) -> Dict[str, Any]:
        """
        Retrieve the current status of both calibration and inference tasks.

        Args:
            mission_id (str): The public UUID of the mission to check.

        Returns:
            dict: A status object containing fields like 'calibration_status' 
                  and 'inference_status'.
        """
        params = {"mission_id": mission_id}
        # Updated to point to /api/model/mission-details (by removing the previous .. hack)
        response = self._request("GET", "/model/mission-details", params=params)
        
        # Unwrap 'data' if present, to return a cleaner object
        if "data" in response:
            return response["data"]
        return response

```

---

### 2. Updated `README.md`

**Changes Made:**

* **`robot_type`**: Removed "husky" and added "UR6". Updated the descriptions to clarify the string-to-int mapping ("SPOT" -> 0, "UR6" -> 1).
* Updated the `create_robot` and `calibrate_model` docstrings to match the new supported types.

```markdown
# RideScan Python SDK

The official Python client for the **RideScan Safety Layer API**. This SDK allows developers to programmatically manage robots, missions, file uploads, model calibration (training), and risk inference directly from their Python applications.

## 📦 Installation

```bash
pip install ridescanapi

```

---

## 🔑 Getting Started

### 1. Obtain your API Key

To use this SDK, you must have a valid API Key.

1. Go to the **RideScan Developer Console**.
2. **Create an account** or Log in.
3. Navigate to the **API Keys** section in your dashboard.
4. Click **Generate New Key**.
5. Copy the key (it starts with `rsk_...`).

### 2. Initialize the Client

You can use the client as a context manager (recommended) to automatically handle session closing, or as a standard object.

**Using Context Manager (Recommended):**

```python
from ridescanapi import RideScanClient

API_KEY = "rsk_your_api_key_here"

with RideScanClient(api_key=API_KEY) as client:
    # Your code here
    robots = client.get_robots()
    print(robots)

```

**Using Standard Initialization:**

```python
client = RideScanClient(api_key=API_KEY)
try:
    robots = client.get_robots()
finally:
    client.session.close() # Always close the session manually

```

---

## 📚 API Reference

### 🤖 Robot Resources

#### `create_robot(name, robot_type)`

Registers a new robot in the system.

* **Arguments:**
* `name` (str): A friendly name for the robot (e.g., "Warehouse-Spot-01").
* `robot_type` (str or int): The type identifier (e.g., `"SPOT"`, `"UR6"`).


* **Returns:** `dict`
```json
{
  "robot_id": "123e4567-e89b-12d3-a456-426614174000",
  "robot_name": "Warehouse-Spot-01",
  "message": "Robot created"
}

```



#### `get_robots(robot_id=None, name=None, robot_type=None)`

Search for robots matching specific criteria. If no arguments are provided, returns all robots.

* **Arguments:**
* `robot_id` (str, optional): Search by specific UUID.
* `name` (str, optional): Filter by name.
* `robot_type` (str, optional): Filter by type.


* **Returns:** `List[dict]`

#### `edit_robot(robot_id, new_name=None, new_type=None)`

Updates a robot's details.

* **Arguments:**
* `robot_id` (str): The UUID of the robot to update.
* `new_name` (str, optional): New name.
* `new_type` (str or int, optional): New type.


* **Returns:** `dict` (Updated robot object).

#### `delete_robot(robot_id)`

Permanently deletes a robot and **all** associated missions and files.

* **Arguments:** `robot_id` (str).
* **Returns:** `dict` (`{"message": "Robot deleted"}`).

---

### 🚀 Mission Resources

#### `create_mission(robot_id, mission_name)`

Creates a new mission scope under a specific robot.

* **Arguments:**
* `robot_id` (str): The UUID of the parent robot.
* `mission_name` (str): Descriptive name (e.g., "Calibration-Run-Jan").


* **Returns:** `dict` containing `mission_id`.

#### `get_missions(robot_id=None, mission_id=None, mission_name=None, ...)`

Search for missions.

* **Arguments:**
* `robot_id` (str, optional): Filter by robot.
* `mission_id` (str, optional): Filter by mission UUID.
* `mission_name` (str, optional): Filter by name.
* `start_time` / `end_time` (str, optional): Filter by date range (ISO format).


* **Returns:** `List[dict]`.

#### `edit_mission(robot_id, mission_id, new_name)`

Renames an existing mission.

* **Arguments:** `robot_id`, `mission_id`, `new_name`.
* **Returns:** `dict` (Updated mission object).

#### `delete_mission(robot_id, mission_id)`

Permanently deletes a mission.

* **Arguments:** `robot_id`, `mission_id`.
* **Returns:** `dict`.

---

### 📂 File Resources

#### `upload_files(robot_id, mission_id, file_paths, file_type='calib_file')`

Bulk uploads files (.bag, .csv, .zip) to the server. This handles large file streaming automatically.

* **Arguments:**
* `robot_id` (str): Robot UUID.
* `mission_id` (str): Mission UUID.
* `file_paths` (List[str]): List of **absolute local paths** to the files.
* `file_type` (str):
* `'calib_file'` (Default) - Use for model training/calibration.
* `'process_file'` - Use for inference/risk analysis.




* **Returns:** `dict`
```json
{
  "success": true,
  "uploaded_files": ["uuid_day1.bag", "uuid_day2.bag"],
  "failed_files": []
}

```



#### `list_files(robot_id, mission_id)`

Lists all files uploaded for a specific mission.

* **Arguments:** `robot_id`, `mission_id`.
* **Returns:** `List[dict]` containing `unique_filename`, `original_filename`, `file_size`, etc.

#### `delete_file(robot_id, mission_id, unique_filename)`

Deletes a specific file from storage and database.

* **Arguments:**
* `robot_id` (str): Robot UUID.
* `mission_id` (str): Mission UUID.
* `unique_filename` (str): The unique ID returned by `list_files` (e.g., `abc123_data.csv`).


* **Returns:** `dict`.

---

### 🧠 Model & Inference Resources

#### `calibrate_model(robot_id, mission_id, epochs=100, robot_type="SPOT", retrain=False, ...)`

Triggers an asynchronous Kubernetes job to train a model using uploaded **calibration files**.

* **Arguments:**
* `robot_id` (str): Robot UUID.
* `mission_id` (str): Mission UUID.
* `epochs` (int): Training duration (Default: 100).
* `robot_type` (str or int): Robot type identifier (Default: `"SPOT"`).
* `retrain` (bool): Force re-training if a model already exists (Default: `False`).
* `file_names` (List[str], optional): specific subset of unique filenames to use. If `None`, uses all uploaded calibration files.


* **Returns:** `dict` indicating the task was queued.
```json
{
  "message": "Training task queued",
  "details": {"task_id": "..."}
}

```



#### `run_inference(robot_id, mission_id, file_names=None, device='cpu')`

Runs risk analysis on uploaded **inference files** using the trained model.

* **Arguments:**
* `robot_id` (str): Robot UUID.
* `mission_id` (str): Mission UUID.
* `device` (str): Compute device (`'cpu'` or `'cuda'`).
* `file_names` (List[str], optional): specific subset of unique filenames to analyze. If `None`, uses all available files.


* **Returns:** `dict` (Inference results).

#### `get_model_status(mission_id)`

Checks the status of calibration or inference tasks.

* **Arguments:** `mission_id`.
* **Returns:** `dict`
```json
{
  "calibration_status": "Training_Completed",
  "inference_status": "processing_completed",
  "epochs": 100,
  "upload_time": "..."
}

```



---

## ⚠️ Error Handling

The SDK raises specific exceptions from `ridescanapi.exceptions` to help you handle errors gracefully.

| Exception Class | HTTP Code | Description |
| --- | --- | --- |
| `AuthenticationError` | 401 | Invalid API Key. Check your dashboard. |
| `ValidationError` | 400 | Missing arguments, invalid file types, or malformed requests. |
| `ResourceNotFoundError` | 404 | Robot, Mission, or File ID does not exist. |
| `ConflictError` | 409 | Resource already exists (e.g., creating a robot with a duplicate ID). |
| `ServerError` | 500+ | Internal backend issue. |
| `RideScanError` | - | Generic base exception for other errors. |

**Example Usage:**

```python
from ridescanapi.exceptions import ResourceNotFoundError, ValidationError

try:
    client.delete_robot("invalid-id")
except ResourceNotFoundError:
    print("Robot not found!")
except ValidationError as e:
    print(f"Invalid input: {e}")

```

---

## 📝 Enums & Values

### `robot_type`

Used in `create_robot` and `calibrate_model`.

* `"SPOT"` (Boston Dynamics Spot) - Maps to integer `0`
* `"UR6"` - Maps to integer `1`

### `file_type`

Used in `upload_files`.

* `"calib_file"`: Files used to train/calibrate the model.
* `"process_file"`: Files used for inference/risk assessment.

### `device`

Used in `run_inference`.

* `"cpu"` (Default)
* `"cuda"` (GPU - Requires backend support)

```

```