# changelog

## 1.4.2

 - Launch bash in interactive mode so that `~/.bashrc` is parsed
 - Improved tests to ignore `screen` in addition to `rbash`

## 1.4.1

 - Improved handling of built in types names in TypeError exceptions on ST2

## 1.4.0

 - Added env_encode(), env_decode(), path_encode() and path_decode() functions

## 1.3.1

 - Fixed a bug on OS X and Linux where changes to the return env dict would be
   persisted upon subsequent calls

## 1.3.0

 - Added the functions `get_user_login_shell()` and `get_user()`

## 1.2.1

 - Fixed environmental variable capitalization on Windows with Sublime Text 2
   to be all uppercase
 - Fixed a bug affecting OS X and Linux where environmental variables were not
   being split properly

## 1.2.0

 - `get_path()` now returns a 2-element tuple with the shell first

## 1.1.0

 - Added `for_process` param to `get_env()`

## 1.0.0

 - Initial release
