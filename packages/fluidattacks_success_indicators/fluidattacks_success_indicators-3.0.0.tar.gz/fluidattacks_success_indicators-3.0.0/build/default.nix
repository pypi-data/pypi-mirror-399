{ nixpkgs, builders, scripts, src, }:
let
  build_bin = bundle:
    nixpkgs.writeShellApplication {
      name = "success-indicators";
      runtimeInputs = [ bundle.env.runtime nixpkgs.sops ];
      text = ''
        success-indicators "''${@}"
      '';
    };
in {
  inherit src;
  root_path = "observes/job/success-indicators";
  module_name = "fluidattacks_success_indicators";
  pypi_token_var = "SUCCESS_INDICATORS_TOKEN";
  override = bundle: bundle // { bin = build_bin bundle; };
}
