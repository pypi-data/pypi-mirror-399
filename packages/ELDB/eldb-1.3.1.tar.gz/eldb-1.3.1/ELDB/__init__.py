import os
import struct
import ast
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

class ELDB:
    def __init__(self, db_name: str = 'mydb'):
        self.db_folder = db_name
        os.makedirs(db_name, exist_ok=True)
        self.tables: Dict[str, Dict] = {}
        self.foreign_keys: Dict[str, List[Dict]] = {}

    # ----------------- Helper: Safe Header Parsing -----------------
    def _parse_header(self, header_line: bytes) -> Dict:
        """Safely parse header using ast.literal_eval"""
        try:
            return ast.literal_eval(header_line.decode())
        except:
            return {}

    def table_path(self, table_name: str) -> str:
        """
        Get the full file path for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            str: Full path to the table file
        """
        return os.path.join(self.db_folder, f"{table_name}.eldb")

    # ----------------- Get Current Timestamp -----------------
    def _get_current_timestamp(self) -> int:
        """Get current timestamp as integer (seconds since epoch)"""
        return int(time.time())

    # ----------------- Format Timestamp -----------------
    def _format_timestamp(self, timestamp: Optional[int]) -> str:
        """Format timestamp for display"""
        if timestamp is None or timestamp == 0:
            return "NULL"
        try:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return str(timestamp)

    # ----------------- Create Table -----------------
    def create_table(self, name: str, columns: Dict, 
                     primary_key: Optional[str] = None, 
                     if_not_exists: bool = False,
                     auto_timestamps: bool = True):
        """
        Create a new table
        
        Args:
            name: Table name
            columns: Dictionary of column definitions
            primary_key: Optional primary key column name
            if_not_exists: If True, don't raise error if table exists
            auto_timestamps: If True, automatically add created_at and updated_at timestamps
        """
        table_path = os.path.join(self.db_folder, f"{name}.eldb")
        
        if os.path.exists(table_path):
            if if_not_exists:
                self.load_table(name)
                return
            raise ValueError(f"Table '{name}' already exists")
        
        # Add auto timestamp columns if enabled
        if auto_timestamps:
            columns['created_at'] = {'type': 'timestamp', 'size': 8, 'nullable': True, 'auto': True}
            columns['updated_at'] = {'type': 'timestamp', 'size': 8, 'nullable': True, 'auto': True}
        
        header = {
            'columns': columns,
            'primary_key': primary_key,
            'row_count': 0,
            'auto_timestamps': auto_timestamps
        }
        
        with open(table_path, 'wb') as f:
            f.write(str(header).encode() + b'\n')
        
        self.tables[name] = {
            'path': table_path,
            'header': header,
            'index': {}
        }
        print(f"Table '{name}' created successfully")

    # ----------------- Load Table -----------------
    def load_table(self, table_name: str):
        table_path = os.path.join(self.db_folder, f"{table_name}.eldb")
        
        if not os.path.exists(table_path):
            raise ValueError(f"Table '{table_name}' does not exist")
        
        with open(table_path, 'rb') as f:
            header_line = f.readline()
            header = self._parse_header(header_line)
        
        self.tables[table_name] = {
            'path': table_path,
            'header': header,
            'index': {}
        }
        
        # Build primary key index if exists
        if header.get('primary_key'):
            self._build_index(table_name)

    # ----------------- Build Index -----------------
    def _build_index(self, table_name: str):
        table = self.tables[table_name]
        pk = table['header'].get('primary_key')
        if not pk:
            table['index'] = {}
            return
        
        rows = self._read_rows(table)
        index = {}
        for i, row in enumerate(rows):
            index[row[pk]] = i
        table['index'] = index

    # ----------------- Read Rows -----------------
    def _read_rows(self, table: Dict) -> List[Dict]:
        """Read rows with minimal memory usage"""
        columns = table['header']['columns']
        
        # Calculate row size
        row_size = 0
        col_sizes = {}
        for col, opts in columns.items():
            if opts['type'] == 'int':
                size = 4
            elif opts['type'] == 'timestamp':
                size = 8
            else:  # 'str'
                size = opts['size']
            col_sizes[col] = size
            row_size += size
        
        rows = []
        with open(table['path'], 'rb') as f:
            f.readline()  # Skip header
            
            while True:
                data = f.read(row_size)
                if not data:
                    break
                
                row = {}
                offset = 0
                for col, opts in columns.items():
                    size = col_sizes[col]
                    typ = opts['type']
                    
                    if typ == 'int':
                        row[col] = struct.unpack('i', data[offset:offset+4])[0]
                        offset += 4
                    elif typ == 'timestamp':
                        # Read as 8-byte signed integer (int64)
                        val = struct.unpack('q', data[offset:offset+8])[0]
                        # Convert 0 to None
                        row[col] = val if val != 0 else None
                        offset += 8
                    else:  # 'str'
                        raw = data[offset:offset+size]
                        # Decode while preserving null bytes
                        text = ''
                        for b in raw:
                            if b == 0:
                                break
                            text += chr(b)
                        row[col] = text if text else None
                        offset += size
                rows.append(row)
        
        return rows

    # ----------------- Save Rows -----------------
    def _save_rows(self, table_name: str, rows: List[Dict], update_timestamps: bool = True):
        """
        Save rows to table
        
        Args:
            table_name: Name of the table
            rows: List of rows to save
            update_timestamps: Whether to update timestamps for auto columns
        """
        table = self.tables[table_name]
        columns = table['header']['columns']
        
        # Get current timestamp for auto updates
        current_time = self._get_current_timestamp() if update_timestamps else 0
        
        with open(table['path'], 'wb') as f:
            f.write(str(table['header']).encode() + b'\n')
            
            for row in rows:
                bin_row = b''
                for col, opts in columns.items():
                    typ = opts['type']
                    size = opts.get('size', 0) if typ == 'str' else (4 if typ == 'int' else 8)
                    val = row.get(col)
                    
                    # Handle auto timestamp columns
                    if opts.get('auto', False) and update_timestamps:
                        if col == 'created_at' and (val is None or val == 0):
                            # Only set created_at if it's None or 0 (new row)
                            val = current_time
                        elif col == 'updated_at':
                            # Always update updated_at when saving
                            val = current_time
                    
                    if typ == 'int':
                        bin_row += struct.pack('i', val if val is not None else 0)
                    elif typ == 'timestamp':
                        # Store as 8-byte signed integer (int64)
                        bin_row += struct.pack('q', val if val is not None else 0)
                    else:  # 'str'
                        if val is None:
                            b_val = b'\x00' * size
                        else:
                            encoded = val.encode('utf-8', errors='ignore')[:size-1]
                            b_val = encoded + b'\x00' * (size - len(encoded))
                        bin_row += b_val
                f.write(bin_row)
        
        # Update row count and rebuild index
        table['header']['row_count'] = len(rows)
        self._build_index(table_name)

    # ----------------- Add Foreign Key -----------------
    def add_foreign_key(self, table_name: str, column: str, 
                       ref_table: str, ref_column: str, 
                       on_delete: str = 'RESTRICT'):
        """Add foreign key constraint (simulated)"""
        if table_name not in self.tables:
            self.load_table(table_name)
        
        # Verify column exists
        if column not in self.tables[table_name]['header']['columns']:
            raise ValueError(f"Column '{column}' doesn't exist in table '{table_name}'")
        
        # Verify referenced table exists
        if ref_table not in self.tables:
            self.load_table(ref_table)
        
        if ref_column not in self.tables[ref_table]['header']['columns']:
            raise ValueError(f"Column '{ref_column}' doesn't exist in table '{ref_table}'")
        
        # Initialize foreign keys dict if needed
        if table_name not in self.foreign_keys:
            self.foreign_keys[table_name] = []
        
        # Check for duplicate foreign key
        for fk in self.foreign_keys[table_name]:
            if fk['column'] == column:
                raise ValueError(f"Foreign key already exists on column '{column}'")
        
        self.foreign_keys[table_name].append({
            'column': column,
            'ref_table': ref_table,
            'ref_column': ref_column,
            'on_delete': on_delete.upper()  # RESTRICT, CASCADE
        })
        
        print(f"Foreign key added: {table_name}.{column} -> {ref_table}.{ref_column}")

    # ----------------- Validate Foreign Key -----------------
    def _validate_foreign_key(self, table_name: str, row: Dict):
        """Validate all foreign key constraints for a row"""
        if table_name not in self.foreign_keys:
            return
        
        for fk in self.foreign_keys[table_name]:
            column = fk['column']
            ref_table = fk['ref_table']
            ref_column = fk['ref_column']
            
            # Skip if column value is None (nullable foreign key)
            if column not in row or row[column] is None:
                continue
            
            fk_value = row[column]
            
            # Check if referenced value exists
            try:
                ref_rows = self.select(ref_table, where={ref_column: ('=', fk_value)}, limit=1)
                if not ref_rows:
                    raise ValueError(
                        f"Foreign key violation: {table_name}.{column}={fk_value} "
                        f"references non-existent {ref_table}.{ref_column}"
                    )
            except ValueError:
                # Table doesn't exist yet (might be created later)
                pass

    # ----------------- Insert -----------------
    def insert(self, table_name: str, row: Dict, auto_timestamps: bool = True):
        """
        Insert a row into a table
        
        Args:
            table_name: Name of the table
            row: Dictionary with column values
            auto_timestamps: Whether to automatically set timestamp columns
        """
        if table_name not in self.tables:
            self.load_table(table_name)
        
        table = self.tables[table_name]
        columns = table['header']['columns']
        
        # Create a copy of row to avoid modifying the original
        row_to_insert = row.copy()
        
        # Validate row structure and types for non-auto columns
        for col, opts in columns.items():
            # Skip auto columns - they will be handled by _save_rows
            if opts.get('auto', False):
                continue
                
            if col not in row_to_insert:
                if not opts.get('nullable', True):
                    raise ValueError(f"Column '{col}' cannot be null")
                row_to_insert[col] = None
            else:
                typ = opts['type']
                val = row_to_insert[col]
                
                if val is not None:
                    if typ == 'int' and not isinstance(val, int):
                        raise TypeError(f"Column '{col}' must be int, got {type(val).__name__}")
                    elif typ == 'timestamp' and not isinstance(val, int):
                        raise TypeError(f"Column '{col}' must be timestamp (int), got {type(val).__name__}")
                    elif typ == 'str' and not isinstance(val, str):
                        raise TypeError(f"Column '{col}' must be str, got {type(val).__name__}")
        
        # Validate foreign keys
        self._validate_foreign_key(table_name, row_to_insert)
        
        # Check primary key uniqueness
        pk = table['header'].get('primary_key')
        if pk and pk in row_to_insert and row_to_insert[pk] is not None:
            if row_to_insert[pk] in table['index']:
                raise ValueError(f"Duplicate primary key value: {row_to_insert[pk]}")
        
        # Insert row
        rows = self._read_rows(table)
        rows.append(row_to_insert)
        self._save_rows(table_name, rows, update_timestamps=auto_timestamps)
        
        print(f"Row inserted into '{table_name}'")

    # ----------------- Select -----------------
    def select(self, table_name: Optional[str] = None, 
               where: Optional[Dict] = None, 
               order_by: Optional[tuple] = None,
               limit: Optional[int] = None,
               columns: Optional[List[str]] = None,
               format_timestamps: bool = True) -> List[Dict]:
        """
        Select rows from table(s)
        
        Args:
            table_name: Name of the table (None for all tables)
            where: WHERE conditions as {column: (operator, value)}
            order_by: (column, reverse) tuple for ordering
            limit: Maximum number of rows to return
            columns: List of columns to return (None for all)
            format_timestamps: Whether to format timestamp values as strings
            
        Returns:
            List of rows as dictionaries
        """
        results = []
        
        # Determine which tables to query
        if table_name:
            tables = [table_name]
        else:
            tables = [f[:-5] for f in os.listdir(self.db_folder) 
                     if f.endswith('.eldb')]
        
        for tbl in tables:
            if tbl not in self.tables:
                self.load_table(tbl)
            
            table = self.tables[tbl]
            rows = self._read_rows(table)
            
            # Format timestamps if requested
            if format_timestamps:
                formatted_rows = []
                for row in rows:
                    formatted_row = row.copy()
                    for col, val in row.items():
                        col_def = table['header']['columns'].get(col, {})
                        if col_def.get('type') == 'timestamp' and val is not None:
                            formatted_row[col] = self._format_timestamp(val)
                    formatted_rows.append(formatted_row)
                rows = formatted_rows
            
            # Apply WHERE clause
            if where:
                filtered = []
                for row in rows:
                    match = True
                    for col, (op, val) in where.items():
                        row_val = row.get(col)
                        
                        if op == '=' and row_val != val:
                            match = False
                        elif op == '!=' and row_val == val:
                            match = False
                        elif op == '>' and not (row_val > val):
                            match = False
                        elif op == '<' and not (row_val < val):
                            match = False
                        elif op == '>=' and not (row_val >= val):
                            match = False
                        elif op == '<=' and not (row_val <= val):
                            match = False
                        
                        if not match:
                            break
                    
                    if match:
                        filtered.append(row)
                rows = filtered
            
            # Apply ORDER BY
            if order_by:
                col, reverse = order_by
                rows.sort(key=lambda x: x.get(col), reverse=reverse)
            
            # Apply LIMIT
            if limit:
                rows = rows[:limit]
            
            # Select specific columns
            if columns:
                rows = [{col: row[col] for col in columns if col in row} 
                       for row in rows]
            
            results.extend(rows)
        
        return results

    # ----------------- Update -----------------
    def update(self, table_name: str, updates: Dict, 
               where: Optional[Dict] = None, auto_timestamps: bool = True):
        """
        Update rows in a table
        
        Args:
            table_name: Name of the table
            updates: Dictionary of column updates
            where: WHERE conditions
            auto_timestamps: Whether to automatically update timestamp columns
        """
        if table_name not in self.tables:
            self.load_table(table_name)
        
        table = self.tables[table_name]
        rows = self._read_rows(table)
        updated_rows = []
        
        for row in rows:
            # Check WHERE condition
            match = True
            if where:
                for col, (op, val) in where.items():
                    row_val = row.get(col)
                    
                    if op == '=' and row_val != val:
                        match = False
                    elif op == '!=' and row_val == val:
                        match = False
                    elif op == '>' and not (row_val > val):
                        match = False
                    elif op == '<' and not (row_val < val):
                        match = False
                    elif op == '>=' and not (row_val >= val):
                        match = False
                    elif op == '<=' and not (row_val <= val):
                        match = False
                    
                    if not match:
                        break
            
            # Apply updates if row matches
            if match:
                # Create updated row
                updated_row = row.copy()
                for col, new_val in updates.items():
                    updated_row[col] = new_val
                
                # Validate foreign keys for updated row
                self._validate_foreign_key(table_name, updated_row)
                updated_rows.append(updated_row)
            else:
                updated_rows.append(row)
        
        self._save_rows(table_name, updated_rows, update_timestamps=auto_timestamps)
        print(f"Table '{table_name}' updated")

    # ----------------- Delete -----------------
    def delete(self, table_name: str, where: Optional[Dict] = None):
        if table_name not in self.tables:
            self.load_table(table_name)
        
        table = self.tables[table_name]
        rows = self._read_rows(table)
        
        # Find rows to delete
        rows_to_delete = []
        rows_to_keep = []
        
        for row in rows:
            keep = True
            
            if where:
                for col, (op, val) in where.items():
                    row_val = row.get(col)
                    
                    if op == '=' and row_val == val:
                        keep = False
                    elif op == '!=' and row_val != val:
                        keep = False
                    elif op == '>' and row_val > val:
                        keep = False
                    elif op == '<' and row_val < val:
                        keep = False
                    elif op == '>=' and row_val >= val:
                        keep = False
                    elif op == '<=' and row_val <= val:
                        keep = False
                    
                    if not keep:
                        break
            
            if keep:
                rows_to_keep.append(row)
            else:
                rows_to_delete.append(row)
        
        # Handle cascading deletes
        if table_name in self.foreign_keys:
            for fk in self.foreign_keys[table_name]:
                if fk.get('on_delete') == 'CASCADE':
                    for row in rows_to_delete:
                        ref_value = row[fk['ref_column']] if fk['ref_column'] in row else None
                        if ref_value is not None:
                            # Find tables that reference this table
                            for other_table, other_fks in self.foreign_keys.items():
                                if other_table == table_name:
                                    continue
                                for other_fk in other_fks:
                                    if (other_fk['ref_table'] == table_name and 
                                        other_fk['ref_column'] == fk['ref_column']):
                                        # Delete referencing rows
                                        self.delete(other_table, 
                                                   where={other_fk['column']: ('=', ref_value)})
        
        # Save remaining rows
        self._save_rows(table_name, rows_to_keep)
        print(f"Deleted {len(rows_to_delete)} rows from '{table_name}'")

    # ----------------- Delete Column -----------------
    def delete_column(self, table_name: str, column_name: str):
        if table_name not in self.tables:
            self.load_table(table_name)
        
        table = self.tables[table_name]
        
        if column_name not in table['header']['columns']:
            raise ValueError(f"Column '{column_name}' doesn't exist")
        
        # Can't delete auto timestamp columns if they're part of auto_timestamps
        if table['header'].get('auto_timestamps', False) and column_name in ['created_at', 'updated_at']:
            raise ValueError(f"Cannot delete auto timestamp column '{column_name}'. Disable auto_timestamps first.")
        
        # Remove from header
        del table['header']['columns'][column_name]
        
        # Update rows
        rows = self._read_rows(table)
        for row in rows:
            if column_name in row:
                del row[column_name]
        
        self._save_rows(table_name, rows)
        print(f"Column '{column_name}' deleted from '{table_name}'")

    # ----------------- Add Column -----------------
    def add_column(self, table_name: str, column_name: str, 
               column_type: str = 'str', size: int = 50, 
               nullable: bool = True, default: Any = None):
        if table_name not in self.tables:
            self.load_table(table_name)
        
        table = self.tables[table_name]
        
        if column_name in table['header']['columns']:
            raise ValueError(f"Column '{column_name}' already exists")
        
        # Read existing rows BEFORE modifying the header
        rows = self._read_rows(table)
        
        # Validate column type
        if column_type not in ['int', 'str', 'timestamp']:
            raise ValueError(f"Invalid column type '{column_type}'. Must be 'int', 'str', or 'timestamp'")
        
        # Set appropriate size for timestamp
        if column_type == 'timestamp':
            size = 8
        
        # Now add the column to header
        table['header']['columns'][column_name] = {
            'type': column_type,
            'size': size,
            'nullable': nullable
        }
        
        # Add default value to each row
        for row in rows:
            row[column_name] = default
        
        # Save with new structure
        self._save_rows(table_name, rows)
        print(f"Column '{column_name}' added to '{table_name}'")

    # ----------------- Clear Table -----------------
    def clear_table(self, table_name: str):
        if table_name not in self.tables:
            self.load_table(table_name)
        
        table = self.tables[table_name]
        
        # Handle foreign key constraints
        if table_name in self.foreign_keys:
            for fk in self.foreign_keys[table_name]:
                if fk.get('on_delete') == 'RESTRICT':
                    raise ValueError(
                        f"Cannot clear table '{table_name}' due to RESTRICT foreign key constraint "
                        f"from '{fk['ref_table']}.{fk['ref_column']}'"
                    )
        
        # Clear all rows
        self._save_rows(table_name, [])
        print(f"Table '{table_name}' cleared")

    # ----------------- Delete Table -----------------
    def delete_table(self, table_name: str, cascade: bool = False):
        table_path = os.path.join(self.db_folder, f"{table_name}.eldb")
        
        if not os.path.exists(table_path):
            raise ValueError(f"Table '{table_name}' doesn't exist")
        
        # Check foreign key references
        for other_table, fks in self.foreign_keys.items():
            for fk in fks:
                if fk['ref_table'] == table_name:
                    if not cascade:
                        raise ValueError(
                            f"Cannot delete table '{table_name}' - referenced by "
                            f"'{other_table}.{fk['column']}'. Use cascade=True to force delete."
                        )
        
        # Remove table
        os.remove(table_path)
        if table_name in self.tables:
            del self.tables[table_name]
        
        # Remove foreign keys referencing this table
        self.foreign_keys = {
            tbl: [fk for fk in fks if fk['ref_table'] != table_name]
            for tbl, fks in self.foreign_keys.items() if tbl != table_name
        }
        
        print(f"Table '{table_name}' deleted")

    # ----------------- Drop All Tables -----------------
    def drop_all_tables(self, cascade: bool = False):
        for f in os.listdir(self.db_folder):
            if f.endswith('.eldb'):
                table_name = f[:-5]
                try:
                    self.delete_table(table_name, cascade)
                except ValueError as e:
                    if not cascade:
                        raise
        
        self.tables = {}
        self.foreign_keys = {}
        print("All tables dropped")

    # ----------------- Get Foreign Keys -----------------
    def get_foreign_keys(self, table_name: Optional[str] = None) -> Dict:
        """Get foreign key information"""
        if table_name:
            return self.foreign_keys.get(table_name, [])
        return self.foreign_keys

    # ----------------- Compact Database -----------------
    def compact(self):
        """Compact database by rebuilding all tables"""
        for table_name in list(self.tables.keys()):
            if table_name in self.tables:
                rows = self._read_rows(self.tables[table_name])
                self._save_rows(table_name, rows)
        
        print("Database compacted")

    # ----------------- Get Table Info -----------------
    def get_table_info(self, table_name: str) -> Dict:
        """Get detailed information about a table"""
        if table_name not in self.tables:
            self.load_table(table_name)
        
        table = self.tables[table_name]
        info = {
            'name': table_name,
            'path': table['path'],
            'columns': table['header']['columns'],
            'primary_key': table['header'].get('primary_key'),
            'row_count': table['header'].get('row_count', 0),
            'auto_timestamps': table['header'].get('auto_timestamps', False),
            'foreign_keys': self.foreign_keys.get(table_name, [])
        }
        
        # Add formatted column info
        formatted_columns = {}
        for col, col_def in info['columns'].items():
            formatted_columns[col] = {
                'type': col_def['type'],
                'size': col_def.get('size', 'N/A'),
                'nullable': col_def.get('nullable', True),
                'auto': col_def.get('auto', False)
            }
        info['formatted_columns'] = formatted_columns
        
        return info

    # ----------------- Set Auto Timestamps -----------------
    def set_auto_timestamps(self, table_name: str, enable: bool = True):
        """Enable or disable auto timestamps for a table"""
        if table_name not in self.tables:
            self.load_table(table_name)
        
        table = self.tables[table_name]
        
        if enable:
            # Add timestamp columns if they don't exist
            if 'created_at' not in table['header']['columns']:
                table['header']['columns']['created_at'] = {
                    'type': 'timestamp', 
                    'size': 8, 
                    'nullable': True, 
                    'auto': True
                }
            if 'updated_at' not in table['header']['columns']:
                table['header']['columns']['updated_at'] = {
                    'type': 'timestamp', 
                    'size': 8, 
                    'nullable': True, 
                    'auto': True
                }
            
            # Update all existing rows with timestamps
            rows = self._read_rows(table)
            current_time = self._get_current_timestamp()
            for row in rows:
                if row.get('created_at') is None or row.get('created_at') == 0:
                    row['created_at'] = current_time
                row['updated_at'] = current_time
            
            self._save_rows(table_name, rows)
        else:
            # Remove auto flag from timestamp columns
            for col in ['created_at', 'updated_at']:
                if col in table['header']['columns']:
                    if 'auto' in table['header']['columns'][col]:
                        del table['header']['columns'][col]['auto']
        
        table['header']['auto_timestamps'] = enable
        print(f"Auto timestamps {'enabled' if enable else 'disabled'} for '{table_name}'")