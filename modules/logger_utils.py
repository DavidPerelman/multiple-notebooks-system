import logging
import os

def setup_logger(log_file_path, logger_name):
    """
    יוצר ומגדיר לוגר עם קובץ לוג נפרד.
    
    :param log_file_path: נתיב קובץ הלוג
    :param logger_name: שם הלוגר (למניעת כפילויות)
    :return: מופע לוגר מוגדר
    """
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)  # יצירת תיקיית לוגים אם לא קיימת
    
    logger = logging.getLogger(logger_name)

    if not logger.hasHandlers():  # מונע הוספת מספר Handlers לאותו לוגר
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(log_file_path, mode='w')  # mode='w' כדי למחוק תוכן קודם
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)

    return logger
