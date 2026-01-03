"""
Spider Dataset Setup Script

Downloads and prepares the Spider dataset for evaluation.
Spider is a large-scale cross-domain text-to-SQL benchmark with 200+ databases.

Official Spider dataset: https://yale-lily.github.io/spider
"""

import os
import json
import zipfile
import urllib.request
import shutil
from pathlib import Path

# Spider dataset URLs
# The main dataset is hosted on Google Drive and requires manual download
# We'll use a direct link that works better for automated downloads
SPIDER_DATASET_URL = "https://drive.usercontent.google.com/download?id=1TqleXec_OykOYFREKKtschzY29dUcVAQ&export=download&confirm=t"

def download_spider_dataset(target_dir="spider_data"):
    """
    Download and extract the Spider dataset.

    Args:
        target_dir: Directory to store the Spider dataset

    Returns:
        Path to the extracted dataset
    """
    print("="*80)
    print("SPIDER DATASET SETUP")
    print("="*80)

    target_path = Path(target_dir)

    # Check if already downloaded
    if target_path.exists() and (target_path / "dev.json").exists():
        print(f"\n✓ Spider dataset already exists at: {target_path}")
        return target_path

    # Create target directory
    target_path.mkdir(parents=True, exist_ok=True)

    print(f"\n1. Downloading Spider dataset...")
    print("   Note: The Spider dataset is ~200MB and hosted on Google Drive")
    print("   If automatic download fails, please manually download from:")
    print("   https://drive.google.com/uc?export=download&id=1TqleXec_OykOYFREKKtschzY29dUcVAQ")

    try:
        zip_path = target_path / "spider.zip"

        print(f"   Downloading to: {zip_path}")
        print("   This may take several minutes (200MB)...")

        # Download with progress
        def download_with_progress(url, filepath):
            try:
                # Add headers to avoid Google Drive warnings
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })

                with urllib.request.urlopen(req) as response:
                    total_size = int(response.headers.get('content-length', 0))
                    block_size = 1024 * 1024  # 1MB chunks
                    downloaded = 0

                    with open(filepath, 'wb') as f:
                        while True:
                            buffer = response.read(block_size)
                            if not buffer:
                                break

                            downloaded += len(buffer)
                            f.write(buffer)

                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                mb_downloaded = downloaded / (1024 * 1024)
                                mb_total = total_size / (1024 * 1024)
                                print(f"\r   Progress: {percent:.1f}% ({mb_downloaded:.1f}MB/{mb_total:.1f}MB)", end='')
                            else:
                                mb_downloaded = downloaded / (1024 * 1024)
                                print(f"\r   Downloaded: {mb_downloaded:.1f}MB", end='')

                    print()  # New line after progress
                    return True
            except Exception as e:
                print(f"\n   ✗ Download failed: {e}")
                return False

        # Try direct download
        success = download_with_progress(SPIDER_DATASET_URL, zip_path)

        if not success:
            print("\n   ❌ Automatic download failed!")
            print("\n   Please download manually:")
            print("   1. Visit: https://drive.google.com/uc?export=download&id=1TqleXec_OykOYFREKKtschzY29dUcVAQ")
            print("   2. Download the spider.zip file")
            print("   3. Place it in: {}".format(target_path / "spider.zip"))
            print("   4. Run this script again")
            return None

        print("\n2. Extracting dataset...")
        print("   This may take a few minutes...")

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # List all files to find the spider directory
                all_files = zip_ref.namelist()

                # Spider dataset usually has a root directory
                # Find common prefix
                if all_files:
                    first_file = all_files[0]
                    if '/' in first_file:
                        root_dir = first_file.split('/')[0]
                        print(f"   Found root directory: {root_dir}")

                        # Extract all files
                        zip_ref.extractall(target_path)

                        # Move contents from root directory to target_path
                        extracted_root = target_path / root_dir
                        if extracted_root.exists() and extracted_root.is_dir():
                            for item in extracted_root.iterdir():
                                dest = target_path / item.name
                                if dest.exists():
                                    if dest.is_dir():
                                        shutil.rmtree(dest)
                                    else:
                                        dest.unlink()
                                shutil.move(str(item), str(target_path))
                            extracted_root.rmdir()
                    else:
                        # No root directory, extract directly
                        zip_ref.extractall(target_path)

        except Exception as e:
            print(f"\n   ✗ Extraction failed: {e}")
            print("   The zip file may be corrupted. Please delete it and try again.")
            return None

        # Clean up zip file
        if zip_path.exists():
            zip_path.unlink()

        print("   ✓ Dataset extracted successfully")

    except Exception as e:
        print(f"\n   ✗ Error during download/extraction: {e}")
        print("\n   Please download manually:")
        print("   1. Go to: https://github.com/taoyds/spider")
        print("   2. Download and extract to: {}".format(target_path))
        return None

    return target_path


