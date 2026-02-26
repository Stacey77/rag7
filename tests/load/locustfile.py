"""Load testing with Locust."""
from locust import HttpUser, task, between, events
import random


class AgentAPIUser(HttpUser):
    """Simulated user for load testing the Agent API."""
    
    # Wait between 1 and 3 seconds between tasks
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts."""
        self.client.verify = False  # For local testing
    
    @task(3)
    def health_check(self):
        """Health check endpoint (frequent)."""
        self.client.get("/health")
    
    @task(2)
    def ready_check(self):
        """Readiness check endpoint."""
        self.client.get("/ready")
    
    @task(1)
    def metrics_info(self):
        """Metrics info endpoint."""
        self.client.get("/metrics-info")
    
    @task(5)
    def root_endpoint(self):
        """Root endpoint."""
        self.client.get("/")


class HeavyLoadUser(HttpUser):
    """User for heavy load testing."""
    
    wait_time = between(0.5, 1.5)
    
    @task
    def concurrent_requests(self):
        """Make multiple concurrent requests."""
        endpoints = ["/health", "/ready", "/", "/metrics-info"]
        endpoint = random.choice(endpoints)
        self.client.get(endpoint)


# Custom events for tracking
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    print("Load test starting...")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops."""
    print("Load test completed!")
    
    # Print statistics
    stats = environment.stats
    print("\n=== Load Test Results ===")
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Total failures: {stats.total.num_failures}")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"Min response time: {stats.total.min_response_time}ms")
    print(f"Max response time: {stats.total.max_response_time}ms")
    print(f"Requests per second: {stats.total.total_rps:.2f}")
    print(f"95th percentile: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"99th percentile: {stats.total.get_response_time_percentile(0.99):.2f}ms")
