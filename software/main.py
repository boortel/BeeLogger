import configparser
import datetime
import logging
import time
import os

from SensorThread import SensorThread
from CameraThread import CameraThread

from Sensors import Relay

from Camera import setCaptureStatus
from CameraThread import stopCamThread
from SensorThread import stopSenThread

def main():

    ## Get current time
    now = datetime.datetime.now()
    timeString = now.strftime("%y%m%d_%H%M")

    ## Open the ini file
    base_path = os.path.dirname(os.path.realpath(__file__))
    cfg_path = os.path.join(base_path, 'BeeLogger.ini')

    cfg = configparser.ConfigParser()
    cfg.read(cfg_path)
 
    ## Create the log directory and its structure if it not exists yet
    
    # Log session base path
    driveName = cfg.get('General', 'driveName', fallback = 'NaN')
    
    if driveName != 'NaN':
        logPath = '/media/pi/' + driveName + '/log/Log_' + timeString
        driveSet = False
    else:
        logPath = 'log/Log_' + timeString
        logPath = os.path.join(base_path, logPath)
        driveSet = True

    if not os.path.exists(logPath):
        os.makedirs(logPath)

    # Initialize program logging
    logging.basicConfig(filename = logPath + '/ProgramLog.txt',  level=logging.DEBUG, format='(%(asctime)s %(threadName)-10s %(levelname)-7s) %(message)s',)

    # Log warning message if the drive not set
    if driveSet:
        logging.warning(': USB drive name is not set, saving to the default path.')

    ## Set the camera capture on and off times
    lightOn_hour = cfg.getint('General', 'lightOn_hour')
    lightOn_minute = cfg.getint('General', 'lightOn_minute')

    lightOff_hour = cfg.getint('General', 'lightOff_hour')
    lightOff_minute = cfg.getint('General', 'lightOff_minute')

    t_on = datetime.time(hour=lightOn_hour, minute=lightOn_minute)
    t_off = datetime.time(hour=lightOff_hour, minute=lightOff_minute)

    if t_on > t_off:
        logging.error(': Capture on time is higher than the off time.')
        return -1

    ## Set the logging stop time and flag
    logOff_year = cfg.getint('General', 'logOff_year')
    logOff_month = cfg.getint('General', 'logOff_month')
    logOff_day = cfg.getint('General', 'logOff_day')
    logOff_hour = cfg.getint('General', 'logOff_hour')
    logOff_minute = cfg.getint('General', 'logOff_minute')

    logStop = cfg.getboolean('General', 'logStop')
    t_stop = datetime.datetime(year=logOff_year, month=logOff_month, day=logOff_day, hour=logOff_hour, minute=logOff_minute)

    if logStop and now > t_stop:
        logging.error(': Stop time is smaller than the current time.')
        return -1

    ## Initialize the relay object
    relay = Relay(1, 5)

    ## Create the sensor and camera thread
    sen = SensorThread(name = 'SensThread', baseLog = logPath, config = cfg)
    cam = CameraThread(name = 'CamThread', baseLog = logPath, config = cfg)

    ## Run the threads
    sen.start()
    cam.start()

    log = True

    ## Control the threads run and the camera capturing
    while log:
        t_now = datetime.datetime.now()
        t_capture = datetime.time(hour=t_now.hour, minute=t_now.minute, second=t_now.second)

        # Turn on and off the camera capture together with the light
        if t_capture >= t_on and t_capture < t_off:
            setCaptureStatus(True)
            relay.on()
        else:
            setCaptureStatus(False)
            relay.off()

        # Stop the logging if the stop flag and time are set
        if logStop and t_now >= t_stop:
            stopCamThread(relay)
            stopSenThread()
            log = False
        
        time.sleep(0.1)


## Run the main function
if __name__ == '__main__':
    main()