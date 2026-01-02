import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

class Config(BaseModel):
    """
    Configuration for agent observability system.
    
    Required:
    - api_key: Must start with 'sk_' and be validated with backend
    
    Optional:
    - api_endpoint: Backend API URL
    - batch_size: Events per batch (1-100)
    - flush_interval_seconds: Max wait before sending (1-300)
    - timeout_seconds: HTTP timeout (1-60)
    - enabled: Enable/disable event sending
    - debug: Enable debug logging
    - verify_key_on_init: Verify API key with backend on startup
    """

    access_key:str = Field(
        ..., # required
        description="Access key for authentication with backend",
        examples=["sk_prod_abc123", "sk_test_xyz789"]
    )

    api_endpoint: str = Field(
        default="https://api.agentobs.io",
        description="Base URL of  backend API",
        examples=["https://api.agentobs.io", "http://localhost:8000"],
    )

    batch_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Max events to buffer before sending to backend",
    )
    
    flush_interval_seconds: int = Field(
        default=5,
        ge=1,
        le=300,
        description="Max seconds to wait before auto-flushing buffered events",
    )
    
    timeout_seconds: int = Field(
        default=5,
        ge=1,
        le=60,
        description="HTTP request timeout in seconds",
    )
    
    enabled: bool = Field(
        default=True,
        description="Whether to send events to backend (can disable for testing)",
    )
    
    debug: bool = Field(
        default=False,
        description="Enable debug logging for troubleshooting",
    )

    verify_key_on_init: bool = Field(
        default=True,
        description="Verify API key with backend on initialization",
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,  # Remove leading/trailing whitespace
        validate_default=True,       # Validate default values
        populate_by_name=True,       # Accept both field name and alias
    )

    @field_validator("access_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """
        Validate API key format.
        
        Rules:
        - Cannot be empty
        - Should start with 'sk_' prefix (production or test)
        - Minimum length of 10 characters
        
        Args:
            v: API key string
        
        Returns:
            str: Validated API key
        
        Raises:
            ValueError: If validation fails
        """
        if not v or not v.strip():
            raise ValueError("api_key cannot be empty")
        
        if not v.startswith("sk_"):
            raise ValueError(
                "api_key should start with 'sk_' (e.g., 'sk_prod_xyz' or 'sk_test_xyz')"
            )
        
        if len(v) < 10:
            raise ValueError("api_key should be at least 5 characters long")
        
        return v.strip()
    
    @field_validator("api_endpoint")
    @classmethod
    def validate_api_endpoint(cls, v: str) -> str:
        """
        Validate API endpoint URL.
        
        Rules:
        - Cannot be empty
        - Should be valid URL (starts with http:// or https://)
        
        Args:
            v: API endpoint URL
        
        Returns:
            str: Validated URL
        
        Raises:
            ValueError: If validation fails
        """
        if not v or not v.strip():
            raise ValueError("api_endpoint cannot be empty")
        
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError(
                "api_endpoint should start with 'http://' or 'https://'"
            )
        
        # Remove trailing slash for consistency
        return v.strip().rstrip("/")
    
    
    @classmethod
    def from_env(cls, **overrides) -> "Config":
        """
        Load configuration from environment variables.
        
        Required:
        - AGENT_OBS_API_KEY: Must be set (starts with 'sk_')
        
        Optional:
        - AGENT_OBS_API_ENDPOINT (default: https://api.agentobs.io)
        - AGENT_OBS_BATCH_SIZE (default: 10)
        - AGENT_OBS_FLUSH_INTERVAL (default: 5)
        - AGENT_OBS_TIMEOUT (default: 5)
        - AGENT_OBS_ENABLED (default: true)
        - AGENT_OBS_DEBUG (default: false)
        """
        access_key = os.getenv("AGENT_OBS_API_KEY", "").strip()
        
        if not access_key:
            raise ValueError(
                "AGENT_OBS_API_KEY environment variable not set.\n"
                "Set it with: export AGENT_OBS_API_KEY='sk_prod_xxx'"
            )
        
        return cls(
            access_key=access_key,
            api_endpoint=os.getenv(
                "AGENT_OBS_API_ENDPOINT", 
                "https://api.agentobs.io"
            ),
            batch_size=int(os.getenv("AGENT_OBS_BATCH_SIZE", "10")),
            flush_interval_seconds=int(os.getenv("AGENT_OBS_FLUSH_INTERVAL", "5")),
            timeout_seconds=int(os.getenv("AGENT_OBS_TIMEOUT", "5")),
            enabled=os.getenv("AGENT_OBS_ENABLED", "true").lower() == "true",
            debug=os.getenv("AGENT_OBS_DEBUG", "false").lower() == "true",
            verify_key_on_init=os.getenv(
                "AGENT_OBS_VERIFY_KEY", "true"
            ).lower() == "true",
            **overrides
        )
    
    def to_dict(self) -> dict:
        """
        Export configuration as dictionary.
        
        Returns:
            dict: Configuration values
        
        Example:
            config = Config.from_env()
            config_dict = config.to_dict()
            print(config_dict)
            # {'api_key': 'sk_...', 'batch_size': 10, ...}
        """
        return self.model_dump()
    
    def __repr__(self) -> str:
        """
        String representation of configuration (safe for logging).
        
        Hides sensitive values (api_key) in output.
        
        Returns:
            str: Safe representation
        
        Example:
            config = Config(api_key="sk_prod_secret123")
            print(config)
            # Config(
            #   api_key="sk_prod_***",
            #   api_endpoint="https://api.agentobs.io",
            #   batch_size=10,
            #   ...
            # )
        """
        data = self.model_dump()
        
        # Mask sensitive fields
        if data.get("access_key"):
            key = data["access_key"]
            # Show first 8 chars and last 3 chars
            if len(key) > 11:
                data["access_key"] = f"{key[:8]}***{key[-3:]}"
            else:
                data["access_key"] = "sk_***"
        
        items = [f"{k}={v!r}" for k, v in data.items()]
        return f"Config({', '.join(items)})"