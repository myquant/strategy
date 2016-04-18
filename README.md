# 掘金策略集锦

量化开源和分享，展示各类经典策略在掘金平台下的实现。

每个策略单独拥有一个目录，目录名即是该策略的简称，里面有一个固定名为info.md的文件，其内容为该策略的简单介绍。
策略的每种实现为单独一个目录，目录名为该策略的实现语言，因为一些语言下的代码实现可能有一系列文件，所以把每一种策略实现语言单列为一个目录，
比如，一个策略有python实现，就有一个python目录，里面是python代码文件，如果还有C#实现，就会有一个csharp目录。


目录结构组织如下：


    －－ strategy  策略名
  
    ｜—— info.md  策略介绍
    
    ｜—— python   策略python实现
    
       ｜— strategy.py  策略代码
       
       ｜－ strategy.ini 策略的配置文件

    ｜—— csharp   策略csharp实现
    
       ｜— strategy.cs  策略代码

       ｜－ strategy.ini 策略的配置文件
       
       
补充：
    因部分策略会比较复杂, python策略中可能会用到时间序列数据的处理包pandas, 时间处理包arrow, 请先行用pip安装。

策略列表，逐步增加中，有需求或计划共享自己实现的一些经典策略的，请fork本项目，然后修改这个文件，并做Pull Request。

1. 双均线策略 dual-ma
2. 区间突破策略 dual-thrust 
3. 动态突破策略 Dynamic Breakout

 ...... 
