import os
import requests
from requests import exceptions as requests_exceptions
from dotenv import load_dotenv
from typing import Optional, Dict, Any, IO, List
import logging
from datetime import datetime
import narwhals as nw
from narwhals.typing import IntoFrameT
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Custom Exceptions
class CrowdCentAPIError(Exception):
    """Base exception for API errors."""

    pass


class AuthenticationError(CrowdCentAPIError):
    """Exception for authentication issues."""

    pass


class NotFoundError(CrowdCentAPIError):
    """Exception for 404 errors."""

    pass


class ClientError(CrowdCentAPIError):
    """Exception for 4xx client errors (excluding 401, 404)."""

    pass


class ServerError(CrowdCentAPIError):
    """Exception for 5xx server errors."""

    pass


class ChallengeClient:
    """
    Client for interacting with a specific CrowdCent Challenge.

    Handles authentication and provides methods for accessing challenge data,
    training datasets, inference data, and managing prediction submissions for
    a specific challenge identified by its slug.
    """

    DEFAULT_BASE_URL = "https://crowdcent.com/api"
    API_KEY_ENV_VAR = "CROWDCENT_API_KEY"

    def __init__(
        self,
        challenge_slug: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initializes the ChallengeClient for a specific challenge.

        Args:
            challenge_slug: The unique identifier (slug) for the challenge.
            api_key: Your CrowdCent API key. If not provided, it will attempt
                     to load from the CROWDCENT_API_KEY environment variable
                     or a .env file.
            base_url: The base URL of the CrowdCent API. Defaults to
                      https://crowdcent.com/api.
        """
        load_dotenv()  # Load .env file if present
        self.api_key = api_key or os.getenv(self.API_KEY_ENV_VAR)
        if not self.api_key:
            raise AuthenticationError(
                f"API key not provided and not found in environment variable "
                f"'{self.API_KEY_ENV_VAR}' or .env file."
            )

        self.challenge_slug = challenge_slug
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Api-Key {self.api_key}"})
        logger.info(
            f"ChallengeClient initialized for '{challenge_slug}' at URL: {self.base_url}"
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        files: Optional[Dict[str, IO]] = None,
        stream: bool = False,
        data: Optional[Dict] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> requests.Response:
        """
        Internal helper method to make authenticated API requests.

        Args:
            method: HTTP method (e.g., 'GET', 'POST').
            endpoint: API endpoint path (e.g., '/challenges/').
            params: URL parameters.
            json_data: JSON data for the request body.
            files: Files to upload (for multipart/form-data).
            stream: Whether to stream the response (for downloads).
            data: Dictionary of form data to send with multipart requests.
            max_retries: Maximum number of retry attempts for connection errors.
            retry_delay: Initial delay between retries (seconds). Will use exponential backoff.

        Returns:
            The requests.Response object.

        Raises:
            AuthenticationError: If the API key is invalid (401).
            NotFoundError: If the resource is not found (404).
            ClientError: For other 4xx errors.
            ServerError: For 5xx errors.
            CrowdCentAPIError: For other request exceptions.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.debug(
            f"Request: {method} {url} Params: {params} JSON: {json_data is not None} "
            f"Data: {data is not None} Files: {files is not None}"
        )

        for attempt in range(max_retries + 1):
            try:
                response = self.session.request(
                    method,
                    url,
                    params=params,
                    json=json_data,
                    files=files,
                    stream=stream,
                    data=data,
                )
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                logger.debug(f"Response: {response.status_code}")
                return response
            except requests_exceptions.HTTPError as e:
                status_code = e.response.status_code

                # Try to parse standardized error format: {"error": {"code": "ERROR_CODE", "message": "Description"}}
                try:
                    error_data = e.response.json()
                    if "error" in error_data and isinstance(error_data["error"], dict):
                        error_code = error_data["error"].get("code", "UNKNOWN_ERROR")
                        error_message = error_data["error"].get(
                            "message", e.response.text
                        )
                    else:
                        error_code = "API_ERROR"
                        error_message = e.response.text
                except requests_exceptions.JSONDecodeError:
                    error_code = "API_ERROR"
                    error_message = e.response.text

                logger.error(
                    f"API Error ({status_code}): {error_code} - {error_message} for {method} {url}"
                )

                if status_code == 401:
                    raise AuthenticationError(
                        f"Authentication failed (401): {error_message} [{error_code}]"
                    ) from e
                elif status_code == 404:
                    raise NotFoundError(
                        f"Resource not found (404): {error_message} [{error_code}]"
                    ) from e
                elif 400 <= status_code < 500:
                    raise ClientError(
                        f"Client error ({status_code}): {error_message} [{error_code}]"
                    ) from e
                elif 500 <= status_code < 600:
                    raise ServerError(
                        f"Server error ({status_code}): {error_message} [{error_code}]"
                    ) from e
                else:
                    raise CrowdCentAPIError(
                        f"HTTP error ({status_code}): {error_message} [{error_code}]"
                    ) from e
            except (
                requests_exceptions.ConnectionError,
                requests_exceptions.Timeout,
            ) as e:
                # Connection errors and timeouts are retryable
                if attempt < max_retries:
                    delay = retry_delay * (2**attempt)  # Exponential backoff
                    logger.warning(
                        f"Connection error: {e}. Retrying in {delay:.1f}s... "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(delay)
                    continue
                logger.error(
                    f"Request failed after {max_retries} retries: {e} for {method} {url}"
                )
                raise CrowdCentAPIError(
                    f"Request failed after {max_retries} retries: {e}"
                ) from e
            except requests_exceptions.RequestException as e:
                logger.error(f"Request failed: {e} for {method} {url}")
                raise CrowdCentAPIError(f"Request failed: {e}") from e

    def _download_file(self, endpoint: str, dest_path: str, description: str) -> None:
        """Download a file from the API with progress bar.

        Args:
            endpoint: API endpoint to download from.
            dest_path: Local file path to save to.
            description: Human-readable description for logging (e.g., "training data v1.0").
        """
        logger.info(f"Downloading {description} to {dest_path}")
        response = self._request("GET", endpoint, stream=True)
        total_size = int(response.headers.get("content-length", 0))

        try:
            from tqdm import tqdm

            with open(dest_path, "wb") as f:
                with tqdm(
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    desc=f"Downloading {os.path.basename(dest_path)}",
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        pbar.update(len(chunk))
            logger.info(f"Successfully downloaded {description} to {dest_path}")
        except IOError as e:
            logger.error(f"Failed to write to {dest_path}: {e}")
            raise CrowdCentAPIError(f"Failed to write file: {e}") from e

    # --- Class Method for Listing All Challenges ---

    @classmethod
    def list_all_challenges(
        cls, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lists all active challenges.

        This is a class method that doesn't require a challenge_slug.
        Use this to discover available challenges before initializing a ChallengeClient.

        Args:
            api_key: Your CrowdCent API key. If not provided, it will attempt
                     to load from the CROWDCENT_API_KEY environment variable
                     or a .env file.
            base_url: The base URL of the CrowdCent API. Defaults to
                      http://crowdcent.com/api.

        Returns:
            A list of dictionaries, each representing an active challenge.
        """
        # Create a temporary session for this request
        load_dotenv()
        api_key = api_key or os.getenv(cls.API_KEY_ENV_VAR)
        if not api_key:
            raise AuthenticationError(
                f"API key not provided and not found in environment variable "
                f"'{cls.API_KEY_ENV_VAR}' or .env file."
            )

        base_url = (base_url or cls.DEFAULT_BASE_URL).rstrip("/")
        session = requests.Session()
        session.headers.update({"Authorization": f"Api-Key {api_key}"})

        url = f"{base_url}/challenges/"
        try:
            response = session.get(url)
            response.raise_for_status()
            return response.json()
        except requests_exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 401:
                raise AuthenticationError("Authentication failed (401)")
            elif status_code == 404:
                raise NotFoundError("Resource not found (404)")
            elif 400 <= status_code < 500:
                raise ClientError(f"Client error ({status_code})")
            elif 500 <= status_code < 600:
                raise ServerError(f"Server error ({status_code})")
            else:
                raise CrowdCentAPIError(f"HTTP error ({status_code})")
        except requests_exceptions.RequestException as e:
            raise CrowdCentAPIError(f"Request failed: {e}")

    # --- Challenge Methods ---

    def get_challenge(self) -> Dict[str, Any]:
        """Gets details for this challenge.

        Returns:
            A dictionary representing this challenge.

        Raises:
            NotFoundError: If the challenge with the given slug is not found.
        """
        response = self._request("GET", f"/challenges/{self.challenge_slug}/")
        return response.json()

    # --- Training Data Methods ---

    def list_training_datasets(self) -> List[Dict[str, Any]]:
        """Lists all training dataset versions for this challenge.

        Returns:
            A list of dictionaries, each representing a training dataset version.

        Raises:
            NotFoundError: If the challenge is not found.
        """
        response = self._request(
            "GET", f"/challenges/{self.challenge_slug}/training_data/"
        )
        return response.json()

    def get_training_dataset(self, version: str) -> Dict[str, Any]:
        """Gets details for a specific training dataset version.

        Args:
            version: The version string of the training dataset (e.g., '1.0', '2.1')
                     or the special value ``"latest"`` to get the latest version.

        Returns:
            A dictionary representing the specified training dataset.

        Raises:
            NotFoundError: If the challenge or the specified training dataset is not found.
        """
        if version == "latest":
            response = self._request(
                "GET", f"/challenges/{self.challenge_slug}/training_data/latest/"
            )
            return response.json()

        response = self._request(
            "GET", f"/challenges/{self.challenge_slug}/training_data/{version}/"
        )
        return response.json()

    def download_training_dataset(self, version: str, dest_path: str):
        """Downloads the training data file for a specific dataset version.

        Args:
            version: The version string of the training dataset (e.g., '1.0', '2.1')
                    or 'latest' to get the latest version.
            dest_path: The local file path to save the downloaded dataset.

        Raises:
            NotFoundError: If the challenge, dataset, or its file is not found.
        """
        if version == "latest":
            latest_info = self.get_training_dataset("latest")
            version = latest_info["version"]

        endpoint = f"/challenges/{self.challenge_slug}/training_data/{version}/download/"
        self._download_file(endpoint, dest_path, f"training data v{version}")

    # --- Inference Data Methods ---

    def list_inference_data(self) -> List[Dict[str, Any]]:
        """Lists all inference data periods for this challenge.

        Returns:
            A list of dictionaries, each representing an inference data period.

        Raises:
            NotFoundError: If the challenge is not found.
        """
        response = self._request(
            "GET", f"/challenges/{self.challenge_slug}/inference_data/"
        )
        return response.json()

    def get_inference_data(self, release_date: str) -> Dict[str, Any]:
        """Gets details for a specific inference data period by its release date.

        Args:
            release_date: The release date of the inference data in 'YYYY-MM-DD' format.
                          You can also pass the special values:
                          - ``"current"`` to fetch the current active inference period
                          - ``"latest"`` to fetch the most recently *available* inference period

        Returns:
            A dictionary representing the specified inference data period.

        Raises:
            NotFoundError: If the challenge or the specified inference data is not found.
            ClientError: If the date format is invalid.
        """
        if release_date == "current":
            response = self._request(
                "GET", f"/challenges/{self.challenge_slug}/inference_data/current/"
            )
            return response.json()

        if release_date == "latest":
            # Simply resolve via list_inference_data(); avoid noisy probe.
            periods = self.list_inference_data()
            if not periods:
                raise NotFoundError(
                    "No inference data periods found for this challenge."
                )

            latest_period = max(periods, key=lambda p: p["release_date"])
            release_date_iso = latest_period["release_date"]
            release_date = release_date_iso.split("T")[0]

        # Validate date format for explicit dates
        try:
            datetime.strptime(release_date, "%Y-%m-%d")
        except ValueError:
            raise ClientError(
                f"Invalid date format: {release_date}. Use 'YYYY-MM-DD' format."
            )

        response = self._request(
            "GET", f"/challenges/{self.challenge_slug}/inference_data/{release_date}/"
        )
        return response.json()

    def download_inference_data(
        self,
        release_date: str,
        dest_path: str,
        poll: bool = True,
        poll_interval: int = 30,
        timeout: Optional[int] = 900,
    ):
        """Downloads the inference features file for a specific period.

        Args:
            release_date: The release date of the inference data in 'YYYY-MM-DD' format
                          or the special values ``"current"`` or ``"latest"``.
            dest_path: The local file path to save the downloaded features file.
            poll: Whether to wait for the inference data to be available before downloading.
            poll_interval: Seconds to wait between retries when polling.
            timeout: Maximum seconds to wait before raising :class:`TimeoutError`.
                ``None`` waits indefinitely.

        Raises:
            NotFoundError: If the challenge, inference data, or its file is not found.
            ClientError: If the date format is invalid.
        """
        if release_date == "current":
            # If polling is enabled, delegate to wait_for_inference_data which wraps
            # this method and adds retry logic. Otherwise attempt a single direct
            # download request.
            if poll:
                self.wait_for_inference_data(dest_path, poll_interval, timeout)
                return

            # Polling disabled → attempt once and propagate NotFoundError on 404.
            endpoint = (
                f"/challenges/{self.challenge_slug}/inference_data/current/download/"
            )
        else:
            if release_date == "latest":
                latest_info = self.get_inference_data("latest")
                release_date_iso = latest_info.get("release_date")
                release_date = (
                    release_date_iso.split("T")[0] if release_date_iso else None
                )
                if not release_date:
                    raise CrowdCentAPIError(
                        "Malformed response when resolving latest inference period."
                    )

            # Validate date format after any resolution.
            try:
                datetime.strptime(release_date, "%Y-%m-%d")
            except ValueError:
                raise ClientError(
                    f"Invalid date format: {release_date}. Use 'YYYY-MM-DD' format."
                )

            endpoint = f"/challenges/{self.challenge_slug}/inference_data/{release_date}/download/"

        self._download_file(endpoint, dest_path, f"inference data {release_date}")

    def wait_for_inference_data(
        self,
        dest_path: str,
        poll_interval: int = 30,
        timeout: Optional[int] = 900,
    ) -> None:
        """Waits for the *current* inference data release to appear and downloads it.

        The internal data-generation pipeline begins around 14:00 UTC, but the
        public inference file becomes available only after it passes data-quality
        checks. This helper repeatedly calls
        :py:meth:`download_inference_data` with ``release_date="current"`` until
        the file is ready (HTTP 404s are silently retried).

        Args:
            dest_path: Local path where the parquet file will be saved once available.
            poll_interval: Seconds to wait between retries.
            timeout: Maximum seconds to wait before raising :class:`TimeoutError`.
                ``None`` waits indefinitely.

        Raises:
            TimeoutError: If *timeout* seconds pass without a successful download.
            CrowdCentAPIError: For unrecoverable errors returned by the API.
        """
        start_time = time.time()
        attempts = 0

        while True:
            attempts += 1
            try:
                # Try to download the *current* period *once*. Pass poll=False to avoid
                # the mutual recursion between `wait_for_inference_data` and
                # `download_inference_data` which would otherwise trigger an infinite
                # loop when the file is not yet available.
                self.download_inference_data("current", dest_path, poll=False)
                logger.info(
                    f"Successfully downloaded inference data after {attempts} attempt(s) to {dest_path}"
                )
                return  # Success – exit the loop
            except NotFoundError:
                # File not published yet – check timeout and sleep before retrying.
                elapsed = time.time() - start_time
                if timeout is not None and elapsed >= timeout:
                    raise TimeoutError(
                        f"Inference data was not available after waiting {timeout} seconds."
                    )
                logger.debug(
                    f"Inference data not yet available (attempt {attempts}). "
                    f"Sleeping {poll_interval}s before retrying."
                )
                time.sleep(poll_interval)

    # --- Submission Methods ---

    def list_submissions(self, period: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists the authenticated user's submissions for this challenge.

        Args:
            period: Optional filter for submissions by period:
                  - 'current': Only show submissions for the current active period
                  - 'YYYY-MM-DD': Only show submissions for a specific inference period date

        Returns:
            A list of dictionaries, each representing a submission.
        """
        params = {}
        if period:
            params["period"] = period

        response = self._request(
            "GET", f"/challenges/{self.challenge_slug}/submissions/", params=params
        )
        return response.json()

    def get_submission(self, submission_id: int) -> Dict[str, Any]:
        """Gets details for a specific submission by its ID.

        Args:
            submission_id: The ID of the submission to retrieve.

        Returns:
            A dictionary representing the specified submission.

        Raises:
            NotFoundError: If the submission with the given ID is not found
                           or doesn't belong to the user.
        """
        response = self._request(
            "GET", f"/challenges/{self.challenge_slug}/submissions/{submission_id}/"
        )
        return response.json()

    @nw.narwhalify
    def submit_predictions(
        self,
        file_path: str = "submission.parquet",
        df: Optional[IntoFrameT] = None,
        slot: int = 1,
        queue_next: bool = True,
        temp: bool = True,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> Dict[str, Any]:
        """Submit predictions for this challenge.

        If a submission window is currently open, the prediction is submitted immediately.
        If no window is open, the prediction is queued and will be automatically submitted
        when the next window opens.

        You can provide either a file path to an existing Parquet file or a DataFrame
        that will be temporarily saved as Parquet for submission.

        The data must contain the required prediction columns specified by the challenge
        (e.g., id, pred_10d, pred_30d).

        Args:
            file_path: Optional path to an existing prediction Parquet file.
            df: Optional DataFrame with the prediction columns. If provided,
                it will be temporarily saved as Parquet for submission.
            slot: Submission slot number (1-based).
            queue_next: Whether to also queue this submission for the next period
                (auto-rollover). Defaults to True. When submitting during an open
                window, this queues a copy for the following period.
            temp: Whether to save the DataFrame to a temporary file.
            max_retries: Maximum number of retry attempts for connection errors (default: 3).
            retry_delay: Initial delay between retries in seconds (default: 1.0).

        Returns:
            A dictionary with submission details. The shape depends on context:

            - **Window open (immediate submission)**: Contains submission fields like
                `id`, `status`, `slot`, `submitted_at`, plus `queued_for_next` (bool).
            - **Window closed (queued)**: Contains `status: "queued"`, `slot`,
                `challenge`, and a `message` describing when it will be submitted.

        Raises:
            ValueError: If neither file_path nor df is provided, or if both are provided.
            FileNotFoundError: If the specified file_path does not exist.
            ClientError: If the submission is invalid (e.g., wrong format, missing columns).

        Examples:
            # Submit from a DataFrame
            client.submit_predictions(df=predictions_df)

            # Submit from a file
            client.submit_predictions(file_path="predictions.parquet")

            # Submit and opt-out of auto-queueing for next period
            client.submit_predictions(df=predictions_df, queue_next=False)
        """
        if df is not None:
            df.write_parquet(file_path)
            logger.info(f"Wrote DataFrame to temporary file: {file_path}")

        logger.info(
            f"Submitting predictions from {file_path} to challenge '{self.challenge_slug}' (Slot: {slot or '1'})"
        )

        try:
            with open(file_path, "rb") as f:
                files = {
                    "prediction_file": (
                        os.path.basename(file_path),
                        f,
                        "application/octet-stream",
                    )
                }
                data_payload = {
                    "slot": str(slot),
                    "also_queue_next": str(queue_next).lower(),
                }
                response = self._request(
                    "POST",
                    f"/challenges/{self.challenge_slug}/submissions/",
                    files=files,
                    data=data_payload,  # Pass slot and queue flag in data
                    max_retries=max_retries,
                    retry_delay=retry_delay,
                )
            
            resp_data = response.json()
            
            # 202=queued, 200=updated, 201=created
            msg = {202: "queued", 200: "updated", 201: "created"}.get(response.status_code, "submitted")
            logger.info(f"Submission {msg} (slot {slot})")
            if resp_data.get("queued_for_next"):
                logger.info("Also queued for next period.")
            
            return resp_data
        except FileNotFoundError as e:
            logger.error(f"Prediction file not found at {file_path}")
            raise FileNotFoundError(f"Prediction file not found at {file_path}") from e
        except IOError as e:
            logger.error(f"Failed to read prediction file {file_path}: {e}")
            raise CrowdCentAPIError(f"Failed to read prediction file: {e}") from e
        finally:
            # Clean up the temporary file if we created one
            if df is not None and temp:
                try:
                    os.unlink(file_path)
                    logger.debug(f"Cleaned up temporary file: {file_path}")
                except Exception as e:
                    logger.warning(
                        f"Failed to clean up temporary file {file_path}: {e}"
                    )

    # --- Challenge Switching ---

    def switch_challenge(self, new_challenge_slug: str) -> None:
        """Switch this client to interact with a different challenge.

        Args:
            new_challenge_slug: The slug identifier for the new challenge.

        Returns:
            None. The client is modified in-place.
        """
        self.challenge_slug = new_challenge_slug
        logger.info(f"Client switched to challenge '{new_challenge_slug}'")

    # --- Historical Performance Methods ---

    def get_performance_history(
        self, 
        scored_only: bool = True,
        slot: Optional[int] = None,
        show_progress: bool = True,
    ):
        """Get historical submission performance as a structured Polars DataFrame.
        
        Fetches all submissions with their scores and percentiles, flattens the 
        nested score data, and returns a clean DataFrame ready for analysis.
        
        Args:
            scored_only: If True (default), only include submissions that have been scored.
            slot: Optional slot filter. If provided, only include submissions from this slot.
            show_progress: If True (default), show progress bar during processing.
        
        Returns:
            A Polars DataFrame with columns:
            - id: Submission ID
            - slot: Submission slot number
            - release_date: The inference period date
            - submitted_at: When the submission was made
            - status: Submission status
            - score_*: Individual score metrics (e.g., score_spearman_10d)
            - percentile_*: Individual percentile metrics (e.g., percentile_spearman_10d)
            - total_score: The composite total score (if available)
            - total_percentile: The composite total percentile (if available)
        
        Example:
            >>> client = ChallengeClient("momentum-alpha")
            >>> df = client.get_performance_history()
            >>> print(df)
            shape: (12, 15)
            ┌─────┬──────┬─────────────┬────────────────────┬──────────────────┐
            │ id  ┆ slot ┆ release_date┆ score_spearman_10d ┆ percentile_ndcg  │
            │ --- ┆ ---  ┆ ---         ┆ ---                ┆ ---              │
            │ i64 ┆ i64  ┆ date        ┆ f64                ┆ f64              │
            ╞═════╪══════╪═════════════╪════════════════════╪══════════════════╡
            │ 123 ┆ 1    ┆ 2024-12-01  ┆ 0.15               ┆ 0.72             │
            │ ...                                                             │
            └─────┴──────┴─────────────┴────────────────────┴──────────────────┘
        """
        import polars as pl
        from tqdm import tqdm
        
        logger.info(f"Fetching submission history for '{self.challenge_slug}'...")
        submissions = self.list_submissions()
        
        if not submissions:
            logger.info("No submissions found.")
            # Return empty DataFrame with expected schema
            return pl.DataFrame({
                "id": pl.Series([], dtype=pl.Int64),
                "slot": pl.Series([], dtype=pl.Int64),
                "release_date": pl.Series([], dtype=pl.Date),
                "submitted_at": pl.Series([], dtype=pl.Datetime),
                "status": pl.Series([], dtype=pl.Utf8),
            })
        
        logger.info(f"Processing {len(submissions)} submissions...")
        rows = []
        iterator = tqdm(submissions, desc="Processing submissions", leave=False, disable=not show_progress)
        for sub in iterator:
            # Skip unscored if requested
            if scored_only and not sub.get("score_details"):
                continue
            
            # Skip if slot filter doesn't match
            if slot is not None and sub.get("slot") != slot:
                continue
            
            row = {
                "id": sub.get("id"),
                "slot": sub.get("slot"),
                "release_date": sub.get("inference_data_release_date"),
                "submitted_at": sub.get("submitted_at"),
                "status": sub.get("status"),
            }
            
            # Flatten score_details
            score_details = sub.get("score_details") or {}
            for key, value in score_details.items():
                row[f"score_{key}"] = value
            
            # Flatten percentile_details
            percentile_details = sub.get("percentile_details") or {}
            for key, value in percentile_details.items():
                row[f"percentile_{key}"] = value
            
            # Extract total score/percentile if present
            if "total" in score_details:
                row["total_score"] = score_details["total"]
            if "total" in percentile_details:
                row["total_percentile"] = percentile_details["total"]
            
            rows.append(row)
        
        if not rows:
            logger.info("No scored submissions found after filtering.")
            return pl.DataFrame({
                "id": pl.Series([], dtype=pl.Int64),
                "slot": pl.Series([], dtype=pl.Int64),
                "release_date": pl.Series([], dtype=pl.Date),
                "submitted_at": pl.Series([], dtype=pl.Datetime),
                "status": pl.Series([], dtype=pl.Utf8),
            })
        
        df = pl.DataFrame(rows)
        
        # Parse dates
        if "release_date" in df.columns:
            df = df.with_columns(
                pl.col("release_date").str.slice(0, 10).str.to_date("%Y-%m-%d")
            )
        if "submitted_at" in df.columns:
            df = df.with_columns(
                pl.col("submitted_at").str.to_datetime("%Y-%m-%dT%H:%M:%S%.f%Z", time_zone="UTC")
            )
        
        # Sort by release_date descending (most recent first)
        if "release_date" in df.columns:
            df = df.sort("release_date", descending=True)
        
        logger.info(f"Loaded {len(df)} scored submissions.")
        return df

    def performance_summary(
        self, 
        slot: Optional[int] = None,
        show_progress: bool = True,
    ) -> Dict[str, Any]:
        """Get aggregate statistics for historical submission performance.
        
        Calculates mean, std, min, max, and count for all score and percentile metrics.
        
        Args:
            slot: Optional slot filter. If provided, only include submissions from this slot.
            show_progress: If True (default), show progress bar during data fetch.
        
        Returns:
            A dictionary with summary statistics:
            {
                "count": 12,
                "date_range": {"first": "2024-09-01", "last": "2024-12-15"},
                "scores": {
                    "spearman_10d": {"mean": 0.12, "std": 0.05, "min": 0.02, "max": 0.25},
                    ...
                },
                "percentiles": {
                    "spearman_10d": {"mean": 0.65, "std": 0.15, "min": 0.32, "max": 0.92},
                    ...
                },
                "total": {
                    "score": {"mean": 0.45, "std": 0.08, ...},
                    "percentile": {"mean": 0.68, "std": 0.12, ...}
                }
            }
        
        Example:
            >>> client = ChallengeClient("momentum-alpha")
            >>> summary = client.performance_summary()
            >>> print(f"Average percentile: {summary['total']['percentile']['mean']:.1%}")
            Average percentile: 68.2%
        """
        df = self.get_performance_history(scored_only=True, slot=slot, show_progress=show_progress)
        
        if df.is_empty():
            return {
                "count": 0,
                "date_range": None,
                "scores": {},
                "percentiles": {},
                "total": None,
            }
        
        # Get score and percentile columns
        score_cols = [c for c in df.columns if c.startswith("score_") and c != "score_total"]
        percentile_cols = [c for c in df.columns if c.startswith("percentile_") and c != "percentile_total"]
        
        def calc_stats(series):
            """Calculate summary stats for a numeric series."""
            clean = series.drop_nulls()
            if len(clean) == 0:
                return None
            return {
                "mean": float(clean.mean()),
                "std": float(clean.std()) if len(clean) > 1 else 0.0,
                "min": float(clean.min()),
                "max": float(clean.max()),
                "count": len(clean),
            }
        
        result = {
            "count": len(df),
            "date_range": {
                "first": str(df["release_date"].min()),
                "last": str(df["release_date"].max()),
            } if "release_date" in df.columns else None,
            "scores": {},
            "percentiles": {},
            "total": None,
        }
        
        # Score stats
        for col in score_cols:
            metric_name = col.replace("score_", "")
            stats = calc_stats(df[col])
            if stats:
                result["scores"][metric_name] = stats
        
        # Percentile stats  
        for col in percentile_cols:
            metric_name = col.replace("percentile_", "")
            stats = calc_stats(df[col])
            if stats:
                result["percentiles"][metric_name] = stats
        
        # Total score/percentile
        total_stats = {}
        if "total_score" in df.columns:
            stats = calc_stats(df["total_score"])
            if stats:
                total_stats["score"] = stats
        if "total_percentile" in df.columns:
            stats = calc_stats(df["total_percentile"])
            if stats:
                total_stats["percentile"] = stats
        
        if total_stats:
            result["total"] = total_stats
        
        return result

    def print_performance_summary(self, slot: Optional[int] = None, show_progress: bool = True) -> None:
        """Print a nicely formatted summary of historical performance.
        
        Args:
            slot: Optional slot filter. If provided, only include submissions from this slot.
            show_progress: If True (default), show progress bar during data fetch.
        
        Example:
            >>> client = ChallengeClient("momentum-alpha")
            >>> client.print_performance_summary()
            
            📊 Performance Summary for momentum-alpha
            ═══════════════════════════════════════════
            Submissions: 12 | Sep 2024 → Dec 2024
            
            Metric              Mean     Std    Min     Max
            ────────────────────────────────────────────────
            spearman_10d       0.124   0.052   0.021   0.248
            ndcg@40_10d        0.532   0.045   0.451   0.612
            ...
            
            Overall Percentile: 68.2% (σ=12.1%)
        """
        summary = self.performance_summary(slot=slot, show_progress=show_progress)
        
        if summary["count"] == 0:
            print(f"\n⚠️  No scored submissions found for '{self.challenge_slug}'")
            return
        
        # Header
        print(f"\n📊 Performance Summary for {self.challenge_slug}")
        if slot:
            print(f"   (Slot {slot})")
        print("═" * 50)
        
        # Date range
        dr = summary["date_range"]
        if dr:
            first = dr["first"][:7].replace("-", " ")  # "2024-09" → "2024 09"
            last = dr["last"][:7].replace("-", " ")
            print(f"Submissions: {summary['count']} | {first} → {last}")
        else:
            print(f"Submissions: {summary['count']}")
        print()
        
        # Scores table
        if summary["scores"]:
            print(f"{'Metric':<20} {'Mean':>8} {'Std':>8} {'Min':>8} {'Max':>8}")
            print("─" * 54)
            for metric, stats in summary["scores"].items():
                print(f"{metric:<20} {stats['mean']:>8.3f} {stats['std']:>8.3f} "
                      f"{stats['min']:>8.3f} {stats['max']:>8.3f}")
        
        # Total percentile highlight
        if summary["total"] and "percentile" in summary["total"]:
            p = summary["total"]["percentile"]
            print()
            print(f"📈 Overall Percentile: {p['mean']:.1%} (σ={p['std']:.1%})")

    # --- Meta-Model Download ---

    def download_meta_model(self, dest_path: str):
        """Downloads the consolidated meta-model file for this challenge.

        The meta-model is typically an aggregation (e.g., average) of all valid
        submissions for past inference periods.

        Args:
            dest_path: The local file path to save the downloaded meta-model.

        Raises:
            NotFoundError: If the challenge or its meta-model file is not found.
            CrowdCentAPIError: For issues during download or file writing.
            PermissionDenied: If the meta-model is not public and user lacks permission.
        """
        endpoint = f"/challenges/{self.challenge_slug}/meta_model/download/"
        self._download_file(endpoint, dest_path, "meta-model")
