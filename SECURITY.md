# Security Policy

## Supported versions

Only the latest version on `main` receives security fixes.

## Reporting a vulnerability

Please do **not** report security issues as public issues or pull requests.

Use GitHub's private reporting instead: **Security → Report a vulnerability** in this repository.
Describe the problem, how to reproduce it and the impact you see.

You will get an acknowledgement within a week. Once a fix is available it is published together with a
security advisory, and you are credited if you wish.

## Scope

adb-tray runs `adb` and `scrcpy` with your user privileges and connects to the addresses you enter.
Relevant issues include, for example:

- command injection through device names, serial numbers or addresses
- files being written outside `~/.config/adb-tray/` or the Pictures folder
- the install scripts doing anything other than what is documented

The security of the `adb` protocol itself and of `scrcpy` is handled by those projects.
