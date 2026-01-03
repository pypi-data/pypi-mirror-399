# SPDX-FileCopyrightText: 2025-present William Born <william.born.git@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Base classes and interfaces for cluster providers."""

from __future__ import annotations

import abc
import subprocess
import time
from typing import Any

from localargo.utils.cli import check_cli_availability, run_subprocess


class ClusterProvider(abc.ABC):
    """
    Abstract base class for Kubernetes cluster providers.

    Args:
        name (str): Name of the cluster.

    """

    def __init__(self, name: str = "localargo") -> None:
        self.name = name

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g., 'kind', 'k3s')."""

    @abc.abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is installed and available."""

    @abc.abstractmethod
    def create_cluster(self, **kwargs: Any) -> bool:  # noqa: ANN401
        """Create a new cluster with the provider."""

    @abc.abstractmethod
    def delete_cluster(self, name: str | None = None) -> bool:
        """Delete a cluster."""

    @abc.abstractmethod
    def get_cluster_status(self, name: str | None = None) -> dict[str, Any]:
        """Get cluster status information."""

    def get_context_name(self, cluster_name: str | None = None) -> str:
        """Get the kubectl context name for this cluster."""
        cluster_name = cluster_name or self.name
        return f"{self.provider_name}-{cluster_name}"

    def _ensure_kubectl_available(self) -> str:
        """
        Ensure kubectl is available and return its path.

        Returns:
            str: Path to kubectl executable

        Raises:
            FileNotFoundError: If kubectl is not found in PATH

        """
        kubectl_path = check_cli_availability("kubectl", "kubectl not found in PATH")
        if not kubectl_path:
            msg = "kubectl not found in PATH"
            raise FileNotFoundError(msg)
        return kubectl_path

    def _run_kubectl_command(
        self,
        cmd: list[str],
        **kwargs: Any,  # noqa: ANN401
    ) -> subprocess.CompletedProcess[str]:
        """
        Run a kubectl command with standardized error handling.

        Args:
            cmd (list[str]): kubectl command as list of strings
            **kwargs (Any): Additional arguments for subprocess.run

        Returns:
            subprocess.CompletedProcess[str]: CompletedProcess from subprocess.run

        """
        kubectl_path = self._ensure_kubectl_available()
        return run_subprocess([kubectl_path, *cmd], **kwargs)

    def _wait_for_cluster_ready(
        self,
        context_name: str,
        timeout: int = 300,
    ) -> None:
        """
        Wait for cluster to become ready by checking cluster-info.

        Args:
            context_name (str): kubectl context name for the cluster
            timeout (int): Maximum time to wait in seconds

        Raises:
            ClusterCreationError: If cluster doesn't become ready within timeout

        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self._run_kubectl_command(
                    ["cluster-info", "--context", context_name],
                    capture_output=True,
                    check=True,
                )
            except subprocess.CalledProcessError:
                time.sleep(2)
            else:
                return

        msg = f"Cluster '{self.name}' failed to become ready within {timeout} seconds"
        raise ClusterCreationError(msg)


class ProviderError(Exception):
    """Base exception for provider-related errors."""


class ProviderNotAvailableError(ProviderError):
    """Raised when a provider is not available."""


class ClusterCreationError(ProviderError):
    """Raised when cluster creation fails."""


class ClusterOperationError(ProviderError):
    """Raised when a cluster operation fails."""
