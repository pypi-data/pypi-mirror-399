{
  description = "Common ETL utils";

  inputs = {
    observes_flake_builder = {
      url =
        "git+ssh://git@gitlab.com/fluidattacks/universe?shallow=1&rev=0951d604631451c9b5f73256089d1690c11350a8&dir=observes/common/std_flake_2";
    };
  };

  outputs = { self, ... }@inputs:
    let
      build_args = { system, python_version, nixpkgs, builders, scripts }:
        import ./build {
          inherit nixpkgs builders scripts;
          src = import ./build/filter.nix nixpkgs.nix-filter self;
        };
    in { packages = inputs.observes_flake_builder.outputs.build build_args; };
}
