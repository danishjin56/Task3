#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e

# --- CONFIGURE THIS SECTION ---
# Replace this with your command to run all tests
run_all_tests() {
  echo "Running all tests..."
  
  local out_file="test_stdout.log"
  local err_file="test_stderr.log"
  
  # Ensure Python path maps to the injected codebase /app location 
  export PYTHONPATH="/app:${PYTHONPATH:-}"
  
  # Allow tests to fail without crashing the script immediately
  set +e
  pytest -v > "$out_file" 2> "$err_file"
  local test_status=$?
  set -e
  
  # Reflect results to standard output/error so the environment sees them
  cat "$out_file"
  cat "$err_file" >&2
  
  # Call parsing.py to build results.json
  if [ -f "$(dirname "$0")/parsing.py" ]; then
      python3 "$(dirname "$0")/parsing.py" "$out_file" "$err_file" results.json || true
  elif [ -f "parsing.py" ]; then
      python3 parsing.py "$out_file" "$err_file" results.json || true
  elif command -v parse_results >/dev/null 2>&1; then
      parse_results "$out_file" "$err_file" results.json || true
  fi
  
  return $test_status
}
# --- END CONFIGURATION SECTION ---

### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests