import socket

def test_dns(host):
    try:
        ip = socket.gethostbyname(host)
        print(f"DNS OK: {host} -> {ip}")
    except Exception as e:
        print(f"DNS FALHA: {host} -> {e}")

if __name__ == "__main__":
    test_dns("google.com")
    test_dns("db.bkckdyiyiypzutixrtmu.supabase.co")
    test_dns("bkckdyiyiypzutixrtmu.supabase.co")
    test_dns("aws-1-us-east-1.pooler.supabase.com")
