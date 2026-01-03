import os
import struct
import ast
from typing import Dict, List, Optional, Any, Union

class ELDB:
    def __init__(self, db_folder: str = 'mydb'):
        self.db_folder = db_folder
        os.makedirs(db_folder, exist_ok=True)
        self.tables: Dict[str, Dict] = {}
        self.foreign_keys: Dict[str, List[Dict]] = {}

    # ----------------- Helper: Safe Header Parsing -----------------
    def _parse_header(self, header_line: bytes) -> Dict:
        """Safely parse header using ast.literal_eval"""
        try:
            return ast.literal_eval(header_line.decode())
        except:
            return {}

    # ----------------- Create Table -----------------
    def create_table(self, name: str, columns: Dict, 
                     primary_key: Optional[str] = None, 
                     if_not_exists: bool = False):
        table_path = os.path.join(self.db_folder, f"{name}.eldb")
        
        if os.path.exists(table_path):
            if if_not_exists:
                self.load_table(name)
                return
            raise ValueError(f"Table '{name}' already exists")
        
        header = {
            'columns': columns,
            'primary_key': primary_key,
            'row_count': 0
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
        """Read rows with minimal memory usage using generator-style approach"""
        columns = table['header']['columns']
        
        # Calculate row size
        row_size = 0
        col_sizes = {}
        for col, opts in columns.items():
            if opts['type'] == 'int':
                size = 4
            else:
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
                    if opts['type'] == 'int':
                        row[col] = struct.unpack('i', data[offset:offset+4])[0]
                        offset += 4
                    else:  # 'str'
                        raw = data[offset:offset+size]
                        # Decode while preserving null bytes
                        text = ''
                        for b in raw:
                            if b == 0:
                                break
                            text += chr(b)
                        row[col] = text
                        offset += size
                rows.append(row)
        
        return rows

    # ----------------- Save Rows -----------------
    def _save_rows(self, table_name: str, rows: List[Dict]):
        table = self.tables[table_name]
        columns = table['header']['columns']
        
        with open(table['path'], 'wb') as f:
            f.write(str(table['header']).encode() + b'\n')
            
            for row in rows:
                bin_row = b''
                for col, opts in columns.items():
                    typ = opts['type']
                    size = opts['size'] if typ == 'str' else 4
                    val = row.get(col)
                    
                    if typ == 'int':
                        bin_row += struct.pack('i', val if val is not None else 0)
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
    def insert(self, table_name: str, row: Dict):
        if table_name not in self.tables:
            self.load_table(table_name)
        
        table = self.tables[table_name]
        columns = table['header']['columns']
        
        # Validate row structure and types
        for col, opts in columns.items():
            if col not in row:
                if not opts.get('nullable', True):
                    raise ValueError(f"Column '{col}' cannot be null")
                row[col] = None
            else:
                typ = opts['type']
                val = row[col]
                
                if val is not None:
                    if typ == 'int' and not isinstance(val, int):
                        raise TypeError(f"Column '{col}' must be int, got {type(val).__name__}")
                    elif typ == 'str' and not isinstance(val, str):
                        raise TypeError(f"Column '{col}' must be str, got {type(val).__name__}")
        
        # Validate foreign keys
        self._validate_foreign_key(table_name, row)
        
        # Check primary key uniqueness
        pk = table['header'].get('primary_key')
        if pk and pk in row and row[pk] is not None:
            if row[pk] in table['index']:
                raise ValueError(f"Duplicate primary key value: {row[pk]}")
        
        # Insert row
        rows = self._read_rows(table)
        rows.append(row)
        self._save_rows(table_name, rows)
        
        print(f"Row inserted into '{table_name}'")

    # ----------------- Select -----------------
    def select(self, table_name: Optional[str] = None, 
               where: Optional[Dict] = None, 
               order_by: Optional[tuple] = None,
               limit: Optional[int] = None,
               columns: Optional[List[str]] = None) -> List[Dict]:
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
               where: Optional[Dict] = None):
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
        
        self._save_rows(table_name, updated_rows)
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
        
        # Add to header
        table['header']['columns'][column_name] = {
            'type': column_type,
            'size': size,
            'nullable': nullable
        }
        
        # Update rows with default value
        rows = self._read_rows(table)
        for row in rows:
            row[column_name] = default
        
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

