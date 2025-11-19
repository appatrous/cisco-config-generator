#!/usr/bin/env python3
"""
Generate secure random secrets for configuration.

This script generates cryptographically secure random secrets that can
be used for SECRET_KEY, JWT_SECRET_KEY, and other sensitive configuration
values.

Usage:
    python utils/generate_secrets.py
    python utils/generate_secrets.py --length 64
    python utils/generate_secrets.py --count 3
"""
import secrets
import argparse


def generate_secret(length: int = 32) -> str:
    """
    Generate a cryptographically secure random secret.

    Args:
        length: Length of the secret in bytes (default: 32)

    Returns:
        URL-safe base64-encoded random string
    """
    return secrets.token_urlsafe(length)


def generate_hex_secret(length: int = 32) -> str:
    """
    Generate a cryptographically secure random secret in hex format.

    Args:
        length: Length of the secret in bytes (default: 32)

    Returns:
        Hexadecimal random string
    """
    return secrets.token_hex(length)


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Generate secure random secrets for configuration'
    )
    parser.add_argument(
        '--length',
        type=int,
        default=32,
        help='Length of secret in bytes (default: 32)'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=1,
        help='Number of secrets to generate (default: 1)'
    )
    parser.add_argument(
        '--hex',
        action='store_true',
        help='Generate secrets in hexadecimal format'
    )
    parser.add_argument(
        '--env',
        action='store_true',
        help='Output in .env file format'
    )

    args = parser.parse_args()

    if args.env:
        # Generate all secrets needed for .env file
        print("# Flask Configuration")
        print(f"SECRET_KEY={generate_secret(32)}")
        print()
        print("# JWT Configuration")
        print(f"JWT_SECRET_KEY={generate_secret(32)}")
        print()
        print("# Database Configuration")
        print(f"DATABASE_PASSWORD={generate_secret(24)}")
        print()
        print("# Admin User")
        print(f"ADMIN_PASSWORD={generate_secret(16)}")
        print()
        print("# Optional: Redis Password")
        print(f"REDIS_PASSWORD={generate_secret(24)}")
    else:
        # Generate individual secrets
        generator = generate_hex_secret if args.hex else generate_secret

        if args.count == 1:
            print(generator(args.length))
        else:
            for i in range(args.count):
                print(f"Secret {i+1}: {generator(args.length)}")


if __name__ == '__main__':
    main()
