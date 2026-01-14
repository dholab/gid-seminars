# GID Seminars - LabKey WebDAV Uploader
"""Upload generated files to LabKey server via WebDAV."""

import os
import time
from pathlib import Path
from typing import Any

import requests
import toml
from requests.auth import HTTPBasicAuth

from src.core.exceptions import DeploymentError
from src.core.utils import DEFAULT_MAX_RETRIES, DEFAULT_RETRY_DELAY, console

# Load environment variables
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


class LabKeyWebDAVUploader:
    """Handles file uploads to LabKey via WebDAV."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.server_url = config["labkey"]["server_url"]
        self.project = config["labkey"]["project"]
        files_folder = config["webdav"].get("files_folder", "@files")

        # Build WebDAV URL path
        # Format: https://server/_webdav/{project}/@files/{filename}
        self.webdav_base_url = (
            f"https://{self.server_url}/_webdav/{self.project}/{files_folder}"
        )

        # Get API key
        api_key_env = config.get("deployment", {}).get("api_key_env", "LABKEY_API")
        self.api_key = os.environ.get(api_key_env)
        if not self.api_key:
            raise DeploymentError(f"{api_key_env} environment variable not set")

        # CSRF token will be fetched when needed
        self.csrf_token: str | None = None

        # Use a session to maintain cookies between requests
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth("apikey", self.api_key)

        # Retry settings
        self.max_retries = config.get("deployment", {}).get("max_retries", DEFAULT_MAX_RETRIES)
        self.retry_delay = config.get("deployment", {}).get("retry_delay", DEFAULT_RETRY_DELAY)

    def get_csrf_token(self, url: str) -> str | None:
        """Get CSRF token from LabKey server via OPTIONS request."""
        try:
            response = self.session.options(url, timeout=10)

            # Extract CSRF token from Set-Cookie header
            for cookie in response.headers.get("Set-Cookie", "").split(","):
                if "X-LABKEY-CSRF" in cookie:
                    csrf_token = cookie.split("=")[1].split(";")[0]
                    return csrf_token

            return None

        except Exception as e:
            console.print(f"    [yellow]Warning: Could not get CSRF token: {e}[/yellow]")
            return None

    def upload_file(
        self, local_file: Path, remote_filename: str | None = None
    ) -> bool:
        """
        Upload a single file to LabKey WebDAV with retry logic.

        Args:
            local_file: Path to local file
            remote_filename: Filename to use on server (defaults to local filename)

        Returns:
            True if successful, False otherwise
        """
        if remote_filename is None:
            remote_filename = local_file.name

        # Build full WebDAV URL for this file
        webdav_url = f"{self.webdav_base_url}/{remote_filename}"

        console.print(f"    Uploading {local_file.name}...")

        for attempt in range(self.max_retries):
            try:
                with open(local_file, "rb") as f:
                    file_content = f.read()

                # Get CSRF token if we don't have one yet
                if not self.csrf_token:
                    self.csrf_token = self.get_csrf_token(webdav_url)

                # Determine content type based on file extension
                content_type = self._get_content_type(local_file)

                # Upload via PUT request
                headers = {"Content-Type": content_type}
                if self.csrf_token:
                    headers["X-LABKEY-CSRF"] = self.csrf_token

                response = self.session.put(
                    webdav_url,
                    data=file_content,
                    headers=headers,
                    timeout=30,
                )

                if response.status_code in [200, 201, 204]:
                    console.print(f"      [green]Uploaded successfully[/green]")
                    return True
                else:
                    console.print(
                        f"      [red]Upload failed: {response.status_code} {response.reason}[/red]"
                    )
                    if attempt < self.max_retries - 1:
                        console.print(
                            f"      Retrying ({attempt + 2}/{self.max_retries})..."
                        )
                        time.sleep(self.retry_delay * (2**attempt))
                        continue
                    else:
                        return False

            except Exception as e:
                console.print(f"      [red]Upload error: {e}[/red]")
                if attempt < self.max_retries - 1:
                    console.print(f"      Retrying ({attempt + 2}/{self.max_retries})...")
                    time.sleep(self.retry_delay * (2**attempt))
                else:
                    return False

        return False

    def upload_all_files(self, output_dir: Path) -> dict[str, bool]:
        """
        Upload all generated files from directory.

        Args:
            output_dir: Directory containing files to upload

        Returns:
            Dictionary mapping filename to upload success status
        """
        webdav_files = self.config.get("webdav", {}).get("files", {})

        # Determine which files to upload
        files_to_upload = []
        if webdav_files.get("upload_html", True):
            files_to_upload.extend(output_dir.glob("*.html"))
        if webdav_files.get("upload_ics", True):
            files_to_upload.extend(output_dir.glob("*.ics"))
        if webdav_files.get("upload_json", True):
            files_to_upload.extend(output_dir.glob("*.json"))

        if not files_to_upload:
            console.print("  [yellow]No files found to upload[/yellow]")
            return {}

        console.print(f"\n[bold]Uploading {len(files_to_upload)} file(s) to LabKey...[/bold]")

        results = {}
        for file_path in sorted(files_to_upload):
            success = self.upload_file(file_path)
            results[file_path.name] = success

        return results

    def get_dashboard_url(self) -> str:
        """Get public URL to view the files."""
        return f"https://{self.server_url}/project/{self.project}/begin.view"

    def _get_content_type(self, file_path: Path) -> str:
        """Determine content type based on file extension."""
        extension_map = {
            ".html": "text/html; charset=utf-8",
            ".ics": "text/calendar; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".css": "text/css",
            ".js": "application/javascript",
        }
        return extension_map.get(file_path.suffix.lower(), "application/octet-stream")


def upload_to_labkey(base_dir: Path | None = None) -> dict[str, bool]:
    """
    Main entry point for uploading to LabKey.

    Args:
        base_dir: Base directory for config files (defaults to cwd)

    Returns:
        Upload results by filename
    """
    base_dir = base_dir or Path.cwd()
    config_dir = base_dir / "config"

    # Load configurations
    labkey_config = toml.load(config_dir / "labkey.toml")
    settings_config = toml.load(config_dir / "settings.toml")

    # Get output directory
    output_dir = base_dir / settings_config.get("output", {}).get(
        "output_dir", "local-outputs"
    )

    if not output_dir.exists():
        console.print("[red]No output directory found. Run generators first.[/red]")
        return {}

    # Initialize uploader
    uploader = LabKeyWebDAVUploader(labkey_config)

    # Upload files
    results = uploader.upload_all_files(output_dir)

    # Report results
    if results:
        successful = sum(1 for v in results.values() if v)
        failed = sum(1 for v in results.values() if not v)

        console.print(f"\n[bold]Upload Summary:[/bold]")
        console.print(f"  Successful: {successful}")
        if failed > 0:
            console.print(f"  Failed: {failed}", style="red")

        if successful > 0:
            dashboard_url = uploader.get_dashboard_url()
            console.print(f"\n  Dashboard URL: {dashboard_url}")

    return results


if __name__ == "__main__":
    upload_to_labkey()
