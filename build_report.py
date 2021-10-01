class BuildReport:
    def __init__(self, indent_size=2, add_new_line=False):
        self.buffer = ''
        self.indent = 0
        self.indent_size = indent_size
        self.indent_str = ''
        self.add_new_line = add_new_line
        # self.table_indent = 0
        # self.table_field_count = 0
        # self.table_field_widths = []
        # self.table_field_format = ''
        # self.table_defs = []

    def set_indent(self, indent=None, permanent=False):
        if indent is None:
            return self.indent_str

        this_indent = self.indent
        if isinstance(indent, str):
            if indent[0] == '-':
                temp_val = int(indent[1:])
                this_indent = this_indent - temp_val
                if this_indent < 0:
                    this_indent = 0

            elif indent[0] == '+':
                temp_val = int(indent[1:])
                this_indent = this_indent + temp_val

            else:
                this_indent = int(indent)

        elif isinstance(indent, int):
            this_indent = int(indent)

        indent_str = this_indent * self.indent_size * ' '

        if permanent is True:
            self.indent = this_indent
            self.indent_str = indent_str

        return indent_str

    def add_line(self, line, indent=None, add_new_line=None):
        indent_str = self.set_indent(indent)
        new_line = ''
        if add_new_line is True or (add_new_line is False and self.add_new_line is True):
            new_line = '\n'

        self.buffer = self.buffer + indent_str + line + new_line

    def add_table(self, list_of_lists=None, list_of_dicts=None, indent=None, headers=None, border=False):
        field_info = []
        table_format, separator, table_data = self.calc_widths(field_info, list_of_lists=list_of_lists,
                                                               list_of_dicts=list_of_dicts, headers=headers,
                                                               border=border)
        if headers is not None:
            if border is True:
                self.add_line(separator, indent=indent)
            self.add_line(table_format % tuple(headers), indent=indent)

        if border is True:
            self.add_line(separator, indent=indent)

        for row in table_data:
            temp_row = []
            for field in row:
                temp_row.append(str(field))
            self.add_line(table_format % tuple(temp_row), indent=indent)

        if border is True:
            self.add_line(separator, indent=indent)

    def calc_widths(self, field_info, list_of_lists=None, list_of_dicts=None, headers=None, border=False,
                    delim=None):
        if delim is None:
            if border is True:
                delim = '|'
            else:
                delim = ' '

        if headers is not None:
            for header in headers:
                field_info.append({'width': len(header), 'align': ''})

        if list_of_lists is not None and list_of_dicts is not None:
            raise ValueError("list_of_lists and list_of_dicts can not be specified at the same time")
        elif list_of_lists is None and list_of_dicts is None:
            raise ValueError("either list_of_lists or list_of_dicts must be specified")
        elif list_of_lists is not None:
            table_data = list_of_lists
        elif list_of_dicts is not None:
            table_data = [(key, value) for key, value in list_of_dicts.items()]

        for row in table_data:
            idx = 0
            row_len = len(row)
            for field in row:
                idx += 1
                field_len = len(str(field))
                field_info_len = len(field_info)

                if isinstance(field, int) or isinstance(field, float):
                    align = ''
                else:
                    align = '-'

                # print("IDX=%d LEN=%d ROWLEN=%d FIELDLEN=%d" % (idx, len(field_info), row_len, field_len))
                if idx > field_info_len:
                    field_info.append({'width': field_len, 'align': align})
                else:
                    if align == '-' and field_info[idx - 1]['align'] == '':
                        field_info[idx - 1]['align'] = '-'

                    if field_info[idx - 1]['width'] < field_len:
                        field_info[idx - 1]['width'] = field_len

        if border is True:
            table_format = '|'
            separator = '|'
            padding = ' '
        else:
            table_format = ''
            separator = ''
            padding = ''

        for field in field_info:
            separator = separator + '-' + field['width'] * '-' + '-|'
            table_format = table_format + padding + '%' + field['align'] + str(field['width']) + 's' + padding + delim

        return table_format + '\n', separator + '\n', table_data


    # def define_table(self, field_formats, indent=None):
    #     self.set_indent()
    #     self.table_defs.clear()
    #     self.table_field_count = len(field_formats)
    #     self.table_field_widths.clear()
    #     for field in field_formats:
    #         self.table_defs.append(field)
    #
    # def add_table_row(self, fields, header=False):
    #     field_len = len(fields)
    #     if field_len != self.table_field_count:
    #         raise ValueError("Table fields passed in does not match current table (%d != %d)",
    #                          field_len, self.table_field_count)

    def get_buffer(self):
        return self.buffer
