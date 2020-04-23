import csv
import itertools
from pathlib import Path

from pii_identifier.recognizers._spacy_recognizer_base import SpacyEntityRulerRecognizer


class DeStateRecognizer(SpacyEntityRulerRecognizer):
    """Recognize German state names in short and long form.

    The long form is also recognized in many declined forms.
    """

    def __init__(self):
        one_word_states = set()
        multi_word_states = set()

        for row in self._read_data():
            for name in row:
                if len(name.split()) == 1:
                    one_word_states.add(name)
                else:
                    multi_word_states.add(name)

        # [{"label": "STATE", "pattern": "Deutschland"}, ...]
        one_word_rules = self._create_rules(one_word_states, "STATE")

        multi_word_patterns = self._compute_multi_word_patterns(multi_word_states)
        # [{"label": "STATE", "pattern": [{"LEMMA": "Bundesrepublik"}, {"LEMMA": "Deutschland"}]}, ...]
        multi_word_rules = self._create_rules(multi_word_patterns, "STATE")

        self.state_rules = one_word_rules + multi_word_rules

    @property
    def rules(self):
        return self.state_rules

    def _read_data(self):
        path = Path(__file__).parent / "data" / "states.csv"
        with open(path) as csv_file:
            reader = csv.reader(csv_file, delimiter=";")
            return list(reader)

    def _compute_multi_word_patterns(self, name_with_multiple_words):
        """Compute several versions of entity ruler patterns for names with multiple words.

        States with multiple words aren't matched exactly but by matching against the lemma of each word.
        Frequently, `lemma(a_lemma)` is not the identity function which could matching lemma against lemma fail.
        Thus, we also add the original word to the pattern to catch cases where `lemma(word) == original_word`."""
        multi_word_states_patterns = []
        for name in name_with_multiple_words:
            # (["vereinigt", "Vereinigte"], ["Staat", "Staaten"])
            variants = self._get_variants(name)

            # [("vereinigt", "Staat"), ("vereinigt", "Staaten"), ... ]
            state_name_variants = itertools.product(*variants)

            for variant in state_name_variants:
                multi_word_states_patterns.append([{"LEMMA": sub} for sub in variant])
        return multi_word_states_patterns

    def _get_variants(self, words):
        """Get the lemma. Mostly to be able to detect declinations of adjectives later on."""
        from pii_identifier.backends.spacy_backend import nlp

        result = ()
        for word in words.split():
            # we want word itself to be a variant of word
            variants = [word]

            lemma = nlp(word)[0].lemma_
            if lemma != word:
                # the lemma is a version, too
                variants.append(lemma)

            result += (variants,)
        return result
