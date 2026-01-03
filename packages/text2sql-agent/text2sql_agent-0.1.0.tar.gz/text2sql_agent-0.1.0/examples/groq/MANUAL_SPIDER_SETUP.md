# Manual Spider Dataset Setup

If the automatic download in `setup_spider.py` doesn't work due to Google Drive restrictions, follow these manual steps:

## Option 1: Direct Download from Google Drive

1. **Download the dataset:**
   - Visit: https://drive.google.com/uc?export=download&id=1TqleXec_OykOYFREKKtschzY29dUcVAQ
   - Or visit: https://yale-lily.github.io/spider and click the download link
   - Save the file as `spider.zip` (~200MB)

2. **Place the file:**
   ```bash
   # Navigate to the groq examples directory
   cd examples/groq

   # Create spider_data directory if it doesn't exist
   mkdir -p spider_data

   # Move your downloaded spider.zip file here
   mv ~/Downloads/spider.zip spider_data/
   ```

3. **Extract the dataset:**
   ```bash
   cd spider_data
   unzip spider.zip

   # The extraction should create these directories/files:
   # - dev.json
   # - train.json (optional)
   # - tables.json
   # - database/ (directory with 200+ database folders)
   ```

4. **If the files are in a subdirectory, move them up:**
   ```bash
   # Check if files are in a subdirectory
   ls -la

   # If you see a directory like "spider/" or "spider-master/", move contents:
   mv spider/* .
   # or
   mv spider-master/* .

   # Then remove the empty directory
   rmdir spider
   # or
   rmdir spider-master
   ```

5. **Verify the structure:**
   ```bash
   # You should see:
   ls -la
   # - dev.json
   # - tables.json
   # - database/

   # Check database count
   ls database/ | wc -l
   # Should show ~200+ directories
   ```

6. **Test the setup:**
   ```bash
   cd ..  # Back to examples/groq
   python test_spider_benchmark.py --limit 1
   ```

## Option 2: Using wget (Linux/Mac)

```bash
cd examples/groq
mkdir -p spider_data
cd spider_data

# Download using wget
wget --no-check-certificate \
  'https://drive.usercontent.google.com/download?id=1TqleXec_OykOYFREKKtschzY29dUcVAQ&export=download&confirm=t' \
  -O spider.zip

# Extract
unzip spider.zip

# Move files if needed (see Option 1, step 4)
```

## Option 3: Using curl (Mac)

```bash
cd examples/groq
mkdir -p spider_data
cd spider_data

# Download using curl
curl -L \
  'https://drive.usercontent.google.com/download?id=1TqleXec_OykOYFREKKtschzY29dUcVAQ&export=download&confirm=t' \
  -o spider.zip

# Extract
unzip spider.zip

# Move files if needed (see Option 1, step 4)
```

## Option 4: Clone from Official Repository

The official Spider GitHub repo contains instructions for downloading the dataset:

```bash
cd examples/groq
git clone https://github.com/taoyds/spider.git temp_spider
cd temp_spider

# Follow the instructions in their README to download the dataset
# Then move the dataset files:
mv spider_data ../spider_data
cd ..
rm -rf temp_spider
```

## Expected Directory Structure

After setup, your `spider_data/` directory should look like this:

```
spider_data/
├── dev.json              # Development set (1,034 examples)
├── train.json            # Training set (optional, 8,659 examples)
├── tables.json           # Database schema metadata
├── database/             # SQLite database files
│   ├── academic/
│   │   └── academic.sqlite
│   ├── activity_1/
│   │   └── activity_1.sqlite
│   ├── aircraft/
│   │   └── aircraft.sqlite
│   ├── allergy_1/
│   │   └── allergy_1.sqlite
│   ├── apartment_rentals/
│   │   └── apartment_rentals.sqlite
│   ├── architecture/
│   │   └── architecture.sqlite
│   ├── battle_death/
│   │   └── battle_death.sqlite
│   ├── behavior_monitoring/
│   │   └── behavior_monitoring.sqlite
│   ├── bike_1/
│   │   └── bike_1.sqlite
│   ├── book_2/
│   │   └── book_2.sqlite
│   ├── ... (~200 more databases)
```

## Verification

To verify your setup is correct:

1. **Check required files exist:**
   ```bash
   cd examples/groq/spider_data

   # Should all exist
   ls -l dev.json
   ls -l tables.json
   ls -ld database/
   ```

2. **Verify database count:**
   ```bash
   ls database/ | wc -l
   # Should show between 140-200
   ```

3. **Check dev.json structure:**
   ```bash
   head -20 dev.json
   # Should show JSON with questions and SQL
   ```

4. **Run verification script:**
   ```bash
   cd examples/groq
   python3 -c "
   import json
   from pathlib import Path

   spider_dir = Path('spider_data')

   # Check files
   assert (spider_dir / 'dev.json').exists(), 'dev.json not found'
   assert (spider_dir / 'tables.json').exists(), 'tables.json not found'
   assert (spider_dir / 'database').exists(), 'database/ not found'

   # Load and check dev.json
   with open(spider_dir / 'dev.json') as f:
       dev_data = json.load(f)
   print(f'✓ Found {len(dev_data)} examples in dev.json')

   # Load and check tables.json
   with open(spider_dir / 'tables.json') as f:
       tables_data = json.load(f)
   print(f'✓ Found {len(tables_data)} database schemas in tables.json')

   # Count databases
   db_dirs = [d for d in (spider_dir / 'database').iterdir() if d.is_dir()]
   print(f'✓ Found {len(db_dirs)} databases')

   print('\n✓ Spider dataset setup verified successfully!')
   "
   ```

## Troubleshooting

### "dev.json not found"
- Make sure you extracted the zip file
- Check if files are in a subdirectory and need to be moved up
- Verify the download completed successfully (spider.zip should be ~200MB)

### "No such file: database/*/db_name.sqlite"
- The database directory should contain subdirectories for each database
- Each subdirectory should have a .sqlite file with the same name
- Example: `database/concert_singer/concert_singer.sqlite`

### "Corrupted zip file"
- Delete spider.zip and download again
- Try a different download method (wget, curl, browser)
- Check that the downloaded file is actually ~200MB

### "Permission denied"
- Make sure you have write permissions in the examples/groq directory
- Try running with appropriate permissions

## Getting Help

If you continue to have issues:

1. Check the official Spider website: https://yale-lily.github.io/spider
2. Visit the GitHub repository: https://github.com/taoyds/spider
3. Check for updated download links in the official documentation

## Once Setup is Complete

After successfully setting up the dataset:

```bash
cd examples/groq

# Quick test with 1 example
python test_spider_benchmark.py --limit 1

# Standard test with 10 examples
python test_spider_benchmark.py --limit 10

# Full evaluation
python test_spider_benchmark.py --limit 50
```

Enjoy benchmarking! 🚀
