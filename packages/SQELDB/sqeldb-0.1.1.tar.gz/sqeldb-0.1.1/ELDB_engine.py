import os
import struct

class ELDB:
    def __init__(self, db_folder='mydb'):
        self.db_folder = db_folder
        os.makedirs(db_folder, exist_ok=True)
        self.tables = {}

    # ----------------- Create Table -----------------
    def create_table(self, name, columns, primary_key=None, if_not_exists=False):
        table_path = os.path.join(self.db_folder, f"{name}.eldb")
        if os.path.exists(table_path):
            if if_not_exists:
                self.load_table(name)
                return
            else:
                raise ValueError("Table already exists")
        header = {'columns': columns, 'primary_key': primary_key, 'row_count': 0}
        with open(table_path, 'wb') as f:
            f.write(str(header).encode() + b'\n')
        self.tables[name] = {'path': table_path, 'header': header, 'index': {}}

    # ----------------- Load Table -----------------
    def load_table(self, table_name):
        table_path = os.path.join(self.db_folder, f"{table_name}.eldb")
        if not os.path.exists(table_path):
            raise ValueError(f"Table '{table_name}' does not exist")
        with open(table_path, 'rb') as f:
            header_line = f.readline()
            header = eval(header_line.decode())
        self.tables[table_name] = {'path': table_path, 'header': header, 'index': {}}
        self._build_index(table_name)  # build primary key index immediately

    
    def _build_index(self, table_name):
        table = self.tables[table_name]
        pk = table['header']['primary_key']
        if not pk:
            table['index'] = {}
            return
        rows = self._read_rows(table)
        index = {}
        for i, row in enumerate(rows):
            index[row[pk]] = i  # store row position in the list
        table['index'] = index
    # ----------------- Helper: Read All Rows -----------------
    def _read_rows(self, table):
        columns = table['header']['columns']
        row_size = sum([opts['size'] if opts['type']=='str' else 4 for opts in columns.values()])
        rows = []
        with open(table['path'], 'rb') as f:
            f.readline()  # skip header
            while True:
                data = f.read(row_size)
                if not data:
                    break
                row = {}
                offset = 0
                for col, opts in columns.items():
                    typ, size = opts['type'], opts['size']
                    if typ == 'int':
                        row[col] = struct.unpack('i', data[offset:offset+4])[0]
                        offset += 4
                    elif typ == 'str':
                        row[col] = data[offset:offset+size].rstrip(b'\x00').decode()
                        offset += size
                rows.append(row)
        return rows

    # ----------------- Save Rows -----------------
    def _save_rows(self, table_name, rows):
        table = self.tables[table_name]
        columns = table['header']['columns']
        with open(table['path'], 'wb') as f:
            f.write(str(table['header']).encode() + b'\n')
            for row in rows:
                bin_row = b''
                for col, opts in columns.items():
                    typ, size = opts['type'], opts['size']
                    val = row.get(col)
                    if typ == 'int':
                        bin_row += struct.pack('i', val if val is not None else 0)
                    elif typ == 'str':
                        b_val = (val.encode() if val else b'')[:size]
                        b_val += b'\x00' * (size - len(b_val))
                        bin_row += b_val
                f.write(bin_row)
        # rebuild index after saving
        self._build_index(table_name)

    
    # ----------------- Insert -----------------
    def insert(self, table_name, row):
        table = self.tables.get(table_name)
        if not table:
            self.load_table(table_name)
            table = self.tables[table_name]
        columns = table['header']['columns']

        for col, opts in columns.items():
            if col not in row:
                if not opts.get('nullable', True):
                    raise ValueError(f"Column '{col}' cannot be null")
                else:
                    row[col] = None
            else:
                typ = opts['type']
                val = row[col]
                if val is not None and ((typ == 'int' and not isinstance(val, int)) or
                                        (typ == 'str' and not isinstance(val, str))):
                    raise TypeError(f"Column '{col}' must be {typ}")

        rows = self._read_rows(table)
        rows.append(row)
        table['header']['row_count'] += 1
        self._save_rows(table_name, rows)

    # ----------------- Select -----------------
    def select(self, table_name=None, where=None, order_by=None, limit=None, columns=None):
        results = []

        tables_to_select = []
        if table_name:
            tables_to_select.append(table_name)
        else:
            tables_to_select = [f.split(".eldb")[0] for f in os.listdir(self.db_folder) if f.endswith('.eldb')]

        for tbl in tables_to_select:
            if tbl not in self.tables:
                self.load_table(tbl)
            table = self.tables[tbl]
            rows = self._read_rows(table)

            # Filter with WHERE
            if where:
                filtered = []
                for row in rows:
                    match = True
                    for k, (op, v) in where.items():
                        if op == '=' and not row[k] == v:
                            match = False
                        elif op == '!=' and not row[k] != v:
                            match = False
                        elif op == '>' and not row[k] > v:
                            match = False
                        elif op == '<' and not row[k] < v:
                            match = False
                        elif op == '>=' and not row[k] >= v:
                            match = False
                        elif op == '<=' and not row[k] <= v:
                            match = False
                    if match:
                        filtered.append(row)
                rows = filtered

            # ORDER BY
            if order_by:
                col, reverse = order_by
                rows.sort(key=lambda x: x[col], reverse=reverse)

            # LIMIT
            if limit:
                rows = rows[:limit]

            # Select only specific columns
            if columns:
                rows = [{col: row[col] for col in columns if col in row} for row in rows]

            results.extend(rows)
        return results

    # ----------------- Update -----------------
    def update(self, table_name, updates, where=None):
        table = self.tables.get(table_name)
        if not table:
            self.load_table(table_name)
            table = self.tables[table_name]
        rows = self._read_rows(table)
        for row in rows:
            match = True
            if where:
                for k, (op, v) in where.items():
                    if op == '=' and not row[k] == v:
                        match = False
                    elif op == '!=' and not row[k] != v:
                        match = False
                    elif op == '>' and not row[k] > v:
                        match = False
                    elif op == '<' and not row[k] < v:
                        match = False
                    elif op == '>=' and not row[k] >= v:
                        match = False
                    elif op == '<=' and not row[k] <= v:
                        match = False
            if match:
                for k, v in updates.items():
                    row[k] = v
        self._save_rows(table_name, rows)

    # ----------------- Delete -----------------
    def delete(self, table_name, where=None):
        table = self.tables.get(table_name)
        if not table:
            self.load_table(table_name)
            table = self.tables[table_name]
        rows = self._read_rows(table)
        new_rows = []
        for row in rows:
            keep = True
            if where:
                for k, (op, v) in where.items():
                    if op == '=' and row[k] == v:
                        keep = False
                    elif op == '!=' and row[k] != v:
                        keep = False
                    elif op == '>' and row[k] > v:
                        keep = False
                    elif op == '<' and row[k] < v:
                        keep = False
                    elif op == '>=' and row[k] >= v:
                        keep = False
                    elif op == '<=' and row[k] <= v:
                        keep = False
            if keep:
                new_rows.append(row)
        table['header']['row_count'] = len(new_rows)
        self._save_rows(table_name, new_rows)

    # ----------------- Delete Column -----------------
    def delete_column(self, table_name, column_name):
        table = self.tables.get(table_name)
        if not table:
            self.load_table(table_name)
            table = self.tables[table_name]
        if column_name not in table['header']['columns']:
            raise ValueError(f"Column '{column_name}' does not exist")
        del table['header']['columns'][column_name]
        rows = self._read_rows(table)
        for row in rows:
            if column_name in row:
                del row[column_name]
        self._save_rows(table_name, rows)

    # ----------------- Add Column -----------------
    def add_column(self, table_name, column_name, column_type='str', size=50, nullable=True, default=None):
        table = self.tables.get(table_name)
        if not table:
            self.load_table(table_name)
            table = self.tables[table_name]

        if column_name in table['header']['columns']:
            raise ValueError(f"Column '{column_name}' already exists in table '{table_name}'")

        table['header']['columns'][column_name] = {'type': column_type, 'size': size, 'nullable': nullable}

        rows = self._read_rows(table)
        for row in rows:
            row[column_name] = default
        self._save_rows(table_name, rows)
        print(f"Column '{column_name}' added to table '{table_name}'")

    # ----------------- Clear Table -----------------
    def clear_table(self, table_name):
        table = self.tables.get(table_name)
        if not table:
            self.load_table(table_name)
            table = self.tables[table_name]
        table['header']['row_count'] = 0
        self._save_rows(table_name, [])

    # ----------------- Delete Table -----------------
    def delete_table(self, table_name):
        table_path = os.path.join(self.db_folder, f"{table_name}.eldb")
        if os.path.exists(table_path):
            os.remove(table_path)
            if table_name in self.tables:
                del self.tables[table_name]
        else:
            print(f"Table '{table_name}' does not exist.")

    # ----------------- Drop All Tables -----------------
    def drop_all_tables(self):
        for f in os.listdir(self.db_folder):
            if f.endswith('.eldb'):
                os.remove(os.path.join(self.db_folder, f))
        self.tables = {}
