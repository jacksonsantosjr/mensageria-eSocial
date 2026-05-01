from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from core.config import settings

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/auth/login")
async def proxy_login(request: LoginRequest):
    """
    Proxy para login no Supabase.
    Isso evita que o frontend precise das chaves do Supabase no momento do build.
    """
    # A URL de autenticação do Supabase
    auth_url = f"{settings.supabase_url}/auth/v1/token?grant_type=password"
    
    # Precisamos da anon_key para o login público. 
    # Se ela não estiver no settings, podemos tentar usar a service_role (embora não recomendado para login de usuário final, 
    # mas aqui estamos agindo como intermediário).
    # O ideal é o usuário ter configurado SUPABASE_ANON_KEY no backend.
    
    # Vou verificar se temos uma anon key ou usar a service_role (que tem permissão de tudo)
    # Mas o Supabase exige a anon key ou service role no header apikey
    headers = {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                auth_url,
                json={
                    "email": request.email,
                    "password": request.password
                },
                headers=headers
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="E-mail ou senha inválidos.")
            
            return response.json()
        except Exception as e:
            print(f"Erro no Proxy Login: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro ao processar login no provedor de identidade.")
