from crontab import CronTab
import sys

my_cron = CronTab(user=True)

if len(sys.argv) < 4:
    print("Expecting 3 input args, got {}".format(str(len(sys.argv) - 1)))
    exit(1)

# excel_path = '/code/docker_result.xls
# mongdb_name = 'mongodb'
python_path = sys.argv[1]
path = sys.argv[2]
mongdb_name = sys.argv[3]

job = my_cron.new(command='{}/python {}/spider.py {} {} >> '
                          '{}/latest_update.log'.format(python_path, path, path,
                                                        mongdb_name, path))

print('started new job :-)')
job.setall('0 0 * * *')
job.set_comment("spider crontab job")

job.enable()
my_cron.write()
