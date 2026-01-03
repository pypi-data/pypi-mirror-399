"""Tests for provider registry functionality."""

# SPDX-FileCopyrightText: 2025-present William Born <william.born.git@gmail.com>
#
# SPDX-License-Identifier: MIT

import pytest

from localargo.providers.kind import KindProvider
from localargo.providers.registry import PROVIDERS, get_provider, list_available_providers


class TestProviderRegistry:
    """Test suite for provider registry."""

    def test_get_provider_kind(self) -> None:
        """Test getting kind provider."""
        provider_class = get_provider("kind")

        assert provider_class == KindProvider

    def test_get_provider_unknown_raises_error(self) -> None:
        """Test getting unknown provider raises ValueError."""
        with pytest.raises(ValueError, match=r"Unknown provider: unknown. Available providers: kind"):
            get_provider("unknown")

    def test_list_available_providers(self) -> None:
        """Test listing available providers."""
        providers = list_available_providers()
        assert providers == ["kind"]

    def test_get_provider_case_sensitive(self) -> None:
        """Test provider names are case sensitive."""
        # Should work for lowercase
        provider_class = get_provider("kind")
        assert provider_class is not None

        # Should fail for uppercase
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("KIND")

    def test_registry_imports(self) -> None:
        """Test that registry imports work correctly."""
        # This test ensures our imports in registry.py work
        assert "kind" in PROVIDERS

        assert PROVIDERS["kind"] == KindProvider
