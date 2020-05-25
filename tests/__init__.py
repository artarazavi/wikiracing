import sys

# Add python package paths for testing in docker.
sys.path.extend(["/src/app", "/src/app/api", "/src/app/common", "/src/app/find"])
