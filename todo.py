from datetime import date
from datetime import timedelta
from collections import namedtuple
from operator import attrgetter

Task = namedtuple('Task', 'description due')
daysofweek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

#returns the next "day" (of the week, 1-7) in "week" weeks
#does not include the current day
def nextDay(day, week):	
	temp = date.today()
	weekspassed = -1
	while weekspassed < week:
		temp = temp + timedelta(1)
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
		tasks.append(Task(description = ' '.join(words[1:len(words)]), due = date(1000, 1, 1)))
		
	sort()
	printTasks()
	writeFile()
	
def sort():
	global tasks
	
	tasks = sorted(tasks, key=attrgetter('due'))


def readFile():
	try:
		f = open("todo.txt", "r")
		lines = str.split(f.read(), "\n")
		f.close()
	except:
		printTasks()
		return
	
	for i in lines:	
		line = str.split(i, ' ')
		if len(line) >= 2:
			tempdate = str.split(line[-1], '-')
			if len(tempdate) >= 3:
				tasks.append(Task(description = " ".join(line[0:len(line) - 1]), due = date(int(tempdate[0]), int(tempdate[1]), int(tempdate[2]))))
	
	sort()		
	printTasks()

def writeFile():
	f = open("todo.txt", "w")
	for task in tasks:
		f.write(task.description + " " + str(task.due) + '\n')
	f.close()
	
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
			writeFile()
		except:
			pass
	return True
	
def printTasks():
	i = 1
	print "=================================================="
	for task in tasks:
		print str(i),
		i += 1
		if task.due == date(1000, 1, 1):
			print task.description
		else:
			print task.description, "due", convertDate(task.due)
	print "=================================================="

def convertDate(temp):
	if type(temp) == date:
		if temp == date.today():
			return "Today"
		elif temp == date.today() - timedelta(1):
			return "Yesterday"
		elif temp == date.today() + timedelta(1):
			return "Tomorrow"
		elif (temp - date.today()).days < -1 and (temp - date.today()).days >= -7:
			return "Last " + daysofweek[temp.weekday()]
		elif (temp - date.today()).days > 1 and (temp - date.today()).days <= 7:
			return daysofweek[temp.weekday()]
		elif (temp - date.today()).days > 7 and (temp - date.today()).days <= 14:
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
								tempdate = date(date.today().year, i, int(words[1]))
								if (tempdate - date.today()).days < 0:
									return date(date.today().year + 1, i, int(words[1]))
								else:
									return tempdate
							except:
								pass
		elif len(words) == 1:
			if len(words[0]) >= 3:
				if str.find('tomorrow', words[0]) == 0:
					return date.today() + timedelta(1)
				elif str.find('today', words[0]) == 0:
					return date.today()
				for i, day in enumerate(lowerdays, start=1):
					if str.find(day, words[0]) == 0:
						return nextDay(i, 0)
			
		return date(1000, 1, 1)

tasks = []

readFile()
while getInput():
	pass
