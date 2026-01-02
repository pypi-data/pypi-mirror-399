from setuptools import setup, find_packages

# Find all packages, but rename root to 'payme'
packages = find_packages(exclude=["tests*", "*.tests*", "dist*", "build*", "*.egg-info"])

setup(
    packages=packages,
    package_dir={'': '.'},  # Root directory is the package
)
