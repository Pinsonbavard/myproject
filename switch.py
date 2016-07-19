from flask import Flask, request, session, g, redirect, render_template, Response
#import asterisk.manager
import json
import uuid
import datetime
import MySQLdb
import MySQLdb.cursors
import time
import os

app = Flask(__name__)
app.secret_key = '123'
app.debug = True
ctx = app.app_context()
ctx.push()

@app.template_filter('pretty_duration')
def _jinja2_filter_pretty_duration(seconds):
	
	minutes, seconds = divmod(seconds, 60)
	return "%02d:%02d" % (minutes, seconds)

@app.template_filter('humandatetime')
def _jinja2_filter_humandatetime(date):
	date = date.replace(tzinfo=None)
	return date.strftime('%a&nbsp;%d&nbsp;%b&nbsp;%Y&nbsp;%H:%M')#.replace(' ', '&nbsp;')

@app.template_filter('humandate')
def _jinja2_filter_humandate(date):
	date = date.replace(tzinfo=None)
	return date.strftime('%a %d %b %Y')#.replace(' ', '&nbsp;')

@app.template_filter('humantime')
def _jinja2_filter_humantime(date):
	date = date.replace(tzinfo=None)
	return date.strftime('%H:%M')

@app.template_filter('humanage')
def _jinja2_filter_humanage(date):
	age = datetime.datetime.utcnow() - date
	if not age.days:
		if age.seconds < 10:
			return "just now"
		if age.seconds < 60:
			return "%d seconds ago"%age.seconds
		minutes = age.seconds / 60
		if minutes == 1:
			return "1 minute ago"
		if minutes < 60:
			return "%d minutes ago"%minutes
		hours = age.seconds /  3600
		if hours == 1:
			return "1 hour ago"
		if hours < 24:
			return "%d hours ago"%hours
	if age.days == 1:
		return "Yesterday"
	if age.days < 7:
		return "%d days ago"%age.days
	weeks = age.days / 7
	if weeks == 1:
		return "1 week ago"
	if weeks < 5:
		return "%d weeks ago"%weeks
	months = age.days / 31
	if months == 1:
		return "1 month ago"
	if months < 13:
		return "%d months ago"%months
	years = age.days / 365
	if years == 1:
		return "1 year ago"
	else:
		return "%d years ago"%years

@app.template_filter('asusertimezone')
def _jinja2_filter_asusertimezone(date, user):
	timezone = pytz.timezone(TIMEZONES[user['county']])
	return date.replace(tzinfo=pytz.UTC).astimezone(timezone).replace(tzinfo=None)

@app.teardown_appcontext
def close_db(error):
#	if hasattr(g, 'db'):
	g.db.close()

@app.before_request
def before_req():
	g.db = MySQLdb.connect(user="root", passwd="root", db="switch", cursorclass=MySQLdb.cursors.DictCursor)
	g.db.autocommit(True)

@app.route('/')
def main():
	return render_template('main.html')

@app.route('/customers')
def users():
	cur = g.db.cursor()
	cur.execute('select * from users order by created desc')
	users = cur.fetchall()
	users = [user.copy() for user in users]
	for user in users:
		cur.execute('select * from destinations where user_id=%s', (user['id'],))
		user['destinations'] = cur.fetchall()
	return render_template('users.html', users=users)

@app.route('/customers/<int:user_id>/edit')
@app.route('/customers/edit')
def user_edit(user_id=None):
	user = session.get('saved-user', {})
	if not user and user_id:
		cur = g.db.cursor()
		cur.execute('select * from users where id=%s', (user_id,))
		user = cur.fetchone()
		if not user:
			return redirect('/customers')
#	else:
#		user = session.pop('saved-user', {})
	return render_template('user-edit.html', user=user)

