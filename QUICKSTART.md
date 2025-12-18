# Quick Start Guide - Swimming Dashboard 🏊

## Getting Started in 3 Easy Steps

### Step 1: Install Dependencies (First Time Only)

Open PowerShell in the project folder and run:

```powershell
pip install --user -r ui/requirements.txt
```

### Step 2: Launch the Dashboard

**Option A - Double-click the batch file:**
- Double-click `START_DASHBOARD.bat` in Windows Explorer

**Option B - Run from command line:**
```powershell
python run_dashboard.py
```

**Option C - Run directly:**
```powershell
python ui/app.py
```

### Step 3: Open in Browser

Open your web browser and go to:
```
http://localhost:8050
```

## What You Can Do

### 1. Individual Performance Tab
- Select a swimmer name
- Choose an event (e.g., "200m Backstroke")
- Click "Analyze Performance"
- See their progression over time with charts and statistics

### 2. Event Distribution Tab
- Select an event to analyze
- Optionally filter by categories (age groups)
- See how times are distributed across swimmers

### 3. Cohort Comparison Tab
- Select a swimmer
- Choose an event
- Select gender (Boys/Girls)
- Compare the swimmer against others born in the same year

### 4. Data Explorer Tab
- View overall database statistics
- Browse recent results
- Check what data is available

## Troubleshooting

**Problem: "Module not found" error**
- Solution: Run `pip install --user -r ui/requirements.txt`

**Problem: "Database not found" error**
- Solution: Make sure `swim_database_2.sqlite3` exists in the project folder

**Problem: Dashboard won't start**
- Solution: Check that Python 3.8+ is installed: `python --version`

**Problem: Port 8050 already in use**
- Solution: Stop other applications using port 8050, or change the port in `ui/app.py`

## Tips

- Use the search function in dropdowns to quickly find swimmers/events
- The "Refresh Data" button reloads data from the database
- All charts are interactive - hover for details, zoom, and pan
- Charts can be downloaded as images (hover over chart for tools)

## Need Help?

Check the full documentation in `ui/README.md` for more details.

---
**Happy analyzing! 🏊‍♂️🏊‍♀️**
