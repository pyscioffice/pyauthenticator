"""
Generate two factor authentication codes on the command line
"""
import argparse
import base64
import json
import os
from otpauth import OtpAuth
import qrcode


config_file = "~/.pyauthenticator"


def load_config():
    """
    Load configuration file

    Returns:
        dict: Dictionary with service names as keys and the otpauth url as values
    """
    abs_config_path = os.path.abspath(
        os.path.expanduser(
            config_file
        )
    )
    if os.path.exists(abs_config_path):
        with open(abs_config_path, "r") as f:
            return json.load(f)
    else:
        return {}


def get_otpauth_dict(otpauth_str):
    """
    Parse otpauth url

    Args:
        otpauth_str: otpauth url as string

    Returns:
        dict: Dictionary with the parameters of the otpauth url as key-value pairs
    """
    return {
        kv[0]: kv[1]
        for kv in [
            otpvar.split("=")
            for otpvar in otpauth_str.replace("?", "&").split("&")[1:]
        ]
    }


def add_padding(main_str, padding_str, padding_length, inverse_padding=False):
    """
    Add padding to a string either in the beginning or at the end

    Args:
        main_str (str): string to add padding to
        padding_str (str): padding character as string
        padding_length (int): the length of the final string should be a multiple of the padding length
        inverse_padding (bool): add padding in the beginning rather than the end

    Returns:
        str: resulting string with padding
    """
    missing_padding = len(main_str) % padding_length
    if missing_padding:
        if inverse_padding:
            main_str = padding_str * (padding_length - missing_padding) + main_str
        else:
            main_str += padding_str * (padding_length - missing_padding)
    return main_str


def init_auth(otpauth_secret):
    """
    Initialize the authenication class

    Args:
        otpauth_secret (str): authentication secret

    Returns:
        optauth.OptAuth: authentication class object instance
    """
    return OtpAuth(
        secret=base64.b32decode(
            add_padding(
                main_str=otpauth_secret,
                padding_str='=',
                padding_length=8,
                inverse_padding=False
            ),
            True
        )
    )


def check_if_key_in_config(key, config_dict):
    """
    Check if a given key is included in a dictionary, raise an ValueError if it is not.

    Args:
        key (str): key as string
        config_dict (dict): configuration dictionary
    """
    if key not in config_dict.keys():
        raise ValueError()


def get_two_factor_code(key, config_dict):
    """
    Generate the two factor authentication code

    Args:
        key (str): lower case name of the service
        config_dict (dict): configuration dictionary

    Returns:
        str: two factor authentication code as string
    """
    check_if_key_in_config(
        key=key,
        config_dict=config_dict
    )
    decode_dict_internal = get_otpauth_dict(
        otpauth_str=config_dict[key]
    )
    auth = init_auth(
        otpauth_secret=decode_dict_internal["secret"]
    )
    if "period" in decode_dict_internal.keys():
        auth_code = auth.totp(
            period=int(
                decode_dict_internal['period']
            )
        )
    else:
        auth_code = auth.totp()
    return add_padding(
        main_str=str(auth_code),
        padding_str="0",
        padding_length=6,
        inverse_padding=True
    )


def generate_qrcode(key, config_dict, file_name=None):
    """
    Write qrcode to file to scan it with a mobile application

    Args:
        key (str): lower case name of the service
        config_dict (dict): configuration dictionary
        file_name (str/ None): default file name <service.png>
    """
    if file_name is None:
        file_name = key + ".png"
    check_if_key_in_config(
        key=key,
        config_dict=config_dict
    )
    qrcode.make(config_dict[key]).save(
        file_name,
        "PNG"
    )


def list_services(config_dict):
    """
    List available services

    Args:
        config_dict (dict): configuration dictionary

    Returns:
        list: list of available services
    """
    return list(config_dict.keys())


def main():
    """
    Main function primarly used for the command line interface
    """
    parser = argparse.ArgumentParser(prog="pyauthenticator")
    parser.add_argument(
        "service",
        help="Service to generate optauth code for. Available services are: "
             + str(list_services(config_dict=load_config()))
    )
    parser.add_argument(
        "--qrcode",
        help="Generate qrcode as <service.png> file."
    )
    args = parser.parse_args()
    if args.qrcode:
        generate_qrcode(key=args.service, config_dict=load_config())
    else:
        print(
            get_two_factor_code(
                key=args.service,
                config_dict=load_config()
            )
        )


if __name__ == "__main__":
    main()