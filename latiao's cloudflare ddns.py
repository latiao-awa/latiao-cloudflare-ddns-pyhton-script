# latiao's cloudflare ddns 
import requests
import time 
email = "email"
api_key = "api_key"
domain = "latiaoawa.top"
subdomain_ipv4 = "ipv4ddns"
subdomain_ipv6 = "ipv6ddns"

ipv4 = requests.get("https://api.ipify.org").text
ipv6 = requests.get("https://api64.ipify.org").text

headers = {
    "X-Auth-Email": email,
    "X-Auth-Key": api_key,
    "Content-Type": "application/json"
}

def get_zone_id(domain):
    url = f"https://api.cloudflare.com/client/v4/zones?name={domain}"
    try:
        response = requests.get(url, headers=headers)
        assert response is not None
        assert response.json()["success"]
        zone_id = response.json()["result"][0]["id"]
        return zone_id
    except AssertionError:
        print("Failed to get zone_id, assertion error:", response.json()["errors"])
        
    except Exception as e:
        print("Failed to get zone_id, exception error:", e)
        

def get_record_name(subdomain, domain):
    return domain if subdomain == "" else f"{subdomain}.{domain}"

def get_record_id(zone_id, record_type, record_name):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type={record_type}&name={record_name}"
    try:
        response = requests.get(url, headers=headers)
        assert response.json()["success"]
        record_id = response.json()["result"][0]["id"]
        old_ip = response.json()["result"][0]["content"]
        return record_id, old_ip
    except AssertionError:
        print("Failed to get record_id or old_ip, assertion error:", response.json()["errors"])
        
    except Exception as e:
        print("Failed to get record_id or old_ip, exception error:", e)
        

def update_ip(zone_id, record_type, record_name, record_id, old_ip, new_ip):
    if new_ip == old_ip:
        print(f"The current {record_type} address {new_ip} is the same as the original {record_type} address {old_ip}, no need to update.")
    else:
        print(f"The current {record_type} address {new_ip} is different from the original {record_type} address {old_ip}, need to update.")
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
        data = {
            "type": record_type,
            "name": record_name,
            "content": new_ip,
        }
        try:
            response = requests.put(url, headers=headers, json=data)
            assert response.json()["success"]
            print(f"Update successful. The IP address of {record_name} has been changed from {old_ip} to {new_ip}.")
        except AssertionError:
            print("Update failed. Assertion error:", response.json()["errors"])
        except Exception as e:
            print("Update failed. Exception error:", e)

while True:

    zone_id = get_zone_id(domain)

    record_name_ipv4 = get_record_name(subdomain_ipv4, domain)
    record_id_ipv4, old_ipv4 = get_record_id(zone_id, "A", record_name_ipv4)
    update_ip(zone_id, "A", record_name_ipv4, record_id_ipv4, old_ipv4, ipv4)

    record_name_ipv6 = get_record_name(subdomain_ipv6, domain)
    record_id_ipv6, old_ipv6 = get_record_id(zone_id, "AAAA", record_name_ipv6)
    update_ip(zone_id, "AAAA", record_name_ipv6, record_id_ipv6, old_ipv6, ipv6)
    time.sleep(60)
