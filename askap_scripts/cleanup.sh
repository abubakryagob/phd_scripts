#!/bin/bash

# This script removes unnecessary files from the variability analysis scripts
# CAUTION: Only run this after you've successfully completed the analysis

echo "This script will remove the following redundant files:"
echo "- simple_analyze.py (debug script)"
echo "- run_variability_analysis.sh (superseded by run_with_venv.sh)"
echo "- run_variability.sh (early version of execution script)"
echo ""
echo "CAUTION: This action cannot be undone."
read -p "Do you want to proceed? (y/n): " confirm

if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
  echo "Removing redundant files..."
  
  # Remove simple_analyze.py if it exists
  if [ -f "simple_analyze.py" ]; then
    rm simple_analyze.py
    echo "- Removed simple_analyze.py"
  fi
  
  # Remove run_variability_analysis.sh if it exists
  if [ -f "run_variability_analysis.sh" ]; then
    rm run_variability_analysis.sh
    echo "- Removed run_variability_analysis.sh"
  fi
  
  # Remove run_variability.sh if it exists
  if [ -f "run_variability.sh" ]; then
    rm run_variability.sh
    echo "- Removed run_variability.sh"
  fi
  
  echo "Cleanup completed."
else
  echo "Cleanup cancelled."
fi
