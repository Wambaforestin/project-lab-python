import threading
import time
import schedule

class Scheduler:
    def __init__(self):
        super().__init__()
        self.__stop_running = threading.Event()
    
    # schedule the task to run every day at 8:00 AM
    def schedule_task(self, hour, minute, task):
        schedule.clear() # clear any existing schedules
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(task) 
        
    # start the scheduler as background thread...
    def start(self):
        self.__stop_running.clear() 
        while not self.__stop_running.is_set():
            schedule.run_pending()
            time.sleep(1)
            
    # stop the scheduler
    def stop(self):
        self.__stop_running.set()
        
    
#test
if __name__ == '__main__':
    # creating a custom task for the scheduler to run
    def task():
        print("Task is running...\n")
        print("Task completed successfully!\n")
    
    scheduler = Scheduler() # create a scheduler instance
    scheduler.start()
    hour = time.localtime().tm_hour # get the current hour
    minute = time.localtime().tm_min + 1 # get the current minute and add 1 to run the task in the next minute
    print(f"Scheduling the task to run every day at {hour:02d}:{minute:02d}...\n")
    scheduler.schedule_task(hour, minute, task) # schedule the task to run every day at the current hour and the next minute
    time.sleep(5) # wait for 20 seconds before stopping the scheduler, ensure the task runs at least once
    scheduler.stop()
         