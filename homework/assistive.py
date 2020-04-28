import logging


goodname = "zombie_good"
badname = "zombie_bad"
single_great_good_logfile = 'great_good_logs.txt'
single_great_error_logfile = 'great_error_logs.txt'
great_single_good_logger = logging.getLogger(goodname)
great_single_good_logger.setLevel(logging.DEBUG)
great_single_error_logger = logging.getLogger(badname)
great_single_error_logger.setLevel(logging.ERROR)
# опишем, куда и как будем сохранять логи: зададим файл и формат
great_single_good_handler = logging.FileHandler(single_great_good_logfile, 'a', 'utf-8')
great_single_error_handler = logging.FileHandler(single_great_error_logfile, 'a', 'utf-8')
great_single_formatter = logging.Formatter("%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s")
great_single_good_handler.setFormatter(great_single_formatter)
great_single_error_handler.setFormatter(great_single_formatter)
great_single_good_logger.addHandler(great_single_good_handler)
great_single_error_logger.addHandler(great_single_error_handler)

#patient's data file
zombie_base_file = "./patient_data.csv"