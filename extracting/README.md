# Extracting Module

This module is responsible for collecting and processing Chrome Web Store extension data.

## Steps to Use

1. **Configuration**
   - Check `config.py` for configuration settings

2. **Data Collection**
   - Use `collecting.py` to collect extension details from Web Store
   - Use `download.py` to download extension packages
   - Use `filtering.py` to filter collected extensions with potential API network requests

3. **Output**
   - Collected data is saved in JSON format

## Notes
- The collector respects rate limits and includes error handling
- Progress is saved in a checkpoint file for resuming interrupted collections
- Only extensions with user count above the minimum threshold are saved
