#!/usr/bin/env python3
"""Generate LLM cost report from Prometheus metrics."""
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List

try:
    import requests
except ImportError:
    print("Installing required packages...")
    os.system("pip install requests pandas matplotlib")
    import requests


def fetch_prometheus_metrics(prometheus_url: str, query: str, start: str, end: str) -> Dict:
    """Fetch metrics from Prometheus.
    
    Args:
        prometheus_url: Prometheus server URL
        query: PromQL query
        start: Start time (ISO format)
        end: End time (ISO format)
        
    Returns:
        Query results
    """
    url = f"{prometheus_url}/api/v1/query_range"
    params = {
        "query": query,
        "start": start,
        "end": end,
        "step": "1h",
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def generate_cost_report():
    """Generate cost report from metrics."""
    prometheus_url = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
    
    # Calculate time range (last 24 hours)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=1)
    
    # Format times for Prometheus
    start = start_time.isoformat() + "Z"
    end = end_time.isoformat() + "Z"
    
    print("# LLM Cost Report")
    print(f"\nGenerated: {datetime.utcnow().isoformat()}")
    print(f"Time Range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}")
    print("\n" + "=" * 80)
    
    # Query for total costs per model
    cost_query = 'sum by (model, provider) (increase(llm_cost_usd_total[24h]))'
    
    try:
        results = fetch_prometheus_metrics(prometheus_url, cost_query, start, end)
        
        if results.get("status") != "success":
            print("\n⚠️  Failed to fetch metrics from Prometheus")
            return
        
        data = results.get("data", {}).get("result", [])
        
        if not data:
            print("\n📊 No cost data available for the specified time range")
            return
        
        print("\n## Cost by Model and Provider\n")
        
        total_cost = 0.0
        model_costs = []
        
        for item in data:
            metric = item.get("metric", {})
            model = metric.get("model", "unknown")
            provider = metric.get("provider", "unknown")
            
            values = item.get("values", [])
            if values:
                # Get the latest value
                cost = float(values[-1][1])
                total_cost += cost
                model_costs.append((model, provider, cost))
        
        # Sort by cost (descending)
        model_costs.sort(key=lambda x: x[2], reverse=True)
        
        # Print table
        print(f"{'Model':<20} {'Provider':<15} {'Cost (USD)':>12}")
        print("-" * 50)
        
        for model, provider, cost in model_costs:
            print(f"{model:<20} {provider:<15} ${cost:>11.2f}")
        
        print("-" * 50)
        print(f"{'TOTAL':<36} ${total_cost:>11.2f}")
        
        # Query for token usage
        print("\n## Token Usage\n")
        
        token_query = 'sum by (model, token_type) (increase(llm_token_usage_total[24h]))'
        token_results = fetch_prometheus_metrics(prometheus_url, token_query, start, end)
        
        if token_results.get("status") == "success":
            token_data = token_results.get("data", {}).get("result", [])
            
            print(f"{'Model':<20} {'Type':<10} {'Tokens':>15}")
            print("-" * 50)
            
            for item in token_data:
                metric = item.get("metric", {})
                model = metric.get("model", "unknown")
                token_type = metric.get("token_type", "unknown")
                
                values = item.get("values", [])
                if values:
                    tokens = int(float(values[-1][1]))
                    print(f"{model:<20} {token_type:<10} {tokens:>15,}")
        
        # Query for API call counts
        print("\n## API Call Statistics\n")
        
        calls_query = 'sum by (model, status) (increase(llm_api_calls_total[24h]))'
        calls_results = fetch_prometheus_metrics(prometheus_url, calls_query, start, end)
        
        if calls_results.get("status") == "success":
            calls_data = calls_results.get("data", {}).get("result", [])
            
            print(f"{'Model':<20} {'Status':<10} {'Calls':>10}")
            print("-" * 45)
            
            total_success = 0
            total_errors = 0
            
            for item in calls_data:
                metric = item.get("metric", {})
                model = metric.get("model", "unknown")
                status = metric.get("status", "unknown")
                
                values = item.get("values", [])
                if values:
                    calls = int(float(values[-1][1]))
                    print(f"{model:<20} {status:<10} {calls:>10,}")
                    
                    if status == "success":
                        total_success += calls
                    elif status == "error":
                        total_errors += calls
            
            total_calls = total_success + total_errors
            if total_calls > 0:
                error_rate = (total_errors / total_calls) * 100
                print("-" * 45)
                print(f"\nTotal Calls: {total_calls:,}")
                print(f"Success Rate: {(total_success/total_calls)*100:.2f}%")
                print(f"Error Rate: {error_rate:.2f}%")
        
        # Recommendations
        print("\n## Recommendations\n")
        
        if total_cost > 100:
            print("⚠️  High daily costs detected (>${:.2f})".format(total_cost))
            print("   Consider:")
            print("   - Implementing more aggressive caching")
            print("   - Using cheaper models for simple tasks")
            print("   - Reducing max_tokens limits")
        
        if model_costs:
            most_expensive = model_costs[0]
            print(f"\n💡 Most expensive model: {most_expensive[0]} (${most_expensive[2]:.2f})")
            print("   Consider using cheaper alternatives for non-critical tasks")
        
        # Save to file
        with open("cost-report.md", "w") as f:
            f.write(f"# LLM Cost Report\n\n")
            f.write(f"Generated: {datetime.utcnow().isoformat()}\n")
            f.write(f"Total Daily Cost: ${total_cost:.2f}\n")
        
        # Save CSV for further analysis
        with open("cost-report.csv", "w") as f:
            f.write("model,provider,cost_usd\n")
            for model, provider, cost in model_costs:
                f.write(f"{model},{provider},{cost:.2f}\n")
        
        print("\n✅ Reports saved: cost-report.md, cost-report.csv")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error connecting to Prometheus: {e}")
        print(f"   Tried: {prometheus_url}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error generating report: {e}")
        sys.exit(1)


if __name__ == "__main__":
    generate_cost_report()
