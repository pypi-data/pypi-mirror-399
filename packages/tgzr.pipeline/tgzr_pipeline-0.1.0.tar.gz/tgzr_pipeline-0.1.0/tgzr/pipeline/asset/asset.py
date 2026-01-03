from pathlib import Path
from functools import cached_property
import importlib

import rich
import pydantic
import toml


class AssetPublishRepo(pydantic.BaseModel):
    name: str
    path: str


class AssetPublishConfig(pydantic.BaseModel):
    publish_to: str = "review"
    repos: list[AssetPublishRepo] = []

    def to_pyproject(self):
        """Returns a dict suitable for the "tool.hatch.publish.tgzr-pipeline-asset" pyproject section."""
        return dict(
            publish_to=self.publish_to,
            repos=dict([(r.name, r.path) for r in self.repos]),
        )


class AssetPackageConfig(pydantic.BaseModel):
    inputs: list[str] = []
    publish: AssetPublishConfig


class InputPosition(pydantic.BaseModel):
    input_name: str
    x: float
    y: float


class AssetGraph(pydantic.BaseModel):
    positions: list[InputPosition] = []


class AssetData(pydantic.BaseModel):
    package: AssetPackageConfig
    tags: set[str] = set([])
    asset_type: str = "basic"
    entity: str | None = None
    graph: AssetGraph

    @classmethod
    def create_default(cls):
        return cls(
            package=AssetPackageConfig(
                publish=AssetPublishConfig(),
            ),
            graph=AssetGraph(),
        )

    @classmethod
    def from_toml(cls, toml_path: Path):
        asset_data = toml.load(toml_path)
        return cls(**asset_data)

    def write_toml(self, toml_path: Path):
        toml_path.write_text(toml.dumps(self.model_dump()))


class Asset:
    def __init__(self, init_file: Path | str):
        self._init_file = Path(init_file)
        # self._data_path = self._init_file / ".." / "DATA"
        self.name = self._init_file.parent.name
        self.asset_toml = (self._init_file / ".." / "asset.toml").resolve()

    def hello(self):
        print(f"Hello from asset {self.name} ({self.is_editable=})")
        rich.print(AssetData.from_toml(self.asset_toml))

    @cached_property
    def is_editable(self) -> bool:
        for parent in self._init_file.parents:
            if (parent / "pyproject.toml").exists():
                return True
        return False

    def get_version(self) -> str:
        version_module = importlib.import_module(self.name + ".__version__")
        return version_module.__version__

    def read_asset_data(self) -> AssetData:
        asset_data = AssetData.from_toml(self.asset_toml)
        return asset_data

    def write_asset_data(self, asset_data: AssetData):
        asset_data.write_toml(self.asset_toml)

    # @property
    # def data_dir(self) -> str:
    #     return str(self._data_path)

    # def pull_data(self):
    #     raise NotImplementedError()
    #     repo = dvc.repo.Repo(self.data_dir)
    #     repo.pull()

    def write_pyproject(self, pyproject_path: Path, hatch_hooks_location: str = ""):
        asset_data = self.read_asset_data()

        name = self.name
        pyproject_data = {
            "project": {
                "name": name,
                "dynamic": ["version"],
                "description": f"{name!r} - A TGZR Pipeline Asset created by tgzr.pipeline.asset.manager",
                "readme": "README.md",
                "dependencies": ["tgzr.pipeline"] + asset_data.package.inputs,
                "scripts": {name: f"{name}:main"},
            },
            "build-system": {
                "requires": [
                    "hatchling",
                    f"tgzr.pipeline{hatch_hooks_location}",
                ],
                "build-backend": "hatchling.build",
            },
            "tool": {
                "hatch": {
                    "envs": {"default": {"installer": "uv"}},
                    "version": {"path": f"src/{name}/__version__.py"},
                    "publish": {
                        "tgzr-pipeline-asset": asset_data.package.publish.to_pyproject()
                    },
                }
            },
        }
        print("Saving pyproject:", pyproject_path)
        pyproject_path.write_text(toml.dumps(pyproject_data))

    def create_editable(self, workspace_path: Path | str, force: bool = False):
        if self.is_editable:
            raise ValueError(
                f"Are you sure you want to create an editable version of {self.name}? \n"
                f"(it is already editable linked to {self._init_file})."
            )
        from ..workspace import Workspace

        workspace_path = Path(workspace_path)
        ws = Workspace(workspace_path)
        if ws.has_editable_asset(self.name):
            if not force:
                raise ValueError(
                    f"The asset {self.name} is already an editable in workspace {workspace_path}."
                )

        print(f"Creating editable asset for {self.name} in workspace {workspace_path}")

        version = self.get_version()
        asset_data = self.read_asset_data()

        ws.asset_manager.create_asset(
            ws._output_path,
            self.name,
            default_repo=None,  # = dont override it in asset_data
            asset_data=asset_data,
            version=version,
        )
