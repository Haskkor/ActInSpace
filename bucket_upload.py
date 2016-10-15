#!/usr/bin/env python

#
# Copyright 2014 Jeff Faudi.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Some parts inspired from paultuckey_s3_bucket_to_bucket_copy.py
#

import boto
import boto.s3
from boto.s3 import connect_to_region
from boto.s3.key import Key
import sys
import os
from Queue import LifoQueue
import threading
import time
import ConfigParser

class Worker(threading.Thread):
	def __init__(self, queue, thread_id, bucket, root_path, aws_key, aws_secret):
		threading.Thread.__init__(self)
		self.queue = queue
		self.done_count = 0
		self.thread_id = thread_id

		self.bucket = bucket
		self.root_path = root_path
		self.aws_key = aws_key
		self.aws_secret = aws_secret

		self.s3_b = None
		self.s3_b = None

	def __init_s3(self):
		print '  t%s: connect to s3\n' % self.thread_id

		# region can be 'eu-west-1' or 'us-east-1' for older buckets
		s3_c = boto.s3.connect_to_region('eu-west-1', aws_access_key_id=self.aws_key, aws_secret_access_key=self.aws_secret)
		self.s3_b = s3_c.get_bucket(self.bucket, validate=True)

	def run(self):
		while True:
			try:
				if self.done_count % 1000 == 0:  # re-init conn to s3 every 1000 copies as we get failures sometimes
					self.__init_s3()
				path = self.queue.get()
				key_name = path.replace('\\', '/')
				filename = os.path.join(self.root_path, path)
				key = self.s3_b.get_key(key_name)

				if not key or not key.exists():
					print '  t%s: uploading: %s' % (self.thread_id, key_name)
					key = Key(self.s3_b)
					key.key = key_name
					key.set_metadata('Content-Type', 'image/jpeg')
					key.set_contents_from_filename(filename, policy='public-read', reduced_redundancy=True)
				else:
					print '  t%s: exists already: %s' % (self.thread_id, key_name)

				self.done_count += 1
			except BaseException:
				print '  t%s: error during upload' % self.thread_id)
			self.queue.task_done()


def upload(root_path, bucket, aws_id, aws_key):

	max_workers = 20
	q = LifoQueue(maxsize=5000)

	for i in range(max_workers):
		print 'Adding worker thread %s for queue processing' % i
		t = Worker(q, i, bucket, root_path, aws_id, aws_key)
		t.daemon = True
		t.start()

	total = 0
	# https://docs.python.org/2/library/os.html
	for root, dirs, files in os.walk(root_path):
		for name in files:
			relative = root.split(root_path + os.sep)[1]
			path = os.path.join(relative, name)
			#print 'Adding %s to the queue' % path
			q.put(path)
			total += 1

			while q.qsize() > (q.maxsize - max_workers):
				time.sleep(10)  # sleep if our queue is getting too big for the next set of keys

	print 'Waiting for queue to be completed'
	q.join()

	print 'Done'


def main():

	def usage(msg=None):
		if msg:
			sys.stderr.write('\n%s\n\n' % msg)
		sys.stderr.write(''.join(['\nUsage: %s local_root_path S3_bucket [aws_access_key_id aws_secret_access_key]\n']) % sys.argv[0])
		sys.exit(1)

	config = ConfigParser.RawConfigParser()
	config.read('main.cfg')
	aws_access_key_id = config.get('awscredentials', 'aws_access_key_id')
	aws_secret_access_key = config.get('awscredentials', 'aws_secret_access_key')

	if len(sys.argv) == 3:
	   	msg = ''
		if aws_access_key_id == '':
			msg += 'Configuration file does not contain aws_access_key_id.\n'
		if aws_secret_access_key == '':
			msg += 'Configuration file does not contain aws_secret_access_key.\n'
		if msg:
			usage(msg + 'Please set aws credentials in environment or pass them in.')
		# root_path = "H:/WorldMap10"
		root_path = sys.argv[1]
		bucket = sys.argv[2]
		upload(root_path, bucket, aws_access_key_id, aws_secret_access_key)
	elif len(sys.argv) == 5:
		root_path = sys.argv[1]
		bucket = sys.argv[2]
		aws_id = sys.argv[3]
		aws_key = sys.argv[4]
		upload(root_path, bucket, aws_id, aws_key)
	else:
		usage()

if __name__ == '__main__':
	main()