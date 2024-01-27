{ lib
, python-wasi
, mkShell
, stdenv
, wasmtime
, writeShellScriptBin
}:

{ pyPackages ? []
}:

let

  pyDeps = lib.concatMap (pkg: lib.remove pkg.pythonModule pkg.requiredPythonModules) pyPackages;
  allPackages = lib.unique (pyPackages ++ pyDeps);

  pythonPath = lib.concatMapStringsSep ":" (pkg: "${pkg}/lib/python3.11/site-packages") allPackages;

  python = writeShellScriptBin "python-wasi" ''
   exec ${wasmtime}/bin/wasmtime run ${python-wasi}/python.wasm \
     --env PYTHONHOME=${python-wasi} \
     --env PYTHONPATH='.:${pythonPath}' \
     --dir ${python-wasi} \
     ${lib.concatMapStringsSep "\\\n  " (pkg: "--dir '${pkg}/lib/python3.11/site-packages' ") allPackages} \
     --dir . \
     -- "$@"
  '';

in mkShell {
  name = "python-wasi";
  packages = [ python ];
}
