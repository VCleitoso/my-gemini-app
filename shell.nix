{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = [
    pkgs.python311
    pkgs.python311Packages.pypdf2
  ];
}
