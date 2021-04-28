from string import Template


def is_empty(string):
    empty = ['', None, chr(8203)]
    return string in empty


class Table:
    def __init__(self, name: str, foreign_key_num: int):
        self.id = 0
        self.name = name
        self.attributes = []
        self.defaults = []
        # 去重前
        self.data_rows_buffer = []
        # 去重后
        self.data_rows = []

        # 外键
        self.foreign_key = []
        # 外键数量
        self.foreign_key_num = foreign_key_num
        # 多次引入外键时每个外键的偏移量
        self.foreign_key_counter = [0 for i in range(self.foreign_key_num)]

        # sql结果
        self.sql = ""

    def add_id(self):
        self.attributes.append("id")
        self.defaults.append(0)
        self.id = 1

    def add_attr(self, name: str, default_value, is_foreign_key: bool):
        if self.attributes.count(name) > 0:
            self.defaults[self.attributes.index(name)] = default_value
            return

        self.attributes.append(name)
        self.defaults.append(default_value)

        if is_foreign_key:
            self.foreign_key.append(name)

    def link(self, attr: list, sheet, column: list, lst_range: tuple):
        assert len(attr) == len(column)

        begin = 0
        if self.id > 0:
            begin = 1
        for i in range(begin, begin + len(attr)):
            self.add_attr(attr[i - begin][0], attr[i - begin][1], attr[i - begin][2])

        for row in range(lst_range[0], lst_range[1] + 1):
            data_row = [0 for i in range(0, len(self.attributes))]
            for i in range(begin, begin + len(attr)):
                # column值为0则全部用default填充
                if column[i - begin] == 0:
                    data_row[i] = self.defaults[i - begin]
                    continue

                data_row[i] = sheet.cell(row, column[i - begin]).value
                if is_empty(data_row[i]):
                    data_row[i] = self.defaults[i - begin]

            self.data_rows_buffer.append(data_row)

    def reference(self, key_map: tuple, table, tar_attr: str, sheet, column: int, lst_range: tuple):
        this_key = key_map[0]
        tar_key = key_map[1]

        assert this_key in self.attributes
        assert tar_key in table.attributes
        assert tar_attr in table.attributes

        tar_attr_index = table.attributes.index(tar_attr)
        this_key_index = self.attributes.index(this_key)
        tar_key_index = table.attributes.index(tar_key)

        tar_attr_list = [row[tar_attr_index] for row in table.data_rows]

        for row in range(lst_range[0], lst_range[1] + 1):
            tar = sheet.cell(row, column).value

            assert not is_empty(tar)
            assert tar in tar_attr_list

            # 本表属性对应行号
            this_row_index = row - lst_range[0] + self.foreign_key_counter[self.foreign_key.index(this_key)]
            # 目标表属性对应行号
            tar_row_index = tar_attr_list.index(tar)

            self.data_rows[this_row_index][this_key_index] = table.data_rows[tar_row_index][tar_key_index]

        self.foreign_key_counter[self.foreign_key.index(this_key)] += (lst_range[1] - lst_range[0] + 1)

    def generate_id(self):
        # 生成id
        for data_row in self.data_rows:
            if "id" in self.attributes:
                data_row[self.attributes.index("id")] = self.id
                self.id += 1

    def unique(self, attr: list):
        # 将attr作为主键去重
        if len(attr) == 0:
            self.data_rows = self.data_rows_buffer
            self.generate_id()
            return

        attr_index = [self.attributes.index(a) for a in attr]
        tag = [True for i in range(0, len(self.data_rows_buffer))]

        for i in range(len(self.data_rows_buffer)):
            data_row = self.data_rows_buffer[i]
            attr_list1 = [data_row[index] for index in attr_index]

            for j in range(i + 1, len(self.data_rows_buffer)):
                data_row = self.data_rows_buffer[j]
                attr_list2 = [data_row[index] for index in attr_index]

                if attr_list1 == attr_list2:
                    tag[j] = False

        for i in range(len(self.data_rows_buffer)):
            if tag[i]:
                self.data_rows.append(self.data_rows_buffer[i])

        self.generate_id()

    def generate_sql(self):
        format = Template("insert into ${name} (${attr}) values (${value});")
        for data_row in self.data_rows:
            attr = ""
            for i in range(len(self.attributes)):
                attr += self.attributes[i]
                if i != len(self.attributes) - 1:
                    attr += ", "

            value = ""
            for i in range(len(data_row)):
                if type(data_row[i]) == str:
                    value += ("'" + data_row[i] + "'")
                else:
                    if data_row[i] is None:
                        value += "null"
                    else:
                        value += str(data_row[i])
                if i != len(data_row) - 1:
                    value += ", "

            sql = format.substitute(name=self.name,
                                    attr=attr,
                                    value=value)
            self.sql += sql + '\n'

    def get_sql(self):
        return self.sql
