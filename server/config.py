from configparser import ConfigParser

def config(filename='database.ini', section='postgresql'):
    # Initialize a parse to parse the files
    parser = ConfigParser()
    # Read config file
    parser.read(filename)
 
    # Retrieve each section of config file
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')
 
    return db