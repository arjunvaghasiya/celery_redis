import logging

class Logger_Class():
    logging.basicConfig(
        filename="/home/arjun.v@ah.zymrinc.com/my_py_dj/celery_redis_project/loggs_all/final_report.log",
        format='%(asctime)s: %(levelname)s: %(message)s',
        datefmt='%d/%m/%Y  %I:%M:%S %p',
        )

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

