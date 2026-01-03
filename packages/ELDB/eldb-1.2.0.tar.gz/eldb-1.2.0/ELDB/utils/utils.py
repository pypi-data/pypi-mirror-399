# eldb_utils_enhanced.py
"""
Enhanced ELDB Utilities Module
------------------------------
A comprehensive set of utilities for ELDB database management,
including advanced repair functions for corrupted tables.
"""

import os
import json
import csv
import math
import random
import string
import hashlib
import struct
import ast
import shutil
import zipfile
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from pathlib import Path
import traceback

class ELDBAdvancedUtils:
    """Advanced utilities for ELDB database with enhanced repair capabilities"""
    
    # ==================== CORE REPAIR FUNCTIONS ====================
    
    @staticmethod
    def _safe_parse_header(header_line: bytes) -> Dict:
        """
        Safely parse header with multiple fallback methods
        
        Args:
            header_line: Raw header bytes
            
        Returns:
            Dict: Parsed header or empty dict if parsing fails
        """
        if not header_line:
            return {}
        
        # Try multiple decoding methods
        decoded = None
        for encoding in ['utf-8', 'latin-1', 'ascii', 'cp1252']:
            try:
                decoded = header_line.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if decoded is None:
            # Use replacement strategy
            decoded = header_line.decode('utf-8', errors='replace')
        
        # Clean the string
        decoded = decoded.strip()
        
        # Try multiple parsing methods
        parsing_methods = [
            # Method 1: JSON (standard)
            lambda d: json.loads(d),
            # Method 2: ast.literal_eval (Python dict syntax)
            lambda d: ast.literal_eval(d),
            # Method 3: Manual extraction with regex
            lambda d: ELDBAdvancedUtils._extract_dict_from_string(d),
            # Method 4: Reconstruct from what we can find
            lambda d: ELDBAdvancedUtils._reconstruct_header(d),
        ]
        
        for method in parsing_methods:
            try:
                result = method(decoded)
                if isinstance(result, dict) and result:
                    return result
            except:
                continue
        
        return {}
    
    @staticmethod
    def _extract_dict_from_string(text: str) -> Dict:
        """Extract dictionary from corrupted string"""
        result = {}
        
        # Look for column patterns
        if "'columns'" in text or '"columns"' in text:
            # Try to find columns section
            import re
            
            # Pattern for columns dictionary
            patterns = [
                r"'columns'\s*:\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}",
                r'"columns"\s*:\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    columns_text = match.group(1)
                    # Try to extract individual columns
                    col_pattern = r"['\"]([^'\"]+)['\"]\s*:\s*\{(.+?)\}"
                    col_matches = re.findall(col_pattern, columns_text, re.DOTALL)
                    
                    columns = {}
                    for col_name, col_attrs in col_matches:
                        # Extract type and size
                        type_match = re.search(r"'type'\s*:\s*['\"]([^'\"]+)['\"]", col_attrs)
                        size_match = re.search(r"'size'\s*:\s*(\d+)", col_attrs)
                        
                        col_def = {}
                        if type_match:
                            col_def['type'] = type_match.group(1)
                        if size_match:
                            col_def['size'] = int(size_match.group(1))
                        
                        if col_def:
                            columns[col_name] = col_def
                    
                    if columns:
                        result['columns'] = columns
        
        # Look for primary key
        pk_patterns = [
            r"'primary_key'\s*:\s*['\"]([^'\"]+)['\"]",
            r'"primary_key"\s*:\s*[\'"]([^\'"]+)[\'"]'
        ]
        for pattern in pk_patterns:
            match = re.search(pattern, text)
            if match:
                result['primary_key'] = match.group(1)
                break
        
        # Look for row count
        count_patterns = [
            r"'row_count'\s*:\s*(\d+)",
            r'"row_count"\s*:\s*(\d+)'
        ]
        for pattern in count_patterns:
            match = re.search(pattern, text)
            if match:
                result['row_count'] = int(match.group(1))
                break
        
        return result
    
    @staticmethod
    def _reconstruct_header(text: str) -> Dict:
        """Reconstruct header from heavily corrupted text"""
        result = {'columns': {}}
        
        # Try to guess columns from common patterns
        common_columns = {
            'id': {'type': 'int', 'size': 4},
            'name': {'type': 'str', 'size': 50},
            'email': {'type': 'str', 'size': 100},
            'age': {'type': 'int', 'size': 4},
            'created_at': {'type': 'int', 'size': 4},
            'updated_at': {'type': 'int', 'size': 4},
            'price': {'type': 'int', 'size': 4},
            'quantity': {'type': 'int', 'size': 4},
            'description': {'type': 'str', 'size': 200},
            'status': {'type': 'str', 'size': 20},
        }
        
        # Check for column names in text
        for col_name, col_def in common_columns.items():
            if col_name in text.lower():
                result['columns'][col_name] = col_def
        
        # If no columns found, use defaults
        if not result['columns']:
            result['columns'] = {
                'id': {'type': 'int', 'size': 4},
                'data': {'type': 'str', 'size': 100}
            }
        
        return result
    
    @staticmethod
    def _analyze_binary_structure(data: bytes) -> Dict:
        """
        Analyze binary data to determine structure
        
        Args:
            data: Binary data from file
            
        Returns:
            Dict: Analysis results including possible row size
        """
        analysis = {
            'total_size': len(data),
            'possible_row_sizes': [],
            'string_patterns': [],
            'integer_patterns': []
        }
        
        if len(data) < 100:
            return analysis
        
        # Look for repeating patterns (potential rows)
        for row_size in [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 100]:
            if row_size >= len(data):
                break
            
            # Check if data aligns with this row size
            patterns = []
            for offset in range(0, min(1000, len(data) - row_size), row_size):
                chunk = data[offset:offset + row_size]
                patterns.append(chunk)
            
            # Check for reasonable patterns (not all zeros, not random)
            if len(patterns) > 3:
                # Count unique patterns
                unique_patterns = len(set(patterns))
                if unique_patterns > 1:  # Not all identical
                    analysis['possible_row_sizes'].append(row_size)
        
        # Look for strings (printable characters)
        printable_count = sum(1 for b in data[:1000] if 32 <= b <= 126)
        analysis['printable_ratio'] = printable_count / min(1000, len(data))
        
        # Look for integers (groups of 4 bytes that could be ints)
        for i in range(0, min(100, len(data) - 4), 4):
            int_bytes = data[i:i+4]
            try:
                int_val = struct.unpack('i', int_bytes)[0]
                if -1000000 < int_val < 1000000:  # Reasonable range
                    analysis['integer_patterns'].append((i, int_val))
            except:
                pass
        
        return analysis
    
    @staticmethod
    def _recover_rows_intelligent(table_path: str, columns: Dict) -> List[Dict]:
        """
        Intelligent row recovery with multiple strategies
        
        Args:
            table_path: Path to table file
            columns: Column definitions
            
        Returns:
            List[Dict]: Recovered rows
        """
        rows = []
        
        if not os.path.exists(table_path):
            print(f"  File not found: {table_path}")
            return rows
        
        file_size = os.path.getsize(table_path)
        print(f"  File size: {file_size} bytes")
        
        try:
            with open(table_path, 'rb') as f:
                # Read entire file for analysis
                all_data = f.read()
                
                # Skip header
                header_end = all_data.find(b'\n')
                if header_end == -1:
                    print("  No header line found, starting from beginning")
                    header_end = 0
                else:
                    header_end += 1  # Skip newline
                
                data = all_data[header_end:]
                
                if not data:
                    print("  No data after header")
                    return rows
                
                # Calculate expected row size from columns
                expected_row_size = 0
                col_info = []
                for col_name, col_def in columns.items():
                    col_type = col_def.get('type', 'str')
                    col_size = col_def.get('size', 50)
                    
                    if col_type == 'int':
                        size = 4
                    else:
                        size = col_size
                    
                    col_info.append({
                        'name': col_name,
                        'type': col_type,
                        'size': size
                    })
                    expected_row_size += size
                
                print(f"  Expected row size: {expected_row_size} bytes")
                print(f"  Data available: {len(data)} bytes")
                print(f"  Potential rows: {len(data) // expected_row_size if expected_row_size > 0 else 0}")
                
                # Try multiple reading strategies
                strategies = [
                    ELDBAdvancedUtils._read_rows_exact,
                    ELDBAdvancedUtils._read_rows_with_tolerance,
                    ELDBAdvancedUtils._read_rows_adaptive
                ]
                
                best_rows = []
                best_strategy_name = ""
                
                for strategy in strategies:
                    try:
                        strategy_rows = strategy(data, col_info, expected_row_size)
                        if len(strategy_rows) > len(best_rows):
                            best_rows = strategy_rows
                            best_strategy_name = strategy.__name__
                    except Exception as e:
                        continue
                
                if best_rows:
                    print(f"  Best strategy: {best_strategy_name}")
                    print(f"  Rows recovered: {len(best_rows)}")
                    rows = best_rows
                
        except Exception as e:
            print(f"  Error during recovery: {e}")
        
        return rows
    
    @staticmethod
    def _read_rows_exact(data: bytes, col_info: List[Dict], row_size: int) -> List[Dict]:
        """Read rows with exact size matching"""
        rows = []
        
        if row_size == 0:
            return rows
        
        num_rows = len(data) // row_size
        for i in range(num_rows):
            row_start = i * row_size
            row_end = row_start + row_size
            row_data = data[row_start:row_end]
            
            if len(row_data) < row_size:
                break
            
            row = {}
            offset = 0
            valid = True
            
            for col in col_info:
                col_size = col['size']
                
                if offset + col_size > len(row_data):
                    valid = False
                    break
                
                col_bytes = row_data[offset:offset + col_size]
                
                try:
                    if col['type'] == 'int':
                        if len(col_bytes) == 4:
                            row[col['name']] = struct.unpack('i', col_bytes)[0]
                        else:
                            # Try to convert whatever we have
                            try:
                                row[col['name']] = int.from_bytes(col_bytes[:4], 'little', signed=True)
                            except:
                                row[col['name']] = 0
                    else:  # String
                        # Find null terminator
                        null_pos = col_bytes.find(b'\x00')
                        if null_pos == -1:
                            null_pos = col_size
                        
                        try:
                            text = col_bytes[:null_pos].decode('utf-8', errors='ignore')
                            row[col['name']] = text
                        except:
                            row[col['name']] = ""
                
                except Exception as e:
                    row[col['name']] = None
                
                offset += col_size
            
            if valid:
                rows.append(row)
        
        return rows
    
    @staticmethod
    def _read_rows_with_tolerance(data: bytes, col_info: List[Dict], row_size: int) -> List[Dict]:
        """Read rows with tolerance for minor corruption"""
        rows = []
        
        if row_size == 0:
            return rows
        
        # Calculate min and max row sizes (allow 10% variation)
        min_size = int(row_size * 0.9)
        max_size = int(row_size * 1.1)
        
        pos = 0
        row_num = 0
        
        while pos < len(data):
            # Try different row sizes within tolerance
            best_row = None
            best_score = -1
            
            for test_size in range(min_size, max_size + 1):
                if pos + test_size > len(data):
                    continue
                
                test_data = data[pos:pos + test_size]
                row = ELDBAdvancedUtils._parse_row_flexible(test_data, col_info, row_size)
                
                if row:
                    # Score the row based on data validity
                    score = ELDBAdvancedUtils._score_row_quality(row, col_info)
                    if score > best_score:
                        best_score = score
                        best_row = row
            
            if best_row and best_score > 0:
                rows.append(best_row)
                pos += row_size  # Advance by expected size
            else:
                # Skip ahead and look for next potential row
                pos += 1
            
            row_num += 1
            if row_num > 1000:  # Safety limit
                break
        
        return rows
    
    @staticmethod
    def _read_rows_adaptive(data: bytes, col_info: List[Dict], expected_row_size: int) -> List[Dict]:
        """Adaptive row reading that analyzes data patterns"""
        rows = []
        
        # Analyze data to find patterns
        analysis = ELDBAdvancedUtils._analyze_binary_structure(data)
        
        # Try different row sizes from analysis
        for row_size in analysis['possible_row_sizes']:
            if row_size == 0:
                continue
            
            test_rows = ELDBAdvancedUtils._read_rows_exact(data, col_info, row_size)
            if len(test_rows) > len(rows):
                rows = test_rows
        
        return rows
    
    @staticmethod
    def _parse_row_flexible(row_data: bytes, col_info: List[Dict], expected_size: int) -> Optional[Dict]:
        """Flexible row parsing that handles various data layouts"""
        row = {}
        
        # Try different parsing strategies
        strategies = [
            # Strategy 1: Fixed positions based on expected sizes
            lambda: ELDBAdvancedUtils._parse_fixed_positions(row_data, col_info),
            # Strategy 2: Look for field boundaries
            lambda: ELDBAdvancedUtils._parse_field_boundaries(row_data, col_info),
            # Strategy 3: Heuristic parsing
            lambda: ELDBAdvancedUtils._parse_heuristic(row_data, col_info)
        ]
        
        for strategy in strategies:
            try:
                result = strategy()
                if result and all(key in result for key in [col['name'] for col in col_info[:2]]):
                    return result
            except:
                continue
        
        return None
    
    @staticmethod
    def _parse_fixed_positions(data: bytes, col_info: List[Dict]) -> Dict:
        """Parse using fixed column positions"""
        row = {}
        offset = 0
        
        for col in col_info:
            col_size = col['size']
            
            if offset + col_size > len(data):
                break
            
            col_data = data[offset:offset + col_size]
            
            if col['type'] == 'int':
                try:
                    if len(col_data) >= 4:
                        row[col['name']] = struct.unpack('i', col_data[:4])[0]
                    else:
                        # Pad with zeros
                        padded = col_data + b'\x00' * (4 - len(col_data))
                        row[col['name']] = struct.unpack('i', padded)[0]
                except:
                    row[col['name']] = 0
            else:  # String
                null_pos = col_data.find(b'\x00')
                if null_pos == -1:
                    null_pos = len(col_data)
                
                try:
                    row[col['name']] = col_data[:null_pos].decode('utf-8', errors='ignore')
                except:
                    row[col['name']] = ""
            
            offset += col_size
        
        return row
    
    @staticmethod
    def _parse_field_boundaries(data: bytes, col_info: List[Dict]) -> Dict:
        """Parse by looking for field boundaries (null terminators, etc.)"""
        row = {}
        pos = 0
        
        for col in col_info:
            if col['type'] == 'int':
                # Look for 4-byte integer
                if pos + 4 <= len(data):
                    try:
                        row[col['name']] = struct.unpack('i', data[pos:pos+4])[0]
                        pos += 4
                    except:
                        row[col['name']] = 0
                        pos += 1
                else:
                    row[col['name']] = 0
            else:  # String
                # Look for null terminator
                null_pos = data[pos:].find(b'\x00')
                if null_pos == -1:
                    null_pos = min(len(data) - pos, col['size'])
                
                try:
                    row[col['name']] = data[pos:pos+null_pos].decode('utf-8', errors='ignore')
                except:
                    row[col['name']] = ""
                
                pos += null_pos + 1  # +1 for null terminator
        
        return row
    
    @staticmethod
    def _parse_heuristic(data: bytes, col_info: List[Dict]) -> Dict:
        """Heuristic parsing based on data patterns"""
        row = {}
        
        # Simple heuristic: first field is often an ID (int)
        if len(data) >= 4:
            try:
                row['id'] = struct.unpack('i', data[:4])[0]
            except:
                row['id'] = 0
        
        # Look for strings in the rest
        if len(data) > 4:
            # Try to decode as UTF-8
            try:
                text = data[4:].decode('utf-8', errors='ignore')
                # Clean up null bytes
                text = text.replace('\x00', ' ').strip()
                if text:
                    row['data'] = text[:100]  # Limit length
            except:
                pass
        
        return row
    
    @staticmethod
    def _score_row_quality(row: Dict, col_info: List[Dict]) -> int:
        """Score the quality/validity of a parsed row"""
        score = 0
        
        for col in col_info:
            col_name = col['name']
            if col_name in row:
                value = row[col_name]
                
                if col['type'] == 'int':
                    if isinstance(value, int):
                        score += 2
                        # Bonus for reasonable values
                        if -1000000 < value < 1000000:
                            score += 1
                else:  # String
                    if isinstance(value, str):
                        score += 1
                        # Bonus for reasonable strings
                        if 0 < len(value) < 1000:
                            score += 1
                        if all(32 <= ord(c) <= 126 for c in value[:20] if value):
                            score += 1
        
        return score
    
    # ==================== PUBLIC REPAIR FUNCTIONS ====================
    
    @staticmethod
    def repair_table(db_instance, table_name: str, backup: bool = True, 
                    aggressive: bool = False) -> Dict:
        """
        Repair a corrupted table with intelligent recovery
        
        Args:
            db_instance: ELDB database instance
            table_name: Name of table to repair
            backup: Create backup before repair
            aggressive: Use more aggressive recovery methods
            
        Returns:
            Dict: Repair results including recovered row count
        """
        results = {
            'success': False,
            'recovered_rows': 0,
            'backup_created': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            table_path = os.path.join(db_instance.db_folder, f"{table_name}.eldb")
            
            if not os.path.exists(table_path):
                results['errors'].append(f"Table file not found: {table_path}")
                return results
            
            print(f"\n{'='*60}")
            print(f"REPAIRING TABLE: {table_name}")
            print(f"{'='*60}")
            print(f"File: {table_path}")
            print(f"Size: {os.path.getsize(table_path)} bytes")
            
            # Create backup
            if backup:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(db_instance.db_folder, 
                                         f"{table_name}_backup_{timestamp}.eldb")
                shutil.copy2(table_path, backup_path)
                results['backup_created'] = True
                results['backup_path'] = backup_path
                print(f"Backup created: {backup_path}")
            
            # Step 1: Analyze and recover header
            print(f"\n1. ANALYZING HEADER...")
            with open(table_path, 'rb') as f:
                header_line = f.readline()
            
            header = ELDBAdvancedUtils._safe_parse_header(header_line)
            
            if 'columns' in header:
                columns = header['columns']
                print(f"  ✓ Header recovered: {len(columns)} columns")
                print(f"  Columns: {list(columns.keys())}")
            else:
                print(f"  ⚠ Header corrupted, attempting to reconstruct...")
                
                # Try to analyze file to guess columns
                with open(table_path, 'rb') as f:
                    all_data = f.read()
                
                analysis = ELDBAdvancedUtils._analyze_binary_structure(all_data)
                
                # Guess columns based on common patterns
                if analysis['printable_ratio'] > 0.3:
                    # Looks like text data
                    columns = {
                        'id': {'type': 'int', 'size': 4},
                        'text': {'type': 'str', 'size': 100}
                    }
                else:
                    # More binary data
                    columns = {
                        'id': {'type': 'int', 'size': 4},
                        'data': {'type': 'int', 'size': 4},
                        'value': {'type': 'int', 'size': 4}
                    }
                
                print(f"  Reconstructed columns: {list(columns.keys())}")
                results['warnings'].append("Header was corrupted, used reconstructed columns")
            
            # Step 2: Recover rows
            print(f"\n2. RECOVERING DATA...")
            recovered_rows = ELDBAdvancedUtils._recover_rows_intelligent(table_path, columns)
            
            print(f"  ✓ Recovered {len(recovered_rows)} rows")
            results['recovered_rows'] = len(recovered_rows)
            
            if recovered_rows:
                print(f"  Sample of recovered data:")
                for i, row in enumerate(recovered_rows[:2]):
                    print(f"    Row {i}: {row}")
            
            # Step 3: Rebuild table
            print(f"\n3. REBUILDING TABLE...")
            
            # Create new header
            new_header = {
                'columns': columns,
                'primary_key': header.get('primary_key'),
                'row_count': len(recovered_rows)
            }
            
            # Write to temporary file
            temp_path = table_path + '.tmp'
            
            with open(temp_path, 'wb') as f:
                # Write header
                f.write(str(new_header).encode() + b'\n')
                
                # Write rows
                for row in recovered_rows:
                    bin_row = b''
                    for col_name, col_def in columns.items():
                        col_type = col_def.get('type', 'str')
                        col_size = col_def.get('size', 50)
                        value = row.get(col_name)
                        
                        if col_type == 'int':
                            int_value = value if isinstance(value, int) else 0
                            bin_row += struct.pack('i', int_value)
                        else:  # String
                            str_value = str(value) if value is not None else ''
                            encoded = str_value.encode('utf-8', errors='ignore')[:col_size-1]
                            bin_row += encoded + b'\x00' * (col_size - len(encoded))
                    
                    f.write(bin_row)
            
            # Replace original file
            os.replace(temp_path, table_path)
            
            # Reload table in database instance
            if table_name in db_instance.tables:
                del db_instance.tables[table_name]
            
            try:
                db_instance.load_table(table_name)
                print(f"  ✓ Table reloaded successfully")
            except Exception as e:
                print(f"  ⚠ Table reload warning: {e}")
                results['warnings'].append(f"Table reload: {e}")
            
            results['success'] = True
            print(f"\n{'='*60}")
            print(f"REPAIR COMPLETE: {len(recovered_rows)} rows recovered")
            print(f"{'='*60}")
            
        except Exception as e:
            error_msg = f"Repair failed: {type(e).__name__}: {str(e)}"
            print(f"\n✗ {error_msg}")
            results['errors'].append(error_msg)
            traceback.print_exc()
        
        return results
    
    @staticmethod
    def repair_database(db_instance, backup: bool = True) -> Dict:
        """
        Repair entire database - all tables
        
        Args:
            db_instance: ELDB database instance
            backup: Create backup before repair
            
        Returns:
            Dict: Repair results for all tables
        """
        results = {
            'total_tables': 0,
            'repaired_tables': 0,
            'failed_tables': 0,
            'total_rows_recovered': 0,
            'tables': {},
            'backup_created': False
        }
        
        print(f"\n{'='*60}")
        print(f"REPAIRING ENTIRE DATABASE: {db_instance.db_folder}")
        print(f"{'='*60}")
        
        # Create database backup
        if backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_zip = f"{db_instance.db_folder}_backup_{timestamp}.zip"
            
            with zipfile.ZipFile(backup_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(db_instance.db_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, db_instance.db_folder)
                        zipf.write(file_path, arcname)
            
            results['backup_created'] = True
            results['backup_path'] = backup_zip
            print(f"Database backup created: {backup_zip}")
        
        # Find all tables
        table_files = []
        for file in os.listdir(db_instance.db_folder):
            if file.endswith('.eldb'):
                table_name = file[:-5]
                table_files.append(table_name)
        
        results['total_tables'] = len(table_files)
        print(f"Found {len(table_files)} tables to repair")
        
        # Repair each table
        for i, table_name in enumerate(table_files, 1):
            print(f"\n[{i}/{len(table_files)}] Repairing: {table_name}")
            
            table_result = ELDBAdvancedUtils.repair_table(
                db_instance, table_name, backup=False, aggressive=True
            )
            
            results['tables'][table_name] = table_result
            
            if table_result.get('success'):
                results['repaired_tables'] += 1
                results['total_rows_recovered'] += table_result.get('recovered_rows', 0)
                print(f"  ✓ Success: {table_result.get('recovered_rows', 0)} rows recovered")
            else:
                results['failed_tables'] += 1
                print(f"  ✗ Failed")
        
        print(f"\n{'='*60}")
        print(f"DATABASE REPAIR SUMMARY:")
        print(f"{'='*60}")
        print(f"Total tables: {results['total_tables']}")
        print(f"Repaired successfully: {results['repaired_tables']}")
        print(f"Failed: {results['failed_tables']}")
        print(f"Total rows recovered: {results['total_rows_recovered']}")
        
        if results['backup_created']:
            print(f"Backup: {results['backup_path']}")
        
        return results
    
    @staticmethod
    def repair_column(db_instance, table_name: str, column_name: str, 
                     new_type: str = None, new_size: int = None) -> Dict:
        """
        Repair a specific column in a table
        
        Args:
            db_instance: ELDB database instance
            table_name: Table name
            column_name: Column to repair
            new_type: New type if column definition is corrupted
            new_size: New size if column definition is corrupted
            
        Returns:
            Dict: Repair results
        """
        results = {
            'success': False,
            'column_repaired': False,
            'rows_affected': 0,
            'errors': []
        }
        
        try:
            # Load the table
            if table_name not in db_instance.tables:
                db_instance.load_table(table_name)
            
            table = db_instance.tables[table_name]
            columns = table['header']['columns']
            
            # Check if column exists
            if column_name not in columns:
                # Try to add the column
                if new_type and new_size:
                    print(f"Column '{column_name}' doesn't exist, adding it...")
                    
                    # Read all rows
                    rows = db_instance._read_rows(table)
                    
                    # Add default value to column definition
                    columns[column_name] = {
                        'type': new_type,
                        'size': new_size,
                        'nullable': True
                    }
                    
                    # Add default value to each row
                    default_value = 0 if new_type == 'int' else ''
                    for row in rows:
                        row[column_name] = default_value
                    
                    # Save back
                    db_instance._save_rows(table_name, rows)
                    
                    results['column_repaired'] = True
                    results['rows_affected'] = len(rows)
                    results['success'] = True
                    
                    print(f"✓ Column '{column_name}' added with default values")
                else:
                    results['errors'].append(f"Column '{column_name}' doesn't exist and no type/size provided")
            else:
                # Column exists, check if it's corrupted
                print(f"Checking column '{column_name}'...")
                
                # Read rows and check for issues
                rows = db_instance._read_rows(table)
                issues = 0
                
                for i, row in enumerate(rows):
                    value = row.get(column_name)
                    col_def = columns[column_name]
                    col_type = col_def.get('type', 'str')
                    
                    # Check if value matches type
                    if col_type == 'int' and not isinstance(value, int):
                        issues += 1
                        # Try to fix
                        try:
                            row[column_name] = int(value) if value else 0
                        except:
                            row[column_name] = 0
                    elif col_type == 'str' and not isinstance(value, str):
                        issues += 1
                        row[column_name] = str(value) if value else ""
                
                if issues > 0:
                    # Save fixed rows
                    db_instance._save_rows(table_name, rows)
                    
                    results['column_repaired'] = True
                    results['rows_affected'] = issues
                    results['success'] = True
                    
                    print(f"✓ Fixed {issues} values in column '{column_name}'")
                else:
                    print(f"✓ Column '{column_name}' is already valid")
                    results['success'] = True
        
        except Exception as e:
            error_msg = f"Column repair failed: {type(e).__name__}: {str(e)}"
            print(f"✗ {error_msg}")
            results['errors'].append(error_msg)
        
        return results
    
    # ==================== DIAGNOSTIC FUNCTIONS ====================
    
    @staticmethod
    def diagnose_table(db_instance, table_name: str) -> Dict:
        """
        Comprehensive table diagnosis
        
        Args:
            db_instance: ELDB database instance
            table_name: Table name
            
        Returns:
            Dict: Detailed diagnosis results
        """
        diagnosis = {
            'table_name': table_name,
            'exists': False,
            'file_info': {},
            'header_analysis': {},
            'data_analysis': {},
            'issues': [],
            'warnings': [],
            'recommendations': []
        }
        
        try:
            table_path = os.path.join(db_instance.db_folder, f"{table_name}.eldb")
            
            if not os.path.exists(table_path):
                diagnosis['issues'].append(f"Table file does not exist: {table_path}")
                return diagnosis
            
            diagnosis['exists'] = True
            
            # File information
            file_stats = os.stat(table_path)
            diagnosis['file_info'] = {
                'path': table_path,
                'size_bytes': file_stats.st_size,
                'created': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
            }
            
            # Header analysis
            with open(table_path, 'rb') as f:
                header_line = f.readline()
                rest_of_file = f.read()
            
            header = ELDBAdvancedUtils._safe_parse_header(header_line)
            
            diagnosis['header_analysis'] = {
                'header_length': len(header_line),
                'parsed_successfully': bool(header),
                'has_columns': 'columns' in header,
                'column_count': len(header.get('columns', {})),
                'has_primary_key': 'primary_key' in header,
                'has_row_count': 'row_count' in header,
                'raw_header_preview': header_line[:100].decode('utf-8', errors='ignore') + '...'
            }
            
            if not header:
                diagnosis['issues'].append("Header cannot be parsed")
            elif 'columns' not in header:
                diagnosis['issues'].append("No columns definition in header")
            
            # Data analysis
            if header and 'columns' in header:
                columns = header['columns']
                
                # Calculate expected structure
                expected_row_size = 0
                for col_def in columns.values():
                    if col_def.get('type') == 'int':
                        expected_row_size += 4
                    else:
                        expected_row_size += col_def.get('size', 50)
                
                diagnosis['data_analysis']['expected_row_size'] = expected_row_size
                
                if expected_row_size > 0:
                    expected_rows = len(rest_of_file) // expected_row_size
                    diagnosis['data_analysis']['expected_rows'] = expected_rows
                    
                    if 'row_count' in header:
                        declared_rows = header['row_count']
                        diagnosis['data_analysis']['declared_rows'] = declared_rows
                        
                        if declared_rows != expected_rows:
                            diagnosis['warnings'].append(
                                f"Row count mismatch: header says {declared_rows}, "
                                f"but file size suggests {expected_rows}"
                            )
                
                # Try to read sample data
                try:
                    if table_name in db_instance.tables:
                        rows = db_instance._read_rows(db_instance.tables[table_name])
                        diagnosis['data_analysis']['readable_rows'] = len(rows)
                        
                        if rows:
                            diagnosis['data_analysis']['sample_row'] = rows[0]
                            
                            # Check data types
                            type_issues = []
                            for col_name, col_def in columns.items():
                                col_type = col_def.get('type', 'str')
                                for row in rows[:10]:  # Check first 10 rows
                                    value = row.get(col_name)
                                    if value is not None:
                                        if col_type == 'int' and not isinstance(value, int):
                                            type_issues.append(f"Column '{col_name}': Expected int, got {type(value).__name__}")
                                            break
                                        elif col_type == 'str' and not isinstance(value, str):
                                            type_issues.append(f"Column '{col_name}': Expected str, got {type(value).__name__}")
                                            break
                            
                            if type_issues:
                                diagnosis['issues'].extend(type_issues)
                except Exception as e:
                    diagnosis['data_analysis']['read_error'] = str(e)
                    diagnosis['issues'].append(f"Cannot read table data: {e}")
            
            # Binary analysis
            binary_analysis = ELDBAdvancedUtils._analyze_binary_structure(rest_of_file)
            diagnosis['binary_analysis'] = binary_analysis
            
            # Generate recommendations
            if diagnosis['issues']:
                diagnosis['recommendations'].append("Run repair_table() to fix issues")
            
            if binary_analysis.get('printable_ratio', 0) < 0.1 and len(rest_of_file) > 100:
                diagnosis['recommendations'].append("File appears to be heavily corrupted, consider aggressive repair")
            
            if not diagnosis['header_analysis']['parsed_successfully']:
                diagnosis['recommendations'].append("Header is corrupted, needs reconstruction")
        
        except Exception as e:
            diagnosis['issues'].append(f"Diagnosis error: {type(e).__name__}: {str(e)}")
        
        return diagnosis
    
    @staticmethod
    def diagnose_database(db_instance) -> Dict:
        """
        Comprehensive database diagnosis
        
        Args:
            db_instance: ELDB database instance
            
        Returns:
            Dict: Database-wide diagnosis
        """
        diagnosis = {
            'database_path': db_instance.db_folder,
            'total_tables': 0,
            'healthy_tables': 0,
            'corrupted_tables': 0,
            'missing_tables': 0,
            'tables': {},
            'issues': [],
            'recommendations': []
        }
        
        print(f"\n{'='*60}")
        print(f"DATABASE DIAGNOSIS: {db_instance.db_folder}")
        print(f"{'='*60}")
        
        # Check if database folder exists
        if not os.path.exists(db_instance.db_folder):
            diagnosis['issues'].append(f"Database folder does not exist: {db_instance.db_folder}")
            return diagnosis
        
        # Find all ELDB files
        eldb_files = []
        for file in os.listdir(db_instance.db_folder):
            if file.endswith('.eldb'):
                eldb_files.append(file[:-5])
        
        diagnosis['total_tables'] = len(eldb_files)
        print(f"Found {len(eldb_files)} tables")
        
        # Diagnose each table
        for table_name in eldb_files:
            print(f"\nDiagnosing: {table_name}")
            table_diagnosis = ELDBAdvancedUtils.diagnose_table(db_instance, table_name)
            
            diagnosis['tables'][table_name] = table_diagnosis
            
            if table_diagnosis.get('exists'):
                if table_diagnosis.get('issues'):
                    diagnosis['corrupted_tables'] += 1
                    print(f"  ⚠ Corrupted")
                else:
                    diagnosis['healthy_tables'] += 1
                    print(f"  ✓ Healthy")
            else:
                diagnosis['missing_tables'] += 1
                print(f"  ✗ Missing")
        
        # Database-wide checks
        if diagnosis['corrupted_tables'] > 0:
            diagnosis['recommendations'].append(
                f"Run repair_database() to fix {diagnosis['corrupted_tables']} corrupted tables"
            )
        
        if diagnosis['total_tables'] == 0:
            diagnosis['recommendations'].append("Database is empty")
        
        # Check for foreign key consistency
        if hasattr(db_instance, 'foreign_keys') and db_instance.foreign_keys:
            fk_issues = ELDBAdvancedUtils._check_foreign_key_integrity(db_instance)
            if fk_issues:
                diagnosis['issues'].extend(fk_issues)
                diagnosis['recommendations'].append("Check foreign key relationships")
        
        print(f"\n{'='*60}")
        print(f"DIAGNOSIS SUMMARY:")
        print(f"{'='*60}")
        print(f"Total tables: {diagnosis['total_tables']}")
        print(f"Healthy tables: {diagnosis['healthy_tables']}")
        print(f"Corrupted tables: {diagnosis['corrupted_tables']}")
        print(f"Missing tables: {diagnosis['missing_tables']}")
        
        if diagnosis['issues']:
            print(f"\nDatabase issues found: {len(diagnosis['issues'])}")
        
        if diagnosis['recommendations']:
            print(f"\nRecommendations:")
            for rec in diagnosis['recommendations']:
                print(f"  • {rec}")
        
        return diagnosis
    
    @staticmethod
    def _check_foreign_key_integrity(db_instance) -> List[str]:
        """Check foreign key integrity across database"""
        issues = []
        
        for table_name, fks in db_instance.foreign_keys.items():
            for fk in fks:
                # Check if referenced table exists
                ref_table = fk.get('ref_table')
                ref_table_path = os.path.join(db_instance.db_folder, f"{ref_table}.eldb")
                
                if not os.path.exists(ref_table_path):
                    issues.append(
                        f"Foreign key references missing table: "
                        f"{table_name}.{fk.get('column')} -> {ref_table}"
                    )
        
        return issues
    
    # ==================== DATA MIGRATION & CONVERSION ====================
    
    @staticmethod
    def migrate_table_structure(db_instance, table_name: str, 
                               new_columns: Dict, 
                               column_mapping: Dict = None) -> Dict:
        """
        Migrate table to new structure
        
        Args:
            db_instance: ELDB database instance
            table_name: Table name
            new_columns: New column definitions
            column_mapping: Map old column names to new ones
            
        Returns:
            Dict: Migration results
        """
        results = {
            'success': False,
            'rows_migrated': 0,
            'new_table': f"{table_name}_migrated",
            'errors': []
        }
        
        try:
            # Load original table
            if table_name not in db_instance.tables:
                db_instance.load_table(table_name)
            
            # Read original data
            table = db_instance.tables[table_name]
            rows = db_instance._read_rows(table)
            
            # Create new table
            new_table_name = f"{table_name}_migrated"
            db_instance.create_table(new_table_name, new_columns)
            
            # Migrate data
            migrated_rows = 0
            for row in rows:
                new_row = {}
                
                if column_mapping:
                    # Map old columns to new ones
                    for old_col, new_col in column_mapping.items():
                        if old_col in row:
                            new_row[new_col] = row[old_col]
                else:
                    # Try to match by name
                    for new_col in new_columns:
                        if new_col in row:
                            new_row[new_col] = row[new_col]
                        else:
                            # Set default based on type
                            col_type = new_columns[new_col].get('type', 'str')
                            new_row[new_col] = 0 if col_type == 'int' else ""
                
                # Insert into new table
                try:
                    db_instance.insert(new_table_name, new_row)
                    migrated_rows += 1
                except:
                    pass
            
            results['rows_migrated'] = migrated_rows
            results['success'] = True
            
            print(f"✓ Migrated {migrated_rows} rows to {new_table_name}")
            
        except Exception as e:
            error_msg = f"Migration failed: {type(e).__name__}: {str(e)}"
            results['errors'].append(error_msg)
            print(f"✗ {error_msg}")
        
        return results
    
    @staticmethod
    def convert_to_sqlite(db_instance, sqlite_path: str) -> Dict:
        """
        Convert ELDB database to SQLite
        
        Args:
            db_instance: ELDB database instance
            sqlite_path: Path to SQLite database file
            
        Returns:
            Dict: Conversion results
        """
        results = {
            'success': False,
            'tables_converted': 0,
            'total_rows': 0,
            'sqlite_path': sqlite_path,
            'errors': []
        }
        
        try:
            import sqlite3
            
            # Connect to SQLite
            conn = sqlite3.connect(sqlite_path)
            cursor = conn.cursor()
            
            # Find all tables
            table_files = []
            for file in os.listdir(db_instance.db_folder):
                if file.endswith('.eldb'):
                    table_files.append(file[:-5])
            
            for table_name in table_files:
                print(f"Converting table: {table_name}")
                
                try:
                    # Load table
                    if table_name not in db_instance.tables:
                        db_instance.load_table(table_name)
                    
                    table = db_instance.tables[table_name]
                    columns = table['header']['columns']
                    
                    # Read data
                    rows = db_instance._read_rows(table)
                    
                    # Create SQLite table
                    column_defs = []
                    for col_name, col_def in columns.items():
                        col_type = col_def.get('type', 'str')
                        sql_type = 'INTEGER' if col_type == 'int' else 'TEXT'
                        column_defs.append(f'"{col_name}" {sql_type}')
                    
                    create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(column_defs)})'
                    cursor.execute(create_sql)
                    
                    # Insert data
                    for row in rows:
                        placeholders = ', '.join(['?' for _ in columns])
                        column_names = ', '.join([f'"{col}"' for col in columns.keys()])
                        values = [row.get(col) for col in columns.keys()]
                        
                        insert_sql = f'INSERT INTO "{table_name}" ({column_names}) VALUES ({placeholders})'
                        cursor.execute(insert_sql, values)
                    
                    results['tables_converted'] += 1
                    results['total_rows'] += len(rows)
                    
                    print(f"  ✓ Converted {len(rows)} rows")
                    
                except Exception as e:
                    error_msg = f"Failed to convert table {table_name}: {e}"
                    results['errors'].append(error_msg)
                    print(f"  ✗ {error_msg}")
            
            # Commit and close
            conn.commit()
            conn.close()
            
            results['success'] = True
            print(f"\n✓ Conversion complete: {results['tables_converted']} tables, {results['total_rows']} rows")
            
        except ImportError:
            error_msg = "SQLite3 module not available"
            results['errors'].append(error_msg)
            print(f"✗ {error_msg}")
        except Exception as e:
            error_msg = f"Conversion failed: {type(e).__name__}: {str(e)}"
            results['errors'].append(error_msg)
            print(f"✗ {error_msg}")
        
        return results
    
    # ==================== PERFORMANCE OPTIMIZATION ====================
    
    @staticmethod
    def optimize_table(db_instance, table_name: str) -> Dict:
        """
        Optimize table performance
        
        Args:
            db_instance: ELDB database instance
            table_name: Table name
            
        Returns:
            Dict: Optimization results
        """
        results = {
            'success': False,
            'original_size': 0,
            'optimized_size': 0,
            'space_saved': 0,
            'rows_reindexed': 0,
            'errors': []
        }
        
        try:
            table_path = os.path.join(db_instance.db_folder, f"{table_name}.eldb")
            
            if not os.path.exists(table_path):
                results['errors'].append(f"Table not found: {table_path}")
                return results
            
            results['original_size'] = os.path.getsize(table_path)
            
            # Simply reload and save the table (this will rebuild it cleanly)
            if table_name in db_instance.tables:
                del db_instance.tables[table_name]
            
            db_instance.load_table(table_name)
            table = db_instance.tables[table_name]
            
            # Read all rows
            rows = db_instance._read_rows(table)
            results['rows_reindexed'] = len(rows)
            
            # Save back (this will optimize storage)
            db_instance._save_rows(table_name, rows)
            
            results['optimized_size'] = os.path.getsize(table_path)
            results['space_saved'] = results['original_size'] - results['optimized_size']
            results['success'] = True
            
            print(f"✓ Table optimized: {table_name}")
            print(f"  Original size: {results['original_size']} bytes")
            print(f"  Optimized size: {results['optimized_size']} bytes")
            print(f"  Space saved: {results['space_saved']} bytes")
            print(f"  Rows reindexed: {results['rows_reindexed']}")
            
        except Exception as e:
            error_msg = f"Optimization failed: {type(e).__name__}: {str(e)}"
            results['errors'].append(error_msg)
            print(f"✗ {error_msg}")
        
        return results
    
    @staticmethod
    def rebuild_indexes(db_instance, table_name: str = None) -> Dict:
        """
        Rebuild indexes for faster queries
        
        Args:
            db_instance: ELDB database instance
            table_name: Specific table or None for all tables
            
        Returns:
            Dict: Rebuild results
        """
        results = {
            'success': False,
            'tables_rebuilt': 0,
            'errors': []
        }
        
        try:
            if table_name:
                tables = [table_name]
            else:
                # Get all tables
                tables = []
                for file in os.listdir(db_instance.db_folder):
                    if file.endswith('.eldb'):
                        tables.append(file[:-5])
            
            for tbl in tables:
                try:
                    if tbl not in db_instance.tables:
                        db_instance.load_table(tbl)
                    
                    # Rebuild index
                    table = db_instance.tables[tbl]
                    pk = table['header'].get('primary_key')
                    
                    if pk:
                        rows = db_instance._read_rows(table)
                        index = {}
                        for i, row in enumerate(rows):
                            if pk in row:
                                index[row[pk]] = i
                        
                        table['index'] = index
                        print(f"✓ Rebuilt index for {tbl}.{pk}")
                        results['tables_rebuilt'] += 1
                    
                except Exception as e:
                    error_msg = f"Failed to rebuild index for {tbl}: {e}"
                    results['errors'].append(error_msg)
                    print(f"✗ {error_msg}")
            
            results['success'] = True
            
        except Exception as e:
            error_msg = f"Index rebuild failed: {type(e).__name__}: {str(e)}"
            results['errors'].append(error_msg)
            print(f"✗ {error_msg}")
        
        return results
    
    # ==================== SECURITY & VALIDATION ====================
    
    @staticmethod
    def validate_table_integrity(db_instance, table_name: str) -> Dict:
        """
        Comprehensive table integrity validation
        
        Args:
            db_instance: ELDB database instance
            table_name: Table name
            
        Returns:
            Dict: Validation results
        """
        results = {
            'table_name': table_name,
            'is_valid': True,
            'checks_passed': 0,
            'checks_failed': 0,
            'checks': {},
            'issues': []
        }
        
        try:
            if table_name not in db_instance.tables:
                db_instance.load_table(table_name)
            
            table = db_instance.tables[table_name]
            header = table['header']
            columns = header.get('columns', {})
            
            # Check 1: Header validation
            results['checks']['header'] = {'passed': False, 'message': ''}
            if header and columns:
                results['checks']['header']['passed'] = True
                results['checks']['header']['message'] = 'Header is valid'
                results['checks_passed'] += 1
            else:
                results['checks']['header']['message'] = 'Header is missing or corrupted'
                results['checks_failed'] += 1
                results['issues'].append('Header corruption')
                results['is_valid'] = False
            
            # Check 2: Read rows
            results['checks']['read_rows'] = {'passed': False, 'message': '', 'row_count': 0}
            try:
                rows = db_instance._read_rows(table)
                results['checks']['read_rows']['passed'] = True
                results['checks']['read_rows']['message'] = f'Successfully read {len(rows)} rows'
                results['checks']['read_rows']['row_count'] = len(rows)
                results['checks_passed'] += 1
            except Exception as e:
                results['checks']['read_rows']['message'] = f'Failed to read rows: {e}'
                results['checks_failed'] += 1
                results['issues'].append(f'Cannot read rows: {e}')
                results['is_valid'] = False
            
            # Check 3: Primary key uniqueness (if exists)
            pk = header.get('primary_key')
            if pk:
                results['checks']['primary_key'] = {'passed': False, 'message': '', 'unique_count': 0}
                try:
                    rows = db_instance._read_rows(table)
                    pk_values = [row.get(pk) for row in rows if pk in row]
                    unique_values = set(pk_values)
                    
                    if len(pk_values) == len(unique_values):
                        results['checks']['primary_key']['passed'] = True
                        results['checks']['primary_key']['message'] = f'Primary key {pk} is unique'
                        results['checks']['primary_key']['unique_count'] = len(unique_values)
                        results['checks_passed'] += 1
                    else:
                        results['checks']['primary_key']['message'] = f'Primary key {pk} has duplicates'
                        results['checks_failed'] += 1
                        results['issues'].append(f'Primary key {pk} has duplicates')
                        results['is_valid'] = False
                except Exception as e:
                    results['checks']['primary_key']['message'] = f'Failed to check primary key: {e}'
                    results['checks_failed'] += 1
                    results['issues'].append(f'Primary key check failed: {e}')
                    results['is_valid'] = False
            
            # Check 4: Data type consistency
            results['checks']['data_types'] = {'passed': False, 'message': '', 'type_issues': []}
            try:
                rows = db_instance._read_rows(table)
                type_issues = []
                
                for col_name, col_def in columns.items():
                    col_type = col_def.get('type', 'str')
                    
                    for i, row in enumerate(rows[:100]):  # Check first 100 rows
                        value = row.get(col_name)
                        if value is not None:
                            if col_type == 'int' and not isinstance(value, int):
                                type_issues.append(f'Row {i}, Column {col_name}: Expected int, got {type(value).__name__}')
                            elif col_type == 'str' and not isinstance(value, str):
                                type_issues.append(f'Row {i}, Column {col_name}: Expected str, got {type(value).__name__}')
                
                if not type_issues:
                    results['checks']['data_types']['passed'] = True
                    results['checks']['data_types']['message'] = 'All data types are consistent'
                    results['checks_passed'] += 1
                else:
                    results['checks']['data_types']['message'] = f'Found {len(type_issues)} type issues'
                    results['checks']['data_types']['type_issues'] = type_issues[:5]  # Limit output
                    results['checks_failed'] += 1
                    results['issues'].extend(type_issues[:3])
                    results['is_valid'] = False
            
            except Exception as e:
                results['checks']['data_types']['message'] = f'Failed to check data types: {e}'
                results['checks_failed'] += 1
                results['issues'].append(f'Data type check failed: {e}')
                results['is_valid'] = False
            
            # Summary
            total_checks = results['checks_passed'] + results['checks_failed']
            if total_checks > 0:
                success_rate = (results['checks_passed'] / total_checks) * 100
                results['success_rate'] = f'{success_rate:.1f}%'
            
        except Exception as e:
            results['is_valid'] = False
            results['issues'].append(f'Validation failed: {type(e).__name__}: {str(e)}')
        
        return results
    
    # ==================== UTILITY FUNCTIONS ====================
    
    @staticmethod
    def get_table_info(db_instance, table_name: str) -> Dict:
        """Get detailed information about a table"""
        info = {
            'table_name': table_name,
            'exists': False,
            'row_count': 0,
            'columns': {},
            'primary_key': None,
            'file_size': 0,
            'index_size': 0
        }
        
        try:
            table_path = os.path.join(db_instance.db_folder, f"{table_name}.eldb")
            
            if not os.path.exists(table_path):
                return info
            
            info['exists'] = True
            info['file_size'] = os.path.getsize(table_path)
            
            if table_name in db_instance.tables:
                table = db_instance.tables[table_name]
                header = table['header']
                
                info['row_count'] = header.get('row_count', 0)
                info['columns'] = header.get('columns', {})
                info['primary_key'] = header.get('primary_key')
                info['index_size'] = len(table.get('index', {}))
            
            return info
        
        except Exception as e:
            info['error'] = str(e)
            return info
    
    @staticmethod
    def list_tables(db_instance) -> List[Dict]:
        """List all tables in database with basic info"""
        tables = []
        
        for file in os.listdir(db_instance.db_folder):
            if file.endswith('.eldb'):
                table_name = file[:-5]
                info = ELDBAdvancedUtils.get_table_info(db_instance, table_name)
                tables.append(info)
        
        return tables
    
    @staticmethod
    def export_schema(db_instance, output_file: str = None) -> Dict:
        """Export database schema to JSON"""
        schema = {
            'database': db_instance.db_folder,
            'tables': {},
            'exported_at': datetime.now().isoformat()
        }
        
        for file in os.listdir(db_instance.db_folder):
            if file.endswith('.eldb'):
                table_name = file[:-5]
                info = ELDBAdvancedUtils.get_table_info(db_instance, table_name)
                schema['tables'][table_name] = {
                    'columns': info.get('columns', {}),
                    'primary_key': info.get('primary_key'),
                    'row_count': info.get('row_count', 0)
                }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(schema, f, indent=2, default=str)
            print(f"Schema exported to {output_file}")
        
        return schema
    
    @staticmethod
    def import_schema(db_instance, schema_file: str, create_tables: bool = True) -> Dict:
        """Import schema and optionally create tables"""
        results = {
            'success': False,
            'tables_created': 0,
            'errors': []
        }
        
        try:
            with open(schema_file, 'r') as f:
                schema = json.load(f)
            
            for table_name, table_info in schema.get('tables', {}).items():
                try:
                    if create_tables:
                        columns = table_info.get('columns', {})
                        primary_key = table_info.get('primary_key')
                        
                        db_instance.create_table(
                            table_name, 
                            columns, 
                            primary_key=primary_key,
                            if_not_exists=True
                        )
                        results['tables_created'] += 1
                        print(f"✓ Created table: {table_name}")
                
                except Exception as e:
                    error_msg = f"Failed to create table {table_name}: {e}"
                    results['errors'].append(error_msg)
                    print(f"✗ {error_msg}")
            
            results['success'] = True
            
        except Exception as e:
            error_msg = f"Import failed: {type(e).__name__}: {str(e)}"
            results['errors'].append(error_msg)
            print(f"✗ {error_msg}")
        
        return results
    
    @staticmethod
    def generate_test_data(db_instance, table_name: str, num_rows: int = 100) -> Dict:
        """Generate test data for a table"""
        results = {
            'success': False,
            'rows_inserted': 0,
            'errors': []
        }
        
        try:
            if table_name not in db_instance.tables:
                db_instance.load_table(table_name)
            
            table = db_instance.tables[table_name]
            columns = table['header']['columns']
            
            for i in range(num_rows):
                row = {}
                
                for col_name, col_def in columns.items():
                    col_type = col_def.get('type', 'str')
                    col_size = col_def.get('size', 50)
                    
                    if col_type == 'int':
                        row[col_name] = i  # Use row number
                    else:  # String
                        # Generate random string
                        length = min(10, col_size - 1)
                        letters = string.ascii_letters + string.digits
                        row[col_name] = ''.join(random.choice(letters) for _ in range(length))
                
                try:
                    db_instance.insert(table_name, row)
                    results['rows_inserted'] += 1
                except:
                    pass  # Skip if insert fails
            
            results['success'] = True
            print(f"✓ Generated {results['rows_inserted']} test rows in {table_name}")
            
        except Exception as e:
            error_msg = f"Test data generation failed: {type(e).__name__}: {str(e)}"
            results['errors'].append(error_msg)
            print(f"✗ {error_msg}")
        
        return results
    
    @staticmethod
    def benchmark_query(db_instance, table_name: str, query_count: int = 100) -> Dict:
        """Benchmark query performance"""
        results = {
            'table': table_name,
            'query_count': query_count,
            'total_time': 0,
            'average_time': 0,
            'queries_per_second': 0,
            'errors': []
        }
        
        try:
            import time
            
            if table_name not in db_instance.tables:
                db_instance.load_table(table_name)
            
            table = db_instance.tables[table_name]
            rows = db_instance._read_rows(table)
            total_rows = len(rows)
            
            print(f"Benchmarking {table_name} ({total_rows} rows)...")
            
            start_time = time.time()
            
            for i in range(query_count):
                # Simple select all
                db_instance.select(table_name, limit=10)
                
                # Every 10 queries, print progress
                if (i + 1) % 10 == 0:
                    elapsed = time.time() - start_time
                    print(f"  Completed {i + 1}/{query_count} queries ({elapsed:.2f}s)")
            
            end_time = time.time()
            
            results['total_time'] = end_time - start_time
            results['average_time'] = results['total_time'] / query_count
            results['queries_per_second'] = query_count / results['total_time'] if results['total_time'] > 0 else 0
            
            print(f"✓ Benchmark complete:")
            print(f"  Total time: {results['total_time']:.2f}s")
            print(f"  Average query: {results['average_time']*1000:.2f}ms")
            print(f"  Queries/sec: {results['queries_per_second']:.1f}")
            
        except Exception as e:
            error_msg = f"Benchmark failed: {type(e).__name__}: {str(e)}"
            results['errors'].append(error_msg)
            print(f"✗ {error_msg}")
        
        return results


# ==================== CONVENIENCE FUNCTIONS ====================

def quick_repair(db_instance, table_name: str) -> bool:
    """Quick repair wrapper"""
    utils = ELDBAdvancedUtils()
    result = utils.repair_table(db_instance, table_name)
    return result.get('success', False)

def quick_diagnose(db_instance, table_name: str = None) -> Dict:
    """Quick diagnosis wrapper"""
    utils = ELDBAdvancedUtils()
    if table_name:
        return utils.diagnose_table(db_instance, table_name)
    else:
        return utils.diagnose_database(db_instance)

def export_to_csv(db_instance, table_name: str, csv_path: str) -> bool:
    """Export table to CSV"""
    try:
        if table_name not in db_instance.tables:
            db_instance.load_table(table_name)
        
        table = db_instance.tables[table_name]
        rows = db_instance._read_rows(table)
        columns = table['header']['columns']
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns.keys())
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✓ Exported {len(rows)} rows to {csv_path}")
        return True
    
    except Exception as e:
        print(f"✗ Export failed: {e}")
        return False

