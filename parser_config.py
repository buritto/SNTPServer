class ParserException(Exception):
    def __init__(self, msg):
        self.msg = msg


class ParserConfig:
    def __init__(self, path_config):
        self.path = path_config
        self.ip_address = "0.0.0.0"
        self.wrong_time = 0
        self.count_client = 1

    def parse(self):
        with open(self.path, 'r') as conf_file:
            all_data_field = conf_file.readlines()
        ignore_char = ' \n\t'
        for field in all_data_field:
            line_data = field.split(':')
            name_field = line_data[0].strip(ignore_char)
            if name_field == 'ip':
                self.ip_address = line_data[1].strip(ignore_char)
            if name_field == 'wrong_time':
                self.wrong_time = self.try_get_value(line_data[1], ignore_char)
            if name_field == 'count_client':
                self.count_client = self.try_get_value(line_data[1], ignore_char)

    def try_get_value(self, value, ignore_char):
        try:
            return int(value.strip(ignore_char))
        except Exception as exc:
            raise ParserException("count_client be wrong(not int) format")
