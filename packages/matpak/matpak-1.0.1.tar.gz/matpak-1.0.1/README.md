# MatPak
Matrix Utilization Python Package.

![MatPak](https://github.com/user-attachments/assets/3fb0d588-3070-4aec-a418-73d369474562)


## Files structure
`src/`: source codes of library lives in here.

`src/matpak/`: **MatPak** package files stored in this directory.

`tests/`: **MatPak** package unit tests are located here.

## Usage
First of all, **MatPak** should be installed via your python package manager (e.g, pip):
```bash
pip install matpak
```

Then by importing `matpak` package in your application files, you can use **MatPak**'s public API functions:

```python
import matpak

def main():
    # import custom matrix from file
    foo_mat = matpak.imp_mat_file("./foo_mat.txt")
    
if __name__ == "__main__":
    main()
```

## Contribution
Feel free to fork, modify and open a pull request in this repository.
Thanks for your contribution.