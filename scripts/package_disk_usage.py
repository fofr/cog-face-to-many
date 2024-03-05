import subprocess
import os
import shutil
from sys import executable

# Command: python -m site --user-site
site_packages = '/root/.pyenv/versions/3.10.6/lib/python3.10/site-packages'

# Command: python -m pip list
installed_packages = subprocess.run([executable, "-m", "pip", "list"], capture_output=True, text=True).stdout

# Process the output to extract package names
packages = [line.split()[0] for line in installed_packages.split('\n')[2:] if line]

# Get the size of each package directory in the site-packages
package_sizes = []
for package in packages:
    package_path = os.path.join(site_packages, package)
    # Check if the package directory exists (this might not always be accurate)
    if os.path.exists(package_path):
        # Calculate the directory size using shutil instead of subprocess
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(package_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        size = f"{total_size / 1024**2:.2f}MB"
        package_sizes.append((package, size))
    else:
        # Package might not be in the expected format or location
        package_sizes.append((package, "N/A"))

# Sort packages by size (ignoring those we couldn't get the size for)
package_sizes.sort(key=lambda x: float(x[1].rstrip('MB')) if x[1] != "N/A" else float('-inf'), reverse=True)

# Print the sizes
for package, size in package_sizes:
    print(f"{package}: {size}")
