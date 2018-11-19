# Check-GIS-Map-Services

-------------------------------------------------------------------------------
 Name:        GISServices_Checks

 Purpose:     Checks GIS Services on GIS Server. If any services are down,
              send an email notifying recipients

 Author:      Joseph Simora, York County Planning Commission

 Created:     11/19/2018

 Updated:

 Description: Checks GIS Services on GIS Server. If any services are down,
              send an email notifying recipients
-------------------------------------------------------------------------------

Check GIS Server details and credentials prior to updating variables in this script.

Script is hardcoded. Scripts provided is a template. You will need to populate the variable section from Line 50 thru 81 to make this work properly.

Script will not run properly unless variables are properly populated. These are the variables that need populated.

Anything with a "" will need to be filled with additional information

Email and GIS Server ports will vary depending on your set up.

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

If you have any questions, let me know. 

Hope this helps. It was fun setting up
Joe Simora


