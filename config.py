import os

# Build the path to the dataset
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "wikipedia.json")

# Optional: safety check so missing dataset is obvious
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(
        f"❌ wikipedia.json not found at: {DATA_PATH}\n"
        f"Make sure 'data/wikipedia.json' exists in the project folder."
    )
