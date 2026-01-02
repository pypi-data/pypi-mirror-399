import requests
import time
import os

class AgentPay:
    """
    SDK Universal 'Irrompible' de AgentPay.
    Diseñado para integrarse en Agentes de IA, MCP Servers y Frameworks Autónomos.
    """
   
    def __init__(self, api_key=None, base_url="https://agentpay-core.onrender.com"):
        self.api_key = api_key or os.getenv("AGENTPAY_API_KEY")
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "X-API-KEY": self.api_key, 
            "Content-Type": "application/json"
        }

    @classmethod
    def from_env(cls):
        """Inicializa el SDK usando variables de entorno."""
        return cls()

    @property
    def email(self):
        """Retorna el email corporativo persistente del agente."""
        if not self.api_key: return None
        clean_id = str(self.api_key).replace("sk_", "")
        return f"bot_{clean_id[:12]}@agentpay-it.com"

    def get_email(self):
        """Método simplificado para obtener el email corporativo del agente sin configuraciones manuales."""
        return self.email

    def _post(self, endpoint, data, timeout=20):
        try:
            if self.api_key and "agent_id" not in data:
                data["agent_id"] = self.api_key
               
            response = requests.post(f"{self.base_url}{endpoint}", json=data, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            try:
                error_detail = response.json().get("message", str(e))
            except:
                error_detail = str(e)
            return {"success": False, "status": "ERROR", "message": error_detail}

    # --- MCP TOOL SCHEMAS ---

    def to_mcp(self):
        """Retorna la definición de herramientas para servidores MCP (Anthropic/Claude)."""
        return [
            {
                "name": "agentpay_pay",
                "description": "Execute a real money payment or buy a service/subscription.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "vendor": {"type": "string", "description": "Domain of the vendor (e.g., store.com)"},
                        "amount": {"type": "number", "description": "USD amount"},
                        "description": {"type": "string", "description": "Purpose of the payment"}
                    },
                    "required": ["vendor", "amount", "description"]
                }
            },
            {
                "name": "agentpay_get_otp",
                "description": "Checks for a verification code (OTP) in the agent's private email inbox.",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "agentpay_get_balance",
                "description": "Check the current wallet balance and spending health.",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    # --- CORE METHODS ---

    def pay(self, vendor, amount, description):
        """Ejecuta un pago auditado por IA Guard."""
        return self._post("/v1/pay", {"vendor": vendor, "amount": float(amount), "description": description})

    def get_status(self):
        """Consulta balance y estado del agente."""
        return self._post("/v1/agent/status", {})

    def wait_for_otp(self, timeout=60, interval=5):
        """Polling inteligente para esperar un código OTP."""
        start = time.time()
        while time.time() - start < timeout:
            res = self._post("/v1/identity/check", {})
            if res.get("status") == "RECEIVED":
                if "otp_code" in res: return res["otp_code"]
                if "latest_message" in res and "otp_code" in res["latest_message"]:
                    return res["latest_message"]["otp_code"]
            time.sleep(interval)
        return None

    def get_otp(self, timeout=60):
        """Alias simplificado para wait_for_otp()."""
        return self.wait_for_otp(timeout=timeout)

    def top_up(self, amount):
        """Genera link de recarga Stripe."""
        return self._post("/v1/topup/create", {"amount": amount})

    @staticmethod
    def register(client_name, base_url="https://agentpay-core.onrender.com"):
        """Registro rápido de nuevos agentes utilizando el servidor de producción por defecto."""
        try:
            res = requests.post(f"{base_url.rstrip('/')}/v1/agent/register", json={"client_name": client_name}, timeout=15).json()
            return res
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- EXTENDED FEATURES ---

    def create_identity(self, needs_phone=False):
        """Crea Email persistente + Proxy."""
        return self._post("/v1/identity/create", {"needs_phone": needs_phone})

    def report_fraud(self, vendor, reason):
        """Reporte a la Mente Colmena."""
        return self._post("/v1/fraud/report", {"vendor": vendor, "reason": reason})

    def set_limits(self, max_tx=None, daily_limit=None):
        """Límites de presupuesto dinámicos."""
        return self._post("/v1/agent/limits", {"max_tx": max_tx, "daily_limit": daily_limit})

    def sign_contract(self, contract_hash):
        """Firma legal automatizada."""
        return self._post("/v1/legal/sign", {"contract_hash": contract_hash})

    def configure(self, webhook_url=None, owner_email=None):
        """Configuración de alertas."""
        return self._post("/v1/agent/settings", {"webhook_url": webhook_url, "owner_email": owner_email})

    # --- ALIASES ---
    def check_otp(self): return self._post("/v1/identity/check", {})
    def get_balance(self): return self.get_status()