from opentelemetry.sdk.trace import SpanProcessor, TracerProvider

from brixo.filtering_by_scope_span_processor import (
    FilteringByScopeSpanProcessor,
)


class BrixoTracerProvider(TracerProvider):
    def __init__(
        self,
        default_blocked_scopes,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.default_blocked_scopes = default_blocked_scopes

    def add_span_processor(self, span_processor: SpanProcessor) -> None:
        if isinstance(span_processor, FilteringByScopeSpanProcessor):
            self._active_span_processor.add_span_processor(span_processor)
        else:
            self._active_span_processor.add_span_processor(
                FilteringByScopeSpanProcessor(
                    span_processor, blocked_scopes=self.default_blocked_scopes
                )
            )
