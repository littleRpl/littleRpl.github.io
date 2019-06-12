> you can click upon botton <code>中文 Chinese</code> to see the chinese version 

#### Paramters
***
<code>pandas.date_range</code>(start=None, end=None, periods=None, freq=None, 
tz=None, normalize=False, name=None, closed=None, \*\*kwargs)

Return a fixed frequency DatetimeIndex.

|paramters|  |
| --- | --- |
|start| str or datetime-like, optional, Left bound for generating dates. |
|end| str or datetime-like, optional, Right bound for generating dates. |
|periods| integer, optional, Number of periods to generate. |
|freq | str or DateOffset, default 'D' Frequency strings can have multiples, e.g. '5H'. See [here](http://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases) for a list of frequency aliases. |
|tz| str or tzinfo, optional, Time zone name for returning localized DatetimeIndex, for example ‘Asia/Hong_Kong’. By default, the resulting DatetimeIndex is timezone-naive. |
|normalize| bool, default False, Normalize start/end dates to midnight before generating date range. |
|name| str, default None, Name of the resulting DatetimeIndex. | 
|closed| {None, ‘left’, ‘right’}, optional, Make the interval closed with respect to the given frequency to the ‘left’, ‘right’, or both sides (None, the default). |
|\*\*kwrags| For compatibility. Has no effect on the result. |


#### Notes
***
Of the four parameters start, end, periods, and freq, exactly three must be specified. If freq is omitted, the resulting DatetimeIndex will have periods linearly spaced elements 
between start and end (closed on both sides).

To learn more about the frequency strings, please see [this link](http://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html).


#### Examples
***
###### Specifying the values
The next four examples generate the same DatetimeIndex, but vary the combination of start, end and periods.Specify start and end, with the default daily frequency.
```python
pd.date_range(start='20180102', end='20180109')

# pd.date_range(start=''1/1/2018’', end='1/9/2018')
DatetimeIndex(['2018-01-02', '2018-01-03', '2018-01-04', '2018-01-05',
               '2018-01-06', '2018-01-07', '2018-01-08', '2018-01-09'],
              dtype='datetime64[ns]', freq='D')
```

Specify start and periods, the number of periods (days).
```python
pd.date_range(start='20180102', periods=8)

DatetimeIndex(['2018-01-02', '2018-01-03', '2018-01-04', '2018-01-05',
               '2018-01-06', '2018-01-07', '2018-01-08', '2018-01-09'],
              dtype='datetime64[ns]', freq='D')
```

Specify end and periods, the number of periods (days).
```python
pd.date_range(end='20180109', periods=8)

DatetimeIndex(['2018-01-02', '2018-01-03', '2018-01-04', '2018-01-05',
               '2018-01-06', '2018-01-07', '2018-01-08', '2018-01-09'],
              dtype='datetime64[ns]', freq='D')

```


Specify start, end, and periods; the frequency is generated automatically (linearly spaced).
```python
pd.date_range(start='20180102', end='20180109', periods=3)

DatetimeIndex(['2018-01-02 00:00:00', '2018-01-05 12:00:00',
               '2018-01-09 00:00:00'],
              dtype='datetime64[ns]', freq=None)
```

###### Other Parameters
Changed the freq (frequency) to 'M' (month end frequency).
```python
pd.date_range(start='1/1/2019', periods=5, freq='M')

DatetimeIndex(['2019-01-31', '2019-02-28', '2019-03-31', '2019-04-30',
               '2019-05-31'],
              dtype='datetime64[ns]', freq='M')
```

Multiples are allowed
```python
pd.date_range(start='1/1/2019', periods=5, freq='3M')

DatetimeIndex(['2019-01-31', '2019-04-30', '2019-07-31', '2019-10-31',
               '2020-01-31'],
              dtype='datetime64[ns]', freq='3M')
```

freq can also be specified as an Offset object.
```python
pd.date_range(start='/1/1/2019', periods=5, freq=pd.offsets.MonthEnd(3))

DatetimeIndex(['2019-01-31', '2019-04-30', '2019-07-31', '2019-10-31',
               '2020-01-31'],
              dtype='datetime64[ns]', freq='3M')
```

Specify tz to set the timezone.
```python
pd.date_range(start='/1/1/2019', periods=5, tz='Asia/Tokyo')

DatetimeIndex(['2019-01-01 00:00:00+09:00', '2019-01-02 00:00:00+09:00',
               '2019-01-03 00:00:00+09:00', '2019-01-04 00:00:00+09:00',
               '2019-01-05 00:00:00+09:00'],
              dtype='datetime64[ns, Asia/Tokyo]', freq='D')
```


closed controls whether to include start and end that are on the boundary. The default includes boundary points on either end.
```python
pd.date_range(start='1/1/2019', end='1/6/2019', closed=None)

DatetimeIndex(['2019-01-01', '2019-01-02', '2019-01-03', '2019-01-04',
               '2019-01-05', '2019-01-06'],
              dtype='datetime64[ns]', freq='D')
```


Use closed='left' to exclude end if it falls on the boundary.
```python
pd.date_range(start='1/1/2019', end='1/6/2019', closed='left')

DatetimeIndex(['2019-01-01', '2019-01-02', '2019-01-03', '2019-01-04',
               '2019-01-05'],
              dtype='datetime64[ns]', freq='D')
```

Use closed='right' to exclude start if it falls on the boundary.
```python
pd.date_range(start='1/1/2019', end='1/6/2019', closed='right')

DatetimeIndex(['2019-01-02', '2019-01-03', '2019-01-04', '2019-01-05',
               '2019-01-06'],
              dtype='datetime64[ns]', freq='D')
```
