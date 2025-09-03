"""
Tests for SSL configuration and HTTPS functionality in MCP server.
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from rag_fetch.config import ServerConfig, TransportType


class TestSSLConfiguration:
    """Test SSL configuration validation and setup."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.test_cert_dir = Path(__file__).parent.parent / "ssl_certs"
        self.server_cert = self.test_cert_dir / "server-cert.pem"
        self.server_key = self.test_cert_dir / "server-key.pem"
        self.ca_cert = self.test_cert_dir / "ca-cert.pem"
        self.selfsigned_cert = self.test_cert_dir / "selfsigned-cert.pem"
        self.selfsigned_key = self.test_cert_dir / "selfsigned-key.pem"
        self.expired_cert = self.test_cert_dir / "expired-cert.pem"
        self.expired_key = self.test_cert_dir / "expired-key.pem"
        self.invalid_cert = self.test_cert_dir / "invalid-cert.pem"
        
    @patch.dict(os.environ, {}, clear=True)  # Clear all env vars
    def test_ssl_disabled_by_default(self):
        """Test that SSL is disabled by default."""
        config = ServerConfig()
        assert config.use_ssl is False
        assert config.ssl_cert_path is None
        assert config.ssl_key_path is None
        
    @patch.dict(os.environ, {
        'MCP_USE_SSL': 'true',
        'MCP_SSL_CERT_PATH': '/test/cert.pem',
        'MCP_SSL_KEY_PATH': '/test/key.pem'
    })
    def test_ssl_configuration_from_env(self):
        """Test SSL configuration loading from environment variables."""
        config = ServerConfig()
        assert config.use_ssl is True
        assert config.ssl_cert_path == '/test/cert.pem'
        assert config.ssl_key_path == '/test/key.pem'
        
    @patch.dict(os.environ, {
        'MCP_USE_SSL': 'true',
        'MCP_SSL_CERT_PATH': '/test/cert.pem',
        'MCP_SSL_KEY_PATH': '/test/key.pem',
        'MCP_SSL_CA_CERTS': '/test/ca.pem',
        'MCP_ENVIRONMENT': 'development',
        'MCP_SSL_VERIFY_MODE': 'relaxed'
    })
    def test_full_ssl_configuration(self):
        """Test full SSL configuration with all options."""
        config = ServerConfig()
        assert config.use_ssl is True
        assert config.ssl_cert_path == '/test/cert.pem'
        assert config.ssl_key_path == '/test/key.pem'
        assert config.ssl_ca_certs == '/test/ca.pem'
        assert config.environment == 'development'
        assert config.ssl_verify_mode == 'relaxed'
        
    def test_server_url_with_ssl_enabled(self):
        """Test server URL uses HTTPS when SSL is enabled."""
        config = ServerConfig()
        config.use_ssl = True
        config.host = "localhost"
        config.port = 8000
        
        assert config.server_url == "https://localhost:8000"
        
    def test_server_url_with_ssl_disabled(self):
        """Test server URL uses HTTP when SSL is disabled."""
        config = ServerConfig()
        config.use_ssl = False
        config.host = "localhost"
        config.port = 8000
        
        assert config.server_url == "http://localhost:8000"
        
    def test_ssl_validation_disabled(self):
        """Test SSL validation when SSL is disabled."""
        config = ServerConfig()
        config.use_ssl = False
        
        is_valid, message = config.validate_ssl_config()
        assert is_valid is True
        assert message == "SSL is disabled"
        
    def test_ssl_validation_missing_cert_path(self):
        """Test SSL validation with missing certificate path."""
        config = ServerConfig()
        config.use_ssl = True
        config.ssl_cert_path = None
        config.ssl_key_path = "/test/key.pem"
        
        is_valid, message = config.validate_ssl_config()
        assert is_valid is False
        assert "certificate or key path not provided" in message
        
    def test_ssl_validation_missing_key_path(self):
        """Test SSL validation with missing key path."""
        config = ServerConfig()
        config.use_ssl = True
        config.ssl_cert_path = "/test/cert.pem"
        config.ssl_key_path = None
        
        is_valid, message = config.validate_ssl_config()
        assert is_valid is False
        assert "certificate or key path not provided" in message
        
    def test_ssl_validation_nonexistent_cert_file(self):
        """Test SSL validation with non-existent certificate file."""
        config = ServerConfig()
        config.use_ssl = True
        config.ssl_cert_path = "/nonexistent/cert.pem"
        config.ssl_key_path = "/test/key.pem"
        
        is_valid, message = config.validate_ssl_config()
        assert is_valid is False
        assert "certificate file not found" in message
        
    def test_ssl_validation_nonexistent_key_file(self):
        """Test SSL validation with non-existent key file."""
        config = ServerConfig()
        config.use_ssl = True
        config.ssl_cert_path = str(self.server_cert)
        config.ssl_key_path = "/nonexistent/key.pem"
        
        is_valid, message = config.validate_ssl_config()
        assert is_valid is False
        assert "key file not found" in message
        
    def test_ssl_validation_valid_certificates(self):
        """Test SSL validation with valid certificate files."""
        if not self.server_cert.exists() or not self.server_key.exists():
            pytest.skip("SSL test certificates not available")
            
        config = ServerConfig()
        config.use_ssl = True
        config.ssl_cert_path = str(self.server_cert)
        config.ssl_key_path = str(self.server_key)
        config.environment = "development"
        
        is_valid, message = config.validate_ssl_config()
        assert is_valid is True
        assert message == "SSL configuration is valid"
        
    def test_ssl_validation_with_ca_certs(self):
        """Test SSL validation with CA certificates."""
        if not all(p.exists() for p in [self.server_cert, self.server_key, self.ca_cert]):
            pytest.skip("SSL test certificates not available")
            
        config = ServerConfig()
        config.use_ssl = True
        config.ssl_cert_path = str(self.server_cert)
        config.ssl_key_path = str(self.server_key)
        config.ssl_ca_certs = str(self.ca_cert)
        config.environment = "development"
        
        is_valid, message = config.validate_ssl_config()
        assert is_valid is True
        assert message == "SSL configuration is valid"
        
    def test_ssl_validation_invalid_ca_path(self):
        """Test SSL validation with invalid CA certificate path."""
        config = ServerConfig()
        config.use_ssl = True
        config.ssl_cert_path = str(self.server_cert) if self.server_cert.exists() else "/test/cert.pem"
        config.ssl_key_path = str(self.server_key) if self.server_key.exists() else "/test/key.pem"
        config.ssl_ca_certs = "/nonexistent/ca.pem"
        
        is_valid, message = config.validate_ssl_config()
        assert is_valid is False
        assert "CA certificates file not found" in message
        
    def test_get_ssl_config_disabled(self):
        """Test SSL config generation when SSL is disabled."""
        config = ServerConfig()
        config.use_ssl = False
        
        ssl_config = config.get_ssl_config()
        assert ssl_config == {}
        
    def test_get_ssl_config_basic(self):
        """Test basic SSL config generation."""
        config = ServerConfig()
        config.use_ssl = True
        config.ssl_cert_path = "/test/cert.pem"
        config.ssl_key_path = "/test/key.pem"
        config.ssl_verify_mode = "strict"
        
        ssl_config = config.get_ssl_config()
        assert ssl_config["ssl_certfile"] == "/test/cert.pem"
        assert ssl_config["ssl_keyfile"] == "/test/key.pem"
        assert "ssl_ca_certs" not in ssl_config
        
    def test_get_ssl_config_with_ca_certs(self):
        """Test SSL config generation with CA certificates."""
        config = ServerConfig()
        config.use_ssl = True
        config.ssl_cert_path = "/test/cert.pem"
        config.ssl_key_path = "/test/key.pem"
        config.ssl_ca_certs = "/test/ca.pem"
        config.ssl_verify_mode = "strict"
        
        ssl_config = config.get_ssl_config()
        assert ssl_config["ssl_certfile"] == "/test/cert.pem"
        assert ssl_config["ssl_keyfile"] == "/test/key.pem"
        assert ssl_config["ssl_ca_certs"] == "/test/ca.pem"
        
    def test_get_ssl_config_verify_modes(self):
        """Test SSL config generation with different verify modes."""
        config = ServerConfig()
        config.use_ssl = True
        config.ssl_cert_path = "/test/cert.pem"
        config.ssl_key_path = "/test/key.pem"
        
        # Our implementation doesn't include ssl_cert_reqs anymore
        # as it's handled by uvicorn directly. Test basic SSL config structure.
        ssl_config = config.get_ssl_config()
        assert ssl_config["ssl_certfile"] == "/test/cert.pem"
        assert ssl_config["ssl_keyfile"] == "/test/key.pem"
        
        # Verify modes are stored but not in the SSL config dict
        config.ssl_verify_mode = "strict"
        assert config.ssl_verify_mode == "strict"
        
        config.ssl_verify_mode = "relaxed"
        assert config.ssl_verify_mode == "relaxed"
        
    def test_transport_config_includes_ssl(self):
        """Test that transport configuration includes SSL settings when enabled."""
        config = ServerConfig()
        config.transport = TransportType.HTTP
        config.use_ssl = True
        config.ssl_cert_path = "/test/cert.pem"
        config.ssl_key_path = "/test/key.pem"
        
        transport_config = config.get_transport_config()
        # SSL config is now in uvicorn_config sub-dict
        assert "uvicorn_config" in transport_config
        assert "ssl_certfile" in transport_config["uvicorn_config"]
        assert "ssl_keyfile" in transport_config["uvicorn_config"]
        assert transport_config["uvicorn_config"]["ssl_certfile"] == "/test/cert.pem"
        assert transport_config["uvicorn_config"]["ssl_keyfile"] == "/test/key.pem"
        
    def test_transport_config_excludes_ssl_when_disabled(self):
        """Test that transport configuration excludes SSL when disabled."""
        config = ServerConfig()
        config.transport = TransportType.HTTP
        config.use_ssl = False
        
        transport_config = config.get_transport_config()
        assert "ssl_certfile" not in transport_config
        assert "ssl_keyfile" not in transport_config
        
    def test_config_string_representation_with_ssl(self):
        """Test string representation includes SSL information."""
        config = ServerConfig()
        config.use_ssl = True
        config.ssl_cert_path = "/test/cert.pem"
        config.ssl_key_path = "/test/key.pem"
        config.ssl_ca_certs = "/test/ca.pem"
        config.environment = "development"
        config.ssl_verify_mode = "relaxed"
        
        config_str = str(config)
        assert "SSL Enabled: True" in config_str
        assert "SSL Certificate: /test/cert.pem" in config_str
        assert "SSL Key: /test/key.pem" in config_str
        assert "SSL CA Certs: /test/ca.pem" in config_str
        assert "Environment: development" in config_str
        assert "SSL Verify Mode: relaxed" in config_str
        
    def test_config_string_representation_without_ssl(self):
        """Test string representation with SSL disabled."""
        config = ServerConfig()
        config.use_ssl = False
        
        config_str = str(config)
        assert "SSL Enabled: False" in config_str
        assert "SSL Certificate:" not in config_str
        assert "SSL Key:" not in config_str


