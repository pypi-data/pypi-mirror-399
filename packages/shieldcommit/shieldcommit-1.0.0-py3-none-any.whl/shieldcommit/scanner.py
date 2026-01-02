from pathlib import Path
from .intelligent_detector import detect_secrets
from .eks_detector import scan_eks_versions
from .rds_detector import scan_rds_versions
from .aks_detector import scan_aks_versions
from .gcp_detector import scan_gcp_versions
from .azure_db_detector import scan_azure_db_versions
from .gcp_db_detector import scan_gcp_cloudsql_versions

def scan_file(path: Path, min_confidence: float = 0.5):
    """
    Scan a file for secrets using intelligent detection.
    Returns findings with line numbers, confidence scores, and detection methods.
    """
    findings = []
    try:
        text = path.read_text(errors="ignore")
    except Exception:
        return findings

    # Use intelligent detection instead of patterns
    detected = detect_secrets(text, min_confidence=min_confidence)
    
    for finding in detected:
        finding['file'] = str(path)
        findings.append(finding)

    return findings


def scan_files(paths):
    """
    Scan files for secrets and warnings (EKS/RDS/AKS/GCP versions + Azure/GCP databases).
    Uses intelligent detection for secrets (no patterns).
    Returns dict with 'findings' (secrets) and 'warnings' (version issues).
    """
    findings = []
    warnings = []
    
    for p in paths:
        p = Path(p)
        if p.is_file():
            findings.extend(scan_file(p))
            # Scan for Kubernetes versions
            warnings.extend(scan_eks_versions(p))
            warnings.extend(scan_aks_versions(p))
            warnings.extend(scan_gcp_versions(p))
            # Scan for database versions
            warnings.extend(scan_rds_versions(p))
            warnings.extend(scan_azure_db_versions(p))
            warnings.extend(scan_gcp_cloudsql_versions(p))
    
    return {
        "findings": findings,
        "warnings": warnings
    }

