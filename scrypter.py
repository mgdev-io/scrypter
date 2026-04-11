from cryptography.fernet import Fernet, InvalidToken
import argparse
import os
import sys

def confirm_overwrite(path):
    """
    Ask the user whether to overwrite an existing file.

    Loops until the user enters 'y' or 'n'.

    Returns:
        bool: True if overwrite is confirmed, False otherwise.
    """

    while True:
        choice = input(f"{path} already exists, overwrite? (y/n): ")
        match choice.lower():
            case "y": return True
            case "n": return False
            case _: print("Invalid choice")

def write_file(path, data):
    """
    Write binary data to a file.

    Returns:
        int: 0 on success, 1 on OS error.
    """

    try:
        with open(path, "wb") as f:
            f.write(data)
        return 0
    except OSError:
        return 1

def encrypt_file(args):
    """
    Encrypt a file using a Fernet key and save it as a .enc file.

    Handles file validation, encryption, and overwrite logic.
    """

    file_path = os.path.abspath(args.file)
    key_path = os.path.abspath(args.key)

    if not os.path.isfile(file_path):
        print("File path doesn't exist")
        return 1
    if not os.path.isfile(key_path):
        print("Key path doesn't exist") 
        return 1

    try:
        with open(key_path, "rb") as f:
            key = f.read()
    except OSError:
        print("Unable to access key")
        return 1

    try:
        fernet = Fernet(key)
    except ValueError:
        print("Corrupted or empty key")
        return 1

    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except OSError:
        print("Unable to access file")
        return 1

    encrypted_data = fernet.encrypt(data)
    encrypted_file_path = file_path + ".enc"

    if not os.path.isfile(encrypted_file_path) or args.force:
        status = write_file(encrypted_file_path, encrypted_data)
        if status == 0:
            print("File encrypted successfully")
            return status
        else:
            print("Couldn't create encrypted file")
            return status
    elif confirm_overwrite(encrypted_file_path):
        status = write_file(encrypted_file_path, encrypted_data)
        if status == 0:
            print("File encrypted successfully")
            return status
        else:
            print("Couldn't create encrypted file")
            return status
    else:
        print("Aborting...")
        return 1

def decrypt_file(args):
    """
    Decrypt a .enc file using a Fernet key.

    Can either print the output or write it to a file.
    Handles invalid keys and decoding errors.
    """

    file_path = os.path.abspath(args.file)
    key_path = os.path.abspath(args.key)

    if not os.path.isfile(file_path):
        print("File path doesn't exist")
        return 1
    if not os.path.isfile(key_path):
        print("Key path doesn't exist") 
        return 1

    try:
        with open(key_path, "rb") as f:
            key = f.read()
    except OSError:
        print("Unable to access key")
        return 1

    try:
        fernet = Fernet(key)
    except ValueError:
        print("Corrupted or empty key")
        return 1
    
    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except OSError:
        print("Unable to access file")
        return 1

    try:
        decrypted_data = fernet.decrypt(data)
    except InvalidToken:
        print("Invalid key")
        return 1

    if args.print:
        try:
            print(decrypted_data.decode("utf-8"))
        except UnicodeDecodeError:
            print("Warning, file contains characters that can't be decoded")
            print(decrypted_data[:500])
            if len(decrypted_data) > 500:
                print("... Data truncated")
        return 0

    if file_path.endswith(".enc"):
        decrypted_file_path = file_path.removesuffix(".enc")
    else:
        print("Unsupported file type")
        return 1

    if not os.path.isfile(decrypted_file_path) or args.force:
        status = write_file(decrypted_file_path, decrypted_data)
        if status == 0:
            print("File decrypted successfully")
            return status
        else:
            print("Couldn't create decrypted file")
            return status
    elif confirm_overwrite(decrypted_file_path):
        status = write_file(decrypted_file_path, decrypted_data)
        if status == 0:
            print("File decrypted successfully")
            return status
        else:
            print("Couldn't create decrypted file")
            return status
    else:
        print("Aborting...")
        return 1

def generate_key(args):
    """
    Generate a new Fernet key and write it to disk.

    Respects overwrite confirmation unless --force is used.
    """

    key_path = os.path.abspath(args.path)
    key = Fernet.generate_key()

    if not os.path.isfile(key_path) or args.force:
        status = write_file(key_path, key)
        if status == 0:
            print("Key file created successfully")
            return status
        else:
            print("Couldn't create key file")
            return status
    elif confirm_overwrite(key_path):
        status = write_file(key_path, key)
        if status == 0:
            print("Key file created successfully")
            return status
        else:
            print("Couldn't create key file")
            return status
    else:
        print("Aborting...")
        return 1

def main():
    """
    Parse command-line arguments and execute the selected command.
    """

    parser = argparse.ArgumentParser(
        prog="Scrypter", 
        description=(
            "Scrypter: Encrypt, decrypt files and manage Fernet keys "
            "easily from the command line."
        )
    )

    subparsers = parser.add_subparsers(
            dest="command", 
            required=True
    )

    encrypt_parser = subparsers.add_parser(
            "encrypt", 
            description=(
                "Encrypt a file using a Fernet key. "
                "The output will be saved with a '.enc' extension."
            ), 
            help="Encrypt a file using a key"
    )

    encrypt_parser.add_argument(
            "file", 
            help="Path to the file you want to encrypt"
    )

    encrypt_parser.add_argument("key", help="Path to the key file used for encryption")
    encrypt_parser.add_argument(
        "-f", "--force", action="store_true", 
        help="Overwrite existing encrypted file without prompting"
    )
    encrypt_parser.set_defaults(func=encrypt_file)

    decrypt_parser = subparsers.add_parser(
        "decrypt", 
        description=(
            "Decrypt an encrypted file using a Fernet key. "
            "The '.enc' suffix will be removed from the output file."
        ), 
        help="Decrypt a file using a key"
    )

    decrypt_parser.add_argument(
            "file", 
            help="Path to the encrypted file"
    )

    decrypt_parser.add_argument(
            "key", 
            help="Path to the key file used for decryption"
    )

    decrypt_parser.add_argument(
        "-f", "--force", 
        action="store_true", 
        help="Overwrite existing decrypted file without prompting"
    )

    decrypt_parser.add_argument(
            "-p", "--print", 
            action=argparse.BooleanOptionalAction, 
            default=False, 
            help="Prints the decrypted file contents to the terminal"
    )
    decrypt_parser.set_defaults(func=decrypt_file)

    key_parser = subparsers.add_parser(
        "gen_key", 
        description=(
            "Generate a new Fernet key and save it to a file. "
            "Use --force to overwrite existing key files."
        ), 
        help="Generate a new Fernet key"
    )

    key_parser.add_argument(
            "path", 
            help="Path to save the generated key file"
    )

    key_parser.add_argument(
        "-f", "--force", 
        action="store_true", 
        help="Overwrite existing key file without prompting"
    )
    key_parser.set_defaults(func=generate_key)

    args = parser.parse_args()
    return args.func(args)

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("Operation Cancelled")
        sys.exit(1)
