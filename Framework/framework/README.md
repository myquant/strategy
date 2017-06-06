## Python 策略框架

*注*：已经兼容python 3 。

提供了基本的数据组织和简单的基于TA-lib库的技术指标封装，目的是把策略的编写简化到只实现一个algo函数和配置ini文件就能快速完成，具体示例可参考demo.py, demo.ini文件(框架使用到的参数配置具体详见ini文件中注释)。

1. 用mixin模式组织各功能模块
2. 设置基本的数据组织，包括历史数据和实时数据的自动更新
3. 方便的K线数据存取、盘口数据存取
4. 简单化下单价格，基于盘口价格取对手价
5. 仓位管理mixin中提供了基本的止赢止损逻辑，可在配置文件中通过参数控制
6. 通过helper, physics方式在外部提供一些简化的接口。
7. 提供了数据转成pandas的dataframe数据结构接口，to_dataframe(Bar数据到dataframe), ticks_to_dataframe(最新盘口数据转dataframe)。


