import pytest

from app.ai.orchestrator import Intent, IntentClassifier


class TestIntentClassifier:
    @pytest.fixture
    def classifier(self) -> IntentClassifier:
        return IntentClassifier()

    def test_classify_emergency(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("I have chest pain and difficulty breathing")
        assert intent == Intent.EMERGENCY
        assert score >= 0.9

    def test_classify_emergency_overdose(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("overdose emergency")
        assert intent == Intent.EMERGENCY
        assert score >= 0.9

    def test_classify_interaction_check(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("Can I take warfarin and ibuprofen together?")
        assert intent == Intent.INTERACTION_CHECK
        assert score >= 0.8

    def test_classify_interaction_check_direct(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("drug interaction between metformin and aspirin")
        assert intent == Intent.INTERACTION_CHECK
        assert score >= 0.8

    def test_classify_drug_info(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("tell me about the drug Augmentin")
        assert intent == Intent.DRUG_INFO
        assert score >= 0.8

    def test_classify_drug_info_side_effects(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("side effects of metformin")
        assert intent == Intent.DRUG_INFO
        assert score >= 0.8

    def test_classify_symptom_guidance(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("I have a bad headache and feel dizzy")
        assert intent == Intent.SYMPTOM_GUIDANCE
        assert score >= 0.7

    def test_classify_symptom_guidance_pain(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("my stomach hurts after eating")
        assert intent == Intent.SYMPTOM_GUIDANCE
        assert score >= 0.7

    def test_classify_medical_qa(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("What is the best treatment for high blood pressure?")
        assert intent == Intent.MEDICAL_QA
        assert score >= 0.6

    def test_classify_medical_qa_safety(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("is it safe to take ibuprofen with high blood pressure?")
        assert intent == Intent.MEDICAL_QA
        assert score >= 0.6

    def test_classify_general(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("What is the weather like today?")
        assert intent == Intent.GENERAL
        assert score < 0.5

    def test_classify_empty_message(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("")
        assert intent == Intent.UNKNOWN
        assert score == 0.0

    def test_classify_whitespace_message(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("   ")
        assert intent == Intent.UNKNOWN
        assert score == 0.0
