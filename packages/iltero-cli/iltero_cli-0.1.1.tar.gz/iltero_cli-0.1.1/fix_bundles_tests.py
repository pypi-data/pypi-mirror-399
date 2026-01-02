#!/usr/bin/env python3
"""Fix bundles tests by adding get_retry_client patches."""

import re

with open('tests/unit/commands/test_bundles_fresh.py', 'r') as f:
    content = f.read()

# Fix marketplace tests - wrap api patches with get_retry_client
# Pattern: Find standalone marketplace.api_ patches and wrap them

def add_wrapper(content, api_pattern, module_name):
    """Add get_retry_client wrapper around API patches that don't have one."""
    lines = content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line starts a patch that needs wrapping
        if f'{module_name}.api_' in line and 'with patch(' in line:
            # Look back to see if there's already a get_retry_client patch
            has_wrapper = False
            for j in range(i-1, max(0, i-8), -1):
                if 'get_retry_client' in lines[j]:
                    has_wrapper = True
                    break
                if lines[j].strip().startswith('def ') or (lines[j].strip() and 'mock_response' in lines[j]):
                    break
            
            if not has_wrapper:
                # Get indentation
                indent = len(line) - len(line.lstrip())
                base = ' ' * indent
                
                # Insert wrapper before this line
                result.append(f'{base}with patch(')
                result.append(f'{base}    "iltero.commands.bundles.{module_name}.get_retry_client"')
                result.append(f'{base}) as mock_get_client:')
                result.append(f'{base}    mock_client, _ = setup_mock_client(mock_get_client)')
                result.append(f'{base}    mock_client.handle_response.return_value = mock_response.parsed')
                
                # Add original line with extra indent
                result.append(' ' * 4 + line)
                i += 1
                
                # Add rest of the test body with extra indent
                while i < len(lines):
                    next_line = lines[i]
                    # Stop at next function or blank line followed by def
                    if next_line.strip().startswith('def '):
                        break
                    if not next_line.strip() and i + 1 < len(lines) and lines[i+1].strip().startswith('def '):
                        result.append(next_line)
                        i += 1
                        break
                    # Add extra indentation to non-empty lines within the test
                    if next_line.strip():
                        result.append(' ' * 4 + next_line)
                    else:
                        result.append(next_line)
                    i += 1
                continue
        
        result.append(line)
        i += 1
    
    return '\n'.join(result)

# Apply fixes
content = add_wrapper(content, 'api_', 'marketplace')

with open('tests/unit/commands/test_bundles_fresh.py', 'w') as f:
    f.write(content)

print("Done!")
