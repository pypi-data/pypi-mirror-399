from pathlib import Path
import subprocess
import platform

import uv as external_uv

from .asset.manager import AssetManager


class Workspace:
    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._name = self.path.name

        bin = "bin"
        if platform.system() != "Linux":
            bin = "Scripts"
        self._venv_name = "inputs"
        self._venv_bin_path = self.path / self._venv_name / bin
        self._external_packages_path = self.path / "external_packages"
        self._output_path = self.path / "outputs"
        self._build_path = self._path / "build"

        self._asset_manager = AssetManager(
            hatch_path=str(self._venv_bin_path / "hatch"),
            uv_path=str(self._venv_bin_path / "uv"),
            python_path=str(self._venv_bin_path / "python"),
        )

        # TODO: make these configurable?
        self._default_repo_name = "review"
        self._blessed_repo_name = "blessed"

        self._default_repos: dict[str, str] = {}

    @property
    def path(self) -> Path:
        """The path of the Workspace, including its name."""
        return self._path

    @property
    def name(self) -> str:
        """The name of the Workspace, deducted from its path."""
        return self._name

    @property
    def exists(self) -> bool:
        return self._venv_bin_path.exists()

    @property
    def asset_manager(self) -> AssetManager:
        return self._asset_manager

    def add_repo(
        self,
        repo_name: str,
        repo_path: str,
        make_blessed: bool = False,
        make_default: bool = True,
    ):
        """
        Add a repo to the workspace.
        All asset created after this will be configured with this repo.
        """
        # TODO: store these in a confif file in the workspace?
        repo_abs_path = (self.path / repo_path).resolve()
        self._default_repos[repo_name] = str(repo_abs_path)
        repo_abs_path.mkdir(parents=True, exist_ok=True)
        print(f"Added repo {repo_name}: {repo_abs_path}")
        if make_blessed:
            self._blessed_repo_name = repo_name
        if make_default:
            self._default_repo_name = repo_name

    def ensure_exists(self, force_build: bool = False):
        if not force_build and self.exists:
            return
        self._path.mkdir(parents=True, exist_ok=True)
        self._external_packages_path.mkdir(parents=True, exist_ok=True)
        self._output_path.mkdir(parents=True, exist_ok=True)
        self._build_path.mkdir(parents=True, exist_ok=True)

        self._recreate_venv()

    def _recreate_venv(self):
        # Create the venv:
        venv_path = self.path / self._venv_name
        uv = external_uv.find_uv_bin()
        cmd = [
            uv,
            "venv",
            "--allow-existing",
            "--prompt",
            f"WS: {self.name}",
            str(venv_path),
        ]
        print(cmd)
        subprocess.call(cmd)

        # Seed with our build system dependencies
        # (Installing assets do not have access to pypi, for security reasons.)
        dependencies = [
            "uv",
            "hatch",
            "hatchling",
            "editables",
        ]
        self.install_external_packages(*dependencies)

        # Install all needed/allowed dependencies:
        # (Installing assets do not have access to pypi, for security reasons.)
        allowlist = []
        self.add_extenal_packages(*allowlist)

    def install_external_packages(self, *requirements):
        """
        Install the given requirements in the workspace venv
        so that they are available if an asset has them as
        dependency.
        """
        if not requirements:
            return
        uv = external_uv.find_uv_bin()
        python = self._venv_bin_path / "python"
        cmd = [
            uv,
            "pip",
            "install",
            "--python",
            python,
            *requirements,
        ]
        print(cmd)
        subprocess.call(cmd)

    def add_extenal_packages(self, *requirements):
        """
        Install the given requirement in the external_packages
        folder. This folder is always use as --find-links so
        this will make theses pacakages available if an asset
        has them as dependency.
        """
        if not requirements:
            return
        uv = external_uv.find_uv_bin()
        cmd = [
            uv,
            "pip",
            "install",
            "--target",
            self._external_packages_path,
            *requirements,
        ]
        print(cmd)
        subprocess.call(cmd)

    def create_asset(
        self, asset_name: str, default_repo: str | None = None, **extra_repos: str
    ):
        """
        Create an output asset in this workspace.
        """
        default_repo = default_repo or self._default_repo_name
        extra_repos.update(self._default_repos)
        self.asset_manager.create_asset(
            self._output_path,
            asset_name,
            default_repo=default_repo,
            asset_data=None,
            version=None,
            **extra_repos,
        )
        self._install_editable(asset_name)

    def _install_editable(self, asset_name: str):
        self.asset_manager.install_editable(
            self._output_path,
            asset_name,
            str(self._external_packages_path),
            self._default_repos[self._blessed_repo_name],
            self._default_repos[self._default_repo_name],
        )

    def tag_asset(self, asset_name: str, *tags: str):
        self.asset_manager.add_tags(self._output_path, asset_name, set(tags))

    def add_inputs(self, asset_name: str, *input_requirements: str):
        """
        Make this asset dependent of the input_requirements.
        Each input_requirement can be like:
            - asset-name
            - asset-name==1.2.3
            - asset-anme>=2.3.4
            - asset-name>=3.4.5<4.0
            etc...
        """
        self.asset_manager.add_inputs(
            self._output_path, asset_name, *input_requirements
        )
        self._install_editable(asset_name)

    def bump_asset(self, asset_name: str, bump: str = "minor"):
        """
        Bumpt the part of the version specified with bump, like:"
            major
            minor
            micro / patch / fix
            a / alpha
            b / alpha
            c / rc / pre / preview
            r / rev / post
            dev

        or a combination like:
            minor,rc
            patch,a
            major,alpha,dev

        Defaults is to bump minor."
        """
        self.asset_manager.bump_asset(self._output_path, asset_name, bump=bump)
        self._install_editable(asset_name)

    def build_asset(self, asset_name: str, bump: str = "minor"):
        self.asset_manager.bump_asset(self._output_path, asset_name, bump=bump)
        self.asset_manager.build_asset(self._output_path, asset_name, self._build_path)

    def publish_asset(self, asset_name: str, repo_name: str | None = None):
        options = {}
        if repo_name is not None:
            options["publish_to"] = repo_name
        self.asset_manager.publish_asset(
            self._output_path,
            asset_name,
            self._build_path,
            **options,
        )

    def install_asset(
        self,
        repo_name: str,
        requirement,
    ):
        try:
            repo_path = self._default_repos[repo_name]
        except KeyError:
            raise ValueError(
                f"The repo {repo_name!r} in not defined "
                f"(got: {sorted(list(self._default_repos.keys()))}"
            )
        self.asset_manager.install(
            repo_path, str(self._external_packages_path), requirement
        )

    def has_editable_asset(self, asset_name: str):
        return (self._output_path / asset_name).exists()

    def turn_asset_editable(self, asset_name: str, force: bool = False):
        """
        Turn an input asset into a output asset.
        The asset must already be installed in the inputs
        """
        if self.has_editable_asset(asset_name):
            if not force:
                raise ValueError(
                    f"The asset {asset_name} is already an editable in workspace {self.path}."
                )

        uv = self._venv_bin_path / "uv"
        python = self._venv_bin_path / "python"
        cmd = [
            str(uv),
            "run",
            "--python",
            str(python),
            "--directory",
            str(self._venv_bin_path),
            "python",
            "-c",
            f"import {asset_name} as package; package.asset.create_editable(workspace_path='{self.path}', force={force})",
        ]
        # print(cmd)
        err_code = subprocess.call(cmd)
        if err_code:
            print(f"Oops, return code is error: {err_code}.")
        else:
            self.asset_manager.bump_asset(self._output_path, asset_name, bump="micro")
            self._install_editable(asset_name)
