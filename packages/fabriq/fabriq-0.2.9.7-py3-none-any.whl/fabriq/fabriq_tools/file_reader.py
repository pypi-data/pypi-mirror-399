import os
from typing import List

class FileReader:
    """
    CodeReader reads code files from a given directory.
    It supports reading files with specific extensions and limits file size.
    """

    def __init__(self, max_file_size_kb: int = 2000):
        self.max_file_size_kb = max_file_size_kb
        self.description = """A tool to read files from a given directory path.
        Input MUST be a direct filesystem path string, not a natural language instruction."""

    def run(self, query: str = None, filters: List[str] = []):
        """
        Read code files from the specified directory path.

        Args:
            query (str, optional): The root directory path to read files from. Defaults to None.
                Example: '/home/user/project'
            filters (List[str]): List of file extensions to filter by (e.g. ['.py', '.md'])
            Only files with these extensions will be read. If empty, all file types are included.

        Returns:
            dict: A dictionary containing file paths as keys and file contents as values.
        """
        repo_data = {}
        path = query
        if path:
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for f in files:
                        ext = os.path.splitext(f)[-1]
                        if not filters or ext in filters:
                            file_path = os.path.join(root, f)
                            rel_path = os.path.relpath(file_path, path)
                            size_kb = os.path.getsize(file_path) / 1024
                            if size_kb <= self.max_file_size_kb:
                                with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
                                    repo_data[rel_path] = fp.read()
            elif os.path.isfile(path):
                ext = os.path.splitext(path)[-1]
                if not filters or ext in filters:
                    size_kb = os.path.getsize(path) / 1024
                    if size_kb <= self.max_file_size_kb:
                        with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                            repo_data[os.path.basename(path)] = fp.read()
            return repo_data
