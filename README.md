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

## Example dotnet and mono builds

De4dot commands to build in dotnet:

```bash
git clone https://github.com/de4dot/de4dot.git
cd de4dot
# This builds a full binary and is large
dotnet publish de4dot.netcore.sln --runtime=linux-x64 --framework=netcoreapp3.1 -c Release
# This builds just the dlls and can be run using dotnet binary and is much smaller and preferred
dotnet build de4dot.netcore.sln -c release
# Take the contents of the Release directory.
```

You can then run de4dot with the command:
./Release/netcoreapp3.1/linux-x64/de4dot

Mono built repos example:
https://github.com/NotPrab/AgileStringDecryptor.git
`msbuild -restore AgileStringDecryptor.sln`

https://github.com/wwh1004/ConfuserExTools.git
`msbuild -restore ConfuserExTools.sln`
