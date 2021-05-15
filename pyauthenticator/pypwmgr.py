"""
Password manager based on the pyauthenticator
"""
import argparse
from pyauthenticator.share import (
    list_services,
    load_config,
    check_if_key_in_config,
    write_config,
)


# default configuration file
config_file = "~/.pypwmgr"


def save_account(
    key, config_dict, username, password, config_file_to_write=config_file
):
    """
    Write qrcode to file to scan it with a mobile application

    Args:
        key (str): lower case name of the service
        config_dict (dict): configuration dictionary
        username (str): username for the service
        password (str): password for the service
        config_file_to_write (str): path to config file
    """
    config_dict[key] = {"username": username, "password": password}
    write_config(config_dict=config_dict, config_file_to_write=config_file_to_write)


def get_username_and_password(key, config_dict):
    """
    Return username and password from config file

    Args:
        key (str): lower case name of the service
        config_dict (dict): configuration dictionary

    Returns:
        dict: dictionary with username and password
    """
    check_if_key_in_config(key=key, config_dict=config_dict)
    return config_dict[key]


def main():
    """
    Main function primarly used for the command line interface
    """
    parser = argparse.ArgumentParser(prog="pypwmgr")
    config_dict = load_config(config_file_to_load=config_file)
    parser.add_argument(
        "service",
        help="Service to generate optauth code for. Available services are: "
        + str(list_services(config_dict=config_dict)),
    )
    parser.add_argument(
        "-u",
        "--username",
        help="Add service by providing the username and password.",
    )
    parser.add_argument(
        "-p",
        "--password",
        help="Add service by providing the username and password.",
    )
    args = parser.parse_args()
    if args.username and args.password:
        save_account(
            key=args.service,
            config_dict=config_dict,
            username=args.username,
            password=args.password,
            config_file_to_write=config_file,
        )
        print(args.service, "added.")
    elif args.username or args.password:
        print(
            "Add service by providing the username (--username) and password (--password)."
        )
    else:
        print(get_username_and_password(key=args.service, config_dict=config_dict))


if __name__ == "__main__":
    main()