@app.route('/save-customer', methods=['POST'])
def user_save():
	user = request.form
	errors = []
	if not user['first_name']:
		errors.append('missing-first-name')
	if not user['last_name']:
		errors.append('missing-last-name')
	if not user['number']:
		errors.append('missing-number')
	if errors:
		user = user.copy()
		user['errors'] = errors
		session['saved-user'] = user
		if 'id' in user:
			return redirect('/customers/%s/edit'%user['id'])
		else:
			return redirect('/customers/edit')
	else:
		session.pop('saved-user', None)
		cur = g.db.cursor()
		if 'id' in user:
			cur.execute('update users set first_name=%s, last_name=%s, number=%s where id=%s', (user['first_name'], user['last_name'], user['number'], user['id']))
			return redirect('/customers/%s'%user['id'])
		else:
			cur.execute('insert into users (first_name, last_name, number, created) values(%s, %s, %s, utc_timestamp())', (user['first_name'], user['last_name'], user['number']))
			return redirect('/customers/%s'%cur.lastrowid)

@app.route('/customers/<int:user_id>')
def user(user_id):
	cur = g.db.cursor()
	cur.execute('select * from users where id=%s', (user_id,))
	user = cur.fetchone()
	if not user:
		return redirect('/customers')
	cur.execute('select * from destinations where user_id=%s', (user_id,))
	destinations = cur.fetchall()
	cur.execute('select distinct monthname(date) as month_name, month(date) as month, year(date) as year from calls where user_id=%s order by date desc', (user_id,))
	dates = cur.fetchall()
	return render_template('user.html', user=user, destinations=destinations, dates=dates)

@app.route('/customers/<int:user_id>/delete', methods=['GET', 'POST'])
def user_delete(user_id):
	cur = g.db.cursor()
	if request.method == 'GET':
		cur.execute('select * from users where id=%s', (user_id,))
		user = cur.fetchone()
		if not user:
			return redirect('/customers')
		return render_template('user-delete.html', user=user)
	if request.method == "POST":
		cur.execute('delete from destinations where user_id=%s', (user_id,))
		cur.execute('delete from calls where user_id=%s', (user_id,))
		cur.execute('delete from users where id=%s', (user_id,))
		return redirect('/customers')

@app.route('/customers/<int:user_id>/destinations/<int:destination_id>')
def destination(user_id, destination_id):
	cur = g.db.cursor()
	cur.execute('select *,users.first_name, users.last_name from destinations left join users on users.id=destinations.user_id where destinations.id=%s', (destination_id,))
	destination = cur.fetchone()
	if not destination:
		return redirect('/customers/%s'%user_id)
	return render_template('destination.html', destination=destination)

@app.route('/customers/<int:user_id>/destinations/edit')
@app.route('/customers/<int:user_id>/destinations/<int:destination_id>/edit')
def destination_edit(user_id, destination_id=None):
	destination = session.pop('saved-destination', {})
	if not destination and destination_id:
		cur = g.db.cursor()
		cur.execute('select * from destinations where id=%s', (destination_id,))
		destination = cur.fetchone()
		if not destination:
			return redirect('/customers/%s'%user_id)
		if destination['expires']:
			destination['day'] = str(destination['expires'].day)
			destination['month'] = str(destination['expires'].month)
			destination['year'] = str(destination['expires'].year)
	return render_template('destination-edit.html', destination=destination, user_id=user_id)

