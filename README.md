# ExcelToSQL
一个根据自定义数据表表结构将Excel表转换成SQL插入语句的python脚本

</br>

数据库实践提供的数据全在*.xlsx文件里，程序员怎么能允许自己重复机械地插入数据呢（滑稽）

</br>

目前可读取*.xslx文件，其他后缀的Excel文件属于未测试内容
使用前须要先拆分已合并的单元格

# Document

## how to use

```python
import ExcelToSQL
```
#### notes:
 - 使用openpyxl

</br>

### is_empty(string: str) -> bool

参数为空则返回True
#### parameters:
 - string：一个字符串

</br>


### Table(): Object
#### attributes:
 - id: int：用于生成自增的id
 - name: str：表名
 - attributes: list：所有属性
 - defaults: list：属性对应的缺省值
 - data_rows_buffer: list：去重前（调用unique()之前）的数据列表
一个二维数组，每行数据与attributes一一对应
行数即为数据条数
 - data_rows: list：去重后，其他同上
 - foreign_key: list：标记是外键的属性
 - foreign_key_num: int：外键数量 
 - foreign_key_counter: list：多次引入外键时每个外键的偏移量
如从第一张sheet读入了5行数据，从第二张sheet读入了10行数据
第一次调用reference()时，用第一张sheet给前五行数据的外键赋值，从data_rows的第0行开始（0 + 该外键的对应的偏移量0）,赋值后偏移量为5
第二次调用reference()时，用第二张sheet给后十行数据的外键复制，从data_rows的第5行开始（0 + 该外键的偏移量5），赋值后偏移量为15
 - sql: str：存储生成的sql语句

</br>

#### methods:
### __init__(self, name: str, foreign_key_num: int)->None
初始化Table类
#### parameters:
 - name：表名
 - foreign_key_num：外键数量

</br>

### add_id(self)->None
增加属性id

</br>

### add_attr(self, name: str, default_value, is_foreign_key: bool)->None
增加一个属性
#### parameters:
 - name：属性名
 - default_value：默认值
 - is_foreign_key：True表示该属性是外键

</br>

### link(self, attr: list, sheet, column: list, lst_range: tuple)->None
将attr中的每个属性与excel中的某一列相关联，表示该属性对应这一列
#### parameters:
 - attr：数据表部分属性列表（真包含与self.attributes）
 - sheet：通过openpyxl库读取到的某excel文件的sheet
 - column：sheet列号列表，与attr一一对应，表示某属性对应sheet中的某一列
column内某元素为0时，表示其对应的属性全部用默认值填充
 - list_range：sheet行的范围

</br>

### reference(self, key_map: tuple, table, tar_attr: str, sheet, column: int, lst_range: tuple)->None
建立一个外键
#### parameters:
 - table：另一张表
 - key_map：（本表的某个属性a， table的某个属性b）
表示foreign key (a) references table (b)
 - tar_attr：目标属性
当b是一个代表，如table的id时，tar_attr就是真正建立外键的对象
若b就是真正建立外键的对象，则tar_attr == b
比如在redCross例子中，donation.office_id和office.id建立外键，但实际上office.id是office.name的代表
 - sheet：通过openpyxl库读取到的某excel文件的sheet
 - column：sheet列号列表，与attr一一对应，表示某属性对应sheet中的某一列
 - list_range：sheet行的范围

#### notes:
 - 必须在table调用unique()后调用，否则会产生非预期的结果
 - 注意若table有属性id，要在generate_id()后调用reference()，否则会产生非预期的结果

</br>

### generate_id(self)->None
#### notes:
 - 如果调用过属性中有id则生成自增的id（目前只支持自增）
 - 会在unique()中被调用

</br>

### unique(self, attr: list)->None
#### parameters:
根据选中的属性对数据进行去重，即若两条数据的这些属性全相同，则认为是两条相同的数据
#### parameters:
 - attr：数据表部分属性列表（真包含与self.attributes）
#### notes:
 - 注意要在所有数据插入后进行去重
 - 去重后数据表才算定义完成，即使不需要去重，也要调用

</br>

### generate_sql(self)->None
生成sql语句
#### notes:
 - 必须在调用了unique()后调用，否则会产生非预期的结果

</br>

### get_sql(self)->None
获取生成的sql语句
#### notes:
 - 必须在generate_sql()之后调用，否则会产生非预期的结果

</br>

## TODO:
支持在实例化表时设置主键，自动根据主键去重
且有诸多不完善，如unique()的复杂度过高，可以用set优化
