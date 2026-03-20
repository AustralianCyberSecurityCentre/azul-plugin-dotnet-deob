# Azul Plugin Dotnet Deob

Configurable plugin for using multiple dotnet Deobfuscators on a single file.

## Development Installation

Installation requires the user to install dotnet the mono.

### installing dotnet locally (ubuntu22+)

sudo apt install dotnet6
sudo apt install dotnet7
sudo apt install mono-complete

### Installing mono (can be different for different linux distros)

Refer to https://www.mono-project.com/download/stable/#download-lin and select the appropriate linux distro (install mono-complete).

### Installing python package

From the root directory of this project:

```bash
pip install -e .
```

## Usage

Usage on local files:

```
$ azul-plugin-dotnet-deob malware.file
... example output goes here ...
```

Check `azul-plugin-dotnet-deob --help` for advanced usage.

## Dotnet commands for building repos

The dotnet binaries in this package were precompiled on linux with mono or dotnet and have bee placed in the folder
auzl_plugin_dotnet_deob/deob/bin. (debug builds currently)

To build these packages the source repos were loaded in windows and compiled and upgraded to the newest version
of dotnet that was practical (.netframework4.8 or .net 6).

If .netframework was the best option mono was used on linux.

## Example Unscrambler and mono builds

Unscrambler commands to build in dotnet:

```bash
git clone https://github.com/AustralianCyberSecurityCentre/Unscrambler
# This builds just the dlls and can be run using dotnet binary and is much smaller and preferred
dotnet build Unscrambler.sln  --configuration Release --framework net8.0
# Take the contents of the Release directory.
```

https://github.com/AustralianCyberSecurityCentre/Unscrambler
```dotnet build Unscrambler.sln  --configuration Release --framework net8.0```
(Note code had to be migrated to dotnet from dotnet framework first which is why it's a fork)


Mono built repos example:
https://github.com/NotPrab/AgileStringDecryptor.git
`msbuild -restore AgileStringDecryptor.sln`

https://github.com/wwh1004/ConfuserExTools.git
`msbuild -restore ConfuserExTools.sln`

## Dependency management

Dependencies are managed in the pyproject.toml and debian.txt file.

Version pinning is achieved using the `uv.lock` file.
Because the `uv.lock` file is configured to use a private UV registry, external developers using UV will need to delete the existing `uv.lock` file and update the project configuration to point to the publicly available PyPI registry instead.

To add new dependencies it's recommended to use uv with the command `uv add <new-package>`
    or for a dev package `uv add --dev <new-dev-package>`

The tool used for linting and managing styling is `ruff` and it is configured via `pyproject.toml`

The debian.txt file manages the debian dependencies that need to be installed on development systems and docker images.

Sometimes the debian.txt file is insufficient and in this case the Dockerfile may need to be modified directly to
install complex dependencies.
