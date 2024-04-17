#
#	03.2024 W.Jee 
#
#	KLMC3 Profiler.py supportive functions
#
# ----------------------------------------------------------
from datetime import datetime

# Global time reference (1970-01-01 00:00:00 UTC)
_UTC_TIME_REF = [1970,1,1]

# Define a mapping from ordinal numbers to integers for day
_ORDINAL_NUMBERS = {
    '1st': 1, '2nd': 2, '3rd': 3, '4th': 4, '5th': 5,
    '6th': 6, '7th': 7, '8th': 8, '9th': 9, '10th': 10,
    '11th': 11, '12th': 12, '13th': 13, '14th': 14, '15th': 15,
    '16th': 16, '17th': 17, '18th': 18, '19th': 19, '20th': 20,
    '21st': 21, '22nd': 22, '23rd': 23, '24th': 24, '25th': 25,
    '26th': 26, '27th': 27, '28th': 28, '29th': 29, '30th': 30, '31st': 31
}
# Define a mapping from month name to month number
_MONTH_NUMBERS = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5,
    'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10,
    'November': 11, 'December': 12
}

def gulp_get_time(s_datetime):

	# format example: '18:07.20 14th November 2023'

	global _ORDINAL_NUMBERS, _MONTH_NUMBERS
	global _UTC_TIME_REF

	parts = s_datetime.split()
	
	# Extract the time and date parts
	time_part = parts[0]  # Should contain '18:07.20'
	date_part = ' '.join(parts[1:])  # Join remaining parts for the date
	
	# Parse the time component
	time_components = time_part.split(':')
	hour = int(time_components[0])  # Extract hour
	minute = int(time_components[1].split('.')[0])  # Extract minute
	second = int(time_components[1].split('.')[1])  # Extract second
	
	# Extract day number, month name, and year from the date part
	day_number, month_name, year = date_part.split()
	
	# Convert the ordinal day number to an integer
	day = _ORDINAL_NUMBERS[day_number]
	# Convert the month name to its corresponding number
	month = _MONTH_NUMBERS[month_name]
	
	# Create a datetime object from parsed components
	dt_object = datetime(year=int(year), month=month, day=day,
	                           hour=hour, minute=minute, second=second)
	
	# Calculate the absolute time in seconds (since epoch)
	#absolute_time_seconds = dt_object.timestamp()
	absolute_time_seconds = (dt_object - datetime(_UTC_TIME_REF[0],_UTC_TIME_REF[1],_UTC_TIME_REF[2])).total_seconds()

	# GULP DOES NOT SUPPORT MICROSECOND
	microsecond = 0

	rdt = {
		'year':year, 'month':month, 'day':day,
		'hour':hour, 'minute':minute, 'second':second, 'microsecond':microsecond,
		'abs':absolute_time_seconds,
	}

	return rdt

def klmc_get_time(s_datetime):

	# format example: '2023-11-14 18:07:01.983661'

	global _UTC_TIME_REF

	dt_object = datetime.strptime(s_datetime,'%Y-%m-%d %H:%M:%S.%f')

	# Extract individual components
	year = dt_object.year
	month = dt_object.month
	day = dt_object.day
	hour = dt_object.hour
	minute = dt_object.minute
	second = dt_object.second
	microsecond = dt_object.microsecond

	# Calculate absolute time in seconds: referenced to _UTC_TIME_REF
	absolute_time_seconds = (dt_object - datetime(_UTC_TIME_REF[0],_UTC_TIME_REF[1],_UTC_TIME_REF[2])).total_seconds()

	rdt = {
		'year':year, 'month':month, 'day':day,
		'hour':hour, 'minute':minute, 'second':second, 'microsecond':microsecond,
		'abs':absolute_time_seconds,
	}

	return rdt

if __name__=='__main__':
	
	# Test time strings
	# (1) GULP  6.1.2 FORMAT: 18:07.02 14th November   2023
	# (2) KLMC3       FORMAT: Job Finished at 18:07.20 14th November   2023
	
	# Input string
	klmc3_input_string = '2023-11-14 18:07:01.983661'

	# Test KLMC3 format	
	ls = klmc3_input_string.split()
	print(ls)	# ['2023-11-14', '18:07:01.983661']
	
	t = klmc_get_time(klmc3_input_string)
	print(t)
	print(t.keys())						# Possible Output: dict_keys(['year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond', 'abs'])
	for key in t.keys():
		print(f'{key} : {t[key]}')		

	# Possible Output
	'''
		year : 2023
		month : 11
		day : 14
		hour : 18
		minute : 7
		second : 1
		microsecond : 983661
		abs : 1699985221.983661
	'''

	# Test GULP format
	gulp_input_string = '18:07.02 14th November   2023'

	t = gulp_get_time(gulp_input_string)

	print(t.keys())
	for key in t.keys():
		print(f'{key} : {t[key]}')

	print(t)
