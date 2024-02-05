from ftplib import FTP
import ftplib

ftp = FTP()
ftp.connect("localhost", 8000)
ftp.login("test", "test")




while True:
    current_path = ftp.pwd()
    print(f"Current directory: {current_path}")

    ftp.dir()

    user_input = input("Enter path or command (type 'exit' to quit): ")

    if user_input.lower() == 'exit':
        break

    try:
        # Try changing to the specified directory
        ftp.cwd(user_input)
        print(f"Changed to directory: {user_input}")
    except ftplib.error_perm:
        # If changing directory fails, try sending it as an FTP command
        try:
            response = ftp.sendcmd(user_input)
            print(f"Command response: {response}")
        except ftplib.error_perm as e:
            print(f"Error: {e}")





