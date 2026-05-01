import requests
import json

user_id = "b560d49a-6e69-40b9-80af-f56f910f0c54"
new_email = "jacksonsantosjr@gmail.com"
url = f"https://bkckdyiyiypzutixrtmu.supabase.co/auth/v1/admin/users/{user_id}"

headers = {
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJrY2tkeWl5aXlwenV0aXhydG11Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjI4ODcyNiwiZXhwIjoyMDkxODY0NzI2fQ.xEjnFuUjh7z3h8-peY1snHPUI28LP96i90TQrA0_h3o",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJrY2tkeWl5aXlwenV0aXhydG11Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjI4ODcyNiwiZXhwIjoyMDkxODY0NzI2fQ.xEjnFuUjh7z3h8-peY1snHPUI28LP96i90TQrA0_h3o",
    "Content-Type": "application/json"
}

data = {
    "email": new_email,
    "email_confirm": True  # Já confirma o email para evitar bloqueios
}

try:
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"SUCESSO: E-mail atualizado para {new_email}")
        print(f"RETORNO: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"ERRO_API: {response.status_code} - {response.text}")
except Exception as e:
    print(f"EXCECAO: {str(e)}")
