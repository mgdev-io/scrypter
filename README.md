# Scrypter

A simple command-line tool to encrypt and decrypt files using [Fernet](https://cryptography.io/en/latest/fernet/) symmetric encryption.

## Requirements

- Python 3.10+
- `cryptography` library

Install the dependency with:

```bash
pip install cryptography
```

## Usage

```bash
python scrypter.py <command> [options]
```

### Commands

---

#### `gen_key` — Generate a new Fernet key

```bash
python scrypter.py gen_key <path> [-f]
```

| Argument | Description |
|----------|-------------|
| `path` | Path where the key file will be saved |
| `-f`, `--force` | Overwrite existing key file without prompting |

**Example:**
```bash
python scrypter.py gen_key mykey.key
```

---

#### `encrypt` — Encrypt a file

```bash
python scrypter.py encrypt <file> <key> [-f]
```

| Argument | Description |
|----------|-------------|
| `file` | Path to the file you want to encrypt |
| `key` | Path to the key file |
| `-f`, `--force` | Overwrite existing encrypted file without prompting |

The encrypted output is saved as `<original_filename>.enc`.

**Example:**
```bash
python scrypter.py encrypt secret.txt mykey.key
# Output: secret.txt.enc
```

---

#### `decrypt` — Decrypt a file

```bash
python scrypter.py decrypt <file> <key> [-f]
```

| Argument | Description |
|----------|-------------|
| `file` | Path to the `.enc` file you want to decrypt |
| `key` | Path to the key file used for encryption |
| `-f`, `--force` | Overwrite existing decrypted file without prompting |

The `.enc` suffix is removed from the output filename.

**Example:**
```bash
python scrypter.py decrypt secret.txt.enc mykey.key
# Output: secret.txt
```

---

## Typical Workflow

```bash
# 1. Generate a key
python scrypter.py gen_key mykey.key

# 2. Encrypt a file
python scrypter.py encrypt document.pdf mykey.key

# 3. Decrypt it later
python scrypter.py decrypt document.pdf.enc mykey.key
```

> ⚠️ **Keep your key file safe.** Without it, encrypted files cannot be recovered.
