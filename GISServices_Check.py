import urllib2, smtplib, datetime, base64, urllib, httplib, json
import arcpy, sys, traceback
from email.mime.text import MIMEText

# write messages to log file with time stamp
def writeMessage(message, logFile):
    timeStamp = time.strftime("%b %d %Y %H:%M:%S")
    with open(logFile, 'a') as f:
        f.write('\n{0} {1}\n'.format(timeStamp,message))
    print message
# end writeMessage

# Time stamp variables
currentTime = datetime.datetime.now()
#Date formatted as Calendar Name (e.g. June)
Date_Month = datetime.date.today().strftime("%B")
# Date formatted as month-day-year (20170612)
dateToday = currentTime.strftime("%Y%m%d")
# Date formated as month-day-year-hours-minutes-seconds
dateTodayTime = currentTime.strftime("%m-%d-%Y-%H-%M-%S")
# Date format for Email send out to SCTF Administrators and others
ServicesTime = time.strftime("%b %d %Y %H:%M:%S")

# Create text file for logging results of script
# Update file path with your parameters
# Each time the script runs, it creates a new text file with the date1 variable as part of the file name
# The example would be GeoprocessingReport_1-1-2017
logFile = r'C:\temp\GISServicesCheck_Report_{}.txt'.format(dateTodayTime)

writeMessage( """
#-------------------------------------------------------------------------------
# Name:        GISServices_Checks
#
# Purpose:     Checks GIS Services on GIS Server. If any services are down,
#              send an email notifying recipients
#
# Author:      Joseph Simora, York County Planning Commission
#
# Created:     11/19/2018
#
# Updated:
#
# Description: Checks GIS Services on GIS Server. If any services are down,
#              send an email notifying recipients
#-------------------------------------------------------------------------------
""", logFile)

writeMessage ("{}\n".format(__file__), logFile)

####################################  Script Variable Section  ################################################

# Server and Admin variables
#GIS Server Name
serverName = ""
#GIS Server Username
username = ""
#GIS Server Password
password = ""
# GIS Server Name Port that is opened for outside commuication
port = 80

# Rest URL of GIS Server (e.g "https://arcweb.ycpc.org/arcgis/rest")
RestURL = ""

#Email variables
# Email Server Name
# Emailserver = 'mail.sctfpa.org'
Emailserver = ""
# Email Server Name Port that is opened for outside commuication (Standard port is 465)
Eport = 465
#Email Server Username
Euser = ""
#Email Server Password
Epassword = ""
# Email Subject
subject = "ATTENTION: GIS SERVICES ARE DOWN"
# Email Sender
sender = ""
# recipient email(s). If you want to email more than one recipient use a commas to seperate emails.
# (e.g. 'jsimora@ycpc.org, joseph_simora@yahoo.com). The comma is used in the python script to split emails recipients
recipient = ""

####################################  Creating ArcGIS Token Section ################################################

# List to used to convert 'token' variable to text. I was not able to convert otherwise without error.
token_list = []

# Token URL is typically http://server[:port]/arcgis/admin/generateToken
# May have to change https to http depending on your SSL certificate
tokenURL = "https://{}/arcgis/admin/generateToken".format(serverName)

# URL-encode the token parameters:-
params = urllib.urlencode({'username': username, 'password': password, 'client': 'requestip', 'f': 'json'})

headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

# Connect to URL and post parameters
httpConn = httplib.HTTPConnection(serverName, port)
httpConn.request("POST", tokenURL, params, headers)

# Read response
response = httpConn.getresponse()
if (response.status != 200):
        httpConn.close()
        writeMessage ("Error while fetch tokens from admin URL. Please check the URL and try again.", logFile)
        #return
else:
        data = response.read()
        httpConn.close()

        # Extract the token from it
        token = json.loads(data)
        #writeMessage (token['token'], logFile)
        token_list.append(str(token['token']))

####################################  Connecting to GIS Server Section  ################################################

#List used to capture all secured or unsecured map services
GISservices = []

