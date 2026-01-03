from pathlib import Path
import os
from decoder import __version__

def main():
    home = Path.home()
    decoder_home = home / ".decoder"
    cache_file = decoder_home / "update_cache.json"

    print(f"Path.home(): {home}")
    print(f"DECODER_HOME (computed): {decoder_home}")
    print(f"decoder.__version__: {__version__}")

    if cache_file.exists():
        print(f"Cache file found at: {cache_file}")
        print(f"Content: {cache_file.read_text()}")
        try:
            cache_file.unlink()
            print("Cache file DELETED successfully.")
        except Exception as e:
            print(f"Failed to delete cache file: {e}")
    else:
        print("Cache file NOT found at expected location.")
        # Try searching in other likely places if needed, but for now just report.
        if (home / ".config/decoder/update_cache.json").exists():
             print(f"Found in .config: {home / '.config' / 'decoder' / 'update_cache.json'}")

if __name__ == "__main__":
    main()
