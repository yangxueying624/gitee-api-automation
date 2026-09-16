import time
from typing import Callable,Any,List
import functools
from utils.log import logger


"""
一、函数对象
1. def hello()：在内存生成函数对象。hello只是变量名，指向这块内存
2. hello：引用函数对象，不执行内部代码；hello()：加括号，调用执行函数。
4. 函数属于对象，支持：赋值给变量、作为参数传递、用return返回函数对象


二、闭包 & 闭包变量
满足全部条件，才构成闭包：
1.函数嵌套，内层函数引用外层函数【局部变量】（非全局）
2.内层函数被return返回出去，脱离外层函数
3.外层函数执行结束后，内层仍然可以访问外层的局部变量
被内层捕获保存的外层局部变量，就是【闭包变量】



三、装饰器
补充1：
name="test"：属于函数调用括号内的关键字参数语法，只能写在()里面，作用是给函数参数赋值
    my_func(name="test") → 形参name拿到字符串test
{"name":"test"}：字典，独立的数据容器
    my_func({"name":"test"}) → 形参name拿到的是整个字典对象，不是字符串test

补充2：*和**，看位置决定是打包还是解包
① 写在函数定义 def wrapper(*args,**kwargs): → 打包
    作用：声明函数可以接收任意多位置参数、任意多关键字参数
    调用wrapper(100,200,name="test")时，自动收集参数
        *args收集位置参数 → 打包成元组 args=(100,200)
        **kwargs收集关键字参数 → 打包成字典 kwargs={"name":"test"}
    
② 写在函数调用func(*args,**kwargs) → 解包
    args是已经打包好的元组(100,200) kwargs是打包好的字典{"name":"test"}
    *args：把元组拆开，还原成独立位置参数100,200
    **kwargs：把字典拆开，还原成关键字参数name="test"
    


1. 无参装饰器api_log（2层嵌套）
def api_log(func):
    def wrapper(*args,**kwargs):
        ...
    return wrapper
    
@api_log等价于func=api_log(func)  
将变量名func重新绑定到包装后的wrapper函数对象地址；原始函数对象仍在内存中，被闭包变量保存引用供内部调用
第一层：接收被装饰的原始函数func
第二层wrapper：只有调用()才执行，用来写增强逻辑


2. 带参装饰器retry（3层def嵌套）
def retry(装饰器配置参数):   #第一层
    def decorator(func):   #第二层，接收原始业务函数
        def wrapper(*args,**kwargs):   #第三层增强逻辑
            ...
        return wrapper
    return decorator

@retry(max_tries=3,delay=1)执行流程：
1. 第一层retry：接收装饰器配置参数，返回decorator函数对象
2. 第二层decorator(func)：接收原始业务函数对象func，返回wrapper
3. 第三层wrapper：被装饰函数加()调用时才执行
@语法硬性规则：@xxx(参数) 括号里只能写配置，不能写被装饰函数。想要在@处传入自定义参数，手写 def 嵌套必须写三层。


四、@functools.wraps(func)
1. 本身是装饰器
2. 作用：把原始函数的元信息（__name__函数名、文档字符串__doc__等）复制给wrapper
3. 仅影响外部读取函数元信息，装饰器内部闭包变量func.__name__不受任何影响
    # 外部访问被装饰完成后的函数对象
    print(create_repo.__name__)
    ❌不写@functools.wraps(func)：输出 wrapper
    ✅写上@functools.wraps(func)：输出 create_repo（真实原始函数名）
    补充：装饰器内部 func.__name__，拿的是闭包保存的原始函数对象，有无 wraps，拿到的都是原函数名字。
"""

def retry(max_retries: int=3,delay: float=1.0,retry_on_none: bool=True):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any,**kwargs: Any) -> Any:
            exceptions_list: List[Exception] = []
            """
            range的用法：
            range(stop)：从0开始，到stop-1结束，range(3) → 0,1,2
            range(start,stop)：包含start，不包含stop，range(1,4) → 1,2,3
            range(start,stop,step)：步长，range(1,10,2) → 1,3,5,7,9
            """
            for attempt in range(1, max_retries + 1):
                try:
                    result=func(*args,**kwargs)
                    # 返回不是None → 业务判定成功，直接return结果
                    if result is not None:
                        if attempt>1:
                            logger.info(f"[重试] {func.__name__} 第{attempt}次重试成功")
                        return result
                    # result 就是None
                    if not retry_on_none:
                        # 如果开关关闭：返回None不重试，直接返回None结束
                        return None
                    # retry_on_none=True,记录警告，进入下一轮循环重试
                    logger.warning(f"[重试] {func.__name__} 第{attempt}次返回None，判定失败")
                except Exception as e:
                    exceptions_list.append(e)
                    logger.warning(f"[重试] {func.__name__} 第{attempt}次失败：{str(e)}")

                if attempt < max_retries:
                    time.sleep(delay)

            logger.error(f"[重试] {func.__name__} 重试{max_retries}次后仍然失败")
            if exceptions_list:
                # 列表推导式
                # - for e in exceptions_list：把列表里面每一个异常对象取出来，变量叫`e`
                # - str(e)：把异常对象转成可读的字符串，比如 TimeoutError("请求超时") → "请求超时"
                # - 外面一层[]：把转换后的全部字符串收集起来，生成新列表
                logger.error(f"历史异常列表：{[str(e) for e in exceptions_list]}")
                # list[-1] → 取列表的最后一个元素（负索引）
                # lst = [A, B, C, D]
                # 索引：  0  1  2  3
                # 负索引:-4 -3 -2 -1
                raise exceptions_list[-1]
            return None
        return wrapper
    return decorator



def api_log(func :Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args: Any,**kwargs: Any) -> Any:
        func_name=func.__name__
        # args[0]是类实例self，args[1:]过滤self，拿到业务位置参数
        logger.info(f"[api_log] >>> {func_name} 调用 | 参数= {args[1:]} {kwargs}")
        # 获取函数执行的开始时间戳
        start_time: float=time.time()
        try:
            # 调用原始业务函数，把收集到的全部参数传给原始函数
            result=func(*args, **kwargs)
            duration: float=round(time.time() -start_time,2)
            logger.info(f"[api_log] <<< {func_name} 完成 | 耗时={duration}秒 | 返回值={result}")
            # 把接口返回结果向外返回，外部用例拿到返回数据
            return result
        except Exception as e:
            # 发生异常，同样计算耗时
            duration: float=round(time.time()-start_time,2)
            logger.error(f"[api_log] !!! {func_name} 异常 | 耗时={duration}秒 | 错误{str(e)}")
            # raise：把异常重新抛出去，不要吞掉错误，pytest才能识别用例失败
            raise
    return wrapper






