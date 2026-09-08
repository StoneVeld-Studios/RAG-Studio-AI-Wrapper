import urllib.request
import json

class OllamaSync:
    """
    Handles real-time API handshakes with the local Ollama runner 
    to dynamically pull model parameters and context limits.
    """
    def __init__(self, host="http://localhost:11434"):
        self.base_url = host

    def check_runner_status(self):
        """Pings the local Ollama server to ensure it is awake and active."""
        try:
            # Silent loopback request to check system availability
            response = urllib.request.urlopen(f"{self.base_url}/", timeout=2)
            if response.status == 200:
                return True
        except Exception:
            return False
        return False

    def get_active_context_limit(self, target_model="qwen2.5-coder:3b"):
        """
        Queries the local engine to find the true context parameter (num_ctx).
        Defaults to a conservative 4096 if custom settings aren't found.
        """
        if not self.check_runner_status():
            return 4096  # Standard offline safety default fallback

        try:
            # Query Ollama's local loaded models endpoint
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=2) as response:
                data = json.loads(response.read().decode())
                
            # If the server is up but no models are running yet, return fallback limit
            if not data.get("models"):
                return 4096

            # Perform local API check for model configuration details
            # If a custom parameter profile exists, extract it directly
            model_info_url = f"{self.base_url}/api/show"
            payload = json.dumps({"name": target_model}).encode('utf-8')
            
            req_info = urllib.request.Request(
                model_info_url, 
                data=payload, 
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req_info, timeout=2) as info_resp:
                info_data = json.loads(info_resp.read().decode())
                
                # Scan model parameter options for custom 'num_ctx' inputs
                parameters = info_data.get("parameters", "")
                if "num_ctx" in parameters:
                    for line in parameters.split('\n'):
                        if "num_ctx" in line:
                            # Extract the exact numerical value assigned by the developer
                            return int(''.join(filter(str.isdigit, line)))
                            
        except Exception:
            pass
            
        return 4096  # Return standard safety baseline if custom parameters aren't set
