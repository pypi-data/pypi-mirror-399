"""
Intelligent Secret Detection System

Detects secrets without relying on predefined patterns.
Uses entropy analysis, semantic analysis, context understanding, and heuristics.
Calculates confidence scores to minimize false positives.
"""

import re
import math
from typing import List, Dict, Tuple


class IntelligentDetector:
    """
    Detects secrets using intelligent heuristics instead of patterns.
    
    Methods:
    - Entropy analysis: Detects high-entropy strings likely to be secrets
    - Semantic analysis: Recognizes variable names suggesting secrets
    - Context analysis: Examines surrounding code for secret indicators
    - Value analysis: Analyzes value characteristics (length, character variety)
    - Heuristic detection: Applies domain knowledge for common secret formats
    """
    
    # Variable name keywords indicating secrets
    SECRET_KEYWORDS = {
        'password', 'passwd', 'pwd', 'secret', 'token', 'api_key', 'apikey',
        'api-key', 'key', 'credential', 'credentials', 'auth', 'auth_token',
        'access_token', 'refresh_token', 'api_secret', 'bearer', 'jwt',
        'private_key', 'private-key', 'ssh_key', 'private_token',
        'oauth_token', 'oauth2_token', 'session', 'session_id', 'session-id',
        'aws_secret', 'aws_key', 'aws_access', 'google_key', 'google_secret',
        'github_token', 'gitlab_token', 'bitbucket_token', 'slack_token',
        'stripe_key', 'stripe_secret', 'database_password', 'db_password',
        'db_pass', 'db_user', 'database_user', 'connection_string',
        'connection-string', 'cert', 'certificate', 'pem', 'rsa', 'dsa',
        'cipher', 'encryption_key', 'hmac', 'hash', 'webhook', 'webhook_secret',
        'signing_key', 'signing-key', 'verification_key', 'access_secret',
        'client_secret', 'client-secret', 'client_id', 'app_secret', 'app-secret',
        'master_key', 'master-key', 'admin_password', 'admin-password',
        'root_password', 'root-password', 'user_password', 'user-password'
    }
    
    # Context keywords that indicate nearby secrets
    CONTEXT_KEYWORDS = {
        'password', 'secret', 'token', 'api', 'key', 'auth', 'credential',
        'token:', 'api_key:', 'secret:', 'password:', 'authorization:',
        'bearer:', 'api-key:', 'access-token:', 'auth-token:'
    }
    
    # Non-secret indicators (things that shouldn't be flagged)
    EXCLUDE_KEYWORDS = {
        'arn:', 'arn-', 'policy_arn', 'role_arn', 'resource_arn',
        'account_id', 'account-id', 'account:', 'region:', 'service:',
        'hash:', 'checksum:', 'uuid:', 'id:', 'identifier:',
        'image_id', 'instance_id', 'version:', 'build:', 'release:',
        'name:', 'description:', 'tag:', 'label:', 'namespace:',
        'project_id', 'project-id', 'org_id', 'org-id',
        'user_id', 'user-id', 'admin_id', 'admin-id',
        'correlation_id', 'correlation-id', 'request_id', 'request-id',
        'trace_id', 'trace-id', 'session_id', 'session-id',
        'bucket_id', 'bucket-id', 'cluster_id', 'cluster-id',
        'instance_name', 'resource_name', 'resource_id'
    }
    
    # Common secret structures (formats likely to be secrets)
    SECRET_STRUCTURES = [
        # Base64-like with specific prefixes
        (r'^AKIA[0-9A-Z]{16}$', 'AWS Access Key'),  # AWS Access Key
        (r'^ASIA[0-9A-Z]{16}$', 'AWS Temporary Key'),  # AWS Temporary Access Key
        (r'^AIza[0-9A-Za-z\-_]{35}$', 'Google API Key'),  # Google API Key
        (r'^ya29\.[0-9A-Za-z\-_]{1,}$', 'Google OAuth Token'),  # Google OAuth
        (r'^sk-[A-Za-z0-9]{20,}$', 'OpenAI API Key'),  # OpenAI
        (r'^pk_live_[0-9a-zA-Z]{24}$', 'Stripe Publishable Key'),  # Stripe
        (r'^sk_live_[0-9a-zA-Z]{24}$', 'Stripe Secret Key'),  # Stripe
        (r'^gh[pousr]_[A-Za-z0-9]{30,}$', 'GitHub Token'),  # GitHub
        (r'^glpat-[0-9a-zA-Z\-]{20,}$', 'GitLab Token'),  # GitLab
        (r'^bbp_[A-Za-z0-9]{32}$', 'Bitbucket App Password'),  # Bitbucket
        (r'^xox[baprs]-[0-9A-Za-z]{10,48}$', 'Slack Token'),  # Slack
        (r'^SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}$', 'SendGrid API Key'),  # SendGrid
        (r'^key-[0-9a-zA-Z]{32}$', 'Mailgun API Key'),  # Mailgun
        (r'^-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----', 'Private Key'),  # SSH Keys
        (r'^Bearer\s+[A-Za-z0-9\-._~+/]+=*$', 'Bearer Token'),  # Bearer tokens
    ]
    
    @staticmethod
    def calculate_entropy(s: str) -> float:
        """
        Calculate Shannon entropy of a string.
        Higher entropy (closer to max) suggests random/secret data.
        Max entropy is 5.7 bits for alphanumeric + symbols.
        """
        if not s or len(s) < 1:
            return 0.0
        
        # Count unique characters
        unique_chars = len(set(s))
        
        # Calculate probabilities and entropy
        entropy = 0.0
        for char in set(s):
            probability = s.count(char) / len(s)
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    @staticmethod
    def is_high_entropy(value: str, min_entropy: float = 3.5, min_length: int = 12) -> bool:
        """
        Check if value has high entropy indicating it could be a secret.
        Balances between:
        - Entropy threshold: 3.5 bits (avoids common words/patterns)
        - Length threshold: 12+ characters (avoids short tokens)
        - Character variety: Mix of different character types
        """
        if len(value) < min_length:
            return False
        
        entropy = IntelligentDetector.calculate_entropy(value)
        if entropy < min_entropy:
            return False
        
        # Check character variety (should have different types)
        has_alpha = bool(re.search(r'[a-zA-Z]', value))
        has_digit = bool(re.search(r'\d', value))
        has_special = bool(re.search(r'[^a-zA-Z0-9]', value))
        
        # Need at least 2 of 3 character types for high entropy to be meaningful
        variety = sum([has_alpha, has_digit, has_special])
        
        return variety >= 2
    
    @staticmethod
    def is_likely_secret_format(value: str) -> Tuple[bool, str]:
        """
        Check if value matches known secret formats.
        Returns (is_secret, format_name)
        """
        for pattern, name in IntelligentDetector.SECRET_STRUCTURES:
            if re.match(pattern, value):
                return True, name
        
        return False, ""
    
    @staticmethod
    def extract_secret_indicator(line: str) -> Tuple[str, float]:
        """
        Extract secret indicator from line (variable name).
        Returns (indicator, confidence_boost)
        """
        # Look for assignment patterns: var = value, var: value, etc.
        match = re.search(r'([a-zA-Z_][a-zA-Z0-9_\-]*)\s*[:=]\s*["\']?([^"\';\s]+)', line)
        if not match:
            return "", 0.0
        
        var_name = match.group(1).lower()
        
        # Check if variable name suggests a secret
        for keyword in IntelligentDetector.SECRET_KEYWORDS:
            if keyword in var_name:
                return var_name, 0.3  # Boost confidence
        
        return var_name, 0.0
    
    @staticmethod
    def has_secret_context(line: str) -> bool:
        """
        Check if line has context keywords suggesting it contains a secret.
        """
        line_lower = line.lower()
        return any(keyword in line_lower for keyword in IntelligentDetector.CONTEXT_KEYWORDS)
    
    @staticmethod
    def is_excluded(value: str, line: str) -> bool:
        """
        Check if value should be excluded (legitimate identifier, not a secret).
        Handles all common production patterns: naming, IDs, URLs, paths, etc.
        """
        value_lower = value.lower()
        line_lower = line.lower()
        
        # ============ INFRASTRUCTURE AS CODE PATTERNS ============
        
        # Terraform/CloudFormation interpolations
        if '${' in value or '}' in value or '{%' in value:
            return True
        
        # Variable references (Terraform, CloudFormation, etc.)
        if 'var.' in value_lower or 'local.' in value_lower or 'data.' in value_lower:
            return True
        if 'data:' in value_lower or 'module.' in value_lower:
            return True
        
        # Terraform resource references (resource_type.resource_name.attribute)
        if re.match(r'^[a-z_]+\.[a-z_]+(\.[a-z_]+)*$', value_lower):
            # This matches patterns like: aws_vpc.main.id, aws_db_instance.postgres.endpoint
            if any(keyword in value_lower for keyword in ['aws_', 'google_', 'azurerm_', 'kubernetes_']):
                return True
        
        # Kubernetes patterns
        if 'kind:' in value_lower or 'apiversion:' in value_lower:
            return True
        if value_lower.startswith('k8s-') or value_lower.startswith('kube-'):
            return True
        
        # ============ AWS IDENTIFIERS ============
        
        if value_lower.startswith('arn:') or 'arn:' in line_lower:
            return True
        if value_lower.startswith('i-') and len(value) == 19:  # EC2 instance ID
            return True
        if value_lower.startswith('ami-') or value_lower.startswith('ami_'):  # AMI ID
            return True
        if value_lower.startswith('sg-'):  # Security group
            return True
        if value_lower.startswith('subnet-'):  # Subnet
            return True
        if value_lower.startswith('vpc-'):  # VPC
            return True
        if value_lower.startswith('vol-'):  # Volume
            return True
        if value_lower.startswith('snap-'):  # Snapshot
            return True
        if value_lower.startswith('rtb-'):  # Route table
            return True
        if value_lower.startswith('acl-'):  # Network ACL
            return True
        if value_lower.startswith('eni-'):  # Network interface
            return True
        if value_lower.startswith('nat-'):  # NAT gateway
            return True
        if value_lower.startswith('igw-'):  # Internet gateway
            return True
        if value_lower.startswith('eip-'):  # Elastic IP
            return True
        if value_lower.startswith('dopt-'):  # DHCP options set
            return True
        
        # ============ GCP IDENTIFIERS ============
        
        if value.startswith('projects/'):  # GCP resource
            return True
        if value_lower.startswith('gke-'):  # GKE cluster
            return True
        if re.match(r'^\d{10,}$', value):  # GCP project number
            return True
        
        # ============ AZURE IDENTIFIERS ============
        
        if value_lower.startswith('/subscriptions/'):  # Azure resource path
            return True
        if value_lower.startswith('guid-') or value_lower.startswith('id-'):
            return True
        
        # ============ STANDARD IDENTIFIERS ============
        
        # UUID
        if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', value_lower):
            return True
        
        # Hashes (MD5, SHA1, SHA256, SHA512)
        if re.match(r'^[a-f0-9]{32}$|^[a-f0-9]{40}$|^[a-f0-9]{64}$|^[a-f0-9]{128}$', value_lower):
            return True
        
        # Git hashes
        if re.match(r'^[0-9a-f]{7,40}$', value_lower) and 'git' in line_lower:
            return True
        
        # Docker SHA
        if value_lower.startswith('sha256:'):
            return True
        if value_lower.startswith('sha512:'):
            return True
        
        # ============ NETWORKING & DNS ============
        
        # URLs and endpoints
        if value_lower.startswith('http://') or value_lower.startswith('https://'):
            return True
        if value_lower.startswith('ws://') or value_lower.startswith('wss://'):
            return True
        if value_lower.startswith('grpc://'):
            return True
        if value_lower.startswith('file://') or value_lower.startswith('ftp://'):
            return True
        
        # Domain names and FQDNs
        if re.match(r'^([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$', value_lower):
            return True
        
        # Email addresses
        if '@' in value and '.' in value:
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                return True
        
        # IP addresses
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', value):  # IPv4
            return True
        if ':' in value and re.match(r'^[0-9a-f:]+$', value_lower):  # IPv6
            if value_lower.count(':') >= 2:
                return True
        
        # Ports in URLs/addresses
        if re.match(r'^\d{1,5}$', value) and int(value) <= 65535:
            return True
        
        # ============ CONTAINER & IMAGE IDENTIFIERS ============
        
        # Docker image names (repo/name:tag)
        if re.match(r'^[a-z0-9\-._/]+:[a-z0-9\-._]+$', value_lower):
            return True
        if re.match(r'^[a-z0-9\-._/]+@sha256:[a-f0-9]{64}$', value_lower):
            return True
        
        # Container registry hosts
        if 'docker.io' in value_lower or 'gcr.io' in value_lower:
            return True
        if 'azurecr.io' in value_lower or 'ecr.aws' in value_lower:
            return True
        
        # ============ PACKAGE & MODULE REFERENCES ============
        
        # Go imports
        if 'github.com/' in value_lower or 'gitlab.com/' in value_lower:
            return True
        
        # Python packages
        if 'pypi.org' in value_lower or 'python.org' in value_lower:
            return True
        
        # Java packages
        if re.match(r'^[a-z]+(\.[a-z0-9]+)+$', value_lower):
            if 'java' in line_lower or 'package' in line_lower:
                return True
        
        # ============ FILE PATHS & DIRECTORIES ============
        
        # File paths
        if '/' in value or '\\' in value:
            if any(ext in value.lower() for ext in ['.tf', '.yaml', '.yml', '.json', '.xml', '.py', '.js', '.go']):
                return True
        
        # Kubernetes paths
        if value.startswith('/var/run/secrets') or value.startswith('/etc/'):
            return True
        
        # ============ VERSION & BUILD INFO ============
        
        # Semantic versions (1.2.3)
        if re.match(r'^\d+\.\d+(\.\d+)?(\-[a-z0-9]+)?$', value_lower):
            return True
        
        # Build numbers and dates
        if re.match(r'^\d{4}-\d{2}-\d{2}', value):  # Dates
            return True
        if re.match(r'^\d{10,}$', value):  # Unix timestamps
            return True
        
        # Commit SHAs in git refs
        if 'commit' in line_lower and re.match(r'^[0-9a-f]{7,}$', value_lower):
            return True
        
        # ============ NAMING PATTERNS ============
        
        # Hyphenated naming (word-word-word, word-word-123) - only if ALL lowercase and short
        if re.match(r'^[a-z0-9]+(-[a-z0-9]+)*(-\d+)?$', value_lower) and value == value_lower:
            # Only exclude if it looks like a resource name, not a secret
            if len(value) < 24:  # Resource names are typically shorter
                return True
        
        # Camel case naming
        if re.match(r'^[A-Z][a-z]+([A-Z][a-z]+)*$', value):
            return True
        
        # ============ CONTEXT-BASED EXCLUSIONS ============
        
        # Exclude if has exclude keywords in context
        for keyword in IntelligentDetector.EXCLUDE_KEYWORDS:
            if keyword in line_lower:
                return True
        
        # Exclude if value is mostly digits (IDs, counts)
        if len(value) > 5 and sum(c.isdigit() for c in value) / len(value) > 0.7:
            return True
        
        # ============ RESOURCE NAMING PATTERNS ============
        
        # Common resource name patterns: env-region-number
        if re.match(r'^[a-z]+-[a-z]+-\d+$', value_lower):
            return True
        
        # DNS-like patterns: subdomain.service.namespace
        if re.match(r'^[a-z0-9]+\.[a-z0-9]+(\.[a-z0-9]+)*$', value_lower):
            return True
        
        return False
    
    @staticmethod
    def calculate_confidence(value: str, line: str = "") -> float:
        """
        Calculate confidence score (0.0 to 1.0) that value is a secret.
        
        Factors:
        - Entropy analysis: High entropy increases confidence
        - Format matching: Known secret formats increase confidence
        - Semantic analysis: Secret keywords in variable names increase confidence
        - Context analysis: Secret context keywords increase confidence
        - Exclusions: Legitimate identifiers decrease confidence to 0
        """
        # Exclusion check: If excluded, confidence is 0
        if IntelligentDetector.is_excluded(value, line):
            return 0.0
        
        confidence = 0.0
        
        # 1. Format matching (high confidence)
        is_known_format, format_name = IntelligentDetector.is_likely_secret_format(value)
        if is_known_format:
            return 0.95  # Known formats are very confident
        
        # 2. Entropy analysis (moderate to high confidence)
        if IntelligentDetector.is_high_entropy(value):
            entropy = IntelligentDetector.calculate_entropy(value)
            # Map entropy 3.5-5.7 to confidence 0.4-0.8
            confidence += min(0.8, (entropy - 3.5) / 2.2 * 0.8)
        
        # 3. Semantic analysis from variable name (moderate confidence)
        var_indicator, indicator_boost = IntelligentDetector.extract_secret_indicator(line)
        if indicator_boost > 0:
            confidence += indicator_boost
        
        # 4. Context analysis (low to moderate confidence)
        if line and IntelligentDetector.has_secret_context(line):
            confidence += 0.15
        
        # 5. Length analysis (longer strings more likely to be secrets)
        if len(value) >= 32:
            confidence += 0.1
        elif len(value) >= 20:
            confidence += 0.05
        
        # 6. Value analysis (special characters, mix of types)
        has_alpha = bool(re.search(r'[a-zA-Z]', value))
        has_digit = bool(re.search(r'\d', value))
        has_special = bool(re.search(r'[^a-zA-Z0-9]', value))
        variety = sum([has_alpha, has_digit, has_special])
        
        if variety == 3:
            confidence += 0.1
        
        # Cap confidence at 1.0
        return min(1.0, confidence)
    
    @staticmethod
    def detect_in_line(line: str, min_confidence: float = 0.5, context: str = "") -> List[Dict]:
        """
        Detect potential secrets in a single line.
        Returns list of findings with confidence scores.
        
        Skips common production patterns: Terraform interpolations, URLs, paths, etc.
        
        Args:
            line: The line to scan
            min_confidence: Minimum confidence threshold
            context: Previous lines for variable name context (e.g., "variable db_password")
        """
        findings = []
        
        # Skip lines with Terraform/CloudFormation interpolations (naming patterns)
        if '${' in line or '}' in line or '{%' in line:
            return findings
        
        # Skip URLs, paths, and references
        if any(proto in line for proto in ['http://', 'https://', 'ws://', 'wss://', 'file://', 'ftp://']):
            return findings
        
        # Skip Kubernetes resources and manifests
        if 'kind:' in line.lower() or 'apiversion:' in line.lower():
            return findings
        
        # Skip common comment lines with examples
        if '#' in line or '//' in line:
            return findings
        
        # Extract potential values from assignments
        # Patterns: var = "value", var = value, var: "value", var: value
        patterns = [
            r'([a-zA-Z_][a-zA-Z0-9_\-]*)\s*[:=]\s*["\']([^"\']+)["\']',  # Quoted
            r'([a-zA-Z_][a-zA-Z0-9_\-]*)\s*[:=]\s*([A-Za-z0-9\-_.+/]+)',   # Unquoted
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, line):
                var_name = match.group(1)
                value = match.group(2)
                
                # Skip very short values
                if len(value) < 8:
                    continue
                
                # Skip common non-secrets
                if value in ['true', 'false', 'null', 'none', 'yes', 'no']:
                    continue
                
                # Skip if value contains variable references or interpolations
                if 'var.' in value or 'local.' in value or 'data.' in value:
                    continue
                
                # Use context-aware confidence calculation
                full_line_context = context + " " + line if context else line
                confidence = IntelligentDetector.calculate_confidence(value, full_line_context)
                
                if confidence >= min_confidence:
                    findings.append({
                        'value': value,
                        'variable': var_name,
                        'confidence': confidence,
                        'detection_method': IntelligentDetector._get_detection_method(value, full_line_context)
                    })
        
        return findings
    
    @staticmethod
    def _get_detection_method(value: str, line: str) -> str:
        """Determine which detection method identified the secret."""
        is_known, fmt = IntelligentDetector.is_likely_secret_format(value)
        if is_known:
            return f"Format: {fmt}"
        
        if IntelligentDetector.is_high_entropy(value):
            return "High Entropy"
        
        var_name, boost = IntelligentDetector.extract_secret_indicator(line)
        if boost > 0:
            return f"Semantic: {var_name}"
        
        if IntelligentDetector.has_secret_context(line):
            return "Context Analysis"
        
        return "Heuristic Analysis"


def detect_secrets(text: str, min_confidence: float = 0.5) -> List[Dict]:
    """
    Detect secrets in text using intelligent analysis.
    
    Args:
        text: Content to scan
        min_confidence: Minimum confidence threshold (0.0-1.0)
    
    Returns:
        List of detected secrets with confidence scores
    """
    findings = []
    lines = text.splitlines()
    
    for line_no, line in enumerate(lines, 1):
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            continue
        
        # Build context from previous lines (look back 3 lines for variable declarations)
        context = line
        for i in range(max(0, line_no - 4), line_no - 1):
            if i < len(lines):
                context = lines[i] + " " + context
        
        line_findings = IntelligentDetector.detect_in_line(line, min_confidence, context)
        
        for finding in line_findings:
            findings.append({
                'file': '',  # Will be set by scanner
                'line': line_no,
                'snippet': line[:200],
                'matched_value': finding['value'],
                'variable': finding['variable'],
                'confidence': finding['confidence'],
                'detection_method': finding['detection_method'],
                'pattern': f"Intelligent Detection: {finding['detection_method']}"
            })
    
    return findings
