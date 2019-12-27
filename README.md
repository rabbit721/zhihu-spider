# zhihu-spider

python 网络爬虫， 每日更新， 输出为excel 并在用户制定的mongodb数据库里建立集合并更新

## 安装要求：
1. python 3.7
2. pip
3. mongodb

### 要用的 Python package （可用pip安装）

- xlwt
- pymongo 
- python-crontab==2.4.0
- requests==2.22.0
- beautifulsoup4==4.8.1

## 运行爬虫：
>
```python
python crontab-control.py <arg1> <arg2> <arg3>
```
>> 

- arg1: 本机python的地址 (可运行```which python``` 查看)
- arg2: 储存代码和输出excel的地址 （fork之后可直接在本目录下运行， 设为```$(pwd)```） 
- arg3: 用于连接mongodb 的url （如使用本地mongod, 为 ```'mongodb://127.0.0.1:27017/'```）

 
## 爬虫的输出：
```
- excel：在本目录下名为  search_results.xls
- mongodb 数据库： 在指定的 mongodb 中 建立数据库 spiderdb， 将爬虫结果存在 wondercv_exe 集合中 并覆盖之前此集合中的文档
```
