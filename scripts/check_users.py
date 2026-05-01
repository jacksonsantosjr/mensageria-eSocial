import requests
import json

url = "https://bkckdyiyiypzutixrtmu.supabase.co/auth/v1/admin/users"
headers = {
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJrY2tkeWl5aXlwenV0aXhydG11Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjI4ODcyNiwiZXhwIjoyMDkxODY0NzI2fQ.xEjnFuUjh7z3h8-peY1snHPUI28LP96i90TQrA0_h3o",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJrY2tkeWl5aXlwenV0aXhydG11Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjI4ODcyNiwiZXhwIjoyMDkxODY0NzI2fQ.xEjnFuUjh7z3h8-peY1snHPUI28LP96i90TQrA0_h3o"
}

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"RAW_DATA: {json.dumps(data, indent=2)}")
        users = data.get('users', []) if isinstance(data, dict) else data
        print(f"USUARIOS_ENCONTRADOS: {len(users)}")
        for user in users:
            print(f"USER: {user.get('email')} - ID: {user.get('id')} - CONFIRMED: {user.get('email_confirmed_at')}")
    else:
        print(f"ERRO_API: {response.status_code} - {response.text}")
except Exception as e:
    print(f"EXCECAO: {str(e)}")
