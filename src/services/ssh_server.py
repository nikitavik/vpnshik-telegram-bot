import paramiko

class SSHServer:
    def __init__(self, ip, username, password=None, key_filename=None):
        self.ip = ip
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connected = False

    def connect(self):
        """Establish SSH connection with proper error handling."""
        if not self.ip:
            raise ValueError("Server IP is not set")
        if not self.username:
            raise ValueError("Username is not set")

        try:
            connect_kwargs = {
                'hostname': self.ip,
                'username': self.username,
            }

            # if self.password:
                # connect_kwargs['password'] = self.password
            # elif self.key_filename:
                # connect_kwargs['key_filename'] = self.key_filename
                # raise ValueError("Either password or key_filename must be provided")

            self.ssh.connect(**connect_kwargs)
            self.connected = True
        except paramiko.AuthenticationException:
            raise ValueError("Authentication failed")
        except paramiko.SSHException as e:
            raise ValueError(f"SSH connection failed: {e}")
        except Exception as e:
            raise ValueError(f"Connection failed: {e}")

    def exec_command(self, command):
        """Execute command and return stdout, handle stderr."""
        if not self.connected:
            raise ValueError("SSH connection not established. Call connect() first.")

        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')

            if error:
                raise ValueError(f"Command failed: {error}")

            return output
        except paramiko.SSHException as e:
            raise ValueError(f"SSH command execution failed: {e}")

    def is_connected(self):
        """Check if SSH connection is active."""
        return self.connected

    def close(self):
        """Close SSH connection."""
        if self.ssh:
            self.ssh.close()
        self.connected = False
