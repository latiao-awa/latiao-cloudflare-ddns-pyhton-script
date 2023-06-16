# Import requests, logging and time modules
import requests
import logging
import time

# Define some constants
EMAIL = "EMAIL@EMAIL.com"
API_KEY = "123456789"
DOMAIN = "DOMAIN.com"
SUBDOMAIN_IPV4 = "ipv4ddns"
SUBDOMAIN_IPV6 = "ipv6ddns"
UPDATE_INTERVAL = 30

# Set the log format and level
logging.basicConfig(
    format="[latiao's cloudflare ddns]" '%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# Define a CloudflareAPI class
class CloudflareAPI:

    # Initialize the class attributes
    def __init__(self, email, api_key):
        self.email = email
        self.api_key = api_key
        self.headers = {
            "X-Auth-Email": email,
            "X-Auth-Key": api_key,
            "Content-Type": "application/json"
        }

    # Define a method to get the zone_id based on the domain name
    def get_zone_id(self, domain):
        url = f"https://api.cloudflare.com/client/v4/zones?name={domain}"
        while True:  # Use an infinite loop until successful or an exception occurs
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()  # Check if the response status code is 200
                data = response.json()
                assert data["success"]  # Check if the response data contains success as True
                zone_id = data["result"][0]["id"]  # Get the id of the first result as zone_id
                return zone_id  # Return zone_id
            except requests.exceptions.HTTPError as e:  # Catch HTTP error exception
                logging.error(f"Failed to get zone_id, HTTP error: {e}")  # Log error message

            except AssertionError:  # Catch assertion error exception
                logging.error(
                    f"Failed to get zone_id, assertion error: {data['errors']}"
                )  # Log error message

            except Exception as e:  # Catch other exceptions
                logging.error(f"Failed to get zone_id, exception error: {e}")  # Log error message

    # Define a method to get the record name based on the subdomain and domain name
    def get_record_name(self, subdomain, domain):
        return domain if subdomain == "" else f"{subdomain}.{domain}"

    # Define a method to get the record id and old ip address based on zone_id, record type and record name
    def get_record_id(self, zone_id, record_type, record_name):
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type={record_type}&name={record_name}"
        while True:  # Use an infinite loop until successful or an exception occurs
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()  # Check if the response status code is 200
                data = response.json()
                assert data["success"]  # Check if the response data contains success as True
                record_id = data["result"][0]["id"]  # Get the id of the first result as record_id
                old_ip = data["result"][0]["content"]  # Get the content of the first result as old_ip
                return record_id, old_ip  # Return record_id and old_ip
            except requests.exceptions.HTTPError as e:  # Catch HTTP error exception
                logging.error(
                    f"Failed to get record_id or old_ip, HTTP error: {e}"
                )  # Log error message

            except AssertionError:  # Catch assertion error exception
                logging.error(
                    f"Failed to get record_id or old_ip, assertion error: {data['errors']}"
                )  # Log error message

            except Exception as e:  # Catch other exceptions
                logging.error(
                    f"Failed to get record_id or old_ip, exception error: {e}"
                )  # Log error message

    # Define a method to update the ip address based on zone_id, record type, record name, record id, old ip and new ip
    def update_ip(self, zone_id, record_type, record_name, record_id, old_ip, new_ip):
        if new_ip == old_ip:  # If the new ip and the old ip are the same
            logging.info(
                f"The current {record_type} address {new_ip} is the same as the original {record_type} address {old_ip}, no need to update."
            )  # Log info message, no need to update
        else:  # If the new ip and the old ip are different
            logging.info(
                f"The current {record_type} address {new_ip} is different from the original {record_type} address {old_ip}, need to update."
            )  # Log info message, need to update
            url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"  # Construct the update request url
            data = {  # Construct the update request data
                "type": record_type,
                "name": record_name,
                "content": new_ip,
            }

            while True:  # Use an infinite loop until successful or an exception occurs
                try:  # Try to send the update request
                    response = requests.put(url, headers=self.headers, json=data)
                    response.raise_for_status()  # Check if the response status code is 200
                    data = response.json()
                    assert data["success"]  # Check if the response data contains success as True
                    logging.info(
                        f"Update successful. The IP address of {record_name} has been changed from {old_ip} to {new_ip}."
                    )  # Log info message, update successful
                    break  # Break out of the loop

                except requests.exceptions.HTTPError as e:  # Catch HTTP error exception
                    logging.error(f"Update failed. HTTP error: {e}")  # Log error message, update failed

                    pass  # Skip exception handling
                except AssertionError:  # Catch assertion error exception
                    logging.error(
                        f"Update failed. Assertion error: {data['errors']}"
                    )  # Log error message, update failed

                    pass  # Skip exception handling 
                except Exception as e:  # Catch other exceptions
                    logging.error(f"Update failed. Exception error: {e}")  # Log error message, update failed

                    pass  # Skip exception handling 

# Create an instance of the CloudflareAPI class, passing in the email and api_key as parameters
cf_api = CloudflareAPI(EMAIL, API_KEY)


# Call the get_zone_id method, passing in the domain name as a parameter, and get the zone_id
zone_id = cf_api.get_zone_id(DOMAIN)

# Use an infinite loop to perform an update operation every interval
while True:

    while True:  # Use an infinite loop until you get the IP address or an exception occurs
        try:
            ipv4 = requests.get("https://api.ipify.org").text  # Get the ipv4 address
            ipv6 = requests.get("https://api64.ipify.org").text  # Get the ipv6 address
            break  # Break out of the loop
        except Exception as e:  # Catch exception
            logging.error(f"Failed to get IP address retry after", e)

    # Call the get_record_name method, passing in the subdomain and domain name as parameters, and get the record name (ipv4)
    record_name_ipv4 = cf_api.get_record_name(SUBDOMAIN_IPV4, DOMAIN)
    # Call the get_record_id method, passing in the zone_id, record type (A) and record name (ipv4) as parameters, and get the record id and old ip address (ipv4)
    record_id_ipv4, old_ipv4 = cf_api.get_record_id(zone_id, "A", record_name_ipv4)
    # Call the update_ip method, passing in the zone_id, record type (A), record name (ipv4), record id, old ip address (ipv4) and new ip address (ipv4) as parameters, and update the ip address (ipv4)
    cf_api.update_ip(zone_id, "A", record_name_ipv4, record_id_ipv4, old_ipv4, ipv4)

    # Call the get_record_name method, passing in the subdomain and domain name as parameters, and get the record name (ipv6)
    record_name_ipv6 = cf_api.get_record_name(SUBDOMAIN_IPV6, DOMAIN)
    # Call the get_record_id method, passing in the zone_id, record type (AAAA) and record name (ipv6) as parameters, and get the record id and old ip address (ipv6)
    record_id_ipv6, old_ipv6 = cf_api.get_record_id(zone_id, "AAAA", record_name_ipv6)
    # Call the update_ip method, passing in the zone_id, record type (AAAA), record name (ipv6), record id, old ip address (ipv6) and new ip address (ipv6) as parameters, and update the ip address (ipv6)
    cf_api.update_ip(zone_id, "AAAA", record_name_ipv6, record_id_ipv6, old_ipv6, ipv6)
    # Wait for a period of time (UPDATE_INTERVAL) before performing the next update operation
    time.sleep(UPDATE_INTERVAL)  
