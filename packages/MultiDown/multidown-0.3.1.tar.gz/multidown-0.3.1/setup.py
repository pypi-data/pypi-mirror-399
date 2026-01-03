from setuptools import setup, find_packages

import platform
import sys
from setuptools import setup, find_packages

def check_arch():
    machine = platform.machine().lower()

    # Linux / Android ARM64
    if machine in ("aarch64", "arm64"):
        return

    print("\n❌ This package supports ONLY ARM64 (aarch64) systems.")
    print(f"❌ Detected architecture: {machine}")
    print("❌ Installation aborted.\n")
    sys.exit(1)

check_arch()

setup(
    name='MultiDown',
    version='0.3.1',
    description='A stylish cross-platform video downloader with web UI',
    author='Bismoy Ghosh',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'yt-dlp',
        'rich',
        'colorama',
        'ffmpeg-python'
    ],
    entry_points={
        'console_scripts': [
            'MultiDown = MultiDown.__main__:main',
        ],
    },
)
