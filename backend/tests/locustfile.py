from locust import HttpUser, between, task


class SmartMediaUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def health(self):
        self.client.get('/api/health')

    @task(1)
    def privacy_policy(self):
        self.client.get('/api/privacy/policy')
