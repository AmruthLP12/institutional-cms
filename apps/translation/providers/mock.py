"""
apps/translation/providers/mock.py — Mock translation provider for tests, local dev, and demonstrations.
"""

from apps.translation.providers.base import BaseTranslationProvider

# Common institutional phrases translated for realism in test/demos
MOCK_DICTIONARY: dict[str, dict[str, str]] = {
    "kn": {
        "Nakashara": "ನಕಾಶರ",
        "Home": "ಮುಖಪುಟ",
        "News": "ಸುದ್ದಿ",
        "Events": "ಕಾರ್ಯಕ್ರಮಗಳು",
        "People": "ಸಿಬ್ಬಂದಿ ಮತ್ತು ಅಧ್ಯಾಪಕರು",
        "Departments": "ವಿಭಾಗಗಳು",
        "Research": "ಸಂಶೋಧನೆ",
        "Documents": "ದಾಖಲೆಗಳು",
        "Policies": "ನೀತಿಗಳು",
        "Contact": "ಸಂಪರ್ಕಿಸಿ",
        "About": "ನಮ್ಮ ಬಗ್ಗೆ",
        "Privacy Policy": "ಗೌಪ್ಯತೆ ನೀತಿ",
        "Terms of Service": "ಸೇವಾ ನಿಯಮಗಳು",
    },
    "hi": {
        "Nakashara": "नकाशरा",
        "Home": "मुख्य पृष्ठ",
        "News": "समाचार",
        "Events": "आयोजन",
        "People": "संकाय एवं कर्मचारी",
        "Departments": "विभाग",
        "Research": "अनुसंधान",
        "Documents": "दस्तावेज़",
        "Policies": "नीतियां",
        "Contact": "संपर्क",
        "About": "हमारे बारे में",
        "Privacy Policy": "गोपनीयता नीति",
        "Terms of Service": "सेवा की शर्तें",
    },
}

LANGUAGE_PREFIXES: dict[str, str] = {
    "kn": "[ಕನ್ನಡ] ",
    "hi": "[हिन्दी] ",
}


class MockTranslationProvider(BaseTranslationProvider):
    """
    Deterministic mock provider that simulates machine translation without network calls.
    Used during test suites and in development environments.
    """

    name = "mock"

    def translate_text(
        self, text: str, target_language: str, source_language: str = "en", is_html: bool = False
    ) -> str:
        if not text:
            return text

        clean_text = text.strip()
        # Look up in standard institutional dictionary if exact match
        dict_map = MOCK_DICTIONARY.get(target_language, {})
        if clean_text in dict_map:
            translated = dict_map[clean_text]
            return text.replace(clean_text, translated)

        # Prepend language prefix if not already present
        prefix = LANGUAGE_PREFIXES.get(target_language, f"[{target_language}] ")
        if text.startswith(prefix):
            return text

        if is_html:
            # For HTML text, wrap content or prepend safely
            if text.startswith("<p>") and text.endswith("</p>"):
                return f"<p>{prefix}{text[3:]}"
            return f"{prefix}{text}"

        return f"{prefix}{text}"
