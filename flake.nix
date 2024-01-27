{
  description = "pygls: The Generic Language Server Framework";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }:

    utils.lib.eachDefaultSystem(system:
      let
        pkgs = import nixpkgs { inherit system; };
        python-wasi = pkgs.callPackage ./nix/python-wasi.nix {};
        # TODO: Perhaps an overlay would allow callPackage to know what python-wasi is.
        mkPythonWASIShell = pkgs.callPackage ./nix/python.nix { python-wasi = python-wasi; };
      in {

        devShells.default = mkPythonWASIShell {
          pyPackages = with pkgs.python311Packages; [
            lsprotocol
          ];
        };
      }
    );
}
