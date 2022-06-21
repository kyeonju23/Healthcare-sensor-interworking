import serial
import json
import requests
import io
import threading
import serial.tools.list_ports
from serial.serialutil import *
import numpy as np
from datetime import datetime
import datetime as dt
import time
import csv
import subprocess
#import matplotlib.pyplot as plt
#from matplotlib.animation import FuncAnimation

class Bx50:
    # Data validity macros
    DATA_INVALID_LIMIT = (-32001)  # limit for special invalid data values */
    DATA_INVALID = (-32767)  # there is no valid data */
    DATA_NOT_UPDATED = (-32766)  # data is not updated */
    DATA_DISCONT = (-32765)  # data discontinuity (calibration ...) */
    DATA_UNDER_RANGE = (-32764)  # data exceeds lower valid limit */
    DATA_OVER_RANGE = (-32763)  # data exceeds upper valid limit */
    DATA_NOT_CALIBRATED = (-32762)  # data is not calibrated */

    # Asynchronous interface specific constants
    FRAMECHAR = 0x7E
    CTRLCHAR = 0x7D
    BIT5 = 0x7C
    BIT5COMPL = 0x5F

    # Datex Record Interface data structure definitions
    DRI_MAX_SUBRECS = 8  # of subrecords in a packet */
    DRI_MAX_PHDBRECS = 5  # of phys.db records in a packet */

    # data packet maintypes
    DRI_MT_PHDB = 0  # Physiological data and related transmission requests.
    DRI_MT_WAVE = 1  # Waveform data and related transmission requests.
    DRI_MT_ALARM = 4  # Alarm data and related transmission requests.

    # data packet subtypes
    DRI_PH_DISPL = 1
    DRI_PH_10S_TREND = 2
    DRI_PH_60S_TREND = 3

    DRI_PHDBCL_REQ_BASIC_MASK = 0  # Enable sending of Basic physiological data class
    DRI_PHDBCL_DENY_BASIC_MASK = 1  # Disable sending of Basic physiological data class
    DRI_PHDBCL_REQ_EXT1_MASK = 2  # Enable sending of Ext1 physiological data class
    DRI_PHDBCL_REQ_EXT2_MASK = 4  # Enable sending of Ext2 physiological data class
    DRI_PHDBCL_REQ_EXT3_MASK = 8  # Enable sending of Ext3 physiological data class

    # Datex Record Interface level types
    DRI_LEVEL_95 = 2
    DRI_LEVEL_97 = 3
    DRI_LEVEL_98 = 4
    DRI_LEVEL_99 = 5
    DRI_LEVEL_2000 = 6
    DRI_LEVEL_2001 = 7
    DRI_LEVEL_2003 = 8
    DRI_LEVEL_2005 = 9

    WF_REQ_CONT_START = 0
    WF_REQ_CONT_STOP = 1

    DRI_EOL_SUBR_LIST = 0xFF

    DRI_WF_CMD = 0

    DRI_WF_CMD = 0
    ECG1 = 1
    ECG2 = 2
    ECG3 = 3
    INVP1 = 4
    INVP2 = 5
    INVP3 = 6
    INVP4 = 7
    PLETH = 8
    CO2 = 9
    N2O = 11
    AA = 12
    AWP = 13
    FLOW = 14
    RESP = 15
    INVP5 = 16
    INVP6 = 17
    EEG1 = 18
    EEG2 = 19
    EEG3 = 20
    EEG4 = 21
    VOL = 23
    TONO_PRESS = 24
    SPI_LOOP_STATUS = 29
    ENT_100 = 32
    EEG_BIS = 35

    r_len = 0
    r_nbr = 0
    r_dri_level = 0
    plug_id = 0
    r_time = 0
    reserved1 = 0
    reserved2 = 0
    reserved3 = 0
    r_maintype = 0
    sr_offset1 = 0
    sr_type1 = 0
    sr_offset2 = 0
    sr_type2 = 0
    sr_offset3 = 0
    sr_type3 = 0
    sr_offset4 = 0
    sr_type4 = 0
    sr_offset5 = 0
    sr_type5 = 0
    sr_offset6 = 0
    sr_type6 = 0
    sr_offset7 = 0
    sr_type7 = 0
    sr_offset8 = 0
    sr_type8 = 0
    
    #mobiu data
    s_HR = []
    s_SPo2 = []
    s_T1 = []
    s_T2 = []
    s_NIBP_Mean = []
    s_NIBP_DIA = []
    s_NIBP_SYS = []
    sTime = []

    #wav_req
    res = 0
    req_type = 0
    type = [0] * 8
    reserved = [0] * 10

    #datex_record_type
    dataRecord = [0] * 1450

    # datex_tx_type
    dataTx = [0] * 49

    # datex_wave_tx_type
    dataWave = [0] * 72

    #phdb_req_type
    phdb_rcrd_type = 0
    tx_interval = 0
    phdb_class_bf = 0
    reservedPrt = 0

    #set transmission
    m_transmissionstart = True

    FrameList = []
    DPortBufSize = 0
    DPort_rxbuf = []

    m_fstart = True
    m_storestart = False
    m_storeend = False
    m_bitshiftnext = False
    m_bList = []

    m_NumericValList = []
    m_NumValHeaders = []
    # m_strbuildvalues = StringBuilder()
    # m_strbuildheaders = StringBuilder()
    m_WaveValResultList = []
    # m_strbuildwavevalues = StringBuilder()

    m_strTimestamp = ""
    m_dataexportset = 1
    m_transmissionstart = True

    m_DeviceID = ""

    # class NumericValResult:
    Timestamp = ""
    PhysioID = ""
    Value = ""
    DeviceID = ""

    # class WaveValResult:
    Timestamp = ""
    PhysioID = []
    Value = []
    DeviceID = ""
    Unitshift = 1

    #dataplot one ECG
    DataECG = []
    DataECGPlot = []
    DataECGPlotecg=[]
    DataTime = []

    #wave set detail
    Waveset = 0 
    
    #transmission interval and data summary list
    tInterval = 0
    tEstimations = []

    #datex_record_type:
    dataRecord = [0]*1450 

    # Create a new SerialPort object with default settings.
    ports = serial.tools.list_ports.comports()
    portList = [port.name for port in ports]

    # listports available.
    print(portList, sep="\n")

    # select port from list available.
    #print("Select the Port to which Datex AS3 Monitor is to be connected, Available Ports:")
    #portName = input("Select the Port to which Datex AS3 Monitor is to be connected, Available Ports:")
    portName = 'ttyUSB0'

    #FOR JNANO AND RASP
    # configure the serial connections (the parameters differs on the device you are connecting to)
    sudo_password = '1234'#write jetson nano password here
    command = 'chmod a+rw /dev/ttyUSB0'
    command = command.split()

    cmd1 = subprocess.Popen(['echo',sudo_password], stdout=subprocess.PIPE)
    cmd2 = subprocess.Popen(['sudo','-S'] + command, stdin=cmd1.stdout, stdout=subprocess.PIPE)

    output = cmd2.stdout.read().decode() 

    dport = serial.Serial('/dev/'+portName, baudrate=19200, bytesize=8, parity='E', stopbits=1, timeout=1)

    dport.dtr = True

    dportBufSize = 4096
    dport_rxbuf = [0] * dportBufSize    

    def MainProgram():
        try:
            Bx50.dport.is_open            
            # transmission rate.
            #print("Enter Numeric data Transmission interval (seconds):")
            
            #sInterval = input("Enter Numeric data Transmission interval (seconds):")
            sInterval = 5
            # converting sInterval from string to integer
            nInterval = 5

            if sInterval != " ":
                nInterval = int(sInterval)
            if nInterval < 5:
                nInterval = 5
                Bx50.tInterval = nInterval
            else:
                nInterval = nInterval
                Bx50.tInterval = nInterval

            
            # export data options
            print()
            print("Data export options:")
            print("1. Export as CSV files")
            print("2. Export as CSV files and JSON to URL")
            #print("Choose data export option (1-2):")
            #sDataExportset = input("Choose data export option (1-2):")
            sDataExportset = 1
            nDataExportset = 1
            if sDataExportset != " ":
                nDataExportset = int(sDataExportset)
                #write to csv file the estimation values
                now = datetime.now()
                dt_string = now.strftime("%d%m%Y")      
                header = ["TIME","ECG HR","NIBP1","NIBP2","NIBP-Mean","SPO2","T1","T2"]
                with open("GE650_SUM_" + dt_string + ".csv", 'a', encoding='UTF8', newline='') as f:                           
                    writer = csv.writer(f)
                    # write the header
                    writer.writerow(header)
                
            if nDataExportset == 2:
                print()
            # wave formate to receive data options
            print()
            print("Waveform data Transmission sets:")
            print("0. None")
            print("1. ECG1, INVP1, INVP2, PLETH")
            print("2. ECG1, INVP1, PLETH, CO2, RESP")
            print("3. ECG1, PLETH, CO2, RESP, AWP, VOL, FLOW")
            print("4. ECG1, ECG2")
            print("5. EEG1, EEG2, EEG3, EEG4")
            print("6. ECG1, ECG2, ECG3")
            #print("Choose Waveform data Transmission set (0-6):")
            #sWaveformSet = input("Choose Waveform data Transmission set (0-6):")
            sWaveformSet = 2
            nWaveformSet = 1
            if sWaveformSet != 0:
                nWaveformSet = int(sWaveformSet)
                Bx50.Waveset = nWaveformSet
                if nWaveformSet == 1:
                    now = datetime.now()
                    dt_string = now.strftime("%d%m%Y")
                    header = ["ECG1","INVP1","INVP2","PLETH"]
                    for i in header:
                        with open("GE650_"+ i +"_" + dt_string + ".csv", 'a', encoding='UTF8', newline='') as f:
                            writer = csv.writer(f)
                            x = ["Time",i]
                            writer.writerow(x)
                            f.close()
                if nWaveformSet == 2:
                    now = datetime.now()
                    dt_string = now.strftime("%d%m%Y")
                    header = ["ECG1","INVP1","PLETH","CO2","RESP"]
                    for i in header:
                        with open("GE650_"+ i +"_" + dt_string + ".csv", 'a', encoding='UTF8', newline='') as f:
                            writer = csv.writer(f)
                            x = ["Time",i]
                            writer.writerow(x)
                            f.close()
                elif nWaveformSet == 3:
                    now = datetime.now()
                    dt_string = now.strftime("%d%m%Y")
                    header = ["ECG1","PLETH","CO2","RESP","AWP","VOL","FLOW"]
                    for i in header:
                        with open("GE650_"+ i +"_" + dt_string + ".csv", 'a', encoding='UTF8', newline='') as f:
                            writer = csv.writer(f)
                            x = ["Time",i]
                            writer.writerow(x)
                            f.close()
                elif nWaveformSet == 4:
                    now = datetime.now()
                    dt_string = now.strftime("%d%m%Y")
                    header = ["ECG1","ECG2"]
                    for i in header:
                        with open("GE650_"+ i +"_" + dt_string + ".csv", 'a', encoding='UTF8', newline='') as f:
                            writer = csv.writer(f)
                            x = ["Time",i]
                            writer.writerow(x)
                            f.close()
                elif nWaveformSet == 5:
                    now = datetime.now()
                    dt_string = now.strftime("%d%m%Y")
                    header = ["EEG1","EEG2","EEG3","EEG4"]
                    for i in header:
                        with open("GE650_"+ i +"_" + dt_string + ".csv", 'a', encoding='UTF8', newline='') as f:
                            writer = csv.writer(f)
                            x = ["Time",i]
                            writer.writerow(x)
                            f.close()
                    
                elif nWaveformSet == 6:
                    now = datetime.now()
                    dt_string = now.strftime("%d%m%Y")      
                    header = ["ECG1","ECG2","ECG3","ECG4"]
                    for i in header:
                        with open("GE650_"+ i +"_" + dt_string + ".csv", 'a', encoding='UTF8', newline='') as f:
                            writer = csv.writer(f)
                            x = ["Time",i]
                            writer.writerow(x)
                            f.close()
            print()
            print("Requesting {0} second Transmission from monitor", nInterval)
            # Console.WriteLine("Requesting Transmission from monitor");
            print("Data will be written to CSV file AS3ExportData.csv in same folder")

            print()
            # Request transfer based on the DRI level of the monitor
            Bx50.RequestTransfer(Bx50.DRI_PH_DISPL, nInterval,Bx50.DRI_LEVEL_2005)  # Add Request Transmission
            Bx50.RequestTransfer(Bx50.DRI_PH_DISPL, nInterval,Bx50.DRI_LEVEL_2003)  # Add Request Transmission
            Bx50.RequestTransfer(Bx50.DRI_PH_DISPL, nInterval,Bx50.DRI_LEVEL_2001)  # Add Request Transmission
            print()
            # Request upto 8 waveforms but total sample rate should be less than 600 samples/sec
            # Sample rate for ECG is 300, INVP 100, PLETH 100, respiratory 25 each
            WaveTrtype = [0] * 8

            Bx50.CreateWaveformSet(nWaveformSet, WaveTrtype)
            #print(*WaveTrtype, sep = ",")

            if nWaveformSet != 0:
                print("Requesting Waveform data from monitor")
                print("Waveform data will be written to multiple CSV files in same folder")
                print()
                Bx50.RequestMultipleWaveTransfer(WaveTrtype, Bx50.WF_REQ_CONT_START,Bx50.DRI_LEVEL_2005)               
                Bx50.RequestMultipleWaveTransfer(WaveTrtype, Bx50.WF_REQ_CONT_START,Bx50.DRI_LEVEL_2003)               
                Bx50.RequestMultipleWaveTransfer(WaveTrtype, Bx50.WF_REQ_CONT_START,Bx50.DRI_LEVEL_2001)
                print()
                print("Press S button to Stop")
                Bx50.ReadBuffer(Bx50.dport)

        except AssertionError as error:
            print(error)

    def CreateWaveformSet(nWaveSetType, WaveTrtype):
        # Request upto 8 waveforms but total sample rate should be less than 600 samples/sec
        # Sample rate for ECG is 300, INVP 100, PLETH 100, respiratory 25 each
        x = Bx50
        if nWaveSetType == 0:
            pass
        elif nWaveSetType == 1:
            WaveTrtype[0] = x.ECG1
            WaveTrtype[1] = x.INVP1
            WaveTrtype[2] = x.INVP2
            WaveTrtype[3] = x.PLETH
            WaveTrtype[4] = x.DRI_EOL_SUBR_LIST

        elif nWaveSetType == 2:
            WaveTrtype[0] = x.ECG1
            WaveTrtype[1] = x.INVP1
            WaveTrtype[2] = x.PLETH
            WaveTrtype[3] = x.CO2
            WaveTrtype[4] = x.RESP
            WaveTrtype[5] = x.DRI_EOL_SUBR_LIST

        elif nWaveSetType == 3:
            WaveTrtype[0] = x.ECG1
            WaveTrtype[1] = x.PLETH
            WaveTrtype[2] = x.CO2
            WaveTrtype[3] = x.RESP
            WaveTrtype[4] = x.AWP
            WaveTrtype[5] = x.VOL
            WaveTrtype[6] = x.FLOW
            WaveTrtype[7] = x.DRI_EOL_SUBR_LIST

        elif nWaveSetType == 4:
            WaveTrtype[0] = x.ECG1
            WaveTrtype[1] = x.ECG2
            WaveTrtype[2] = x.DRI_EOL_SUBR_LIST

        elif nWaveSetType == 5:
            WaveTrtype[0] = x.EEG1
            WaveTrtype[1] = x.EEG2
            WaveTrtype[2] = x.EEG3
            WaveTrtype[3] = x.EEG4
            WaveTrtype[4] = x.DRI_EOL_SUBR_LIST

        elif nWaveSetType == 6:
            WaveTrtype[0] = x.ECG1
            WaveTrtype[1] = x.ECG2
            WaveTrtype[2] = x.ECG3
            WaveTrtype[3] = x.DRI_EOL_SUBR_LIST

        else:
            WaveTrtype[0] = x.ECG1
            WaveTrtype[1] = x.INVP1
            WaveTrtype[2] = x.INVP2
            WaveTrtype[3] = x.PLETH
            WaveTrtype[4] = x.DRI_EOL_SUBR_LIST

    def RequestTransfer(Trtype, Interval, DRIlevel):
        # Set Record Header
        Bx50.r_len = 49  # size of hdr + phdb type
        Bx50.r_dri_level = DRIlevel
        Bx50.r_time = 0
        Bx50.r_maintype = Bx50.DRI_MT_PHDB
        Bx50.sr_offset1 = 0
        Bx50.sr_type1 = 0;  # Physiological data request
        Bx50.sr_offset2 = 0
        Bx50.sr_type2 = 0xFF  # Last // Request transmission subrecord
        Bx50.tx_interval = Interval
        Bx50.phdb_rcrd_type = Trtype
        if Interval != 0:
            Bx50.phdb_class_bf = Bx50.DRI_PHDBCL_REQ_BASIC_MASK | Bx50.DRI_PHDBCL_REQ_EXT1_MASK | Bx50.DRI_PHDBCL_REQ_EXT2_MASK | Bx50.DRI_PHDBCL_REQ_EXT3_MASK
        else:
            Bx50.phdb_class_bf = 0x0000
        
        #print(Bx50.phdb_class_bf)
        # Get pointer to structure in memory
        try:

            Bx50.dataTx[0] = Bx50.r_len
            Bx50.dataTx[3] = Bx50.r_dri_level
            Bx50.dataTx[21] = Bx50.sr_type2
            Bx50.dataTx[40] = Bx50.phdb_rcrd_type
            Bx50.dataTx[41] = Bx50.tx_interval
            Bx50.dataTx[43] = Bx50.phdb_class_bf

            Bx50.WriteBuffer(Bx50.dataTx)
            #print(Bx50.dataTx)

        except AssertionError as error:
            print(error)

    def RequestMultipleWaveTransfer(TrWavetype, TrSignaltype, DRIlevel):
        # Set Record Header
        Bx50.r_len = 72;  # size of hdr + wfreq type
        Bx50.r_dri_level = DRIlevel;
        Bx50.r_time = 0;
        Bx50.r_maintype = Bx50.DRI_MT_WAVE;

        # The packet contains only one subrecord
        # 0 = Waveform data transmission request
        Bx50.sr_offset1 = 0
        Bx50.sr_type1 = Bx50.DRI_WF_CMD
        Bx50.sr_offset2 = 0
        Bx50.sr_type2 = Bx50.DRI_EOL_SUBR_LIST # Last subrecord

        # Request transmission subrecord
        # wave_request_ptr.wfreq.req_type = DataConstants.WF_REQ_CONT_START;
        Bx50.req_type = TrSignaltype
        Bx50.res = 0
        # wave_request_ptr.wfreq.type[0] = DataConstants.DRI_WF_ECG1;

        # wave_request_ptr.wfreq.type[0] = TrWavetype;
        # wave_request_ptr.wfreq.type[1] = DataConstants.DRI_EOL_SUBR_LIST;
        for i in range(0, 8, 1):
            Bx50.type[i] = TrWavetype[i]
            if i < 7:
                Bx50.type[i + 1] = Bx50.DRI_EOL_SUBR_LIST
        
        try:
            Bx50.dataWave[0] = Bx50.r_len
            Bx50.dataWave[3] = Bx50.r_dri_level
            Bx50.dataWave[21] = Bx50.sr_type2
            Bx50.dataWave[14] = Bx50.r_maintype
            Bx50.dataWave[40] = Bx50.req_type
            position = 44
            size = len(TrWavetype)
            n = 0            
            for i in range(0, size, 1):
                Bx50.dataWave[position] = TrWavetype[n]
                position = position + 1
                n = n + 1
            Bx50.WriteBuffer(Bx50.dataWave)
            #print(Bx50.dataWave)
        except AssertionError as error:
            print(error)

    def WriteBuffer(txbuf):
        framebyte = [Bx50.CTRLCHAR, Bx50.FRAMECHAR and Bx50.BIT5COMPL, 0]
        ctrlbyte = [Bx50.CTRLCHAR, Bx50.CTRLCHAR and Bx50.BIT5COMPL, 0]

        check_sum = 0
        b1 = 0
        b2 = 0

        txbuflen = len(txbuf) + 1

        # //Create write packet buffer
        temptxbuff = [0] * txbuflen

        for j in range(0, txbuflen - 1, 1):
            temptxbuff[j] = 0

        temptxbuff[0] = Bx50.FRAMECHAR

        i = 1

        for b in txbuf:
            if b == Bx50.FRAMECHAR:
                temptxbuff[i] = framebyte[0]
                temptxbuff[i + 1] = framebyte[1]
                i = i + 2
                b1 = b1 + framebyte[0]
                b1 = b1 + framebyte[1]
                check_sum = check_sum + b1


            elif b == Bx50.CTRLCHAR:
                temptxbuff[i] = ctrlbyte[0]
                temptxbuff[i + 1] = ctrlbyte[1]
                i = i + 2
                b2 = b2 + ctrlbyte[0]
                b2 = b2 + ctrlbyte[1]
                check_sum = check_sum + b2

            else:
                temptxbuff[i] = b
                if b == 255:
                    i = i + 1
                    check_sum = check_sum - 1
                else:
                    i = i + 1
                    check_sum = check_sum + b
        buflen = i
        finaltxbuff = [0] * (buflen + 2)

        for j in range(0, buflen, 1):
            finaltxbuff[j] = temptxbuff[j]

        # Send Checksum
        finaltxbuff[buflen] = check_sum
        # Send stop frame characters
        finaltxbuff[buflen + 1] = Bx50.FRAMECHAR
        try:           
            Bfinaltxbuff = bytes(finaltxbuff)           
            Bx50.dport.write(Bfinaltxbuff)           

        except AssertionError as error:
            print(error)

    def ClearReadBuffer():
        for i in range(0, Bx50.dportBufSize, 1):
            Bx50.dport_rxbuf[i] = 0

    def ReadBuffer(DPort):
        Bx50.ClearReadBuffer()
        try:                
            while True:
                bytesreadtotal = 0
                lenread = 0
            
                Bx50.dport_rxbuf = DPort.read(4096)
                lenread = len(Bx50.dport_rxbuf)               
                copyarray = [0] * lenread
    
                for i in range(0, lenread, 1):
                    copyarray[i] = Bx50.dport_rxbuf[i]
                    Bx50.CreateFrameListFromByte(copyarray[i])

                #if len(Bx50.DataECG)>15:
                    #Bx50.ExportWaveToCSV()

                
        except:            
            print('You Stoped Wave transmission..please wait')                           
            Bx50.StopTransfer()
            Bx50.StopwaveTransfer()
            #Bx50.dport.close()
            print('CSV successfully seved')
                
    def CreateFrameListFromByte(b):
        if b == Bx50.FRAMECHAR and Bx50.m_fstart:

            Bx50.m_fstart = False
            Bx50.m_storestart = True

        elif b == Bx50.FRAMECHAR and Bx50.m_fstart == False:

            Bx50.m_fstart = True
            Bx50.m_storeend = True
            Bx50.m_storestart = False

            if b != Bx50.FRAMECHAR:
               Bx50.m_bList.append(b)

        if Bx50.m_storestart == True:

            if b == Bx50.CTRLCHAR:
                Bx50.m_bitshiftnext = True

            else:
                if Bx50.m_bitshiftnext == True:
                    b |= Bx50.BIT5;
                    Bx50.m_bitshiftnext = False;
                    Bx50.m_bList.append(b)

                elif b != Bx50.FRAMECHAR:
                    Bx50.m_bList.append(b)

        elif Bx50.m_storeend == True:

            framelen = len(Bx50.m_bList)           
                    

            if framelen != 0:   
                bArray = [0]*framelen                                 
                bArray =Bx50.m_bList  
                                   
                Bx50.FrameList.append(bArray)
                if framelen ==  1153:
                    Bx50.Estimations(Bx50.m_bList)
                else:                    
                    Bx50.CreateRecordList(Bx50.m_bList)
                    Bx50.FrameList.clear()
                        
                            
                Bx50.m_bList.clear()
                Bx50.m_storeend = False                
            else:
                Bx50.m_storestart = True
                Bx50.m_storeend = False
                Bx50.m_fstart = False            

    def CreateRecordList(data):        
        recorddatasize = 0
        size = 1490                
        recorddatasize = len(data)
        fullrecord = [0]*1490
        dataRecord = [0]*1450

        for i in range(0,len(data),1):
            fullrecord[i] = data[i]           
              
        byteTime = bytes(fullrecord[6:10])
        timestamp = int.from_bytes(byteTime, byteorder='little', signed=False)           
        #Bx50.r_time = datetime.datetime.fromtimestamp(timestamp)
        Bx50.DataTime.append(timestamp)
        #wTime=Bx50.r_time.strftime('%Y-%m-%d %H:%M:%S')        

        datasave = 0        
        for n in range(40,len(fullrecord),1):
            if fullrecord[40] == 44:                
                dataRecord[datasave] =fullrecord[n]
                datasave += 1
        
        if len(dataRecord) > 0:            
            Bx50.ReadMultipleWaveSubRecords(dataRecord)           
            Bx50.dataRecord.clear()            

    def StopwaveTransfer():
        Bx50.RequestWaveTransfer(0, Bx50.WF_REQ_CONT_STOP, Bx50.DRI_LEVEL_2005)
        Bx50.RequestWaveTransfer(0, Bx50.WF_REQ_CONT_STOP, Bx50.DRI_LEVEL_2003)
        Bx50.RequestWaveTransfer(0, Bx50.WF_REQ_CONT_STOP, Bx50.DRI_LEVEL_2001)

    def StopTransfer():
        #RequestTransfer(DataConstants.DRI_PH_60S_TREND, 0);
        Bx50.RequestTransfer(Bx50.DRI_PH_DISPL, 0, Bx50.DRI_LEVEL_2005);
        Bx50.RequestTransfer(Bx50.DRI_PH_DISPL, 0, Bx50.DRI_LEVEL_2003);
        Bx50.RequestTransfer(Bx50.DRI_PH_DISPL, 0, Bx50.DRI_LEVEL_2001);

    def RequestWaveTransfer(TrWavetype, TrSignaltype, DRIlevel):
        # Set Record Header
        Bx50.r_len = 72;  # size of hdr + wfreq type
        Bx50.r_dri_level = DRIlevel;
        Bx50.r_time = 0;
        Bx50.r_maintype = Bx50.DRI_MT_WAVE;

        # The packet contains only one subrecord
        # 0 = Waveform data transmission request
        Bx50.sr_offset1 = 0
        Bx50.sr_type1 = Bx50.DRI_WF_CMD
        Bx50.sr_offset2 = 0
        Bx50.sr_type2 = Bx50.DRI_EOL_SUBR_LIST # Last subrecord

        # Request transmission subrecord
        # wave_request_ptr.wfreq.req_type = DataConstants.WF_REQ_CONT_START;
        Bx50.req_type = TrSignaltype
        Bx50.res = 0
        # wave_request_ptr.wfreq.type[0] = DataConstants.DRI_WF_ECG1;

        Bx50.type[0] = TrWavetype
        Bx50.type[1] = Bx50.DRI_EOL_SUBR_LIST

        try:
            Bx50.dataWave[0] = Bx50.r_len
            Bx50.dataWave[3] = Bx50.r_dri_level
            Bx50.dataWave[21] = Bx50.sr_type2
            Bx50.dataWave[14] = Bx50.r_maintype
            Bx50.dataWave[40] = Bx50.req_type

            Bx50.WriteBuffer(Bx50.dataWave)
            #print(Bx50.dataWave)
        except AssertionError as error:
            print(error)

    def ReadMultipleWaveSubRecords(data):
        sroffArray = Bx50.get_sroffArray(Bx50.type)                   
        dxrecordmaintype = Bx50.r_maintype           
        if dxrecordmaintype == Bx50.DRI_MT_WAVE:               
            srtypeArray = Bx50.type                
            unixtime = Bx50.r_time              
           
            for i in range(0, 8, 1):
                if srtypeArray[i] != Bx50.DRI_EOL_SUBR_LIST and srtypeArray[i] != 0:
                    offset = sroffArray[i]
                    nextoffset = 0
                    # read subrecord length from header to get nextoffset                            
                    srsamplelenbytes = [0] * 2
                    srsamplelenbytes[0] = data[offset]
                    srsamplelenbytes[1] = data[offset + 1]
                    srheaderlen = 6
                    subrecordlen = srheaderlen + int.from_bytes(srsamplelenbytes, byteorder='little', signed=False) * 2
                    nextoffset = offset + subrecordlen
                            
                    buflen = nextoffset - offset - 6
                    buffer = [0]*buflen 
                                            
                    for j in range(0, buflen, 1):                                
                        buffer[j] = data[6 + j + offset]                    
                            
                    validate = [-32001, -32767, -32766, -32765, -32764, -32763, -32762]                            
                    
                    WaveValList = []                    
                    for j in range(0, len(buffer), 2):
                        z = bytes(buffer[j:2 + j])
                        wavedata = int.from_bytes(z, byteorder='little', signed=True)
                        if wavedata in validate:
                            WaveValList.append(0)                         
                        else:
                            wavedata = round(wavedata*0.01,2)                 
                            WaveValList.append(wavedata)
                            #print(WaveValList)

                    #pleth data
                    now = datetime.now()
                    dt_string = now.strftime("%S") #"%H:%M:%S"
                    Bx50.DataECG.append(WaveValList)
                    if len(WaveValList)== 100:
                        Bx50.DataECGPlot.append(WaveValList)
                        print("pleth: ",WaveValList)
                        list = { 
                            'waveform_pleth' : WaveValList, 'time' : dt_string
                        }
                        with open("waveform_pleth.json", 'w') as file:
                            json.dump(list, file, indent = 4) 

                    #ecg data
                    elif len(WaveValList)== 300:
                        Bx50.DataECGPlotecg.append(WaveValList)
                        print("ecg: ",WaveValList)
                        list = { 
                            'waveform_ecg' : WaveValList
                        }
                        with open("waveform_ecg.json", 'w') as file:
                            json.dump(list, file, indent = 4) 

    def get_sroffArray(data):
         #sampling rates for each sensor
        ECG = 606  #sampling rate 300
        EEG = 206  #sampling rate 100
        INVP = 206   #sampling rate 100
        PLETH = 206  #sampling rate 100
        CO2 = 56  #sampling rate 25
        RESP = 56 #sampling rate 25
        AWP = 56 #sampling rate 25
        VOL = 56 #sampling rate 25
        FLOW = 56 #sampling rate 25       
        Bx50.PhysioID = []
        sroffArray = [0]*8
        next = 1
        start = 0

        for i in data:
            if i == 1:
                Bx50.PhysioID.append("ECG1")
                Bx50.Unitshift = 0.01
                sroffArray[next] = ECG
                next += 1
                start = ECG

            elif i == 2:
                Bx50.PhysioID.append("ECG2")
                Bx50.Unitshift = 0.01
                
                
            elif i == 3:
                Bx50.PhysioID.append("ECG3")
                Bx50.Unitshift = 0.01
                
            elif i == 4:
                Bx50.PhysioID.append("INVP1")
                Bx50.Unitshift = 0.01
                start = start + INVP
                sroffArray[next] = start 
                next += 1
            elif i == 5:
                Bx50.PhysioID.append("INVP2")
                Bx50.Unitshift = 0.01
                start = start + INVP
                sroffArray[next] = start 
                next += 1
            elif i == 6:
                Bx50.PhysioID.append("INVP3")
                Bx50.Unitshift = 0.01
                start = start + INVP
                sroffArray[next] = start 
                next += 1
            elif i == 7:
                Bx50.PhysioID.append("INVP4")
                Bx50.Unitshift = 0.01
                start = start + INVP
                sroffArray[next] = start 
                next += 1
            elif i == 8:
                Bx50.PhysioID.append("PLETH")
                Bx50.Unitshift = 0.01
                start = start + PLETH
                sroffArray[next] = start 
                next += 1
            elif i == 9:
                Bx50.PhysioID.append("CO2")
                Bx50.Unitshift = 0.01
                start = start + CO2
                sroffArray[next] = start 
                next += 1
            elif i == 10:
                Bx50.PhysioID.append("O2")
                Bx50.Unitshift = 0.01
                start = start + 56
                sroffArray[next] = start 
                next += 1
            elif i == 11:
                Bx50.PhysioID.append("N2O")
                Bx50.Unitshift = 0.01
                start = start + 56
                sroffArray[next] = start 
                next += 1
            elif i == 12:
                Bx50.PhysioID.append("AA")
                Bx50.Unitshift = 0.01
            elif i == 13:
                Bx50.PhysioID.append("AWP")
                Bx50.Unitshift = 0.1
                start = start + AWP
                sroffArray[next] = start 
                next += 1
            elif i == 14:
                Bx50.PhysioID.append("FLOW")
                Bx50.Unitshift = 0.01
                start = start + 56
                sroffArray[next] = start 
                next += 1
            elif i == 15:
                Bx50.PhysioID.append("RESP")
                Bx50.Unitshift = 0.01
                start = start + RESP
                sroffArray[next] = start 
                next += 1
            elif i == 16:
                Bx50.PhysioID.append("INVP5")
                Bx50.Unitshift = 0.01
            elif i == 17:
                Bx50.PhysioID.append("INVP6")
                Bx50.Unitshift = 0.01
            elif i == 18:
                Bx50.PhysioID.append("EEG1")
                Bx50.Unitshift = 1
                start = start + EEG
                sroffArray[next] = start 
                next += 1
            elif i == 19:
                Bx50.PhysioID.append("EEG2")
                Bx50.Unitshift = 1
                start = start + EEG
                sroffArray[next] = start 
                next += 1
            elif i == 20:
                Bx50.PhysioID.append("EEG3")
                Bx50.Unitshift = 1
                start = start + EEG
                sroffArray[next] = start 
                next += 1
            elif i == 21:
                Bx50.PhysioID.append("EEG4")
                Bx50.Unitshift = 1
                start = start + EEG
                sroffArray[next] = 0 
                next += 1
            elif i == 23:
                Bx50.PhysioID.append("VOL")
                Bx50.Unitshift = -1
                start = start + 56
                sroffArray[next] = start 
                next += 1
            elif i == 24:
                Bx50.PhysioID.append("TONO_PRESS")
                Bx50.Unitshift = 1
            elif i == 29:
                Bx50.PhysioID.append("SPI_LOOP_STATUS")
                Bx50.Unitshift = 1
            elif i == 32:
                Bx50.PhysioID.append("ENT_100")
                Bx50.Unitshift = 1
            elif i == 35:
                Bx50.PhysioID.append("EEG_BIS")
                Bx50.Unitshift = 1
        return sroffArray              

    def ExportWaveToCSV():        
        #for i in Bx50.PhysioID:
        ECG1 = 300
        ECG2 = 300
        ECG3 = 300
        INVP1 = 100
        INVP2  = 100                      
        PLETH  = 100
        CO2 = 100                                  
        AWP  = 100
        FLOW = 25
        RESP  = 25           
        EEG1  = 100
        EEG2  = 100
        EEG3  = 100
        EEG4  = 100
        VOL  = 25

        #full csv lists
        ECG1 = []
        ECG2 = []
        ECG3 = []
        INVP1 = []
        INVP2 = []
        INVP3 = []
        INVP4 = []
        PLETH = []
        AWP = []
        FLOW = []
        RESP= []
        INVP5 = []
        INVP6 = []
        EEG1 = []
        EEG2 = []
        EEG3 = []
        EEG4 = []
        VOL = []
        CO2 = []
       
        
        #Time for physiological data        
        
        data = Bx50.DataECG
        NewTime = Bx50.DataTime

        headerNames = Bx50.PhysioID        
        Tosave = len(Bx50.PhysioID)
        counter = 0
        counterTime = 0
        dataindex = 0
        ff1 = 3
        ff3 = 10
        ff2 = 0
        now = datetime.now()
        dt_string = now.strftime("%d%m%Y")
        dt_string1 = now.strftime("%m%d") 
        while dataindex != len(data):            
            #for i in headerNames:
            with open("GE650_"+headerNames[counter] + "_" + dt_string +'.csv', 'a', encoding='UTF8') as f:
                locals()[headerNames[counter]].append(data[dataindex])
                for j in data[dataindex]:
                    writer = csv.writer(f,lineterminator = '\n')                         
                    #for j in data:
                    if len(data[dataindex])==300:
                        saveTime = datetime.fromtimestamp(NewTime[counterTime])
                        wTime=saveTime.strftime('%H%M%S.')                    
                        ff2 += ff1
                        x = (dt_string[-2:]+ dt_string1 + wTime + f'{ff2:03}')
                        dataSave = [x, j]
                        # write the data                    
                        writer.writerow(dataSave)
                        
                    else:
                        saveTime = datetime.fromtimestamp(NewTime[counterTime])                        
                        wTime=saveTime.strftime('%H%M%S.')                    
                        ff2 += ff3
                        x = (dt_string[-2:] + dt_string1 + wTime + f'{ff2:03}')
                        dataSave = [x, j]
                        # write the data                    
                        writer.writerow(dataSave)

            ff2 = 0                        
            counter = counter + 1
            dataindex = dataindex + 1            
                
            if dataindex == len(data):
                Bx50.fullcsv(ECG1,ECG2,ECG3,INVP1,INVP2,PLETH,CO2,RESP,EEG1,EEG2,EEG3,EEG4,AWP,VOL,FLOW)
                break
                
            if counter == Tosave:
                counter = 0
                counterTime = counterTime + 1

    def Estimations(x):      
        HR = bytes(x[50:52])
        NIBP1 = bytes(x[122:124])
        NIBP2 = bytes(x[124:126])
        NIBP3 = bytes(x[126:128])
        SpO2 = bytes(x[168:170])
        T1 = bytes(x[136:138])
        T2 = bytes(x[144:146])
        y = int.from_bytes(HR,byteorder='little', signed=True)
        y1 = int.from_bytes(NIBP1,byteorder='little', signed=True)
        y2 = int.from_bytes(NIBP2,byteorder='little', signed=True)
        y3 = int.from_bytes(NIBP3,byteorder='little', signed=True)
        y4 = int.from_bytes(SpO2,byteorder='little', signed=True)
        y5 = int.from_bytes(T1,byteorder='little', signed=True)
        y6 = int.from_bytes(T2,byteorder='little', signed=True)
        estimations = [ ]
        estimations.append(y)
        estimations.append(y1)
        estimations.append(y2)
        estimations.append(y3)
        estimations.append(y4)
        estimations.append(y5)
        estimations.append(y6)

        Time = x[6:10]
        TimeBytes = bytes(Time)
        TimeInt = int.from_bytes(TimeBytes, byteorder='little', signed=True)
        timestamp = datetime.fromtimestamp(TimeInt)
        EstTime = timestamp.strftime('%H%M%S')       
        

        x = Bx50.validate(estimations)
        #addlist to tEstimation for time t
        Bx50.tEstimations.append(x)
        # print()
        # print(f"{EstTime} PyCapture Current Summary Data")
        # print(f"ECG HR {x[0]}/min NIBP {x[1]}/{x[2]}({x[3]})mmHg SpO2 {x[4]}% ETCO2 {0}mmHg")
        # print(f"IBP1 {0}/{0}({0})mmHg IBP2 {0}/{0}({0})mmHg MAC {0} T1 {x[5]}°C T2 {x[6]}°C")
        # print()  

        list = { 
            'HR' : int(x[0]) , 
            'NIBP_H' : int(x[1]) , 
            'NIBP_L' : int(x[2]) , 
            'NIBP_M' : int(x[3]), 
            'SpO2' : int(x[4]) ,
            'T' : x[6] 
        }

        with open("Estimations.json", 'w') as file:
            json.dump(list, file, indent = 4)                                    
                  
    def validate(list):
        validate = [-32001, -32767, -32766, -32765, -32764, -32763, -32762]
        newlist = []
        for i in list:
            if i in validate:
                newlist.append(0)
            else:
                if i == list[0]:
                    newlist.append(i*1)
                else:
                    newlist.append(round(i*0.01,2))

        return newlist

    def fullcsv(ECG1,ECG2,ECG3,INVP1,INVP2,PLETH,CO2,RESP,EEG1,EEG2,EEG3,EEG4,AWP,VOL,FLOW):
        now = datetime.now()
        dt_string = now.strftime("%d%m%Y%H%M%S")
        counterTime = 0
        NewTime = Bx50.DataTime
        values = Bx50.tEstimations       
        ntime = Bx50.tInterval       
        index = 0
        check = 1

        ECGHR = []
        NIBP1 = []
        NIBP2 = []
        NIBPm = []
        SPO2 = []
        T1 = []
        T2 = []
        

        for pp in range(0, len(ECG1), 1):
            ECGHR.append([""]*300)
            NIBP1.append([""]*300)
            NIBP2.append([""]*300)
            NIBPm.append([""]*300)
            SPO2.append([""]*300)
            T1.append([""]*300)
            T2.append([""]*300)

        for kk in range(ntime-1, len(ECG1), ntime):
            ECGHR[kk][-1] = values[index][check]
            NIBP1[kk][-1] = values[index][check + 1]
            NIBP2[kk][-1] = values[index][check+2]
            NIBPm[kk][-1] = values[index][check + 3]
            SPO2[kk][-1] = values[index][check+4]
            T1[kk][-1] = values[index][check + 5]
            T2[kk][-1] = values[index][check+6]
            index += 1

        header = ["TIME","ECG1","ECG2","ECG3","INVP1","INVP2","PLETH","CO2","RESP","EEG1","EEG2","EEG3","EEG4","AWP", "VOL", "FLOW","HR","NIBP1","NIBP2","NIBP-Mean","SPO2","T1","T2"]
        if len(ECG1)==0:
            ECG1 = [[""]] * len(EEG1)
        if len(ECG2)==0:
            ECG2 = [[""]] * len(ECG1)
        if len(ECG3)==0 :
            ECG3 = [[""]] * len(ECG1)
        if len(INVP1)==0:
            INVP1 = [[""]] * len(ECG1)
        if len(INVP2)==0:
            INVP2 = [[""]] * len(ECG1)
        if len(PLETH)==0:
            PLETH = [[""]] * len(ECG1)
        if len(CO2)==0:
            CO2 = [[""]] * len(ECG1)
        if len(RESP)==0:
            RESP = [[]] * len(ECG1)
        if len(EEG1)==0:
            EEG1 = [[""]] * len(ECG1)
        if len(EEG2)==0:
            EEG2 = [[""]] * len(ECG1)
        if len(EEG3)==0:
            EEG3 = [[""]] * len(ECG1)
        if len(EEG4)==0:
            EEG4 = [[""]] * len(ECG1)
        if len(AWP)==0:
            AWP = [[""]] * len(ECG1)
        if len(VOL)==0:
            VOL = [[""]] * len(ECG1)
        if len(FLOW)==0:
            FLOW = [[""]] * len(ECG1)  
        
        ff1 = 3
        ff2 = 0
        now = datetime.now()
        dt_string = now.strftime("%d%m%Y")
        dt_string1 = now.strftime("%m%d")
        file = open("GE650_CUR_ALL_"+dt_string +".csv", "a")
        writer = csv.writer(file,lineterminator = '\n')
        writer.writerow(header)
        for i in range(0,len(ECG1),1):
            ECGHR1=ECGHR[i]
            NIBP11=NIBP1[i]
            NIBP21=NIBP2[i]
            NIBPm1=NIBPm[i]
            SPO21=SPO2[i]
            T11=T1[i]
            T21=T2[i]

            ECG_1 = ECG1[i]
            ECG_2 = ECG2[i]
            ECG_3 = ECG3[i]

            INVP_1 = INVP1[i]
            INVP_2 = INVP2[i]           
            PLETH_0 = PLETH[i]
            CO2_0 = CO2[i]
            RESP_0 = RESP[i]
            EEG_1 = EEG1[i]
            EEG_2 = EEG2[i]
            EEG_3 = EEG3[i]
            EEG_4 = EEG4[i]
            AWP_0 = AWP[i]
            VOL_0 = VOL[i]
            FLOW_0 =FLOW[i]

            ex1 = []
            if len(INVP_1)<90:
                ex1=[""]*300
            else:
                for q in INVP_1:
                    ex1.extend([q]*3)

            ex2 = []
            if len(INVP_2)<90:
                ex2=[""]*300
            else:
                for r in INVP_2:
                    ex2.extend([r]*3)

            ex3 = []
            if len(PLETH_0)<90:
                ex3=[""]*300
            else:
                for t in PLETH_0:
                    ex3.extend([t]*3)          

            ex5 = []
            if len(RESP_0)==0:
                ex5=[""]*300
            else:
                for k in RESP_0:
                    ex5.extend([k]*12)
            
            
            ex15 = ECG_1
            #expanding data to ECG sampling rate       
         
            #ex4 = np.resize(CO2_0, (300))
            ex4=[""]*300          
            #ex6 = np.resize(EEG_1, (300))
            ex6=[""]*300
            #ex7 = np.resize(EEG_2, (300))
            ex7=[""]*300
            #ex8 = np.resize(EEG_3, (300))
            ex8=[""]*300
            #ex9 = np.resize(EEG_4, (300))
            ex9=[""]*300
            #ex10 = np.resize(AWP_0, (300))
            ex10=[""]*300
            #ex11 = np.resize(VOL_0, (300))
            ex11=[""]*300
            #ex12 = np.resize(FLOW_0, (300))
            ex12=[""]*300
            #ex13 = np.resize(ECG_2, (300))
            ex13=[""]*300
            #ex14 = np.resize(ECG_3, (300))
            ex14=[""]*300
            
            

            saveTime = datetime.fromtimestamp(NewTime[counterTime])
            wTime=saveTime.strftime('%H%M%S.')            

            for w in range(300):
                ff2 += ff1
                x = (dt_string[-2:] + dt_string1 + wTime + f'{ff2:03}')               
                writer.writerow([x,ex15[w],ex13[w],ex14[w],ex1[w],ex2[w],ex3[w],ex4[w],ex5[w],ex6[w],ex7[w],ex8[w],ex9[w],ex10[w],ex11[w],ex12[w],ECGHR1[w],NIBP11[w],NIBP21[w],NIBPm1[w],SPO21[w],T11[w],T21[w]])
            ff2 = 0
                
            counterTime = counterTime + 1

        #sending sensor data to oneM2M
    
        file.close()

Bx50.MainProgram()