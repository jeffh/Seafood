include:
	- directories
	
minecraft-server:
    file.managed:
        - name: '/opt/minecraft-server/server.jar'
        - source: https://s3.amazonaws.com/Minecraft.Download/versions/1.6.2/minecraft_server.1.6.2.jar
        - source_hash: sha256=654726af24a9a6b138b11ae426f3025621259211dd50abead7b0b2880fa9b0d8
            - file: '/opt/minecraft-server/'

'/opt/minecraft-server/':
	file.directory:
		- user: {{ pillar['root']['user'] }}
		- group: {{ pillar['root']['group'] }}
		- file_mode: 755
		- dir_mode: 755
		- require:
			- file: '/opt/'
