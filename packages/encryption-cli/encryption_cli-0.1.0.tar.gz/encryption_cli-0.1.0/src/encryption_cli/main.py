#Imports
import os
from InquirerPy import inquirer
from cryptography.fernet import Fernet
from pathlib import Path
from rich import print
from rich.console import Console
from rich.table import Table
from multiprocessing import Pool

#Credits table stuff
console = Console()
table = Table(title="Credits", style="bold white")
table.add_column("Credited", justify="center", style="bold yellow")
table.add_column("What For", justify="center", style="bold cyan")
table.add_row("Franek Kurzawa", "Programmer")
table.add_row("rich", "Displayment of fancy colored text")
table.add_row("pathlib", "Taking Care of The Paths")
table.add_row("Fernet", "Encrypting/Decrypting Files")
table.add_row("InquirerPy", "Easy Fancy Inputs")

#Get files function
def get_files(dir):
    files = [str(file) for file in dir.rglob("*") if file.is_file()]
    return files

def warning():
    print("REMEMBER that you are encrypting your files. If you lose the key, it's not my fault and I am not responsible for that.\n")
    consent = inquirer.text(
        message="Type YES if you agree, or type NO if you decline.",
        validate=lambda text: str(text).lower() in ("yes", "no")
    ).execute()
    if str(consent).lower() == "yes":
        return True
    elif str(consent).lower() == "no":
        return False
    else:
        print("Idk how but you broke the program. Congratulations!")
    
#Encryption function
def encryption():
    if warning():
        #Ask for encryption fernet_key
        fernet_key = inquirer.secret(
            "Enter Your Fernet Key: "
        ).execute()
        fernet_key = str(fernet_key).encode()
        print()
        #Get all files in the directory
        files_path = Path(".")
        files = get_files(files_path)
        for file in files:

            file_path = files_path / str(file)

            read_perm = os.access(file, os.R_OK)
            write_perm = os.access(file, os.W_OK)
            exists = os.path.exists(file)

            if read_perm and write_perm and exists:
                
                with open(file_path, "rb") as unencrypted_file:
                    unencrypted_data = unencrypted_file.read()
                
                encrypted_data = Fernet(fernet_key).encrypt(unencrypted_data)

                with open(file_path, "wb") as encrypted_file:
                    encrypted_file.write(encrypted_data)
                
                print(f"[bold][#ff0000]Encrypted[/#ff0000]: {file}[/bold]")
            else:
                print(f"[bold][#ffff00]Skipped[/#ffff00]: {file} (No Permission)[/bold]")
    else:
            print("\nHave a nice day :)\n")

#Decryption function
def decryption():
    #Ask for encryption fernet_key
    fernet_key = inquirer.secret(
        "Enter Your Fernet Key: "
    ).execute()
    fernet_key = str(fernet_key).encode()
    print()
    #Get all files in the directory
    files_path = Path(".")
    files = get_files(files_path)
    for file in files:
            
        file_path = files_path / str(file)

        read_perm = os.access(file, os.R_OK)
        write_perm = os.access(file, os.W_OK)
        exists = os.path.exists(file)

        if read_perm and write_perm and exists:

            with open(file_path, "rb") as encrypted_file:
                encrypted_data = encrypted_file.read()
                
                decrypted_data = Fernet(fernet_key).decrypt(encrypted_data)

                with open(file_path, "wb") as decrypted_file:
                    decrypted_file.write(decrypted_data)
                
                print(f"[bold][#00ff00]Decrypted[/#00ff00]: {file}[/bold]")
        else:
            print(f"[bold][#ffff00]Skipped[/#ffff00]: {file} (No Permission)[/bold]")

#Credits :)
def credits():
    console.print(table)
    print("\n\n")
    main()

def generate_keys():
    key = Fernet.generate_key()
    key = key.decode()
    print(f"[grey]Your [white bold italic]Key[/white bold italic] is:[/grey] [bold yellow]{key}[/]")

#Main Function
def main():

    #Action Selection
    try:
        option = inquirer.select(
            message="Chose Action: ",
            choices=[
                "Encrypt",
                "Decrypt",
                "Generate Key",
                "Credits"
            ]
        ).execute()
    
        if option == "Encrypt":
            with Pool() as pool:
                pool.apply(encryption)
        elif option == "Decrypt":
            with Pool() as pool:
                pool.apply(decryption)
        elif option == "Generate Key":
            generate_keys()
        elif option == "Credits":
            credits()
        else:
            print("Idk how but you broke the program. Congratulations!")
            
    except KeyboardInterrupt:
        print("\nSee [bold]you[/] later!\n")
        exit()


if __name__ == "__main__":
    main()