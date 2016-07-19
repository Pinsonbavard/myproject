#!/usr/bin/python

import asterisk.agi
import asterisk.manager
import sys

agi = asterisk.agi.AGI()
src = agi.env['agi_arg_1']
dst = agi.env['agi_arg_2']

manager = asterisk.manager.Manager()
manager.connect('localhost')
manager.login('switch', 'switch')

manager.originate('Local/%s@callback-dial/n'%src, exten=dst, context='callback-answer', priority='1', async=True, timeout='60000', variables={})
manager.close()
