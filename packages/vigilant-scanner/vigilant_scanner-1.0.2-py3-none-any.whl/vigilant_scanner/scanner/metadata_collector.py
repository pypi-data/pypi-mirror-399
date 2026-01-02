class FileMetadata:
    """
    A data container for storing metadata of a file.

    Attributes:
        path (str): The full path to the file.
        generated_hash (str): The computed hash of the file's contents.
        size (int): The size of the file in bytes.
        permissions (str): The file's permissions in octal format (e.g., "0o644").
        owner (int): The user ID of the file's owner.
        modified_time (float): The last modification time of the file as a Unix timestamp.

    Methods:
        to_dict(): Convert the file metadata to a dictionary representation.
        __str__(): Provide a human-readable string representation of the metadata.
    """
    def __init__(self, path, generated_hash, size, permissions, owner, modified_time):
        self.path = path
        self.generated_hash = generated_hash
        self.size = size
        self.permissions = permissions
        self.owner = owner
        self.modified_time = modified_time

    def to_dict(self):
        """Convert the file metadata to a dictionary representation."""
        return {
            "path": self.path,
            "generated_hash": self.generated_hash,
            "size": self.size,
            "permissions": self.permissions,
            "owner": self.owner,
            "modified_time": self.modified_time,
        }

    def __str__(self):
        """Provide a human-readable string representation of the metadata."""
        return (
            f"FileMetadata(path={self.path}, hash={self.generated_hash}, size={self.size}, "
            f"permissions={self.permissions}, owner={self.owner}, modified_time={self.modified_time})"
        )
