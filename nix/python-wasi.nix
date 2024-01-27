{ fetchzip, stdenv }:

stdenv.mkDerivation {
  pname = "python-wasi";
  version = "3.11.4";

  src = fetchzip {
    url = "https://github.com/brettcannon/cpython-wasi-build/releases/download/v3.11.4/python-3.11.4-wasi_sdk-16.zip";
    stripRoot = false;
    sha256 = "sha256-AZGdgpRvHcu6FY/a7capldjDhTpkfhGkqYnm127nAN8=";
  };

  buildCommand = ''
   mkdir $out
   cp -r $src/* $out
  '';
}
