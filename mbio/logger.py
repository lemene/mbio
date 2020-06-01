import logging, time, sys, os

def init_logger():
    if not os.path.lexists("__log__"):
        os.mkdir("__log__")
        
    logger = logging.getLogger("IPDs")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

    hfile = logging.FileHandler("__log__/"+time.strftime("%Y%m%d") + ".log")
    hfile.setFormatter(formatter)
    logger.addHandler(hfile)

    hconsole = logging.StreamHandler(sys.stdout)
    hconsole.setFormatter(formatter)
    logger.addHandler(hconsole)
    return logger


logger = init_logger()

def addlog(func):
    def warpper(*args,**kwargs):
        logger.info("Start Function %s", func.__name__)
        func(*args, *kwargs)
        logger.info("End  Function %s", func.__name__)
    return warpper
