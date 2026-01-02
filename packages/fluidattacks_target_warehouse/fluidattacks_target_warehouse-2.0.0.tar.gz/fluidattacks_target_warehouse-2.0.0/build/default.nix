{ nixpkgs, builders, scripts, src, }:
let
  build_bin = bundle:
    nixpkgs.writeShellApplication {
      name = "target-warehouse";
      runtimeInputs = [ bundle.env.runtime nixpkgs.sops ];
      text = ''
        target-warehouse "''${@}"
      '';
    };
in {
  inherit src;
  root_path = "observes/singer/target-warehouse";
  module_name = "fluidattacks_target_warehouse";
  pypi_token_var = "TARGET_WAREHOUSE_TOKEN";
  override = bundle: bundle // { bin = build_bin bundle; };
}

