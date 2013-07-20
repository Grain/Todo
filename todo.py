import gflags
import httplib2

import datetime

from collections import namedtuple
from operator import attrgetter

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run



Task = namedtuple('Task', 'description due')
daysofweek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

#returns the next "day" (of the week, 1-7) in "week" weeks
#does not include the current day
def nextDay(day, week):	
	temp = datetime.date.today()
	weekspassed = -1
	while weekspassed < week:
		temp = temp + datetime.timedelta(1)
		if temp.isoweekday() == day:
			weekspassed += 1
	return temp
	
def addTask(line):
	words = line.split(' ')
	lowerwords = line.lower().split(' ')
	index = -1
	try:
		index = lowerwords.index('due')
	except:	#no due date
		pass
	
	if index + 1 < len(words) and index != -1:	#an actual due date exists, probably
		tasks.append(Task(description = ' '.join(words[1:index]), due = convertDate(' '.join(lowerwords[index + 1:len(lowerwords)]))))
	else:	
		tasks.append(Task(description = ' '.join(words[1:len(words)]), due = datetime.date(1000, 1, 1)))
		
	sort()
	printTasks()
	writeTasks()
	
def sort():
	global tasks
	
	tasks = sorted(tasks, key=attrgetter('due'))


def readTasks():
	try:
		tempTasks = service.tasks().list(tasklist='@default').execute()

		for task in tempTasks['items']:
			if task['title'].strip() == '':
				service.tasks().delete(tasklist='@default', task=task['id']).execute()
			else:
				try:
					line = task['due'].split('T')[0].split('-')
					tempDate = datetime.date(int(line[0]), int(line[1]), int(line[2]))
				except:
					tempDate = datetime.date(1000, 1, 1)
				tasks.append(Task(description = task['title'], due = tempDate))
	except KeyError:	#no tasks
		pass

	sort()		
	printTasks()

def writeTasks():
	try:
		tempTasks = service.tasks().list(tasklist='@default').execute()

		for task in tempTasks['items']:
			service.tasks().delete(tasklist='@default', task=task['id']).execute()
	except KeyError:	#no tasks
		pass
	
	for task in tasks:
		if task.due == datetime.date(1000, 1, 1):
			temp = {'title': task.description}
		else:
			temp = {'title': task.description, 'due': task.due.isoformat() + 'T00:00:00.000Z'}
		service.tasks().insert(tasklist='@default', body=temp).execute()
	
def getInput():
	line = raw_input(">")
	if line.lower() == 'exit':
		return False
	elif line.lower() == 'show' or line.lower() == 'print':
		printTasks()
	elif str.find(line.lower(), "add ") == 0:
		addTask(line)
	elif str.find(line.lower(), "done ") == 0 or str.find(line.lower(), "finish ") == 0:
		try:
			tasks.pop(int(str.split(line, ' ')[-1]) - 1)
			printTasks()
			writeTasks()
		except:
			pass
	return True
	
def printTasks():
	i = 1
	print "=================================================="
	for task in tasks:
		print str(i),
		i += 1
		if task.due == datetime.date(1000, 1, 1):
			print task.description
		else:
			print task.description, "due", convertDate(task.due)
	print "=================================================="

def convertDate(temp):
	if type(temp) == datetime.date:
		if temp == datetime.date.today():
			return "Today"
		elif temp == datetime.date.today() - datetime.timedelta(1):
			return "Yesterday"
		elif temp == datetime.date.today() + datetime.timedelta(1):
			return "Tomorrow"
		elif (temp - datetime.date.today()).days < -1 and (temp - datetime.date.today()).days >= -7:
			return "Last " + daysofweek[temp.weekday()]
		elif (temp - datetime.date.today()).days > 1 and (temp - datetime.date.today()).days <= 7:
			return daysofweek[temp.weekday()]
		elif (temp - datetime.date.today()).days > 7 and (temp - datetime.date.today()).days <= 14:
			return "Next " + daysofweek[temp.weekday()] 
		else:
			return months[temp.month - 1] + " " + str(temp.day)
	elif type(temp) == str:
		words = temp.split(' ')
		lowermonths = []
		lowerdays = []
		
		for month in months:
			lowermonths.append(month.lower())
		for day in daysofweek:
			lowerdays.append(day.lower())
		
		if len(words) == 2:
			if words[0] == 'next':
				if len(words[1]) >= 3:
					for i, day in enumerate(lowerdays, start=1):
						if str.find(day, words[1]) == 0:
							return nextDay(i, 1)
			else:
				if len(words[0]) >= 3:
					for i, month in enumerate(lowermonths, start=1):
						if str.find(month, words[0]) == 0:
							try:
								tempdate = datetime.date(datetime.date.today().year, i, int(words[1]))
								if (tempdate - datetime.date.today()).days < 0:
									return datetime.date(datetime.date.today().year + 1, i, int(words[1]))
								else:
									return tempdate
							except:
								pass
		elif len(words) == 1:
			if len(words[0]) >= 3:
				if str.find('tomorrow', words[0]) == 0:
					return datetime.date.today() + datetime.timedelta(1)
				elif str.find('today', words[0]) == 0:
					return datetime.date.today()
				for i, day in enumerate(lowerdays, start=1):
					if str.find(day, words[0]) == 0:
						return nextDay(i, 0)
			
		return datetime.date(1000, 1, 1)
print "Connecting to Google Tasks..."

FLAGS = gflags.FLAGS

# Set up a Flow object to be used if we need to authenticate. This
# sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
# the information it needs to authenticate. Note that it is called
# the Web Server Flow, but it can also handle the flow for native
# applications
# The client_id and client_secret are copied from the API Access tab on
# the Google APIs Console
FLOW = OAuth2WebServerFlow(
	client_id='YOUR_CLIENT_ID',
	client_secret='YOUR_CLIENT_SECRET',
	scope='https://www.googleapis.com/auth/tasks',
	user_agent='TODO/0.1')

# To disable the local server feature, uncomment the following line:
# FLAGS.auth_local_webserver = False

# If the Credentials don't exist or are invalid, run through the native client
# flow. The Storage object will ensure that if successful the good
# Credentials will get written back to a file.
storage = Storage('todo.dat')
credentials = storage.get()
if credentials is None or credentials.invalid == True:
	credentials = run(FLOW, storage)

# Create an httplib2.Http object to handle our HTTP requests and authorize it
# with our good Credentials.
http = httplib2.Http()
http = credentials.authorize(http)

# Build a service object for interacting with the API. Visit
# the Google APIs Console
# to get a developerKey for your own application.
service = build(serviceName='tasks', version='v1', http=http,
	developerKey='YOUR_DEVELOPERKEY')

print "Done."

tasks = []

readTasks()
while getInput():
	pass
