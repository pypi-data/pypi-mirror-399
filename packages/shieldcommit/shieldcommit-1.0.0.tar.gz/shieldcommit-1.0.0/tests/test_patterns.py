from shieldcommit.intelligent_detector import IntelligentDetector

def test_intelligent_detector_has_secret_keywords():
    """Verify intelligent detector has secret keywords configured."""
    assert len(IntelligentDetector.SECRET_KEYWORDS) > 0
    assert 'password' in IntelligentDetector.SECRET_KEYWORDS
    assert 'api_key' in IntelligentDetector.SECRET_KEYWORDS
    assert 'token' in IntelligentDetector.SECRET_KEYWORDS


def test_intelligent_detector_has_secret_structures():
    """Verify intelligent detector has known secret formats."""
    assert len(IntelligentDetector.SECRET_STRUCTURES) > 0
    # Should have AWS, Stripe, GitHub, and other formats
    format_count = len(IntelligentDetector.SECRET_STRUCTURES)
    assert format_count >= 10


def test_intelligent_detector_has_exclusions():
    """Verify intelligent detector has exclusion keywords."""
    assert len(IntelligentDetector.EXCLUDE_KEYWORDS) > 0
    assert 'arn:' in IntelligentDetector.EXCLUDE_KEYWORDS
    assert 'version:' in IntelligentDetector.EXCLUDE_KEYWORDS
