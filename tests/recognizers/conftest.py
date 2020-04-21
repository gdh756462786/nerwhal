import pytest

from pii_identifier.recognizers import FlairStatisticalRecognizer
from pii_identifier.recognizers import SpacyStatisticalRecognizer


@pytest.fixture(params=[SpacyStatisticalRecognizer(), pytest.param(FlairStatisticalRecognizer(), marks=pytest.mark.slow)])
def stat_recognizer(request):
    return request.param


@pytest.fixture
def set_up_backend():
    def function(recognizer):
        if recognizer.backend == "spacy":
            from pii_identifier.backends.spacy_backend import SpacyBackend

            backend = SpacyBackend()
        elif recognizer.backend == "re":
            from pii_identifier.backends.re_backend import ReBackend

            backend = ReBackend()
        elif recognizer.backend == "flair":
            from pii_identifier.backends.flair_backend import FlairBackend

            backend = FlairBackend()
        else:
            raise ValueError(f"Unknown backend {recognizer.backend}")

        backend.register_recognizer(recognizer)
        return backend

    return function


@pytest.fixture
def embed():
    def function(text, piis):
        """
        This assumes piis to be sorted ascending and non-overlapping.
        """

        for pii in reversed(piis):
            text = text[: pii.start] + pii.type + text[pii.end :]
        return text

    return function