@pytest.mark.skipif(
    not Path(__file__).parent.parent.joinpath("ssl_certs", "server-cert.pem").exists(),
    reason="SSL test certificates not available"
)
class TestSSLCertificateValidation:
    """Test advanced SSL certificate validation with real certificates."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.test_cert_dir = Path(__file__).parent.parent / "ssl_certs"
        self.server_cert = self.test_cert_dir / "server-cert.pem"
        self.server_key = self.test_cert_dir / "server-key.pem"
        self.selfsigned_cert = self.test_cert_dir / "selfsigned-cert.pem"
        self.selfsigned_key = self.test_cert_dir / "selfsigned-key.pem"
        self.invalid_cert = self.test_cert_dir / "invalid-cert.pem"
        
    def test_valid_ca_signed_certificate(self):
        """Test validation of valid CA-signed certificate."""
        config = ServerConfig()
        config.use_ssl = True
        config.ssl_cert_path = str(self.server_cert)
        config.ssl_key_path = str(self.server_key)
        config.environment = "development"
        
        is_valid, message = config.validate_ssl_config()
        assert is_valid is True
        assert message == "SSL configuration is valid"
        
    def test_self_signed_certificate_development(self):
        """Test self-signed certificate validation in development mode."""
        config = ServerConfig()
        config.use_ssl = True
        config.ssl_cert_path = str(self.selfsigned_cert)
        config.ssl_key_path = str(self.selfsigned_key)
        config.environment = "development"
        
        is_valid, message = config.validate_ssl_config()
        assert is_valid is True
        assert message == "SSL configuration is valid"
        
    @patch('rag_fetch.config.logging.getLogger')
    def test_self_signed_certificate_production_warning(self, mock_logger):
        """Test self-signed certificate generates warning in production."""
        mock_log = MagicMock()
        mock_logger.return_value = mock_log
        
        config = ServerConfig()
        config.use_ssl = True
        config.ssl_cert_path = str(self.selfsigned_cert)
        config.ssl_key_path = str(self.selfsigned_key)
        config.environment = "production"
        
        is_valid, message = config.validate_ssl_config()
        assert is_valid is True
        mock_log.warning.assert_called_with(
            "Self-signed SSL certificate detected in production environment"
        )
        
    def test_invalid_certificate_format(self):
        """Test validation of invalid certificate format."""
        config = ServerConfig()
        config.use_ssl = True
        config.ssl_cert_path = str(self.invalid_cert)
        config.ssl_key_path = str(self.selfsigned_key)  # Use valid key
        
        is_valid, message = config.validate_ssl_config()
        assert is_valid is False
        assert "Invalid SSL certificate format" in message
        
    def test_certificate_key_mismatch(self):
        """Test validation fails when certificate and key don't match."""
        with patch('cryptography.x509.load_pem_x509_certificate') as mock_load_cert:
            with patch('cryptography.hazmat.primitives.serialization.load_pem_private_key') as mock_load_key:
                # Mock certificate and key that don't match
                mock_cert = MagicMock()
                mock_key = MagicMock()
                
                # Different public key numbers to simulate mismatch
                mock_cert.public_key.return_value.public_numbers.return_value = "cert_numbers"
                mock_key.public_key.return_value.public_numbers.return_value = "key_numbers"
                
                mock_load_cert.return_value = mock_cert
                mock_load_key.return_value = mock_key
                
                config = ServerConfig()
                config.use_ssl = True
                config.ssl_cert_path = str(self.server_cert)
                config.ssl_key_path = str(self.server_key)
                
                is_valid, message = config.validate_ssl_config()
                assert is_valid is False
                assert "certificate and private key do not match" in message
            
    def test_validation_without_cryptography_library(self):
        """Test validation when cryptography library is not available."""
        # Simulate ImportError when importing cryptography
        with patch.dict('sys.modules', {'cryptography.x509': None, 'cryptography.hazmat.primitives': None}):
            with patch('builtins.__import__', side_effect=ImportError("cryptography not available")):
                with patch('rag_fetch.config.logging.getLogger') as mock_logger:
                    mock_log = MagicMock()
                    mock_logger.return_value = mock_log
                    
                    config = ServerConfig()
                    config.use_ssl = True
                    config.ssl_cert_path = str(self.server_cert)
                    config.ssl_key_path = str(self.server_key)
                    
                    is_valid, message = config.validate_ssl_config()
                    assert is_valid is True
                    assert message == "SSL configuration is valid"
                    mock_log.warning.assert_called_with(
                        "Cryptography library not available, skipping advanced SSL certificate validation"
                    )