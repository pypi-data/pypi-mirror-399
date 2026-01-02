import argparse
import random
import string

# Class to create a custom help message (i.e. The output of >> create_password -h)
class CustomHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        pass
    def add_arguments(self, actions):
        pass

def omit(string, omit_chars=None):
    chars = ''.join(c for c in string if c not in omit_chars)
    string = chars
    return string

def get_available_chars(omit_chars=None, just_letters_and_numbers=False):

    if just_letters_and_numbers:
        available_chars = ''.join(dict.fromkeys(string.ascii_letters + string.digits))
    else:
        available_chars = ''.join(dict.fromkeys(string.ascii_letters + string.digits + string.punctuation))

    if omit_chars:
        available_chars = omit(available_chars, omit_chars)

    return available_chars

def shuffle_string(string):

    char_list = list(string)
    random.shuffle(char_list)
    shuffled_string = ''.join(char_list)

    return shuffled_string

def generate_password(length, omit_chars=None, just_letters_and_numbers=False, add_characters=None):

    available_chars = get_available_chars(omit_chars, just_letters_and_numbers)
    
    if not available_chars:
        raise ValueError("No characters available after omitting specified characters.")
    
    password = ''
    i = 0

    if add_characters:
        add_characters = shuffle_string(add_characters)
        i = round(length * 0.5)
        password = add_characters[:i]
        password = omit(password, omit_chars)
        i = len(password)

    for _ in range(length - i):

        if len(available_chars) < 1:
            
            available_chars = get_available_chars(omit_chars, just_letters_and_numbers)
        
        random_char = random.choice(available_chars)
        password += random_char

        available_chars = available_chars.replace(random_char, '')

    password = shuffle_string(password)
    
    return password

def main():
    passwords_str_example = "\033[1m\033[32m" + "\n".join(["k=(qs!yEO0)£/%$", 
                                                   "8()!/$x=£6c%HCI", 
                                                   "aQ£(!kl%=/)Si8$", 
                                                   "£/)W!=(4Atm$o%M"]) + "\033[0m"
    
    ArgumentParser_desc = (
    " \nGenerates a random password.\n"
    "Here's an example command to print 4 random 15-character long passwords omitting these characters: *+^ and using only letters and numbers and adding these characters: !\"£$%/()=: to the pool of characters to choose from: \n\n"
    ">> create_password -n 4 -l 15 -o *+d -j -a !\"£$%/()=\n\n"
    f"This command will return something like: \n\n{passwords_str_example}\n\n"
    "The default command is:\n"
    ">> create_password -n 1 -l 16 (prints 1 password of length 16)\n\n "
    "The arguments are:\n "
    "-l (or --password_length): sets the password length\n "
    "-o (or --characters_to_omit): sets the characters to omit (cannot be used with the -i argument)\n "
    "-n (or --number_of_passwords): sets how many passwords to return\n "
    "-j (or --just_letters_and_numbers): returns passwords using only letters and numbers\n "
    "-a (or --add_characters): adds characters to the pool of characters to choose from to create the passwords\n\n "
    "See the repository for further info: https://github.com/GTBSinclair/RandomPasswordCreator\n "
)

    parser = argparse.ArgumentParser(
        description=ArgumentParser_desc,
        formatter_class=CustomHelpFormatter,
        add_help=True
    )

    group = parser.add_mutually_exclusive_group()

    parser.add_argument(
        "-l",
        "--password_length",
        type=int,
        nargs="?",
        default=16,
        help="Length of the password (default: 16)"
    )
    group.add_argument(
        "-o",
        "--characters_to_omit",
        type=str,
        nargs="?",
        default="",
        help="Characters to exclude from the password (default: none)"
    )
    parser.add_argument(
        "-n",
        "--number_of_passwords",
        type=int,
        nargs="?",
        default=1,
        help="Number of passwords to show (default: 1)"
    )
    parser.add_argument(
        "-j",
        "--just_letters_and_numbers",
        action="store_true",
        default=False,
        help="Create passwords with just letters and numbers (default: False)"
    )
    parser.add_argument(
        "-a",
        "--add_characters",
        type=str,
        nargs="?",
        default="",
        help="Add characters to include in the passwords (default: none)"
    )
    
    args = parser.parse_args()
    
    try:
        passwords = [generate_password(args.password_length, args.characters_to_omit, args.just_letters_and_numbers, args.add_characters) for _ in range(args.number_of_passwords)]

        print(f"\n")

        for password in passwords:
            print(f"\033[1m\033[32m{password}\033[0m")

        print(f"\n")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# if __name__ == "__main__":
#     main()