"""
Spider Dataset Setup for Ollama

This script helps set up the Spider dataset for use with Ollama.
Since the dataset is the same regardless of LLM provider, we share
the dataset with the Groq examples to save disk space.

The Spider dataset will be downloaded to ../groq/spider_data/
and used by both Groq and Ollama examples.
"""

import os
import sys
from pathlib import Path

def setup_spider_for_ollama():
    """Set up Spider dataset for Ollama examples."""
    print("="*80)
    print("SPIDER DATASET SETUP FOR OLLAMA")
    print("="*80)

    # Paths
    current_dir = Path(__file__).parent
    groq_dir = current_dir.parent / "groq"
    groq_spider_dir = groq_dir / "spider_data"
    groq_setup_script = groq_dir / "setup_spider.py"

    print("\nThe Spider dataset is shared between Groq and Ollama examples.")
    print(f"Dataset location: {groq_spider_dir}")

    # Check if dataset already exists
    if groq_spider_dir.exists() and (groq_spider_dir / "dev.json").exists():
        print("\n✓ Spider dataset already exists!")
        print(f"   Location: {groq_spider_dir}")

        # Show statistics
        import json
        try:
            with open(groq_spider_dir / "dev.json") as f:
                dev_data = json.load(f)
            print(f"   Examples: {len(dev_data)}")

            with open(groq_spider_dir / "tables.json") as f:
                tables_data = json.load(f)
            print(f"   Databases: {len(tables_data)}")

            print("\n✓ You're ready to run the Ollama Spider benchmark!")
            print("\nNext steps:")
            print("  1. Make sure Ollama is running:")
            print("     ollama serve")
            print("\n  2. Pull a model if needed:")
            print("     ollama pull llama3.1")
            print("\n  3. Run the benchmark:")
            print("     python test_spider_benchmark.py --limit 10")

            return True

        except Exception as e:
            print(f"\n⚠ Warning: Could not read dataset files: {e}")

    # Dataset doesn't exist - need to download
    print("\n❌ Spider dataset not found.")
    print("\nTo set up the dataset, run the setup script from the Groq directory:")
    print(f"\n  cd {groq_dir}")
    print("  python setup_spider.py")
    print("\nThis will download the dataset (~200MB) which will be shared")
    print("between Groq and Ollama examples.")

    # Ask if user wants to run it now
    response = input("\nRun the setup now? (y/n): ")

    if response.lower() == 'y':
        print("\nRunning Spider dataset setup...")
        print("="*80 + "\n")

        # Change to groq directory and run setup
        original_dir = os.getcwd()
        try:
            os.chdir(groq_dir)
            # Run the setup script
            import subprocess
            result = subprocess.run([sys.executable, "setup_spider.py"], check=True)

            os.chdir(original_dir)

            if result.returncode == 0:
                print("\n" + "="*80)
                print("✓ SPIDER DATASET SETUP COMPLETE!")
                print("="*80)
                print("\nYou can now run the Ollama Spider benchmark:")
                print("  python test_spider_benchmark.py --limit 10")
                return True
            else:
                print("\n✗ Setup failed. Please run manually:")
                print(f"  cd {groq_dir}")
                print("  python setup_spider.py")
                return False

        except Exception as e:
            os.chdir(original_dir)
            print(f"\n✗ Error running setup: {e}")
            print("\nPlease run manually:")
            print(f"  cd {groq_dir}")
            print("  python setup_spider.py")
            return False
    else:
        print("\nSetup cancelled. Run this command when ready:")
        print(f"  cd {groq_dir}")
        print("  python setup_spider.py")
        return False


def main():
    """Main function."""
    success = setup_spider_for_ollama()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
