"""Error handling examples for Graedin Cline SDK."""

from graedin_cline import GraedinClient
from graedin_cline.exceptions import (
    APIError,
    AuthenticationError,
    GraedinError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)


def example_with_fail_secure():
    """Example with fail-secure mode enabled (default)."""
    client = GraedinClient(
        api_key="your-api-key-here",
        base_url="http://localhost:8000",
        fail_secure=True,  # Default
        max_retries=3,
    )

    try:
        # Even if the API is down, fail-secure will return a "block" response
        # instead of raising an exception
        result = client.check_prompt("Test prompt")

        if result.attack_type == "system.fail_secure":
            print("⚠️ System error - failing secure (blocking prompt)")
            print(f"Reason: {result.reason}")
        elif result.is_safe:
            print("✅ Prompt is safe")
        else:
            print(f"⚠️ Blocked: {result.attack_type}")

    finally:
        client.close()


def example_without_fail_secure():
    """Example with fail-secure mode disabled."""
    client = GraedinClient(
        api_key="your-api-key-here",
        base_url="http://localhost:8000",
        fail_secure=False,  # Disabled
        max_retries=3,
    )

    try:
        result = client.check_prompt("Test prompt")
        print(f"Result: {result.attack_type}")

    except AuthenticationError:
        print("❌ Authentication failed - check your API key")

    except RateLimitError as e:
        print(f"❌ Rate limit exceeded: {e}")
        # You might want to back off and retry later

    except TimeoutError:
        print("❌ Request timed out - API might be slow or unavailable")

    except APIError as e:
        print(f"❌ API error: {e}")

    except ValidationError as e:
        print(f"❌ Validation error: {e}")

    except GraedinError as e:
        print(f"❌ Unexpected error: {e}")

    finally:
        client.close()


def example_with_retries():
    """Example showing retry behavior."""
    client = GraedinClient(
        api_key="your-api-key-here",
        base_url="http://localhost:8000",
        max_retries=5,  # Retry up to 5 times
        timeout=5.0,  # 5 second timeout per request
        fail_secure=True,
    )

    try:
        # The SDK will automatically retry on transient errors:
        # - Network timeouts
        # - 5xx server errors
        # - Temporary connection issues
        #
        # It uses exponential backoff between retries
        result = client.check_prompt("Test prompt")

        print(f"Result: {result.attack_type}")

    finally:
        client.close()


def example_handling_specific_attacks():
    """Example of handling specific attack types."""
    with GraedinClient(api_key="your-api-key-here", base_url="http://localhost:8000") as client:
        result = client.check_prompt("Your test prompt here")

        if result.is_safe:
            # Process the prompt normally
            print("✅ Safe to process")
            return

        # Handle specific attack types
        if result.attack_type == "injection.prompt":
            print("⚠️ Prompt injection detected")
            print("Action: Log and block user")

        elif result.attack_type == "injection.sql":
            print("⚠️ SQL injection attempt detected")
            print("Action: Log, block, and alert security team")

        elif result.attack_type == "abuse.spam":
            print("⚠️ Spam detected")
            print("Action: Rate limit user")

        elif result.attack_type == "system.fail_secure":
            print("⚠️ System error - fail secure mode activated")
            print("Action: Queue for manual review")

        else:
            print(f"⚠️ Unknown attack type: {result.attack_type}")
            print("Action: Block and log for review")

        # Log additional details
        print("\nDetails:")
        print(f"  Reason: {result.reason}")
        print(f"  Confidence: {result.confidence:.2%}")


if __name__ == "__main__":
    print("=== Fail-Secure Mode (Default) ===")
    example_with_fail_secure()

    print("\n=== Without Fail-Secure ===")
    example_without_fail_secure()

    print("\n=== With Custom Retries ===")
    example_with_retries()

    print("\n=== Handling Specific Attacks ===")
    example_handling_specific_attacks()
