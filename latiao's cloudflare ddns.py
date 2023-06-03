import requests
import logging 

 
EMAIL = "EMAIL"  
API_KEY = "API_KEY"  
DOMAIN = "DOMAIN"  
SUBDOMAIN_IPV4 = "SUBDOMAIN_IPV4"
SUBDOMAIN_IPV6 = "SUBDOMAIN_IPV6"
UPDATE_INTERVAL = 0

 
logging.basicConfig(format="[latiao's cloudflare ddns]" '%(asctime)s - %(levelname)s - %(message)s' , level=logging.INFO)

 
class CloudflareAPI:

    def __init__(self, email, api_key):
        self.email = email
        self.api_key = api_key
        self.headers = {
            "X-Auth-Email": email,
            "X-Auth-Key": api_key,
            "Content-Type": "application/json"
        }

    def get_zone_id(self, domain):
        url = f"https://api.cloudflare.com/client/v4/zones?name={domain}"
        while True:  
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()  
                data = response.json()
                assert data["success"]  
                zone_id = data["result"][0]["id"]
                return zone_id
            except requests.exceptions.HTTPError as e:
                logging.error(f"Failed to get zone_id, HTTP error: {e}")
 
            except AssertionError:
                logging.error(f"Failed to get zone_id, assertion error: {data['errors']}")
 
            except Exception as e:
                logging.error(f"Failed to get zone_id, exception error: {e}")
 

    def get_record_name(self, subdomain, domain):
        return domain if subdomain == "" else f"{subdomain}.{domain}"

    def get_record_id(self, zone_id, record_type, record_name):
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type={record_type}&name={record_name}"
        while True: 
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status() 
                data = response.json()
                assert data["success"] 
                record_id = data["result"][0]["id"]
                old_ip = data["result"][0]["content"]
                return record_id, old_ip
            except requests.exceptions.HTTPError as e:
                logging.error(f"Failed to get record_id or old_ip, HTTP error: {e}")
 
            except AssertionError:
                logging.error(f"Failed to get record_id or old_ip, assertion error: {data['errors']}")
 
            except Exception as e:
                logging.error(f"Failed to get record_id or old_ip, exception error: {e}")
 

    def update_ip(self, zone_id, record_type, record_name, record_id, old_ip, new_ip):
        if new_ip == old_ip:
            logging.info(f"The current {record_type} address {new_ip} is the same as the original {record_type} address {old_ip}, no need to update.")
        else:
            logging.info(f"The current {record_type} address {new_ip} is different from the original {record_type} address {old_ip}, need to update.")
            url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
            data = {
                "type": record_type,
                "name": record_name,
                "content": new_ip,
            }
 
            try:
                response = requests.put(url, headers=self.headers, json=data)
                response.raise_for_status()  
                data = response.json()
                assert data["success"] 
                logging.info(f"Update successful. The IP address of {record_name} has been changed from {old_ip} to {new_ip}.")
         
            except requests.exceptions.HTTPError as e:
                logging.error(f"Update failed. HTTP error: {e}")
             
                pass 
            except AssertionError:
                logging.error(f"Update failed. Assertion error: {data['errors']}")
                 
                pass  
            except Exception as e:
                logging.error(f"Update failed. Exception error: {e}")
    
                pass  


 
cf_api = CloudflareAPI(EMAIL, API_KEY)

 
zone_id = cf_api.get_zone_id(DOMAIN)

while True:

    while True:  
        try:
            ipv4 = requests.get("https://api.ipify.org").text
            ipv6 = requests.get("https://api64.ipify.org").text
            break 
        except Exception as e:
            logging.error(f"Failed to get IP address retry after", e)
             

    record_name_ipv4 = cf_api.get_record_name(SUBDOMAIN_IPV4, DOMAIN)
    record_id_ipv4, old_ipv4 = cf_api.get_record_id(zone_id, "A", record_name_ipv4)
    cf_api.update_ip(zone_id, "A", record_name_ipv4, record_id_ipv4, old_ipv4, ipv4)

    record_name_ipv6 = cf_api.get_record_name(SUBDOMAIN_IPV6, DOMAIN)
    record_id_ipv6, old_ipv6 = cf_api.get_record_id(zone_id, "AAAA", record_name_ipv6)
    cf_api.update_ip(zone_id, "AAAA", record_name_ipv6, record_id_ipv6, old_ipv6, ipv6)


