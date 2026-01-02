import logging
import re

from colorama import Fore
from opentelemetry.sdk.trace import SpanProcessor


class FilteringByScopeSpanProcessor(SpanProcessor):
    def __init__(
        self, delegate, allowed_scopes=None, blocked_scopes=None, required_root_span_attributes=None
    ):
        self._delegate = delegate
        self.allowed_scopes = tuple(allowed_scopes or ())
        self.blocked_scopes = tuple(blocked_scopes or ())
        self.required_root_span_attributes = dict(required_root_span_attributes or {})

    def on_end(self, span):
        scope_name = self._get_scope_name(span)

        if self._should_filter(scope_name):
            return

        self._validate_required_root_span_attributes(span)
        self._delegate.on_end(span)

    def _get_scope_name(self, span):
        scope = getattr(span, "instrumentation_scope", None)
        if scope is None:
            # older SDKs: fallback for backwards compatibility
            scope = getattr(span, "instrumentation_info", None)

        return getattr(scope, "name", None)

    def _should_filter(self, scope_name):
        if (
            self.allowed_scopes
            and scope_name
            and all(not re.match(pattern, scope_name) for pattern in self.allowed_scopes)
        ):
            return True
        return bool(
            self.blocked_scopes
            and scope_name
            and any(re.match(pattern, scope_name) for pattern in self.blocked_scopes)
        )

    def _validate_required_root_span_attributes(self, span):
        attributes = getattr(span, "attributes", {}) or {}

        if not (self.required_root_span_attributes and attributes.get("brixo.span.kind") == "ROOT"):
            return

        missing_attributes = [
            label
            for key, label in self.required_root_span_attributes.items()
            if key not in attributes
        ]

        if missing_attributes:
            logging.getLogger(__name__).warning(
                "%s[Brixo] The following required attributes are missing from your "
                "Brixo SDK traces: %s%s",
                Fore.YELLOW,
                ", ".join(missing_attributes),
                Fore.RESET,
            )

    def shutdown(self):
        self._delegate.shutdown()

    def force_flush(self, timeout_millis=None):
        return self._delegate.force_flush(timeout_millis)
