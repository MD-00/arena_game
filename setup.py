import configparser

cp = configparser.RawConfigParser()
FileName = "config.cfg"
cp.read(FileName)

height = int(cp.get('setup', 'height'))
width = int(cp.get('setup', 'width'))
name = str(cp.get('setup', 'name'))