{ pkgs, ... }:

{

	difftastic.enable = true;

	languages.python = {
		enable = true;
		venv = {
			enable = true;
		};
	};

	pre-commit.hooks = {
			black.enable = true;
	};
}
