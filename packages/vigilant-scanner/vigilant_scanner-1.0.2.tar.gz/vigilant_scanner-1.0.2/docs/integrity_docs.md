## 📋 Files Integrity Monitoring

### CLI Commands

1. **Initialize the Database**
   Create a snapshot of the current directory state and store metadata in the database:
   ```bash
   vgls init <directory>
   ```

2. **Scan and Compare**
   Scan the directory and compare results with the last snapshot:
   ```bash
   vgls scan <directory>
   ```

3. **Update the Database**
   Update the database with the current state of the directory:
   ```bash
   vgls update <directory>
   ```


---

## ⚙️ How It Works

```bash
# Initialize the database with the current state of a directory
vgls init /var/www

# Perform a scan to detect changes
vgls scan /var/www

# Update the database after legitimate changes are made (deploy was conducted etc.)
vgls update /var/www
```

1. **Initialization (`init`)**
   - Scans a directory and stores metadata (file path, hash, size, permissions, etc.) in a SQLite database.

2. **Scanning and Comparison (`scan`)**
   - Scans the directory again and compares the current state with the stored metadata.
   - Outputs new, modified, and deleted files.

3. **Updating the Database (`update`)**
   - Updates the database to reflect the latest directory state.
   - Inserts new files, updates modified files, and removes deleted files.


---