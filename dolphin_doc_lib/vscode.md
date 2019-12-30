# Extensions:
*  Code Runner
*  Mypy
*  Python
*  Visual Studio IntelliCode

# Formatter:
*  yapf

# Set Python Path
*  Add dolphin-doc to PYTHONPATH

# Disable Mypy Import Error
1. Create a mypy.ini file, which whitelists all the necessary modules. For example, whitelist for bs4:

    ```  
   [mypy-bs4.*]
   ignore_missing_imports = True
   ```
1. In vscode settings, search for mypy, and set config file path to be the absolute path of mypy.ini file just added.