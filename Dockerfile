FROM python:3.7
ADD . /code
WORKDIR /code
RUN pip install -i https://pypi.doubanio.com/simple/ --trusted-host pypi.douban.com  -r requirements.txt
CMD ["python", "spider.py", "/code", "mongodb"]
