import configparser

# Configration class that reads configuraiton data from a file
class RobotConfig:
	GENERAL_SECTION = 'OPTIONS'
	SERVER_ADDRESS_CFG = 'server_address'
	STATUS_PORT_CFG = 'status_port'
	VIDEO_PORT_CFG = 'video_port'
	COMMAND_PORT_CFG = 'command_port'
	ROBOT_NAME_CFG = 'robot_name'
	NETWORK_ADAPTER_CFG = 'network_adapter'
	IP_LOCATION_PORT_CFG = 'ip_controller_port'
	ADDRESS_TOP_CFG = 'address_top'
	
	def __init__(self, config_filename):
		self.config_filename = config_filename
		self.config = configparser.ConfigParser()
		self.config.read(config_filename)

	def get_option_str(self, parameter):
		value = self.config.get(self.GENERAL_SECTION, parameter, fallback="")
		if value != "":
			print("Found '" + parameter + "' config option in " + self.config_filename + " configuration file")
		else:
			print("Warning '" + parameter + "' config option not found in " + self.config_filename + " configuration file")
			
		return str(value)

	def get_option_bool(self, parameter):
		value = self.config.getboolean(self.GENERAL_SECTION, parameter, fallback="False")
		if value != "":
			print("Found '" + parameter + "' config option in " + self.config_filename + " configuration file")
		else:
			print("Warning '" + parameter + "' config option not found in " + self.config_filename + " configuration file")
		
		return bool(value)
		

# RobotConfig test code
if __name__ == "__main__":
	rc = RobotConfig("../robot1_config/config.txt")
	rc.get_option_str(rc.SERVER_ADDRESS_CFG)
	rc.get_option_str(rc.STATUS_PORT_CFG)
	rc.get_option_str(rc.VIDEO_PORT_CFG)
	rc.get_option_str(rc.COMMAND_PORT_CFG)
	rc.get_option_str(rc.ROBOT_NAME_CFG)
	rc.get_option_str(rc.NETWORK_ADAPTER_CFG)
	rc.get_option_str(rc.IP_LOCATION_PORT_CFG)
	rc.get_option_str(rc.ADDRESS_TOP_CFG)	

