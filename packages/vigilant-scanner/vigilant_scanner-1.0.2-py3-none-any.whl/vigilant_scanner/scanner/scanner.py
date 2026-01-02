from pathlib import Path
import os
import hashlib
from .metadata_collector import FileMetadata
from .db_manager import DatabaseManager


class Scanner:
    def __init__(self, directory):
        self.directory = directory
        self.db_manager = DatabaseManager(directory)

    def _compute_hash(self, file_path):
        """Compute the SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _collect_metadata(self, file_path):
        """Collect metadata for a single file."""
        stats = file_path.stat()
        hash_value = self._compute_hash(file_path)
        return FileMetadata(
            path=str(file_path),
            generated_hash=hash_value,
            size=stats.st_size,
            permissions=oct(stats.st_mode),
            owner=stats.st_uid,
            modified_time=stats.st_mtime,
        )

    def scan_directory(self):
        """
        Scan the directory and return metadata for all files (excluding .log files), plus any errors encountered.
        """
        metadata_list = []
        errors = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith(".log"):
                    continue  # Skip .log files
                full_path = Path(root) / file
                try:
                    metadata = self._collect_metadata(full_path)
                    metadata_list.append(metadata)
                except (OSError, PermissionError) as exc:
                    errors.append(f"{full_path}: {exc}")
                    continue
        return metadata_list, errors

    def compare_with_database(self):
        """Compare the current scan results with the database and return changes plus scan errors."""

        current_metadata_list, errors = self.scan_directory()
        current_files = {metadata.path: metadata for metadata in current_metadata_list}

        stored_metadata = self.db_manager.get_all_metadata()

        results = []

        # Check for modifications and new files
        for file_path, current_metadata in current_files.items():
            stored_entry = stored_metadata.get(file_path)
            if stored_entry:
                if (
                    stored_entry[1] != current_metadata.generated_hash or
                    stored_entry[2] != current_metadata.size or
                    stored_entry[3] != current_metadata.permissions or
                    stored_entry[4] != current_metadata.owner or
                    stored_entry[5] != current_metadata.modified_time
                ):
                    results.append(("Modified", file_path))
            else:
                results.append(("New", file_path))

        # Check for deleted files
        for stored_file in stored_metadata.keys():
            if stored_file not in current_files:
                results.append(("Deleted", stored_file))

        return results, errors
