{ nixpkgs, builders, scripts, src, }: {
  inherit src;
  root_path = "observes/sdk/timedoctor";
  module_name = "fluidattacks_timedoctor_sdk";
  pypi_token_var = "TIMEDOCTOR_SDK_TOKEN";
  override = b: b;
}
