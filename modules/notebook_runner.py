import subprocess
import threading
import time
import logging
import os

def setup_logger(log_file_path):
    logger = logging.getLogger(log_file_path)
    logger.setLevel(logging.INFO)
    
    handler = logging.FileHandler(log_file_path)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    if not logger.hasHandlers():
        logger.addHandler(handler)
    
    return logger, handler

def run_notebook(notebook_path, log_file_path, error_flag, last_executed_notebook):
    logger, handler = setup_logger(log_file_path)
    
    logger.info(f"Starting execution of {notebook_path}")
    print(f"🔵 Running: {notebook_path}")

    result = subprocess.run(
        ['jupyter', 'nbconvert', '--to', 'notebook', '--execute', notebook_path],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        logger.error(f"❌ Error in {notebook_path}: {result.stderr}")
        print(f"\n❌ Error in {notebook_path}:\n{result.stderr}")
        error_flag[0] = True
    else:
        logger.info(f"✅ Notebook {notebook_path} executed successfully")
        print(f"✅ Finished: {notebook_path}")

    last_executed_notebook[0] = notebook_path  # שמירת המחברת האחרונה שרצה
    handler.flush()
    handler.close()
    logger.removeHandler(handler)

def tail_log_file(file_path, stop_event, interval=1):
    """ הצגת הלוג בזמן אמת """
    last_pos = 0
    while not stop_event.is_set():
        try:
            with open(file_path, 'r') as log_file:
                log_file.seek(last_pos)
                new_logs = log_file.read()
                if new_logs:
                    print(new_logs, end='')
                last_pos = log_file.tell()
        except FileNotFoundError:
            pass
        time.sleep(interval)

def run_notebooks_sequentially(notebooks):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    error_flag = [False]  
    last_executed_notebook = ["None"]  
    
    for i, notebook_path in enumerate(notebooks, start=1):
        log_file_path = os.path.join(log_dir, f'notebook{i}_logfile.log')

        # מחיקת התוכן הישן של קובץ הלוג
        open(log_file_path, 'w').close()

        stop_event = threading.Event()
        
        notebook_thread = threading.Thread(target=run_notebook, args=(notebook_path, log_file_path, error_flag, last_executed_notebook))
        tail_thread = threading.Thread(target=tail_log_file, args=(log_file_path, stop_event))
        
        notebook_thread.start()
        tail_thread.start()
        
        notebook_thread.join()
        stop_event.set()
        tail_thread.join()
        
        if error_flag[0]:  
            print(f"\n⛔ Execution stopped due to an error in {notebook_path}")
            break

    print(f"\n🔎 Last executed notebook: {last_executed_notebook[0]}")
