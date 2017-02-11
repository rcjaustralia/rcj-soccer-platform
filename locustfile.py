from locust import HttpLocust, TaskSet, task

class UserBehavior(TaskSet):
	def on_start(self):
		pass

	@task(2)
	def index(self):
		self.client.get("/qld/soccer/app/results")

	"""@task(1)
	def random_game(self):
		for i in xrange(90, 227):
			self.client.get("/qld/soccer/app/results/{}".format(i))"""

class WebsiteUser(HttpLocust):
	task_set = UserBehavior
	min_wait=200
	max_wait=500