@app.route('/save-destination', methods=['POST'])
def destination_save():
	destination = request.form
	errors = []
	if not destination['did']:
		errors.append('missing-did')
	if not destination['number']:
		errors.append('missing-number')
	if destination['day'] or destination['month'] or destination['year']:
		if not destination['day']:
			errors.append('missing-day')
		if not destination['month']:
			errors.append('missing-month')
		if not destination['year']:
			errors.append('missing-year')
	expires = None
	if destination['day'] and destination['month'] and destination['year']:
		try:
			expires = datetime.datetime(day=int(destination['day']), month=int(destination['month']), year=int(destination['year']))
		except:
			errors.append('invalid-date')
	if errors:
		destination = destination.copy()
		destination['errors'] = errors
		session['saved-destination'] = destination
		if 'id' in destination:
			return redirect('/customers/%s/destinations/%s/edit'%(destination['user_id'], destination['id']))
		else:
			return redirect('/customers/%s/destinations/edit'%destination['user_id'])
	else:
		session.pop('saved-destination', None)
		cur = g.db.cursor()
		if 'id' in destination:
			cur.execute('update destinations set did=%s, number=%s, record=%s, auth_did=%s, auth_gw=%s, gateway=%s, channel=%s, own=%s, expires=%s where id=%s', (
					destination['did'], destination['number'], 'record' in destination, 'auth_did' in destination, 'auth_gw' in destination, destination['gateway'], destination['channel'], destination['own'], expires, destination['id']))
		else:
			cur.execute('insert into destinations (created, did, number, user_id, record, auth_did, auth_gw, gateway, channel, own, expires) values(utc_timestamp(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (
					destination['did'], destination['number'], destination['user_id'], 'record' in destination, 'auth_did' in destination, 'auth_gw' in destination, destination['gateway'], destination['channel'], destination['own'], expires))
		return redirect('/customers/%s'%destination['user_id'])

@app.route('/customers/<int:user_id>/destinations/<int:destination_id>/delete', methods=['GET', 'POST'])
def destination_delete(user_id, destination_id):
	cur = g.db.cursor()
	if request.method == 'GET':
		cur.execute('select * from destinations where id=%s', (destination_id,))
		destination = cur.fetchone()
		if not destination:
			return redirect('/customers/%s'%user_id)
		return render_template('destination-delete.html', destination=destination)
	if request.method == "POST":
		cur.execute('delete from destinations where id=%s', (destination_id,))
		return redirect('/customers/%s'%user_id)

@app.route('/customers/<int:user_id>/calls/<int:year>/<int:month>')
def user_calls(user_id, year, month):
	cur = g.db.cursor()
	cur.execute("""select *,users.first_name,users.last_name from calls left join users on calls.user_id=users.id
			where users.id=%s and month(date)=%s and year(date)=%s order by date desc""", (user_id, month, year))
	calls = cur.fetchall()
	return render_template('calls.html', calls=calls)

@app.route('/delete-recording')
def delete_recording():
	call_id = request.args['id']
	filename = '/var/spool/asterisk/monitor/%s.mp3'%call_id
	if os.path.isfile(filename):
		os.unlink(filename)
	cur = g.db.cursor()
	cur.execute('update calls set has_recording=null where id=%s', (call_id,))
	return redirect(request.args['url'])

def handle_event(event, manager):
	print event
	with ctx:
		if event.name == 'CoreShowChannel':
			user_id = event.message['AccountCode']
			data = {
					'user_id': user_id,
					'caller_id': event.message['CallerIDnum'],
					'channel': event.message['Channel'],
					'duration': event.message['Duration'],
					'context': event.message['Context'],
					'extension': event.message['Extension'],
					'line': event.message['ConnectedLineNum'],
					#'channel_state': event.message['ChannelState'],
					'channel_state': event.message['ChannelStateDesc'],
					}
			cur = g.db.cursor()
			cur.execute('select * from users where id=%s', (user_id,))
			user = cur.fetchone()
			if user:
				data.update({
						'first_name': user['first_name'],
						'last_name': user['last_name']
						})
			g.channels.append(data)
		if event.name == 'CoreShowChannelsComplete':
			g.complete = True

@app.route('/live-calls')
def live_calls():
	g.complete = False
	g.channels = []
	manager = asterisk.manager.Manager()
	manager.connect('localhost')
	manager.login('switch', 'switch')
	manager.register_event('*', handle_event)
	res = manager.send_action({'Action':'CoreShowChannels'})
	while not g.complete:
		time.sleep(0.1)
		print g.complete
	manager.close()
	return json.dumps(g.channels)

@app.route('/calls')
def calls():
	return render_template('live.html')

if __name__ == "__main__":
	#app.debug = True
	#app.run(host='0.0.0.0')
      app.run(debug=True,port=400)
