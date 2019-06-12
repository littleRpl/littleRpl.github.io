
#### 前言
***
pandas中的date_range()函数用来生成一个日期序列，在需要构造一个日期序列的时候非常方便。
本篇文章是对英文文档的翻译，英文版点击上面的<code>英文 English</code>查看，或者[点击这里](http://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.date_range.html)查看网页原文


####  参数解释
***
<code>pandas.date_range</code>(start=None, end=None, periods=None, freq=None, 
tz=None, normalize=False, name=None, closed=None, \*\*kwargs)

此函数返回一个固定频率的DatetimeIndex类型的数据（就是返回一个时间序列)

start：生成日期序列的左区间，str或datetime-like类型， 参数可选。



end： 生成日期序列的右区间，str或datetime-like类型， 参数可选。



periods：要生成的周期数，周期是指生成的序列的长度， int整型， 参数可选。



freq：要生成的日期的频次， 频次是指两个相邻日期间隔时间， 可以是5小时:"5H"， 1天："D"， 3个月："3M"等等，
点击[查看](http://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases)具体频次别名表



tz：时区，返回所选时区的日期时间，如：'Asia/Hong_Kong'，默认生成的日期序列与时区无关，str类型，参数可选。



normalize：在生成日期序列之前，将start/end标准化为午夜。 bool类型，默认False。



name： 生成的DatetimeIndex序列的名字， str类型，默认None。



closed：左右日期区间是否闭合可取。'left'：左闭右开，'right'：左开右闭。默认：None， 左右都是闭区间。



\*\*kwargs：向后兼容性考虑，对结果没有影响。



#### 注意
***
start，end，periods，freq四个参数中只有三个需要明确指定。如果freq被忽略，则生成的日期序列的periods（天数）是线性间隔的，包括开始和结束日期。（具体看例子就明白了）


#### 实例
***

###### 日期参数实例

以下的四个例子都生成了相同的日期序列，但使用了不同的start， end， periods组合。

1. 指定start和end， freq默认为days

```python
pd.date_range(start='20180102', end='20180109')

# 或者 pd.date_range(start=''1/1/2018’', end='1/9/2018')
DatetimeIndex(['2018-01-02', '2018-01-03', '2018-01-04', '2018-01-05',
               '2018-01-06', '2018-01-07', '2018-01-08', '2018-01-09'],
              dtype='datetime64[ns]', freq='D')

```

2.指定start和periods， periods周期数是天
```python
pd.date_range(start='20180102', periods=8)

DatetimeIndex(['2018-01-02', '2018-01-03', '2018-01-04', '2018-01-05',
               '2018-01-06', '2018-01-07', '2018-01-08', '2018-01-09'],
              dtype='datetime64[ns]', freq='D')
```

3.指定end和periods
```python
pd.date_range(end='20180109', periods=8)

DatetimeIndex(['2018-01-02', '2018-01-03', '2018-01-04', '2018-01-05',
               '2018-01-06', '2018-01-07', '2018-01-08', '2018-01-09'],
              dtype='datetime64[ns]', freq='D')
```

4.指定start，end， periods。freq频次自动
```python
pd.date_range(start='20180102', end='20180109', periods=3)

DatetimeIndex(['2018-01-02 00:00:00', '2018-01-05 12:00:00',
               '2018-01-09 00:00:00'],
              dtype='datetime64[ns]', freq=None)
```

###### 其他参数实例

将freq频率参数改为'M'(月末频率), 默认是'D'(天）
```python
pd.date_range(start='1/1/2019', periods=5, freq='M')

DatetimeIndex(['2019-01-31', '2019-02-28', '2019-03-31', '2019-04-30',
               '2019-05-31'],
              dtype='datetime64[ns]', freq='M')
```
频率可以**多倍数**表示
```python
pd.date_range(start='1/1/2019', periods=5, freq='3M')

DatetimeIndex(['2019-01-31', '2019-04-30', '2019-07-31', '2019-10-31',
               '2020-01-31'],
              dtype='datetime64[ns]', freq='3M')
```

freq也可以指定为偏移量对象
```python
pd.date_range(start='/1/1/2019', periods=5, freq=pd.offsets.MonthEnd(3))

DatetimeIndex(['2019-01-31', '2019-04-30', '2019-07-31', '2019-10-31',
               '2020-01-31'],
              dtype='datetime64[ns]', freq='3M')
```

指定**tz**来设置时区
```python
pd.date_range(start='/1/1/2019', periods=5, tz='Asia/Tokyo')

DatetimeIndex(['2019-01-01 00:00:00+09:00', '2019-01-02 00:00:00+09:00',
               '2019-01-03 00:00:00+09:00', '2019-01-04 00:00:00+09:00',
               '2019-01-05 00:00:00+09:00'],
              dtype='datetime64[ns, Asia/Tokyo]', freq='D')
```
参数**closed**控制是否包含start和end的边界，默认是包含这两个端点的。（类似区间两端点的开闭）
```python
pd.date_range(start='1/1/2019', end='1/6/2019', closed=None)

DatetimeIndex(['2019-01-01', '2019-01-02', '2019-01-03', '2019-01-04',
               '2019-01-05', '2019-01-06'],
              dtype='datetime64[ns]', freq='D')
```

closed='left'，左闭右开，只包含start端点，不包含end端点
```python
pd.date_range(start='1/1/2019', end='1/6/2019', closed='left')

DatetimeIndex(['2019-01-01', '2019-01-02', '2019-01-03', '2019-01-04',
               '2019-01-05'],
              dtype='datetime64[ns]', freq='D')
```

closed='right', 左开右闭，不包含start端点，但包含end端点
```python
pd.date_range(start='1/1/2019', end='1/6/2019', closed='right')

DatetimeIndex(['2019-01-02', '2019-01-03', '2019-01-04', '2019-01-05',
               '2019-01-06'],
              dtype='datetime64[ns]', freq='D')
```