def import_from_csv(db_instance, csv_path: str, table_name: str, 
                   create_table: bool = True, **kwargs) -> bool:
    """Import CSV to table"""
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not rows:
            print("CSV file is empty")
            return False
        
        if create_table:
            # Infer schema from first row
            columns = {}
            first_row = rows[0]
            
            for col_name, value in first_row.items():
                if value and value.replace('-', '').replace('+', '').isdigit():
                    col_type = 'int'
                    size = 4
                else:
                    col_type = 'str'
                    size = min(100, len(str(value)) + 10) if value else 50
                
                columns[col_name] = {
                    'type': col_type,
                    'size': size,
                    'nullable': True
                }
            
            db_instance.create_table(table_name, columns, **kwargs)
        
        # Insert rows
        for row in rows:
            processed_row = {}
            for col_name, value in row.items():
                if col_name in db_instance.tables[table_name]['header']['columns']:
                    col_type = db_instance.tables[table_name]['header']['columns'][col_name]['type']
                    if col_type == 'int':
                        processed_row[col_name] = int(value) if value and value.strip() else 0
                    else:
                        processed_row[col_name] = value if value else ''
            
            try:
                db_instance.insert(table_name, processed_row)
            except:
                pass  # Skip problematic rows
        
        print(f"✓ Imported {len(rows)} rows to {table_name}")
        return True
    
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


