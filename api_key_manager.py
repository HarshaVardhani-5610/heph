#!/usr/bin/env python3
"""
Perplexity AI API Key Rotation Manager
Handles automatic failover between multiple API keys when credits are exhausted
"""
import os
import json
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import asyncio
import httpx
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIKeyStatus:
    """Track the status of each API key"""
    key_id: str
    key_value: str
    is_active: bool = True
    last_used: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    credits_exhausted: bool = False
    retry_after: Optional[datetime] = None

class PerplexityAPIManager:
    """
    Manages rotation of Perplexity AI API keys with automatic failover
    """
    
    def __init__(self, config_file: str = "perplexity_config.json"):
        self.config_file = config_file
        self.api_keys: List[APIKeyStatus] = []
        self.current_key_index = 0
        self.base_url = "https://api.perplexity.ai"
        self.model_name = "llama-3.1-sonar-large-128k-online"  # Latest Sonar model
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        
        # Load configuration
        self._load_config()
        self._validate_keys()
    
    def _load_config(self) -> None:
        """Load API keys from environment variables and config file"""
        
        # First, try to load from config file if it exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.api_keys = [
                        APIKeyStatus(
                            key_id=key_data['key_id'],
                            key_value=key_data['key_value'],
                            is_active=key_data.get('is_active', True),
                            error_count=key_data.get('error_count', 0),
                            credits_exhausted=key_data.get('credits_exhausted', False)
                        )
                        for key_data in config.get('api_keys', [])
                        if key_data['key_value'].strip()  # Only load non-empty keys
                    ]
                    logger.info(f"Loaded {len(self.api_keys)} API keys from config file")
                    return
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        
        # Load from environment variables (10 placeholders)
        api_keys_loaded = []
        for i in range(1, 11):  # PERPLEXITY_API_KEY_1 through PERPLEXITY_API_KEY_10
            env_var = f"PERPLEXITY_API_KEY_{i}"
            api_key = os.getenv(env_var)
            
            if api_key and api_key.strip():  # Only add non-empty keys
                api_keys_loaded.append(APIKeyStatus(
                    key_id=f"key_{i}",
                    key_value=api_key.strip(),
                    is_active=True
                ))
                logger.info(f"Loaded API key from {env_var}")
        
        self.api_keys = api_keys_loaded
        
        if not self.api_keys:
            logger.warning("No API keys found! Please set environment variables PERPLEXITY_API_KEY_1 through PERPLEXITY_API_KEY_10")
            raise ValueError("No valid Perplexity API keys configured")
        
        # Save initial configuration
        self._save_config()
    
    def _save_config(self) -> None:
        """Save current API key status to config file"""
        try:
            config = {
                "api_keys": [
                    {
                        "key_id": key.key_id,
                        "key_value": key.key_value,
                        "is_active": key.is_active,
                        "error_count": key.error_count,
                        "credits_exhausted": key.credits_exhausted,
                        "last_error": key.last_error,
                        "last_used": key.last_used.isoformat() if key.last_used else None
                    }
                    for key in self.api_keys
                ],
                "current_key_index": self.current_key_index,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def _validate_keys(self) -> None:
        """Validate that we have at least one working API key"""
        active_keys = [key for key in self.api_keys if key.is_active and not key.credits_exhausted]
        
        if not active_keys:
            logger.error("No active API keys available!")
            raise ValueError("All API keys are either inactive or have exhausted credits")
        
        logger.info(f"Validated {len(active_keys)} active API keys out of {len(self.api_keys)} total")
    
    def get_current_key(self) -> Optional[APIKeyStatus]:
        """Get the currently active API key"""
        if not self.api_keys:
            return None
            
        # Find next available key starting from current index
        for i in range(len(self.api_keys)):
            key_index = (self.current_key_index + i) % len(self.api_keys)
            key = self.api_keys[key_index]
            
            # Check if key is usable
            if (key.is_active and 
                not key.credits_exhausted and 
                (key.retry_after is None or datetime.utcnow() > key.retry_after)):
                
                self.current_key_index = key_index
                return key
        
        logger.error("No usable API keys available!")
        return None
    
    def mark_key_exhausted(self, key_id: str, error_message: str = "") -> None:
        """Mark an API key as having exhausted credits"""
        for key in self.api_keys:
            if key.key_id == key_id:
                key.credits_exhausted = True
                key.error_count += 1
                key.last_error = error_message
                key.retry_after = datetime.utcnow() + timedelta(hours=24)  # Retry after 24 hours
                logger.warning(f"API key {key_id} marked as exhausted: {error_message}")
                break
        
        self._save_config()
        self._rotate_to_next_key()
    
    def mark_key_error(self, key_id: str, error_message: str = "") -> None:
        """Mark an API key as having an error (but not necessarily exhausted)"""
        for key in self.api_keys:
            if key.key_id == key_id:
                key.error_count += 1
                key.last_error = error_message
                
                # If too many errors, temporarily disable
                if key.error_count >= 5:
                    key.retry_after = datetime.utcnow() + timedelta(minutes=30)
                    logger.warning(f"API key {key_id} temporarily disabled due to errors: {error_message}")
                
                break
        
        self._save_config()
    
    def reset_key_status(self, key_id: str) -> None:
        """Reset the status of an API key (useful for manual recovery)"""
        for key in self.api_keys:
            if key.key_id == key_id:
                key.credits_exhausted = False
                key.error_count = 0
                key.last_error = None
                key.retry_after = None
                key.is_active = True
                logger.info(f"Reset status for API key {key_id}")
                break
        
        self._save_config()
    
    def _rotate_to_next_key(self) -> None:
        """Rotate to the next available API key"""
        original_index = self.current_key_index
        
        for i in range(1, len(self.api_keys)):
            next_index = (self.current_key_index + i) % len(self.api_keys)
            next_key = self.api_keys[next_index]
            
            if (next_key.is_active and 
                not next_key.credits_exhausted and 
                (next_key.retry_after is None or datetime.utcnow() > next_key.retry_after)):
                
                self.current_key_index = next_index
                logger.info(f"Rotated from key {original_index} to key {next_index}")
                return
        
        logger.error("No available keys to rotate to!")
    
    async def make_api_call(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Make an API call to Perplexity with automatic key rotation on failure
        
        Args:
            prompt: The prompt to send to Perplexity
            **kwargs: Additional parameters for the API call
            
        Returns:
            API response as dictionary
            
        Raises:
            Exception: If all API keys fail
        """
        
        for attempt in range(self.max_retries):
            current_key = self.get_current_key()
            
            if not current_key:
                raise Exception("No available API keys")
            
            try:
                # Prepare the request
                headers = {
                    "Authorization": f"Bearer {current_key.key_value}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": kwargs.get("model", self.model_name),
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": kwargs.get("max_tokens", 4000),
                    "temperature": kwargs.get("temperature", 0.2),
                    "top_p": kwargs.get("top_p", 0.9),
                    "return_citations": kwargs.get("return_citations", True),
                    "search_domain_filter": kwargs.get("search_domain_filter", ["perplexity.ai"]),
                    "return_images": kwargs.get("return_images", False),
                    "return_related_questions": kwargs.get("return_related_questions", False),
                    "search_recency_filter": kwargs.get("search_recency_filter", "month"),
                    "top_k": kwargs.get("top_k", 0),
                    "stream": False,
                    "presence_penalty": kwargs.get("presence_penalty", 0),
                    "frequency_penalty": kwargs.get("frequency_penalty", 1)
                }
                
                # Make the API call
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    
                    # Update last used time
                    current_key.last_used = datetime.utcnow()
                    
                    if response.status_code == 200:
                        logger.info(f"Successful API call using key {current_key.key_id}")
                        self._save_config()
                        return response.json()
                    
                    elif response.status_code == 429:
                        # Rate limit or credits exhausted
                        error_msg = f"Rate limit/credits exhausted: {response.text}"
                        logger.warning(f"Key {current_key.key_id}: {error_msg}")
                        self.mark_key_exhausted(current_key.key_id, error_msg)
                        
                        # Wait a bit before retrying with next key
                        await asyncio.sleep(self.retry_delay)
                        continue
                    
                    elif response.status_code == 401:
                        # Invalid API key
                        error_msg = f"Invalid API key: {response.text}"
                        logger.error(f"Key {current_key.key_id}: {error_msg}")
                        self.mark_key_exhausted(current_key.key_id, error_msg)
                        continue
                    
                    else:
                        # Other error
                        error_msg = f"HTTP {response.status_code}: {response.text}"
                        logger.warning(f"Key {current_key.key_id}: {error_msg}")
                        self.mark_key_error(current_key.key_id, error_msg)
                        
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay)
                            continue
                        else:
                            raise Exception(f"API call failed after {self.max_retries} attempts: {error_msg}")
            
            except httpx.TimeoutException:
                error_msg = "Request timeout"
                logger.warning(f"Key {current_key.key_id}: {error_msg}")
                self.mark_key_error(current_key.key_id, error_msg)
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    raise Exception(f"API call timed out after {self.max_retries} attempts")
            
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(f"Key {current_key.key_id}: {error_msg}")
                self.mark_key_error(current_key.key_id, error_msg)
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    raise Exception(f"API call failed after {self.max_retries} attempts: {error_msg}")
        
        raise Exception("All API key rotation attempts failed")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of all API keys"""
        return {
            "total_keys": len(self.api_keys),
            "active_keys": len([k for k in self.api_keys if k.is_active and not k.credits_exhausted]),
            "exhausted_keys": len([k for k in self.api_keys if k.credits_exhausted]),
            "current_key": self.current_key_index,
            "keys": [
                {
                    "key_id": key.key_id,
                    "is_active": key.is_active,
                    "credits_exhausted": key.credits_exhausted,
                    "error_count": key.error_count,
                    "last_error": key.last_error,
                    "last_used": key.last_used.isoformat() if key.last_used else None,
                    "retry_after": key.retry_after.isoformat() if key.retry_after else None
                }
                for key in self.api_keys
            ]
        }

# Global instance
perplexity_manager = None

def get_perplexity_manager() -> PerplexityAPIManager:
    """Get or create the global Perplexity API manager instance"""
    global perplexity_manager
    if perplexity_manager is None:
        perplexity_manager = PerplexityAPIManager()
    return perplexity_manager

async def call_perplexity_api(prompt: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to call Perplexity API with automatic key rotation
    
    Args:
        prompt: The prompt to send to Perplexity
        **kwargs: Additional parameters for the API call
        
    Returns:
        API response as dictionary
    """
    manager = get_perplexity_manager()
    return await manager.make_api_call(prompt, **kwargs)

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_api():
        """Test the API key rotation system"""
        try:
            # Initialize manager
            manager = get_perplexity_manager()
            
            # Show initial status
            print("Initial API Key Status:")
            print(json.dumps(manager.get_status(), indent=2))
            
            # Test API call
            result = await call_perplexity_api(
                "What is the latest version of Python?",
                max_tokens=1000,
                temperature=0.1
            )
            
            print(f"\nAPI Response: {json.dumps(result, indent=2)}")
            
            # Show final status
            print("\nFinal API Key Status:")
            print(json.dumps(manager.get_status(), indent=2))
            
        except Exception as e:
            print(f"Test failed: {e}")
    
    # Run test
    asyncio.run(test_api())
