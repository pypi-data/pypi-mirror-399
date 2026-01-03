# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# Loads .cici/config.yaml
# Defines targes, variables and metadata about the project.


import logging
import re
from pathlib import Path
from typing import Any, Optional, Union

import msgspec
import ruamel.yaml
from msgspec.structs import replace

from . import models as cici_config

decoder = msgspec.json.Decoder(type=cici_config.File)
target_decoder = msgspec.json.Decoder(type=cici_config.Target)
image_fqdn_regex = re.compile(r"^[\w\.-]+/")


# make sure each variable has its 'name' field set from its key
def inject_variable_names(variables: dict[str, Union[str, dict]]) -> dict[str, dict]:
    patched = {}
    for key, value in variables.items():
        if isinstance(value, str):
            value = {"value": value}
        # if value is None or not a dict, treat it as empty dict
        if not isinstance(value, dict):
            raise TypeError(f"Expected dict for variable {key}, got {type(value)}")
        # only add name if missing
        value.setdefault("name", key)
        patched[key] = value
    return patched


def load_targets_from_dir(target_dir: Path) -> list[cici_config.Target]:
    if not target_dir.exists() or not target_dir.is_dir():
        return []

    yaml = ruamel.yaml.YAML(typ="safe")
    targets: list[cici_config.Target] = []

    # checking for .yaml
    for file in sorted(target_dir.glob("*.yaml")):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = yaml.load(f) or {}

            # make sure name exists before decoding
            data.setdefault("name", file.stem)

            # decode using msgspec for validation and type safety
            target_obj = target_decoder.decode(msgspec.json.encode(data))
            targets.append(target_obj)

        except msgspec.ValidationError as e:
            logging.warning(f"Validation failed for {file.name}: {e}")
        except Exception as e:
            logging.warning(f"Failed to load target {file.name}: {e}")

    logging.info(f"Loaded {len(targets)} valid targets from {target_dir}")
    return targets


def resolve_targets(
    cici_config_file: Optional[cici_config.File], config_path: Path
) -> Optional[cici_config.File]:
    # Resolve and merge targets from .cici/config.yaml and from .cici/targets/*.yaml

    # - Directory targets override config.yaml targets with the same name
    # - If no targets dir exists, use the targets defined in the config.yaml
    # - returns updated 'cici_config.File' with merged targets

    if not cici_config_file:
        return None

    # get directory that could exist targets
    targets_dir = config_path.parent / "targets"

    # get targets from config.yaml
    config_targets: list[cici_config.Target] = list(cici_config_file.targets)

    # load targets from '.cici/targets/' if there are any
    dir_targets: list[cici_config.Target] = []
    if targets_dir.exists() and any(targets_dir.glob("*.yaml")):
        logging.info(f"loading targets from directory: {targets_dir}")
        dir_targets = load_targets_from_dir(targets_dir)

    # combine all targets
    all_targets = list(config_targets) + list(dir_targets)

    # get target names
    target_names = [
        target.name for target in all_targets if getattr(target, "name", None)
    ]

    # check duplicates
    if len(target_names) != len(set(target_names)):
        raise ValueError(
            f"Duplicate target names found: {', '.join(sorted(target_names))}"
        )

    # create new file with merged target list
    resolved_file = replace(cici_config_file, targets=all_targets)
    return resolved_file


def patch_image(image: str, container_proxy: str = "${CONTAINER_PROXY}") -> str:
    """Patch in $CONTAINER_PROXY to image unless the following are true:

    A: Does the image URL contain ${CONTAINER_PROXY} (the literal string)
    B: Is the image URL a fully-qualified container URL?
    C: Does the image already start with a variable?
    """

    if not image:
        return image
    if container_proxy in image:
        return image

    if image_fqdn_regex.match(image):
        return image

    if image.startswith("$"):
        return image

    return f"{container_proxy}{image}"


def loads(
    text: str,
    gitlab_ci_jobs: Optional[dict[str, Any]] = None,
    precommit_hooks: Optional[dict[str, Any]] = None,
) -> cici_config.File:
    # parse YAML into fully-typed File object
    if gitlab_ci_jobs is None:
        gitlab_ci_jobs = {}
    if precommit_hooks is None:
        precommit_hooks = {}

    yaml = ruamel.yaml.YAML(typ="safe")
    data = yaml.load(text)

    # verify targets exists even if empty
    data.setdefault("targets", [])

    # Inject precommit/gitlab includes into each target

    # Debug to test injection
    # print("Before injection:", data["targets"])

    for target in data["targets"]:
        target["precommit_hook"] = {"name": target["name"]}
        target["gitlab_include"] = {"name": target["name"]}

    # Debug to test injection
    # print("After injection:", data["targets"])

    if "variables" in data:
        data["variables"] = inject_variable_names(data["variables"])

    # decode into file_struct
    file_struct = decoder.decode(msgspec.json.encode(data))

    # post process to patch CONTAINER_PROXY to container images
    patched_targets = []
    for target in file_struct.targets:
        if target.container is not None:
            patched_container = replace(
                target.container,
                image=patch_image(target.container.image),
            )
            patched_targets.append(replace(target, container=patched_container))
        else:
            patched_targets.append(target)

    return replace(file_struct, targets=patched_targets)


def load(
    file: Union[str, Path],
    gitlab_ci_jobs: Optional[dict[str, Any]] = None,
    precommit_hooks: Optional[dict[str, Any]] = None,
) -> cici_config.File:
    return loads(
        open(file).read(),
        gitlab_ci_jobs=gitlab_ci_jobs,
        precommit_hooks=precommit_hooks,
    )