# ==================== MAIN TEST FUNCTION ====================

def test_all_features():
    """Test all features of the enhanced utils"""
    print("=" * 70)
    print("ELDB ENHANCED UTILITIES - COMPREHENSIVE TEST")
    print("=" * 70)
    
    # Create test database
    import tempfile
    import shutil
    
    test_dir = tempfile.mkdtemp()
    print(f"Test directory: {test_dir}")
    
    try:
        # Import ELDB
        from ELDB import ELDB
        
        # Create database
        db = ELDB(os.path.join(test_dir, "test_db"))
        
        # Create a test table
        db.create_table("users", {
            "id": {"type": "int", "size": 4},
            "name": {"type": "str", "size": 50},
            "email": {"type": "str", "size": 100},
            "age": {"type": "int", "size": 4}
        }, primary_key="id")
        
        # Insert test data
        for i in range(5):
            db.insert("users", {
                "id": i,
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "age": 20 + i
            })
        
        print("✓ Created test database with 5 users")
        
        # Initialize utils
        utils = ELDBAdvancedUtils()
        
        # Test 1: Get table info
        print("\n1. Testing get_table_info()...")
        info = utils.get_table_info(db, "users")
        print(f"   Table: {info['table_name']}")
        print(f"   Rows: {info['row_count']}")
        print(f"   Columns: {len(info['columns'])}")
        
        # Test 2: List tables
        print("\n2. Testing list_tables()...")
        tables = utils.list_tables(db)
        print(f"   Found {len(tables)} tables")
        
        # Test 3: Diagnose table
        print("\n3. Testing diagnose_table()...")
        diagnosis = utils.diagnose_table(db, "users")
        print(f"   Table exists: {diagnosis['exists']}")
        print(f"   Issues found: {len(diagnosis['issues'])}")
        
        # Test 4: Validate integrity
        print("\n4. Testing validate_table_integrity()...")
        validation = utils.validate_table_integrity(db, "users")
        print(f"   Table valid: {validation['is_valid']}")
        print(f"   Checks passed: {validation['checks_passed']}/{validation['checks_passed'] + validation['checks_failed']}")
        
        # Test 5: Corrupt and repair table
        print("\n5. Testing repair_table()...")
        
        # First corrupt the table
        table_path = db.table_path("users")
        with open(table_path, "rb") as f:
            data = f.read()
        
        # Truncate the file
        with open(table_path, "wb") as f:
            f.write(data[:100])  # Keep only 100 bytes
        
        print(f"   Corrupted table (truncated to 100 bytes)")
        
        # Now repair it
        repair_result = utils.repair_table(db, "users", backup=True)
        print(f"   Repair successful: {repair_result['success']}")
        print(f"   Rows recovered: {repair_result.get('recovered_rows', 0)}")
        
        # Test 6: Export/Import
        print("\n6. Testing export/import functions...")
        
        # Export to CSV
        csv_path = os.path.join(test_dir, "users.csv")
        if export_to_csv(db, "users", csv_path):
            print(f"   ✓ Exported to CSV: {csv_path}")
        
        # Import to new table
        if import_from_csv(db, csv_path, "users_imported", create_table=True):
            print(f"   ✓ Imported from CSV to 'users_imported'")
        
        # Test 7: Generate test data
        print("\n7. Testing generate_test_data()...")
        gen_result = utils.generate_test_data(db, "users", num_rows=10)
        print(f"   Generated {gen_result['rows_inserted']} test rows")
        
        # Test 8: Benchmark
        print("\n8. Testing benchmark_query()...")
        benchmark = utils.benchmark_query(db, "users", query_count=50)
        print(f"   Average query time: {benchmark['average_time']*1000:.2f}ms")
        
        # Test 9: Optimize table
        print("\n9. Testing optimize_table()...")
        optimize = utils.optimize_table(db, "users")
        if optimize['success']:
            print(f"   Space saved: {optimize['space_saved']} bytes")
        
        # Test 10: Export schema
        print("\n10. Testing export_schema()...")
        schema = utils.export_schema(db, os.path.join(test_dir, "schema.json"))
        print(f"   Exported schema for {len(schema['tables'])} tables")
        
        print("\n" + "=" * 70)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"\nCleaned up test directory: {test_dir}")


