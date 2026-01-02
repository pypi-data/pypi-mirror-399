# ShellLite: The English-Like Programming Language
### By Shrey Naithani

**ShellLite** is a programming language designed to be as readable as plain English. It strips away the complex syntax of traditional languages and replaces it with natural, human-friendly commands.

Whether you are automating your desktop, building a website, or just learning to code, ShellLite makes it simple.

## Quick Start

### Installation
ShellLite is easiest to install globally on Windows.

1.  **Download & Install**:
    Run the `shl.exe` file. It will automatically set itself up in your system PATH.

2.  **Verify**:
    Open a new terminal and type:
    ```bash
    shl
    ```
    If you see the `>>>` prompt, you are ready to go!

### Your First Program
Create a file named `hello.shl`:

```javascript
say "Hello, World!"
name = ask "What is your name? "
say "Nice to meet you, " + name
```

Run it:
```bash
shl hello.shl
```


### Package Manager (New!)
You can install packages from GitHub using `shl get`:

```bash
shl get "shreyn/math-plus"
```

Then use it in your code:
```javascript
use "math-plus" as mp
```

---

## Documentation
We have a comprehensive guide to help you master ShellLite:

1.  [**Getting Started**](docs/01_Getting_Started.md) - Installation, VS Code setup, and running code.
2.  [**Language Basics**](docs/02_Language_Basics.md) - Variables, types, and basic input/output.
3.  [**Control Flow**](docs/03_Control_Flow.md) - Making decisions with `if`, `when`, and loops.
4.  [**Data Structures**](docs/04_Data_Structures.md) - Lists, dictionaries, and sets.
5.  [**Functions & OOP**](docs/05_Functions_and_OOP.md) - Reusable code and Object-Oriented Programming.
6.  [**Modules & Standard Lib**](docs/06_Modules_and_StdLib.md) - Math, Time, CSV, and more.
7.  [**System Mastery**](docs/07_System_Mastery.md) - File manipulation and desktop automation.
8.  [**Web Development**](docs/08_Web_Development.md) - Building websites with English syntax.

---
*Made by Shrey Naithani*
