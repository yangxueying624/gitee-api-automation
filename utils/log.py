import logging
import os
from datetime import datetime

"""
os.path.dirname：去掉最后一级内容
os.path.join：拼接路径

__file__: Python的内置变量，表示当前代码文件自身的绝对路径：D:/Pycharm/Gitee_api_test/utils/log.py
第一次调用os.path.dirname(__file__)：D:/Pycharm/Gitee_api_test/utils
第二次调用os.path.dirname(...): ：D:/Pycharm/Gitee_api_test
os.path.join(path1,path2): 
拼接两个路径（自动处理不同系统的路径分隔符，如Windows的\和linux的/）：D:/Pycharm/Gitee_api_test/logs
"""
# 日志保存路径（在utils同级新建文件夹，存放日志文件）
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

"""
os.path.exists(log_dir)：判断路径是否存在，返回True或False
os.makedirs()：递归创建[文件夹]（如果父目录不存在也会一起创建，避免报错）
"""
if  not os.path.exists(log_dir):
    os.makedirs(log_dir)

"""
在Python中，并非所有类的方法都需要创建实例才能调用。类方法（@classmethod）和静态方法（@staticmethod）可以直接通过类本身调用，不需要创建实例
方法的类型决定了调用的方式：
（1）实例方法：方法需要用 self 访问实例属性，必须通过实例调用(obj.method())
class Person:
    def __init__(self, name, age):
        self.name = name  # 实例属性（实例状态的一部分）
        self.age = age
    # 实例方法：依赖实例状态（需要访问 self.name 和 self.age）
    def introduce(self):
        return f"我叫{self.name}，今年{self.age}岁"
p1 = Person("张三", 20)
print(p1.introduce())  # 必须通过实例调用，因为需要 p1 的 name 和 age


（2）类方法：用@classmethod装饰，方法需要用 cls 访问类属性，直接通过类调用(class.method())
class School:
    student_count = 0  # 类属性（类的状态的一部分，所有实例共享）
    def __init__(self, name):
        self.name = name  # 实例属性
    # 类方法：依赖类的状态（需要访问和修改 cls.student_count）
    @classmethod
    def add_student(cls):
        cls.student_count += 1  # 修改类属性（类的状态）
# 直接通过类调用，修改类的状态
School.add_student()
School.add_student()
print(School.student_count)  # 输出：2（类的状态被修改）


（3）静态方法：用@staticmethod装饰，方法不需要访问任何类属性或实例属性，仅靠输入参数即可工作
class MathUtils:
    # 静态方法：不依赖类或实例的状态（不需要 self 或 cls 参数）
    @staticmethod
    def add(a, b):
        return a + b  # 仅依赖输入参数，与类/实例无关
# 可以通过类直接调用，也可以通过实例调用（但没必要）
print(MathUtils.add(2, 3))  # 输出：5
"""

"""
datetime.now()：datetime类的[类方法]（不用先创建实例，直接通过类调用），作用是 “获取当前时间”，返回一个 datetime 实例
strftime('%Y-%m-%d')：将时间格式化为字符串
"""
# 定义日志文件路径  D:\Pycharm\Gitee_api_test\logs\2025-11-01.log
log_file=os.path.join(log_dir,f"{datetime.now().strftime('%Y-%m-%d')}.log")


"""
logging.basicConfig()：用于配置日志基础参数
level=logging.INFO：日志级别（DEBUG<INFO<WARNING<ERROR<CRITICAL）,表示只会记录INFO以上级别的日志

%(xxx)s：是日志模块预定义的占位符
%(asctime)s：日志产生的时间
%(levelname)s：日志级别
%(message)s：日志的具体内容（用logging.info("xxx")传入的字符串）
"""
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),  # 把日志写入log_file指定的文件
        logging.StreamHandler(stream=open("CON", "w", encoding="utf-8"))       # 把日志输出到控制台
    ]
)
# 创建一个"和当前模块绑定的日志器实例，后续代码记录日志时，就用这个实例
logger=logging.getLogger(__name__)