# For loop - Running thru service with proper token authentication. Token should access secured services.
# Loops thru services and appends service name into GISservices List
for t in token_list:
    baseUrl = "http://{}:{}/arcgis/admin/services".format(serverName, str(port))
    catalog = json.load(urllib2.urlopen(baseUrl + "/" + "?f=json&token=" + t))
    print 'Root'
    services = catalog['services']
    for service in services:
        response = json.load(urllib2.urlopen(baseUrl + '/' + service['serviceName'] + '/' + service['type'] + "?f=json&token=" + t))
        print '  %s %s (%s)' % (service['serviceName'], service['type'], 'ERROR' if "error" in response else 'SUCCESS')
        if service['type'] == "MapServer" or service['type'] == "GeocodeServer" or service['type'] == "GPServer":
            GISservices.append(service['serviceName'] + "/" + service['type'])
    folders = catalog['folders']
    for folderName in folders:
        catalog = json.load(urllib2.urlopen(baseUrl + "/" + folderName + "?f=json&token=" + t))
        print folderName
        services = catalog['services']
        for service in services:
            response = json.load(urllib2.urlopen(baseUrl + '/' + service['serviceName'] + '/' + service['type'] + "?f=json&token=" + t))
            print '  %s %s (%s)' % (service['serviceName'], service['type'], 'ERROR' if "error" in response else 'SUCCESS')
            if service['type'] == "MapServer" or service['type'] == "GeocodeServer" or service['type'] == "GPServer":
                if folderName != "Utilities" and folderName != "System":
                    GISservices.append(str(folderName) + "/" + service['serviceName'] + "/" + service['type'])

####################################  Check GIS Services Section  ################################################

# Negative and Positive Parameters
RestURLNeg =""
RestURLPos =""

# Check if services are running and operational. If services is operational, for loop populates 'RestURLPos'
# variable in the "try" section. If service is down, for loop populates 'RestURLNeg' variable in "except" sections
try:
    for s in GISservices:
        url ="%s/services/%s" %(RestURL,s)
        e = ""
        writeMessage(url, logFile)
        try:
            request = urllib2.Request(url)
            base64string = base64.b64encode('%s:%s' % (username, password))
            request.add_header("Authorization", "Basic %s" % base64string)
            result = urllib2.urlopen(request)
            writeMessage(result.code, logFile)
            RestURLPos = RestURLPos + "\n" + url + ": RESPONDING (code." + str(result.getcode()) + ")"
        except urllib2.HTTPError, e:
            writeMessage(e.code,logFile)
            RestURLNeg = RestURLNeg + "\n" + url + ": NOT RESPONDING (code." + str(e.code) + ")"
        except urllib2.URLError, e:
            writeMessage(e.args,logFile)
            writeMessage(e.reason.errno, logFile)
            RestURLNeg = RestURLNeg + "\n" + url +  ": NOT RESPONDING (cod." + str(e.reason.errno) + ")"

####################################  Email Recipients Section  ################################################

    # Email step
    # if there is any services down, following steps will send an email out to email recipients notifying
    # services are down.
    if RestURLNeg != "" :
        writeMessage("{} \n{} Service(s) is down\n".format(RestURLNeg, s.split("/")[-1]), logFile)

        if RestURLPos == "":
            RestURLPos = RestURLPos + "\n" + "No Map Services are running currently "

        # sender
        # sending client email (the source email)
        me = sender

        # recipient email
        you = recipient

        # e-mail message container
        # e-mail message
        msg = MIMEText("Hello All,\n \n\
 As of {}, the following GIS Services from {} are currently down. Please check GIS Services or contact the GIS Administrator to restart services\n \n\
 Current Map Services Down:\
             {} \n \n\
 Current Map Services Running:\
             {} \n \n\
 GIS Services should be up and running shortly \n \n".format(ServicesTime, serverName, RestURLNeg, RestURLPos))

        # e-mail subject
        msg['Subject'] = subject
        msg['From'] = me
        msg['To'] = you

        # server settings
        server = smtplib.SMTP_SSL(Emailserver, Eport)

        server.set_debuglevel(1)

        writeMessage("Created connection to e-mail server \n", logFile)

        # login to server
        server.login(Euser, Epassword)

        writeMessage("Logged in to e-mail server \n", logFile)

        # send message
        server.sendmail(me, you.split(','), msg.as_string())

        # close server
        server.quit()

        writeMessage("Closed connection to server \n", logFile)

    else:
        # if services are all running properly (RestURLNeg is empty)
        writeMessage(RestURLPos + "\n \n{} All GIS Services are operational\n".format(s.split("/")[-1]), logFile)

####################################  Finishing Steps  ################################################

# If an error occurs running geoprocessing tool(s) capture error and write message
# handle error outside of Python system
except EnvironmentError as ee:
    tbEE = sys.exc_info()[2]
    # Write the line number the error occured to the log file
    writeMessage("Failed at Line %i \n" % tbEE.tb_lineno, logFile)
    # Write the error message to the log file
    writeMessage("Error: {}".format(str(ee)), logFile)
# handle exception error
except Exception as e:
    # Store information about the error
    tbE = sys.exc_info()[2]
    # Write the line number the error occured to the log file
    writeMessage("Failed at Line %i \n" % tbE.tb_lineno,logFile)
    # Write the error message to the log file
    writeMessage("Error: {}".format(e.message), logFile)

writeMessage("Checking GIS Services Script is finished", logFile)
# Script Finished
