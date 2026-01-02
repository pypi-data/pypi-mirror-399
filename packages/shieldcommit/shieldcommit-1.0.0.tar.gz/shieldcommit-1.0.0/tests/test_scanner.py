from shieldcommit.scanner import scan_file
from pathlib import Path
import tempfile


def test_scan_detects_aws_key():
    """Test intelligent detection of AWS access keys."""
    text = 'my_key = "AKIAAAAAAAAAAAAAAAAA"'
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
        f.write(text)
        f.flush()
        
        results = scan_file(Path(f.name))
        
        # Should detect the AWS key
        assert len(results) > 0
        assert any('AWS' in finding.get('detection_method', '') or 
                  finding.get('confidence', 0) > 0.5
                  for finding in results)


def test_scan_detects_high_entropy_secrets():
    """Test intelligent detection of high-entropy strings."""
    text = 'password = "aB3$Kx9@mL2pQ5vN8xR1yT4gH"'
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
        f.write(text)
        f.flush()
        
        results = scan_file(Path(f.name))
        
        # Should detect high-entropy secret
        assert len(results) > 0


def test_scan_excludes_arns():
    """Test that ARNs are excluded from detection."""
    text = 'arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"'
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
        f.write(text)
        f.flush()
        
        results = scan_file(Path(f.name))
        
        # Should NOT detect ARNs
        assert len(results) == 0 or all('arn:aws' not in r.get('matched_value', '') for r in results)


def test_scan_detects_semantic_secrets():
    """Test semantic detection using variable names."""
    text = 'api_key = "randomstringvalue1234567890"'
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
        f.write(text)
        f.flush()
        
        results = scan_file(Path(f.name))
        
        # Should detect based on semantic analysis
        assert len(results) > 0
