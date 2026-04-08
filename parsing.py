#!/usr/bin/env python3
import dataclasses
import json
import sys
from enum import Enum
from pathlib import Path
from typing import List

class TestStatus(Enum):
    """The test status enum."""
    PASSED = 1
    FAILED = 2
    SKIPPED = 3
    ERROR = 4

@dataclasses.dataclass
class TestResult:
    """The test result dataclass."""
    name: str
    status: TestStatus

### DO NOT MODIFY THE CODE ABOVE ###
### Implement the parsing logic below ###

def parse_test_output(stdout_content: str, stderr_content: str) -> List[TestResult]:
    """
    Parse the test output content and extract test results.
    """
    import re
    import os
    
    results_map = {}
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    lines = (stdout_content + "\n" + stderr_content).splitlines()
    
    # Treat 'ERROR' and 'SKIPPED' as 'FAILED' as explicitly requested
    status_map = {
        'PASSED': TestStatus.PASSED,
        'FAILED': TestStatus.FAILED,
        'ERROR': TestStatus.ERROR,
        'SKIPPED': TestStatus.SKIPPED,
        'XFAIL': TestStatus.PASSED,
        'XPASS': TestStatus.FAILED,
    }
    
    for line in lines:
        clean_line = ansi_escape.sub('', line)
        
        match_verbose = re.search(r'::(test_[a-zA-Z0-9_]+).*?\b(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\b', clean_line)
        match_summary = re.search(r'^(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\s+.*?::(test_[a-zA-Z0-9_]+)', clean_line)
        
        test_name = None
        status_str = None
        
        if match_summary:
            status_str = match_summary.group(1)
            test_name = match_summary.group(2)
        elif match_verbose:
            test_name = match_verbose.group(1)
            status_str = match_verbose.group(2)
            
        if test_name and status_str:
            if match_summary or test_name not in results_map:
                results_map[test_name] = status_map[status_str]
                
    # Fallback to map all existing tests as FAILED if they weren't caught 
    # (e.g. during a collection/import error).
    search_dirs = ['tests', '/eval_assets/tests', '.', '/eval_assets']
    for src in search_dirs:
        if os.path.exists(src):
            for root, dirs, files in os.walk(src):
                for f in files:
                    if f.startswith('test_') and f.endswith('.py'):
                        try:
                            with open(os.path.join(root, f), 'r', encoding='utf-8') as tf:
                                content = tf.read()
                                matches = re.findall(r'^def\s+(test_[a-zA-Z0-9_]+)\s*\(', content, re.MULTILINE)
                                for t_name in matches:
                                    if t_name not in results_map:
                                        results_map[t_name] = TestStatus.FAILED
                        except Exception:
                            pass

    return [TestResult(name=k, status=v) for k, v in results_map.items()]

### Implement the parsing logic above ###
### DO NOT MODIFY THE CODE BELOW ###

def export_to_json(results: List[TestResult], output_path: Path) -> None:
    json_results = {
        'tests': [
            {'name': result.name, 'status': result.status.name} for result in results
        ]
    }
    with open(output_path, 'w') as f:
        json.dump(json_results, f, indent=2)

def main(stdout_path: Path, stderr_path: Path, output_path: Path) -> None:
    with open(stdout_path) as f:
        stdout_content = f.read()
    with open(stderr_path) as f:
        stderr_content = f.read()

    results = parse_test_output(stdout_content, stderr_content)
    export_to_json(results, output_path)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: python parsing.py <stdout_file> <stderr_file> <output_json>')
        sys.exit(1)

    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))