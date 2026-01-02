# Encryption CLI

Encryption CLI is a command-line tool for encrypting and decrypting files in a directory.

## ⚠️ WARNING

This tool modifies files **in place**.

If used incorrectly, it **may permanently destroy your files**.  
If you lose the encryption key, **data recovery is impossible**.

Use with caution.

The author is **not responsible** for any data loss or damage caused by using this tool.


## Installation

```bash
pip install encryption_cli
```

## Usage

To run this tool, execute:

```bash
encryption_cli
```

You need a Fernet key (your encryption key).

Don’t worry — this tool can generate one for you.