import sys
import os

# Set working directory to android/ folder
android_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(android_dir)

# Add parent root directory to sys.path for shared imports
sys.path.insert(0, os.path.dirname(android_dir))

from app import ArrowEscapeApp

if __name__ == '__main__':
    ArrowEscapeApp().run()
