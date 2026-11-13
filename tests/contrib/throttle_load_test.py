
"""
Load-generation script for the MQTT throttle plugin.

Simulates multiple MQTT clients publishing messages to a broker
and measures publishing throughput.

Run with:
    python tests/contrib/throttle_load_test.py

The broker must already be running.
"""

import argparse
import asyncio
import time

from amqtt.client import MQTTClient


async def publish_messages(client_number, uri, topic, message_count):
    """Connect one client and publish a specified number of messages."""

    client = MQTTClient()
    published = 0

    try:
        await client.connect(uri)

        for message_number in range(message_count):
            payload = (
                f"Client {client_number}: message {message_number}"
            ).encode()

            await client.publish(topic, payload)
            published += 1

    finally:
        await client.disconnect()

    return published


async def run_load_test(uri, topic, num_clients, messages_per_client):
    """Run multiple publishing clients and measure performance."""

    print("Starting MQTT load test...")
    print(f"Number of clients: {num_clients}")
    print(f"Messages per client: {messages_per_client}")

    start_time = time.perf_counter()

    results = await asyncio.gather(
        *[
            publish_messages(
                client_number,
                uri,
                topic,
                messages_per_client,
            )
            for client_number in range(num_clients)
        ]
    )

    elapsed_time = time.perf_counter() - start_time

    total_published = sum(results)
    throughput = total_published / elapsed_time if elapsed_time > 0 else 0

    print("\n--- Load Test Results ---")
    print(f"Total messages published: {total_published}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    print(f"Publishing throughput: {throughput:.2f} messages/second")


def main():
    parser = argparse.ArgumentParser(
        description="Generate MQTT publishing load."
    )

    parser.add_argument("--uri", default="mqtt://127.0.0.1:1883/")
    parser.add_argument("--topic", default="throttle/load-test")
    parser.add_argument("--clients", type=int, default=5)
    parser.add_argument("--messages", type=int, default=100)

    args = parser.parse_args()

    if args.clients < 1 or args.messages < 1:
        parser.error("--clients and --messages must be positive integers")

    asyncio.run(
        run_load_test(
            args.uri,
            args.topic,
            args.clients,
            args.messages,
        )
    )


if __name__ == "__main__":
    main()
