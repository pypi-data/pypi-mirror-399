import os
import re
import json
from pathlib import Path

class LogAnalyzer:
    """
    LogAnalyzer class to scan logs for malicious patterns.
    """

    def __init__(self, directory, patterns_path=None):
        self.directory = directory
        self.BRUTE_FORCE_THRESHOLD = 50

        # If no custom path was given, look for `patterns.json` in the same directory as log_analyzer.py
        if patterns_path is None:
            base_dir = os.path.dirname(__file__)
            patterns_path = os.path.join(base_dir, "patterns.json")

        # Load patterns from the JSON file
        with open(patterns_path, "r") as f:
            raw_patterns = json.load(f)

        # Compile the regex patterns
        self.malicious_patterns = {
            name: re.compile(data["pattern"], re.IGNORECASE)
            for name, data in raw_patterns.items()
        }

    def scan_log_file(self, log_file):
        """
        Scan a single log file for malicious activity patterns.

        Args:
            log_file (str): Path to the log file.

        Returns:
            dict: Detected malicious activities and their counts.
        """
        detections = {pattern_name: [] for pattern_name in self.malicious_patterns}
        brute_force_count = 0

        try:
            with open(str(log_file), "r") as file:
                for line_number, line in enumerate(file, start=1):
                    for pattern_name, pattern in self.malicious_patterns.items():
                        # Handle brute force detection specifically
                        if pattern_name.lower().startswith("brute_force"):
                            if pattern.search(line):
                                brute_force_count += 1
                                detections[pattern_name].append((line_number, line.strip()))
                        else:
                            if pattern.search(line):
                                detections[pattern_name].append((line_number, line.strip()))

            # Check brute force threshold
            if brute_force_count >= self.BRUTE_FORCE_THRESHOLD:
                print(f"Brute force attack detected: {brute_force_count} failed attempts.")

        except FileNotFoundError:
            print(f"Log file not found: {log_file}")
        except Exception as e:
            print(f"An error occurred while scanning {log_file}: {e}")

        return detections

    def conduct_logs_analysis(self):
        """
        Recursively scan all .log files in the provided directory for malicious patterns.

        Returns:
            dict: A dictionary of log files and their detected patterns.
        """
        results = {}
        if not os.path.isdir(self.directory):
            return {"error": f"Invalid directory: {self.directory}"}

        log_files = list(Path(self.directory).rglob("*.log"))
        if not log_files:
            return {"info": "No .log files found in the directory."}

        for log_file in log_files:
            file_results = self.scan_log_file(str(log_file))
            results[str(log_file)] = file_results

        return results
