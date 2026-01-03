import os
import joblib

from tone.fusion.fused_classifier import FusedClassifier

from tone.rules.persuasive_rules import (
    persuasive_rule,
    PERSUASIVE_INTENT_VERBS
)
from tone.rules.questioning_rules import questioning_rule
from tone.rules.formal_rules import formal_rule
from tone.rules.assertive_rules import (
    assertive_rule,
    ASSERTIVE_INTENT_VERBS
)
from tone.rules.authoritative_rules import (
    authoritative_rule,
    AUTHORITATIVE_INTENT_VERBS
)
from tone.rules.narrative_rules import narrative_rule
from tone.rules.negation import is_negated_intent


class ToneAnalyzer:
    """
    Unified API for tone analysis (v1)
    """

    def __init__(self, artifacts_path: str):
        if not os.path.isdir(artifacts_path):
            raise ValueError(f"Invalid artifacts path: {artifacts_path}")

        self.persuasive = self._load(
            artifacts_path,
            "persuasive_model.joblib",
            persuasive_rule,
            alpha=0.6,
            neg_fn=is_negated_intent,
            verbs=PERSUASIVE_INTENT_VERBS
        )

        self.questioning = self._load(
            artifacts_path,
            "questioning_model.joblib",
            questioning_rule,
            alpha=0.8
        )

        self.formal = self._load(
            artifacts_path,
            "formal_model.joblib",
            formal_rule,
            alpha=0.4
        )

        self.assertive = self._load(
            artifacts_path,
            "assertive_model.joblib",
            assertive_rule,
            alpha=0.5,
            neg_fn=is_negated_intent,
            verbs=ASSERTIVE_INTENT_VERBS
        )

        self.authoritative = self._load(
            artifacts_path,
            "authoritative_model.joblib",
            authoritative_rule,
            alpha=0.5,
            neg_fn=is_negated_intent,
            verbs=AUTHORITATIVE_INTENT_VERBS
        )

        self.narrative = self._load(
            artifacts_path,
            "narrative_model.joblib",
            narrative_rule,
            alpha=0.6
        )

    def _load(
        self,
        base_path,
        filename,
        rule_fn,
        alpha,
        neg_fn=None,
        verbs=None
    ):
        path = os.path.join(base_path, filename)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Missing model artifact: {path}")

        model = joblib.load(path)

        return FusedClassifier(
            model=model,
            rule_fn=rule_fn,
            alpha=alpha,
            negation_fn=neg_fn,
            intent_verbs=verbs
        )

    def analyze(self, text: str) -> dict:
        """
        Analyze input text across all tone axes.
        """
        return {
            "persuasive": bool(self.persuasive.predict(text)),
            "questioning": bool(self.questioning.predict(text)),
            "formal": bool(self.formal.predict(text)),
            "assertive": bool(self.assertive.predict(text)),
            "authoritative": bool(self.authoritative.predict(text)),
            "narrative": bool(self.narrative.predict(text)),
        }
