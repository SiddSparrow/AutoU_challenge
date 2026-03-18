from app.core.interfaces import Classifier
from app.services.classifier.claude_classifier import ClaudeClassifier


class ClassifierFactory:
    """Factory for creating classifier instances (Strategy Pattern)."""

    _classifiers: dict[str, type[Classifier]] = {
        "claude": ClaudeClassifier,
    }

    @staticmethod
    def create(provider: str = "claude") -> Classifier:
        classifier_class = ClassifierFactory._classifiers.get(provider)
        if classifier_class is None:
            raise ValueError(
                f"Unknown classifier provider: {provider}. "
                f"Available: {list(ClassifierFactory._classifiers.keys())}"
            )
        return classifier_class()