def verify_spider_structure(spider_dir):
    """
    Verify that the Spider dataset has the expected structure.

    Args:
        spider_dir: Path to Spider dataset directory

    Returns:
        True if structure is valid, False otherwise
    """
    print("\n3. Verifying dataset structure...")

    required_files = ["dev.json", "tables.json"]
    required_dirs = ["database"]

    spider_path = Path(spider_dir)

    # Check for required files
    for file in required_files:
        file_path = spider_path / file
        if not file_path.exists():
            print(f"   ✗ Missing required file: {file}")
            return False
        print(f"   ✓ Found: {file}")

    # Check for database directory
    database_dir = spider_path / "database"
    if not database_dir.exists():
        print(f"   ✗ Missing database directory")
        return False

    # Count databases
    db_dirs = [d for d in database_dir.iterdir() if d.is_dir()]
    print(f"   ✓ Found {len(db_dirs)} databases")

    # Load and verify dev.json
    try:
        with open(spider_path / "dev.json", 'r') as f:
            dev_data = json.load(f)
        print(f"   ✓ Dev set has {len(dev_data)} examples")
    except Exception as e:
        print(f"   ✗ Error loading dev.json: {e}")
        return False

    # Load and verify tables.json
    try:
        with open(spider_path / "tables.json", 'r') as f:
            tables_data = json.load(f)
        print(f"   ✓ Tables metadata has {len(tables_data)} database schemas")
    except Exception as e:
        print(f"   ✗ Error loading tables.json: {e}")
        return False

    return True


def get_spider_statistics(spider_dir):
    """
    Print statistics about the Spider dataset.

    Args:
        spider_dir: Path to Spider dataset directory
    """
    print("\n4. Spider Dataset Statistics...")

    spider_path = Path(spider_dir)

    # Load dev data
    with open(spider_path / "dev.json", 'r') as f:
        dev_data = json.load(f)

    # Get unique databases
    databases = set(example['db_id'] for example in dev_data)

    # Difficulty distribution
    difficulties = {}
    for example in dev_data:
        diff = example.get('difficulty', 'unknown')
        difficulties[diff] = difficulties.get(diff, 0) + 1

    print(f"\n   📊 Dev Set Statistics:")
    print(f"      • Total examples: {len(dev_data)}")
    print(f"      • Unique databases: {len(databases)}")
    print(f"      • Difficulty distribution:")
    for diff, count in sorted(difficulties.items()):
        print(f"         - {diff}: {count} ({count/len(dev_data)*100:.1f}%)")

    # Sample databases
    print(f"\n   📁 Sample databases:")
    sample_dbs = sorted(databases)[:10]
    for db in sample_dbs:
        print(f"      • {db}")
    if len(databases) > 10:
        print(f"      ... and {len(databases) - 10} more")


def main():
    """Main setup function."""
    # Download and extract
    spider_dir = download_spider_dataset()

    if spider_dir is None:
        print("\n✗ Setup failed - manual download required")
        return False

    # Verify structure
    if not verify_spider_structure(spider_dir):
        print("\n✗ Dataset structure verification failed")
        return False

    # Show statistics
    get_spider_statistics(spider_dir)

    # Success message
    print("\n" + "="*80)
    print("✓ SPIDER DATASET SETUP COMPLETE!")
    print("="*80)
    print(f"\nDataset location: {Path(spider_dir).absolute()}")
    print("\nNext steps:")
    print("  1. Run the Spider benchmark:")
    print("     python test_spider_benchmark.py")
    print("\n  2. Or run with custom options:")
    print("     python test_spider_benchmark.py --limit 10 --model llama-3.3-70b-versatile")

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
