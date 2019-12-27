from crontab import CronTab

my_cron = CronTab(user=True)

path = '/users/k.j./Documents/GitHub/zhihu-spider'
job = my_cron.new(command='/Library/Frameworks/Python.framework/Versions/3.7'
                          '/bin/python3 {}/spider.py >> ~/latest_update.log'
                          .format(path, path))
print('started new job :-)')
job.setall('*/5 * * * *')
job.set_comment("spider crontab job")

job.enable()
my_cron.write()
