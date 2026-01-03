# mydb/utils.py
import os
import json
import csv
import math
import random
import string
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
import struct
import ast  # Add this import for safe parsing

class ELDBUtils:
    """Utility functions for ELDB database operations"""
    
    @staticmethod
    def _parse_header(header_line: bytes) -> Dict:
        """Safely parse header that might use single quotes (like ast.literal_eval)"""
        try:
            # First try JSON (double quotes)
            return json.loads(header_line.decode())
        except json.JSONDecodeError:
            try:
                # Fall back to ast.literal_eval for single quotes
                return ast.literal_eval(header_line.decode())
            except:
                return {}
    
    # ----------------- Data Validation -----------------
    @staticmethod
    def validate_column_value(col_type: str, value: Any, size: int = None) -> bool:
        """
        Validate if a value matches the column type
        
        Args:
            col_type: 'int' or 'str'
            value: Value to validate
            size: For string columns, maximum size
            
        Returns:
            bool: True if valid
        """
        if value is None:
            return True
            
        if col_type == 'int':
            return isinstance(value, int)
        elif col_type == 'str':
            if not isinstance(value, str):
                return False
            if size and len(value.encode('utf-8')) > size:
                return False
            return True
        return False
    
    @staticmethod
    def validate_row_structure(row: Dict, columns: Dict) -> Tuple[bool, str]:
        """
        Validate if a row matches the table structure
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        for col_name, col_spec in columns.items():
            if col_name not in row:
                if not col_spec.get('nullable', True):
                    return False, f"Column '{col_name}' is required"
                continue
                
            value = row[col_name]
            if value is None and not col_spec.get('nullable', True):
                return False, f"Column '{col_name}' cannot be null"
                
            if value is not None:
                col_type = col_spec.get('type', 'str')
                size = col_spec.get('size', 50)
                if not ELDBUtils.validate_column_value(col_type, value, size):
                    return False, f"Column '{col_name}' expects {col_type}, got {type(value).__name__}"
        
        return True, ""
    
    # ----------------- Data Type Conversion -----------------
    @staticmethod
    def to_int(value: Any, default: int = 0) -> int:
        """Safely convert value to integer"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def to_str(value: Any, default: str = "") -> str:
        """Safely convert value to string"""
        if value is None:
            return default
        return str(value)
    
    @staticmethod
    def serialize_value(value: Any, col_type: str, size: int = 50) -> bytes:
        """
        Serialize a value to bytes according to column type
        
        Args:
            value: Value to serialize
            col_type: 'int' or 'str'
            size: For string columns, maximum size
            
        Returns:
            bytes: Serialized value
        """
        if value is None:
            if col_type == 'int':
                return struct.pack('i', 0)
            else:
                return b'\x00' * size
        
        if col_type == 'int':
            return struct.pack('i', value)
        else:  # 'str'
            encoded = value.encode('utf-8', errors='ignore')[:size-1]
            return encoded + b'\x00' * (size - len(encoded))
    
    @staticmethod
    def deserialize_value(data: bytes, col_type: str, size: int = 50) -> Any:
        """
        Deserialize bytes to value according to column type
        """
        if col_type == 'int':
            return struct.unpack('i', data[:4])[0]
        else:  # 'str'
            # Find null terminator
            null_pos = data.find(b'\x00')
            if null_pos == -1:
                null_pos = size
            text_data = data[:null_pos]
            return text_data.decode('utf-8', errors='ignore')
    
    # ----------------- File Operations -----------------
    @staticmethod
    def backup_database(db_folder: str, backup_name: str = None) -> str:
        """
        Create a backup of the entire database
        
        Args:
            db_folder: Database folder path
            backup_name: Optional backup name (defaults to timestamp)
            
        Returns:
            str: Path to backup file
        """
        import zipfile
        
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"eldb_backup_{timestamp}"
        
        backup_path = f"{backup_name}.zip"
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(db_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, db_folder)
                    zipf.write(file_path, arcname)
        
        print(f"Database backed up to: {backup_path}")
        return backup_path
    
    @staticmethod
    def restore_database(backup_path: str, restore_folder: str = None) -> str:
        """
        Restore database from backup
        
        Args:
            backup_path: Path to backup zip file
            restore_folder: Folder to restore to (defaults to backup name without extension)
            
        Returns:
            str: Path to restored database
        """
        import zipfile
        
        if restore_folder is None:
            restore_folder = os.path.splitext(os.path.basename(backup_path))[0]
        
        os.makedirs(restore_folder, exist_ok=True)
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(restore_folder)
        
        print(f"Database restored to: {restore_folder}")
        return restore_folder
    
    @staticmethod
    def get_database_stats(db_folder: str) -> Dict:
        """
        Get statistics about the database
        
        Returns:
            Dict: Database statistics
        """
        stats = {
            'total_tables': 0,
            'total_rows': 0,
            'total_size_bytes': 0,
            'tables': {}
        }
        
        for file in os.listdir(db_folder):
            if file.endswith('.eldb'):
                table_name = file[:-5]
                file_path = os.path.join(db_folder, file)
                
                # Get file size
                file_size = os.path.getsize(file_path)
                
                # Try to read header for row count
                row_count = 0
                try:
                    with open(file_path, 'rb') as f:
                        header_line = f.readline()
                        header = ELDBUtils._parse_header(header_line)
                        row_count = header.get('row_count', 0)
                except:
                    pass
                
                stats['tables'][table_name] = {
                    'rows': row_count,
                    'size_bytes': file_size,
                    'path': file_path
                }
                stats['total_tables'] += 1
                stats['total_rows'] += row_count
                stats['total_size_bytes'] += file_size
        
        return stats
    
    # ----------------- Data Import/Export -----------------
    @staticmethod
    def export_to_csv(table_path: str, output_csv: str = None) -> bool:
        """
        Export table data to CSV file
        
        Args:
            table_path: Path to .eldb table file
            output_csv: Output CSV file path (defaults to table_name.csv)
            
        Returns:
            bool: True if successful
        """
        try:
            # Read table header
            with open(table_path, 'rb') as f:
                header_line = f.readline()
                header = ELDBUtils._parse_header(header_line)  # Use safe parsing
            
            if not header:
                print(f"Failed to parse header from {table_path}")
                return False
                
            columns = header.get('columns', {})
            if not columns:
                print(f"No columns found in table header")
                return False
                
            col_names = list(columns.keys())
            
            # Determine output CSV path
            if output_csv is None:
                table_name = os.path.splitext(os.path.basename(table_path))[0]
                output_csv = f"{table_name}.csv"
            
            # Read rows
            rows = []
            col_sizes = {}
            row_size = 0
            
            for col, opts in columns.items():
                if opts.get('type') == 'int':
                    size = 4
                else:
                    size = opts.get('size', 50)  # Default size
                col_sizes[col] = size
                row_size += size
            
            with open(table_path, 'rb') as f:
                f.readline()  # Skip header
                
                while True:
                    data = f.read(row_size)
                    if not data:
                        break
                    
                    row = {}
                    offset = 0
                    for col, opts in columns.items():
                        size = col_sizes[col]
                        if opts.get('type') == 'int':
                            try:
                                row[col] = struct.unpack('i', data[offset:offset+4])[0]
                            except:
                                row[col] = 0
                            offset += 4
                        else:  # 'str' or unspecified
                            raw = data[offset:offset+size]
                            null_pos = raw.find(b'\x00')
                            if null_pos == -1:
                                null_pos = size
                            text = raw[:null_pos].decode('utf-8', errors='ignore')
                            row[col] = text
                            offset += size
                    rows.append(row)
            
            # Write to CSV
            with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=col_names)
                writer.writeheader()
                writer.writerows(rows)
            
            print(f"Exported {len(rows)} rows from {table_path} to {output_csv}")
            return True
            
        except Exception as e:
            print(f"Export failed: {e}")
            import traceback
            traceback.print_exc()  # Add this for debugging
            return False
    
    @staticmethod
    def import_from_csv(csv_path: str, db_instance, table_name: str, 
                       create_table: bool = True, **table_kwargs) -> bool:
        """
        Import data from CSV to table
        
        Args:
            csv_path: Path to CSV file
            db_instance: ELDB instance
            table_name: Target table name
            create_table: If True, create table with inferred schema
            **table_kwargs: Additional arguments for create_table
            
        Returns:
            bool: True if successful
        """
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
            
            if not rows:
                print("CSV file is empty")
                return False
            
            # Infer schema from first row
            if create_table:
                columns = {}
                first_row = rows[0]
                
                for col_name, value in first_row.items():
                    # Try to determine type
                    if value and value.replace('-', '').replace('+', '').isdigit():
                        col_type = 'int'
                        size = 4
                    else:
                        col_type = 'str'
                        # Estimate size (string length + some buffer)
                        size = min(100, len(value) + 10) if value else 50
                    
                    columns[col_name] = {
                        'type': col_type,
                        'size': size,
                        'nullable': True
                    }
                
                # Create table
                db_instance.create_table(table_name, columns, **table_kwargs)
            
            # Insert rows
            for row in rows:
                # Convert types
                processed_row = {}
                for col_name, value in row.items():
                    if col_name in db_instance.tables[table_name]['header']['columns']:
                        col_type = db_instance.tables[table_name]['header']['columns'][col_name]['type']
                        if col_type == 'int':
                            processed_row[col_name] = int(value) if value and value.strip() else 0
                        else:
                            processed_row[col_name] = value if value else ''
                
                db_instance.insert(table_name, processed_row)
            
            print(f"Imported {len(rows)} rows from {csv_path} to {table_name}")
            return True
            
        except Exception as e:
            print(f"Import failed: {e}")
            return False
    
    # ----------------- Query Utilities -----------------
    @staticmethod
    def build_where_clause(conditions: Dict) -> str:
        """
        Build SQL-like WHERE clause string from conditions dictionary
        
        Args:
            conditions: Dictionary of conditions
                e.g., {'age': ('>', 18), 'name': ('=', 'John')}
                
        Returns:
            str: SQL-like WHERE clause
        """
        if not conditions:
            return ""
        
        parts = []
        for column, (operator, value) in conditions.items():
            if isinstance(value, str):
                value_str = f"'{value}'"
            else:
                value_str = str(value)
            
            if operator == '=':
                parts.append(f"{column} = {value_str}")
            elif operator == '!=':
                parts.append(f"{column} != {value_str}")
            elif operator == '>':
                parts.append(f"{column} > {value_str}")
            elif operator == '<':
                parts.append(f"{column} < {value_str}")
            elif operator == '>=':
                parts.append(f"{column} >= {value_str}")
            elif operator == '<=':
                parts.append(f"{column} <= {value_str}")
            elif operator == 'LIKE':
                parts.append(f"{column} LIKE '{value}'")
            elif operator == 'IN':
                if isinstance(value, (list, tuple)):
                    in_values = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) 
                                          for v in value])
                    parts.append(f"{column} IN ({in_values})")
        
        return " AND ".join(parts)
    
    @staticmethod
    def paginate_query(results: List, page: int = 1, per_page: int = 10) -> Dict:
        """
        Paginate query results
        
        Args:
            results: List of results
            page: Page number (1-indexed)
            per_page: Items per page
            
        Returns:
            Dict: {'items': [...], 'page': X, 'per_page': X, 'total': X, 'pages': X}
        """
        total = len(results)
        pages = math.ceil(total / per_page)
        
        if page < 1:
            page = 1
        if page > pages:
            page = pages
        
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            'items': results[start:end],
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages
        }
    
    # ----------------- Performance Utilities -----------------
    @staticmethod
    def create_index(db_instance, table_name: str, column: str, 
                    index_name: str = None) -> bool:
        """
        Create an index on a column (simulated)
        
        Args:
            db_instance: ELDB instance
            table_name: Table name
            column: Column to index
            index_name: Optional index name
            
        Returns:
            bool: True if successful
        """
        if table_name not in db_instance.tables:
            db_instance.load_table(table_name)
        
        if column not in db_instance.tables[table_name]['header']['columns']:
            print(f"Column '{column}' doesn't exist in table '{table_name}'")
            return False
        
        if index_name is None:
            index_name = f"idx_{table_name}_{column}"
        
        print(f"Index '{index_name}' created on {table_name}.{column}")
        return True
    
    @staticmethod
    def analyze_query_performance(db_instance, table_name: str, 
                                query_count: int = 100) -> Dict:
        """
        Analyze query performance
        
        Args:
            db_instance: ELDB instance
            table_name: Table name
            query_count: Number of queries to test
            
        Returns:
            Dict: Performance statistics
        """
        import time
        
        if table_name not in db_instance.tables:
            db_instance.load_table(table_name)
        
        table = db_instance.tables[table_name]
        total_rows = table['header'].get('row_count', 0)
        
        # Test different query types
        results = {
            'table': table_name,
            'total_rows': total_rows,
            'queries': {}
        }
        
        # Test 1: Full table scan
        start = time.time()
        for _ in range(query_count):
            rows = db_instance._read_rows(table)
        results['queries']['full_scan'] = {
            'time_per_query': (time.time() - start) / query_count,
            'rows_scanned': total_rows
        }
        
        # Test 2: Primary key lookup (if exists)
        pk = table['header'].get('primary_key')
        if pk and table['index']:
            # Use existing index
            test_value = list(table['index'].keys())[0] if table['index'] else None
            if test_value:
                start = time.time()
                for _ in range(query_count):
                    if test_value in table['index']:
                        pass  # Index lookup
                results['queries']['pk_lookup'] = {
                    'time_per_query': (time.time() - start) / query_count,
                    'index_used': True
                }
        
        return results
    
    # ----------------- Data Generation -----------------
    @staticmethod
    def generate_test_data(table_name: str, columns: Dict, 
                         row_count: int = 100) -> List[Dict]:
        """
        Generate test data for a table
        
        Args:
            table_name: Table name (for context)
            columns: Column definitions
            row_count: Number of rows to generate
            
        Returns:
            List[Dict]: Generated rows
        """
        rows = []
        
        for i in range(row_count):
            row = {}
            for col_name, col_spec in columns.items():
                col_type = col_spec.get('type', 'str')
                size = col_spec.get('size', 50)
                
                if col_type == 'int':
                    # Generate random integer
                    row[col_name] = random.randint(1, 10000)
                else:  # 'str'
                    # Generate random string
                    length = random.randint(5, min(20, size - 1))
                    letters = string.ascii_letters + string.digits + ' '
                    row[col_name] = ''.join(random.choice(letters) for _ in range(length))
            
            rows.append(row)
        
        return rows
    
    @staticmethod
    def generate_fake_table(db_instance, table_name: str, 
                          column_count: int = 5, row_count: int = 100) -> bool:
        """
        Generate a fake table with random data
        
        Args:
            db_instance: ELDB instance
            table_name: Table name
            column_count: Number of columns
            row_count: Number of rows
            
        Returns:
            bool: True if successful
        """
        try:
            # Generate column definitions
            columns = {}
            for i in range(column_count):
                col_name = f"col_{i+1}"
                col_type = random.choice(['int', 'str'])
                
                if col_type == 'int':
                    columns[col_name] = {
                        'type': 'int',
                        'size': 4,
                        'nullable': random.choice([True, False])
                    }
                else:
                    columns[col_name] = {
                        'type': 'str',
                        'size': random.choice([50, 100, 200]),
                        'nullable': random.choice([True, False])
                    }
            
            # Create table
            db_instance.create_table(table_name, columns)
            
            # Generate and insert data
            rows = ELDBUtils.generate_test_data(table_name, columns, row_count)
            for row in rows:
                db_instance.insert(table_name, row)
            
            print(f"Generated fake table '{table_name}' with {column_count} columns and {row_count} rows")
            return True
            
        except Exception as e:
            print(f"Failed to generate fake table: {e}")
            return False
    
    # ----------------- Security Utilities -----------------
    @staticmethod
    def encrypt_value(value: str, key: str = None) -> str:
        """
        Simple string encryption (for demonstration only - not production secure)
        """
        import base64
        
        if key is None:
            key = "eldb-default-key"
        
        # Simple XOR encryption (not secure for production!)
        key_bytes = key.encode()
        value_bytes = value.encode()
        encrypted = bytearray()
        
        for i in range(len(value_bytes)):
            encrypted.append(value_bytes[i] ^ key_bytes[i % len(key_bytes)])
        
        return base64.b64encode(encrypted).decode()
    
    @staticmethod
    def decrypt_value(encrypted: str, key: str = None) -> str:
        """
        Decrypt string (for demonstration only)
        """
        import base64
        
        if key is None:
            key = "eldb-default-key"
        
        encrypted_bytes = base64.b64decode(encrypted)
        key_bytes = key.encode()
        decrypted = bytearray()
        
        for i in range(len(encrypted_bytes)):
            decrypted.append(encrypted_bytes[i] ^ key_bytes[i % len(key_bytes)])
        
        return decrypted.decode()
    
    @staticmethod
    def hash_password(password: str, salt: str = None) -> Dict:
        """
        Hash a password with salt
        """
        if salt is None:
            salt = os.urandom(16).hex()
        
        # Use a proper hashing algorithm
        hash_obj = hashlib.sha256()
        hash_obj.update((password + salt).encode())
        password_hash = hash_obj.hexdigest()
        
        return {
            'hash': password_hash,
            'salt': salt
        }
    
    # ----------------- Diagnostic Utilities -----------------
    @staticmethod
    def check_table_integrity(db_instance, table_name: str) -> Dict:
        """
        Check table integrity and report issues
        
        Returns:
            Dict: Integrity check results
        """
        results = {
            'table': table_name,
            'issues': [],
            'warnings': [],
            'is_valid': True
        }
        
        try:
            if table_name not in db_instance.tables:
                db_instance.load_table(table_name)
            
            table = db_instance.tables[table_name]
            rows = db_instance._read_rows(table)
            header = table['header']
            
            # Check 1: Row count matches header
            if len(rows) != header.get('row_count', 0):
                results['warnings'].append(
                    f"Row count mismatch: header says {header.get('row_count', 0)}, "
                    f"but found {len(rows)} rows"
                )
            
            # Check 2: Check for null in non-nullable columns
            for i, row in enumerate(rows):
                for col_name, col_spec in header['columns'].items():
                    if not col_spec.get('nullable', True) and row.get(col_name) is None:
                        results['issues'].append(
                            f"Row {i}: Column '{col_name}' is null but marked as non-nullable"
                        )
                        results['is_valid'] = False
            
            # Check 3: Check primary key uniqueness
            pk = header.get('primary_key')
            if pk:
                seen = set()
                for i, row in enumerate(rows):
                    pk_value = row.get(pk)
                    if pk_value in seen:
                        results['issues'].append(
                            f"Row {i}: Duplicate primary key value: {pk_value}"
                        )
                        results['is_valid'] = False
                    seen.add(pk_value)
            
            # Check 4: Check foreign key constraints
            if table_name in db_instance.foreign_keys:
                for fk in db_instance.foreign_keys[table_name]:
                    column = fk['column']
                    ref_table = fk['ref_table']
                    ref_column = fk['ref_column']
                    
                    # Get all referenced values
                    ref_rows = db_instance.select(ref_table, columns=[ref_column])
                    ref_values = {row[ref_column] for row in ref_rows if ref_column in row}
                    
                    # Check each row
                    for i, row in enumerate(rows):
                        fk_value = row.get(column)
                        if fk_value is not None and fk_value not in ref_values:
                            results['issues'].append(
                                f"Row {i}: Foreign key violation: {column}={fk_value} "
                                f"references non-existent {ref_table}.{ref_column}"
                            )
                            results['is_valid'] = False
            
        except Exception as e:
            results['issues'].append(f"Error checking integrity: {str(e)}")
            results['is_valid'] = False
        
        return results
    
    @staticmethod
    def repair_table(db_instance, table_name: str, backup: bool = True) -> bool:
        """
        Attempt to repair a corrupted table
        
        Args:
            db_instance: ELDB instance
            table_name: Table name to repair
            backup: Whether to create backup before repair
            
        Returns:
            bool: True if repair was attempted
        """
        try:
            if backup:
                # Create backup
                backup_path = os.path.join(db_instance.db_folder, 
                                         f"{table_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.eldb")
                import shutil
                original_path = os.path.join(db_instance.db_folder, f"{table_name}.eldb")
                shutil.copy2(original_path, backup_path)
                print(f"Backup created: {backup_path}")
            
            # Reload table and rebuild
            if table_name in db_instance.tables:
                del db_instance.tables[table_name]
            
            db_instance.load_table(table_name)
            rows = db_instance._read_rows(db_instance.tables[table_name])
            db_instance._save_rows(table_name, rows)
            
            print(f"Table '{table_name}' repaired")
            return True
            
        except Exception as e:
            print(f"Repair failed: {e}")
            return False
    
    # ----------------- Formatting Utilities -----------------
    @staticmethod
    def format_results(results: List[Dict], max_width: int = 80) -> str:
        """
        Format query results as a pretty table string
        
        Args:
            results: List of dictionaries
            max_width: Maximum width of output
            
        Returns:
            str: Formatted table
        """
        if not results:
            return "No results"
        
        # Get all column names
        columns = list(results[0].keys())
        
        # Calculate column widths
        col_widths = {}
        for col in columns:
            # Column name width
            name_len = len(str(col))
            # Max data width in this column
            data_len = max(len(str(row.get(col, ''))) for row in results)
            col_widths[col] = min(max(name_len, data_len) + 2, max_width // len(columns))
        
        # Build header
        header = "|"
        separator = "+"
        for col in columns:
            width = col_widths[col]
            header += f" {col:<{width-2}} |"
            separator += f"{'-'*width}+"
        
        # Build rows
        rows_str = ""
        for row in results:
            row_line = "|"
            for col in columns:
                width = col_widths[col]
                value = str(row.get(col, ''))
                if len(value) > width - 2:
                    value = value[:width-5] + "..."
                row_line += f" {value:<{width-2}} |"
            rows_str += row_line + "\n"
        
        return f"{separator}\n{header}\n{separator}\n{rows_str}{separator}"
    
    @staticmethod
    def export_schema(db_instance, output_file: str = None) -> Dict:
        """
        Export database schema as JSON
        
        Args:
            db_instance: ELDB instance
            output_file: Optional file to save schema to
            
        Returns:
            Dict: Schema dictionary
        """
        schema = {
            'database': db_instance.db_folder,
            'tables': {},
            'foreign_keys': db_instance.foreign_keys
        }
        
        # Load all tables
        for f in os.listdir(db_instance.db_folder):
            if f.endswith('.eldb'):
                table_name = f[:-5]
                try:
                    if table_name not in db_instance.tables:
                        db_instance.load_table(table_name)
                    
                    table = db_instance.tables[table_name]
                    schema['tables'][table_name] = {
                        'columns': table['header']['columns'],
                        'primary_key': table['header'].get('primary_key'),
                        'row_count': table['header'].get('row_count', 0)
                    }
                except:
                    schema['tables'][table_name] = {'error': 'Could not load table'}
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(schema, f, indent=2)
            print(f"Schema exported to {output_file}")
        
        return schema
    
    @staticmethod
    def print_database_info(db_instance):
        """
        Print database information in a human-readable format
        """
        stats = ELDBUtils.get_database_stats(db_instance.db_folder)
        
        print(f"\n{'='*60}")
        print(f"ELDB DATABASE: {db_instance.db_folder}")
        print(f"{'='*60}")
        print(f"Total Tables: {stats['total_tables']}")
        print(f"Total Rows: {stats['total_rows']:,}")
        print(f"Total Size: {stats['total_size_bytes']:,} bytes ({stats['total_size_bytes']/1024:.1f} KB)")
        print(f"{'='*60}")
        
        if stats['tables']:
            print("\nTABLES:")
            print("-" * 60)
            print(f"{'Table':<20} {'Rows':>10} {'Size (KB)':>12} {'Path':<30}")
            print("-" * 60)
            
            for table_name, table_info in stats['tables'].items():
                size_kb = table_info['size_bytes'] / 1024
                print(f"{table_name:<20} {table_info['rows']:>10,} {size_kb:>12.1f} {table_info['path'][-30:]:<30}")
        
        if db_instance.foreign_keys:
            print(f"\nFOREIGN KEYS:")
            print("-" * 60)
            for table_name, fks in db_instance.foreign_keys.items():
                for fk in fks:
                    print(f"{table_name}.{fk['column']} -> {fk['ref_table']}.{fk['ref_column']} ({fk['on_delete']})")
        
        print(f"{'='*60}\n")


# Shortcut functions for common operations
def export_table_to_csv(db_instance, table_name: str, output_csv: str = None) -> bool:
    """Shortcut to export table to CSV"""
    table_path = os.path.join(db_instance.db_folder, f"{table_name}.eldb")
    return ELDBUtils.export_to_csv(table_path, output_csv)

def import_csv_to_table(db_instance, csv_path: str, table_name: str, **kwargs) -> bool:
    """Shortcut to import CSV to table"""
    return ELDBUtils.import_from_csv(csv_path, db_instance, table_name, **kwargs)

def get_table_stats(db_instance, table_name: str) -> Dict:
    """Shortcut to get table statistics"""
    stats = ELDBUtils.get_database_stats(db_instance.db_folder)
    return stats['tables'].get(table_name, {})

def pretty_print(results: List[Dict], max_width: int = 80) -> None:
    """Shortcut to pretty print query results"""
    print(ELDBUtils.format_results(results, max_width))

__all__ = ["get_table_stats", "pretty_print", "import_csv_to_table", "ELDBUtils"]