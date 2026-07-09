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

    def test_classify_contraindication_check(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("Is it safe to take ibuprofen with a history of ulcers?")
        assert intent == Intent.CONTRAINDICATION_CHECK
        assert score >= 0.6

    def test_classify_contraindication_check_direct(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("contraindication of metformin in kidney disease")
        assert intent == Intent.CONTRAINDICATION_CHECK
        assert score >= 0.6

    def test_classify_dosage_verify(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("verify the dosage of amoxicillin for a child")
        assert intent == Intent.DOSAGE_VERIFY
        assert score >= 0.6

    def test_classify_dosage_verify_is_correct(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("is the dose of metformin 500mg correct?")
        assert intent == Intent.DOSAGE_VERIFY
        assert score >= 0.6

    def test_classify_prescription_explain(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("explain this prescription to me")
        assert intent == Intent.PRESCRIPTION_EXPLAIN
        assert score >= 0.6

    def test_classify_doctor_assist(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("doctor assist: review these medications")
        assert intent == Intent.DOCTOR_ASSIST
        assert score >= 0.6

    def test_classify_doctor_assist_review(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("prepare a medication review for my patient")
        assert intent == Intent.DOCTOR_ASSIST
        assert score >= 0.6

    def test_classify_pharmacy_assist(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("pharmacy assist review this prescription")
        assert intent == Intent.PHARMACY_ASSIST
        assert score >= 0.6

    def test_classify_pharmacy_assist_alternative(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("what are the alternatives for metformin")
        assert intent == Intent.PHARMACY_ASSIST
        assert score >= 0.6

    def test_classify_reminders(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("remind me to take my medication")
        assert intent == Intent.REMINDERS
        assert score >= 0.6

    def test_classify_reminder_schedule(self, classifier: IntentClassifier) -> None:
        intent, score = classifier.classify("set a reminder for my medication schedule")
        assert intent == Intent.REMINDERS
        assert score >= 0.6