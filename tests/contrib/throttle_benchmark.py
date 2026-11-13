
"""
Benchmarking framework for MQTT rate-limiting algorithms.

Accepts any rate limiter implementing the shared allow() interface.
This allows token bucket and sliding window implementations
to be compared using the same workload.
"""

import time


def benchmark_limiter(
    name,
    limiter,
    num_clients=5,
    messages_per_client=1000,
):
    """Measure the performance of one rate limiter."""

    allowed = 0
    rejected = 0

    start_time = time.perf_counter()

    for client_number in range(num_clients):
        client_id = f"client_{client_number}"

        for _ in range(messages_per_client):
            if limiter.allow(client_id):
                allowed += 1
            else:
                rejected += 1

    elapsed_time = time.perf_counter() - start_time

    total_messages = allowed + rejected

    throughput = (
        total_messages / elapsed_time
        if elapsed_time > 0
        else 0
    )

    return {
        "algorithm": name,
        "allowed": allowed,
        "rejected": rejected,
        "elapsed_seconds": elapsed_time,
        "throughput": throughput,
    }


def print_comparison(results):
    """Display benchmark results for multiple algorithms."""

    print("\n========== RATE LIMITER BENCHMARK ==========")

    for result in results:
        print(f"\nAlgorithm: {result['algorithm']}")
        print(f"Allowed messages: {result['allowed']}")
        print(f"Rejected messages: {result['rejected']}")
        print(
            f"Time elapsed: "
            f"{result['elapsed_seconds']:.6f} seconds"
        )
        print(
            f"Throughput: "
            f"{result['throughput']:.2f} messages/second"
        )

    print("\n============================================")


# Once both implementations are available, create one instance
# of each and pass them to benchmark_limiter().
#
# Example:
#
# token_results = benchmark_limiter(
#     "Token Bucket", token_bucket_limiter
# )
#
# window_results = benchmark_limiter(
#     "Sliding Window", window_limiter
# )
#
# print_comparison([token_results, window_results])
