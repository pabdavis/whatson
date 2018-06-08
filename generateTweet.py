'''
whatson bot

bot runs every 15 minutes from 4am to 11pm
checks a specific twitter list for users
RTs last status from each user, waiting 30 seconds between users
If RT was already sent, it doesn't RT
every time it runs, it adds its everything it RTs to a log
it runs again at 12pm, sending an email reporting on its progress
it then clears the log so it can start again
'''
#import libraries
import time, tweepy, locale
from time import sleep
import smtplib
import datetime

#establish keys as global variables
secret_keys = []
run_time = datetime.datetime.now()

#hacky fix to solve unpredictable locale problems
try:
	locale.setlocale(locale.LC_ALL, 'en_US.utf8')
except:
	locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

#Our main worker function
def main():
	tweet()
	if _check_time(run_time):
		print "Time to send an email!"
		sendMail()

def sendMail():
	_get_secrets()
	session = smtplib.SMTP('smtp.gmail.com', 587)
	session.ehlo()
	session.starttls()
	session.login('whatson.wral', secret_keys[4])
	headers = "\r\n".join(["from: " + 'kantaro.wral',
		"subject: " + "@WhatsOnWRAL report for " + datetime.date.today().strftime('%m/%d/%Y'),
		#"to: " + 'tdukes@wral.com',
		"to: " + 'tdukes@wral.com'+',wgatlin@wral.com'
		"mime-version: 1.0",
		"content-type: text/html"])

	with open('dailylog.txt','r') as log:
		report = ''
		for line in log:
			report += line + '<br /><br />'

	with open('email-body.txt','r') as email:
		email_body = email.read()

	# body_of_email can be plaintext or html!
	content = headers + "\r\n\r\n" + email_body.format(report)

	session.sendmail('whatson.wral', ['tdukes@wral.com','wgatlin@wral.com'], content)

	#after the email is sent, clear out the file we use to store messages
	with open('dailylog.txt', 'w') as log_file:
		log_file.write('')

def tweet():
	#if it's after a specified time, overwrite log file

	#generate auth details and assign
	_get_secrets()
	consumer_key = secret_keys[0]
	consumer_secret = secret_keys[1]
	access_token = secret_keys[2]
	access_token_secret = secret_keys[3]

	try:

		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)

		#create tweepy object
		api = tweepy.API(auth)

		#gather user names to watch from twitter list
		#getting this list loads in the last tweets of each of these users
		user_list = []
		id_list = []
		for u in api.list_members('@WhatsOnWRAL', 'nbc-bot'):
			user_list.append(u.screen_name)
			id_list.append(u.status.id)
		print user_list

		#retweet each user
		with open('dailylog.txt', 'a') as log_file:
			for tweet_id in id_list:
				try:
					api.retweet(tweet_id)
					tweet = api.get_status(tweet_id).text
					print 'RTed. Waiting 30 seconds ...'
					log_file.write('RTed: ' + str(tweet.encode('utf-8')) + ' at ' + str(time.asctime(time.localtime(time.time()))) +'\n')
					sleep(30)
				except tweepy.TweepError, e:
					print 'Skipping:', e[0][0]['message']

	except tweepy.TweepError, e:
		with open('dailylog.txt', 'a') as log_file:
			log_file.write('Error sending tweet:', e[0][0]['message'])
			print 'Error sending tweet:', e[0][0]['message']

#utility function for retrieving secret keys
def _get_secrets():
	global secret_keys
	with open('.keys') as f:
		secret_keys = f.read().splitlines()

#utility function to check to see if bot is running in a certain time window
#should eventually set this to between 12 and 1 (noting local time) and set cron job
#to only run once that hour
def _check_time(time_to_check):
	window_start = time_to_check.replace(hour=5, minute=00, second=0, microsecond=0)
	window_end = time_to_check.replace(hour=5, minute=15, second=0, microsecond=0)
	if window_start <= time_to_check <= window_end:
		return True
	else:
		return False


if __name__ == '__main__':
	print 'Checking for tweets ...'
	main()
	print 'All done.'