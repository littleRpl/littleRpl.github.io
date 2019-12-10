---
layout:       post
title:        "python 内存数据压缩为zip"
subtitle:     '跳过文件保存后在压缩，直接将数据保存为压缩格式'
date:         2019-12-09 14:30:00
author:       "Rpl"

# header-style:   text
header-img:   "img/python6.png"
header-mask:  0.5
catalog:      true

multilingual: false

tags:
  - 原创
  - 技术
  - python

---

> 工作中需要将大批的数据，压缩为zip存储。按照传统的处理办法需要将数据先存储到本地磁盘，再从磁盘读文件压缩成zip文件。
> 传统方法需要多次磁盘IO，性能很低，如果跳过文件存储，直接将内存的数据压缩保存，会大大减少磁盘IO，提升性能。

> 不需要看解析的，可以直接看最后完整的python代码



创建一个类: InMemoryZIP(), 来处理所有的程序。

```python
class InMemoryZIP(object):
```

### 一 __init__() 创建一个类文件对象

```python
	def __init__(self):
		# create the in-memory file-like object
		self.in_memory_zip = BytesIO()
```

### 二 append() 内存数据添加到zip对象
```python
	def append(self, filename_in_zip, file_contents):
		""" Appends a file with name filename_in_zip \
        and contents of file_contents to the in-memory zip.
        """

        # create a handle to the in-memory zip in append mode\
		if not isinstance(file_contents, bytes):
			file_contens = bytes(str(file_contens), encoding='utf-8')

		# write the file to the in-memory zip
		zf = zipfile.ZipFile(self.in_memory_zip, 'a', zipfile.ZIP_DEFLATED, False)

		zf.writestr(filename_in_zip, file_contents)

		# mark the files as having been created on Windows
        # so that Unix permissions are not inferred as 0000
		for zfiel in zf.filelist:
			zfile.create_system = 0

		return self

```

### 三 appendfile() 文件添加到zip对象
```python
	def appendfile(self, file_path, file_name=None):
		""" Read a file with path file_path \
        and append to in-memory zip with name file_name.
        """

        # file_path is abs path
		if file_name is None:
			file_name = os.path.split(file_path)[1]


		with open(file_path, 'rb') as f:
			file_contents = f.read()
			self.append(file_name, file_contents)

		return self
```

### 四 read() 读取zip数据流
```python
	def read(self):
		""" Returns a string with the contents of the in-memory zip.
        """

		self.in_memory_zip.seek(0)
		return self.in_memory_zip.read()
```

### 五 writetofile() 内存zip流保存为zip文件
```python
def writetofile(self, zip_filename):
	"""
        Write the in-memory zip to a file
    """

	with open(zip_filename, 'wb') as f:
		f.write(self.read())

```


### 六 完整版python代码
```python
# !user/bin/env python3
# -*-coding : utf-8 -*-

import zipfile
from io import BytesIO
import os


class InMemoryZIP(object):
    def __init__(self):
        # create the in-memory file-like object
        self.in_memory_zip = BytesIO()

    def append(self, filename_in_zip, file_contents):
        """ Appends a file with name filename_in_zip \
        and contents of file_contents to the in-memory zip.
        """
        # create a handle to the in-memory zip in append mode\
        if not isinstance(file_contents, bytes):
            file_contents = bytes(str(file_contents), encoding='utf-8')

        zf = zipfile.ZipFile(self.in_memory_zip, 'a',
                             zipfile.ZIP_DEFLATED, False)

        # write the file to the in-memory zip
        zf.writestr(filename_in_zip, file_contents)

        # mark the files as having been created on Windows
        # so that Unix permissions are not inferred as 0000
        for zfile in zf.filelist:
            zfile.create_system = 0
        return self

    def appendfile(self, file_path, file_name=None):
        """ Read a file with path file_path \
        and append to in-memory zip with name file_name.
        """
        if file_name is None:
            file_name = os.path.split(file_path)[1]

        f = open(file_path, 'rb')
        file_contents = f.read()
        self.append(file_name, file_contents)
        f.close()
        return self

    def read(self):
        """ Returns a string with the contents of the in-memory zip.
        """
        self.in_memory_zip.seek(0)
        return self.in_memory_zip.read()

    def writetofile(self, filename):
        """
        Write the in-memory zip to a file
        """
        f = open(filename, 'wb')
        f.write(self.read())
        f.close()


if __name__ == '__main__':

	pass

	# contens = 'xxxxxxxxx'  # 内存数据
    # imz = InMemoryZIP()
    # imz.append('test.txt', contens)
    # imz.writetofile('test.zip')
   

```