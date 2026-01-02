"""Tests for retry utilities."""

import pytest

from yoinkr.utils.retry import RetryConfig, RetryHandler, with_retry


class TestRetryConfig:
    """Tests for RetryConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 30.0

    def test_get_delay_exponential(self):
        """Test exponential backoff delay."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=(0, 0))

        # Without jitter for predictable testing
        delay0 = config.get_delay(0)
        delay1 = config.get_delay(1)
        delay2 = config.get_delay(2)

        assert delay0 == 1.0  # 1 * 2^0
        assert delay1 == 2.0  # 1 * 2^1
        assert delay2 == 4.0  # 1 * 2^2

    def test_get_delay_max_cap(self):
        """Test delay is capped at max_delay."""
        config = RetryConfig(base_delay=10.0, max_delay=15.0, jitter=(0, 0))

        delay = config.get_delay(5)  # Would be 320 without cap
        assert delay == 15.0

    def test_should_retry_within_limit(self):
        """Test should retry within limit."""
        config = RetryConfig(max_retries=3)

        assert config.should_retry(Exception("error"), 0) is True
        assert config.should_retry(Exception("error"), 2) is True
        assert config.should_retry(Exception("error"), 3) is False

    def test_should_retry_exception_type(self):
        """Test should retry based on exception type."""
        config = RetryConfig(retry_on=(ValueError,))

        assert config.should_retry(ValueError("error"), 0) is True
        assert config.should_retry(TypeError("error"), 0) is False

    def test_should_retry_custom_condition(self):
        """Test should retry with custom condition."""
        config = RetryConfig(retry_if=lambda e: "retry" in str(e))

        assert config.should_retry(Exception("please retry"), 0) is True
        assert config.should_retry(Exception("do not"), 0) is False


class TestRetryHandler:
    """Tests for RetryHandler."""

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful execution without retry."""
        handler = RetryHandler()

        async def success_func():
            return "success"

        result = await handler.execute(success_func)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_execute_retry_then_success(self):
        """Test retry then success."""
        config = RetryConfig(max_retries=3, base_delay=0.01)
        handler = RetryHandler(config)

        attempts = []

        async def flaky_func():
            attempts.append(1)
            if len(attempts) < 3:
                raise ValueError("temporary error")
            return "success"

        result = await handler.execute(flaky_func)

        assert result == "success"
        assert len(attempts) == 3

    @pytest.mark.asyncio
    async def test_execute_max_retries_exceeded(self):
        """Test max retries exceeded."""
        config = RetryConfig(max_retries=2, base_delay=0.01)
        handler = RetryHandler(config)

        async def always_fails():
            raise ValueError("always fails")

        with pytest.raises(ValueError, match="always fails"):
            await handler.execute(always_fails)

    @pytest.mark.asyncio
    async def test_execute_sync_function(self):
        """Test executing sync function."""
        handler = RetryHandler()

        def sync_func():
            return "sync result"

        result = await handler.execute(sync_func)
        assert result == "sync result"


class TestWithRetryDecorator:
    """Tests for @with_retry decorator."""

    @pytest.mark.asyncio
    async def test_decorator_success(self):
        """Test decorator with successful function."""

        @with_retry()
        async def success_func():
            return "success"

        result = await success_func()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_decorator_retry(self):
        """Test decorator with retry."""
        attempts = []

        @with_retry(RetryConfig(max_retries=3, base_delay=0.01))
        async def flaky_func():
            attempts.append(1)
            if len(attempts) < 2:
                raise ValueError("temporary")
            return "success"

        result = await flaky_func()

        assert result == "success"
        assert len(attempts) == 2

    @pytest.mark.asyncio
    async def test_decorator_max_retries(self):
        """Test decorator max retries."""

        @with_retry(RetryConfig(max_retries=1, base_delay=0.01))
        async def always_fails():
            raise ValueError("error")

        with pytest.raises(ValueError):
            await always_fails()