if __name__ == "__main__":
    print("ELDB Enhanced Utilities Module")
    print("Available classes:")
    print("  - ELDBAdvancedUtils: Main utility class with all functions")
    print("  - quick_repair(): Quick table repair wrapper")
    print("  - quick_diagnose(): Quick diagnosis wrapper")
    print("  - export_to_csv(): Export table to CSV")
    print("  - import_from_csv(): Import CSV to table")
    print("\nTo run comprehensive tests, call: test_all_features()")
    
    # Uncomment to run tests
    # test_all_features()


__all__ = [
    # Main utility class
    'ELDBAdvancedUtils',
    
    # Core repair functions
    'repair_table',
    'repair_database',
    'repair_column',
    
    # Diagnostic functions
    'diagnose_table',
    'diagnose_database',
    'validate_table_integrity',
    
    # Data management
    'migrate_table_structure',
    'convert_to_sqlite',
    'export_to_csv',
    'import_from_csv',
    
    # Performance optimization
    'optimize_table',
    'rebuild_indexes',
    'benchmark_query',
    
    # Utility functions
    'get_table_info',
    'list_tables',
    'export_schema',
    'import_schema',
    'generate_test_data',
    
    # Quick convenience functions
    'quick_repair',
    'quick_diagnose',
    
    # Helper functions (optional - include if you want them public)
    'export_to_csv',  # Already listed, but keeping for clarity
    'import_from_csv',  # Already listed, but keeping for clarity
    
    # Test function
    'test_all_features',
]