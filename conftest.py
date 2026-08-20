import sys
import os

# Add backend and ml directories to python path for pytest execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "ml")))
