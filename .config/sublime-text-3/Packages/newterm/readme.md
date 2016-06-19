# newterm

This is a Package Control dependency that allows Sublime Text packages to open
a terminal to a specific folder with the option to override environmental
variables.

## Version

1.0.0 - [changelog](changelog.md)

## API

This dependency exposes one function for package developers to utilize:

 - `newterm.launch_terminal()`

`launch_terminal()` accepts one required position parameter:

 1. A unicode string of the directory to open the terminal to

It also accepts five keyword arg parameters:
 
 - `env`
 - `terminal`
 - `args`
 - `width`
 - `use_tabs`

`env` accepts a dictionary of custom environmental variable values to set in
the terminal.

`terminal` accepts a unicode string of the terminal to open. All platforms
allow a unicode string of the path to the terminal, or the name of an executable
in the `PATH`. On OS X, two special values are allowed: `Termina.app` and
`iTerm.app`. On Windows, two special values are allowed: `powershell.exe` and
`cmd.exe`. If `None` is specified, `launch_terminal()` will pick the OS default.

`args` accepts a list of unicode string of arguments to pass to the terminal.

On Windows, the `width` parameter is an integer that allows setting the width of
the terminal window when the terminal is `None`, `powershell.exe` or `cmd.exe`.

On OS X, the `use_tabs` parameter is a boolean that tells the terminal program
to open the directory in a new tab instead of a new window. Works when the
terminal is `None`, `Terminal.app` or `iTerm.app`.

## Usage

To have a package require `newterm`, add a file named `dependencies.json` into
the root folder of your Sublime Text package, and add the following:

```json
{
    "*": {
        "*": [
            "shellenv",
            "newterm"
        ]
    }
}
```

This indicates that for all operating systems (`*`), and all versions of
Sublime Text (nested `*`), require the `shellenv` and `newterm` dependencies.
You can also read the
[official documentation about dependencies](https://packagecontrol.io/docs/dependencies).
