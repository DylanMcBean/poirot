# IMPORTS ---------------------------------------------------------------------
import requests, json, re, sys, os, bs4
from termcolor import colored


# INFORMATION VARIABLES -------------------------------------------------------
module_name = "Poirot: osint tool for searching usernames."
__version__ = "0.0.1"
top_art = """
                    ██████        ██████████  ██████████        ██████                  
                  ████        ██████████████████████████████        ████                
                  ████    ██████████████████████████████████████    ████                
                  ██████████████████████████████████████████████████████                
                    ████████████████████████  ████████████████████████                  
                      ██████████████████          ██████████████████                    
                          ████████                      ████████                        

"""


# FUNCTIONS -------------------------------------------------------------------
def main():
	print(f"Poirot Version: {__version__}\n{module_name}\n{top_art}") # print module information
	
	# get username from args
	username = "Tiffany_Douglas"#sys.argv[1]
	curr_working_dir = os.path.join(os.path.dirname(__file__))
	
	json_site_data = json.load(open(f"{curr_working_dir}/resources/site_data.json"))
	json_accounts_data = json.load(open(f"{curr_working_dir}/resources/accounts_data.json"))
	
	for item in json_site_data:
		site_data = json_site_data[item] # Get Site Data from JSON
		search_url = site_data['url'].replace('{}', username)
		
		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
		response = requests.get(url=search_url, headers=headers)
		
		if has_error(item,site_data,response):
			continue
		
		print_text = f"{colored(item,'green')} - {site_data['main_url'].replace('{}', username)}"
		other_print_data = get_extra_content(username, item, site_data, json_accounts_data, response)
		
		if other_print_data == None:
			print(f"{colored(item,'red')} - No Match Found")
		else:
			print(f"{print_text}{other_print_data}")

def has_error(item,site_data,response):
	response_content = response.content.decode("utf-8", errors="ignore")
	
	if site_data["error_type"] == "status" and response.status_code == site_data["error_value"]:
		print(f"{colored(item,'red')} - No Match Found")
		return True
	elif site_data["error_type"] == "message" and site_data["error_value"] in response_content:
		print(f"{colored(item,'red')} - No Match Found")
		return True
	elif site_data["error_type"] == "message_group" and sum(x in response_content for x in site_data["error_value"]) > 0:
		print(f"{colored(item,'red')} - No Match Found")
		return True
	return False

def get_extra_content(username, item, site_data, json_accounts_data, response):
	beautiful_responce_content = bs4.BeautifulSoup(response.text, "html.parser")
	
	try:
		extra_print_text = ""
		if "extra_information" in site_data or site_data["has_bio"]: # Get extra info from responce data
			extra_print_text += ", Extra Information: "

		# get bio info
		if site_data["has_bio"]:
			bio_content = []
			try:
				if site_data["bio_type"] == "class":
					bio_content = beautiful_responce_content.find_all("div", {"class": site_data["bio_search_text"]})[0].prettify()
				elif site_data["bio_type"] == "script":
					bio_content = beautiful_responce_content.find_all("script", type=site_data["bio_search_text"])[0].prettify()

				for account in json_accounts_data:
					regex_match = re.findall(json_accounts_data[account]['regex_match'], bio_content,re.IGNORECASE)
					if len(regex_match) > 0 and regex_match[0] != username:
						extra_print_text += f"{account} = \"{regex_match[-1]}\", "
			except Exception as e:
				pass

		# get extra data
		if "extra_information" in site_data:
			response_content = response.content.decode("utf-8", errors="ignore")
			for extra in site_data["extra_information"]:
				regex_match = re.findall(site_data['extra_information'][extra]['regex_match'], response_content,re.IGNORECASE)[0]
				if len(regex_match) > 0 and regex_match != username:
					extra_print_text += f"{extra} = \"{regex_match}\", "
			
		return extra_print_text if extra_print_text != ", Extra Information: " else ""
	except Exception as e:
		print("oops")
		return None

# if running this file directly from the command line
if __name__ == "__main__":
    main()
