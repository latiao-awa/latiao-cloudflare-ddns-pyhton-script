
import requests


while True:
    print("start")
    EMAIL = "EMAIL"
    API_KEY = "API_KEY"
    DOMAIN = "DOMAIN"
    SUBDOMAIN_IPV4 = "SUBDOMAIN_IPV4"
    SUBDOMAIN_IPV6 = "SUBDOMAIN_IPV6"

    class CloudflareAPI:
        def __init__(self, email, api_key):
            self.email = email
            self.api_key = api_key
            self.base_url = "https://api.cloudflare.com/client/v4/"
            self.headers = {
                "X-Auth-Email": email,
                "X-Auth-Key": api_key,
                "Content-Type": "application/json",
            }

        def request(self, method, endpoint, data=None):
            url = self.base_url + endpoint
            response = requests.request(method, url, headers=self.headers, json=data)
            return response.json()


        def get_zone_id(self, domain):
            endpoint = f"zones?name={domain}"
            data = self.request("GET", endpoint)
            return data["result"][0]["id"]

        def get_record_id(self, zone_id, record_type, record_name):
            endpoint = f"zones/{zone_id}/dns_records?type={record_type}&name={record_name}"
            data = self.request("GET", endpoint)
            result = data["result"][0]
            return result["id"], result["content"]

        def update_ip(self, zone_id, record_type, record_name, record_id, new_ip):
            endpoint = f"zones/{zone_id}/dns_records/{record_id}"
            data = {"type": record_type, "name": record_name, "content": new_ip}
            self.request("PUT", endpoint, data)


    cloudflare_api = CloudflareAPI(EMAIL, API_KEY)

    
    zone_id = cloudflare_api.get_zone_id(DOMAIN)

    record_id_ipv4, _ = cloudflare_api.get_record_id(zone_id, "A", f"{SUBDOMAIN_IPV4}.{DOMAIN}")
    new_ip_ipv4 = requests.get("https://api.ipify.org").text
    print(new_ip_ipv4)
    cloudflare_api.update_ip(zone_id, "A", f"{SUBDOMAIN_IPV4}.{DOMAIN}", record_id_ipv4, new_ip_ipv4)

    record_id_ipv6, _ = cloudflare_api.get_record_id(zone_id, "AAAA", f"{SUBDOMAIN_IPV6}.{DOMAIN}")
    
    new_ip_ipv6 = requests.get("https://api64.ipify.org").text
    print(new_ip_ipv6)
    cloudflare_api.update_ip(zone_id, "AAAA", f"{SUBDOMAIN_IPV6}.{DOMAIN}", record_id_ipv6, new_ip_ipv6)

    print("fin")