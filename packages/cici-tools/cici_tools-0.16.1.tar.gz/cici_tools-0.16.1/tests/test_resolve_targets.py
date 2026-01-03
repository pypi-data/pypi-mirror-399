# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import textwrap
from typing import Optional

import pytest

from cici.config.project.serializers import load, resolve_targets


def strip_proxy(image: Optional[str]) -> Optional[str]:
    if not image:
        return image
    if image and image.startswith("${CONTAINER_PROXY}"):
        return image[len("${CONTAINER_PROXY}") :]
    return image


@pytest.mark.parametrize(
    "config_yaml, target_files, expected_names, expected_images",
    [
        # inline-only targets in config.yaml
        (
            """
            name: blah
            targets:
              - name: alpha
                container:
                  image: ubuntu:22.04
            """,
            {},  # no targets directory
            ["alpha"],
            ["ubuntu:22.04"],
        ),
        # both inline + directory (no duplicate names)
        (
            """
            name: blah
            targets:
              - name: theta
                container:
                  image: old:version
              - name: delta
                container:
                  image: busybox
            """,
            {
                "gamma.yaml": """
                name: gamma
                container:
                  image: alpine:latest
                """
            },
            ["theta", "delta", "gamma"],
            ["old:version", "busybox", "alpine:latest"],
        ),
    ],
)
# resolve_targets correctly handles inline, directory, and mixed
def test_resolving_targets(
    tmp_path, config_yaml, target_files, expected_names, expected_images
):
    # setup test directory structure
    cici_dir = tmp_path / ".cici"
    cici_dir.mkdir()

    config_path = cici_dir / "config.yaml"
    config_path.write_text(textwrap.dedent(config_yaml))

    targets_dir = cici_dir / "targets"
    if target_files:
        targets_dir.mkdir()
        for filename, content in target_files.items():
            (targets_dir / filename).write_text(textwrap.dedent(content))

    # load config and resolve
    config_file = load(config_path)
    resolved = resolve_targets(config_file, config_path)

    # assertions
    names = [target.name for target in resolved.targets]
    images = [
        getattr(target.container, "image", None)
        for target in resolved.targets
        if getattr(target, "container", None)
    ]

    normalized_images = [strip_proxy(img) for img in images]

    assert sorted(names) == sorted(expected_names)
    assert sorted(normalized_images) == sorted(expected_images)


@pytest.mark.parametrize(
    "image, expected",
    [
        # Image without registry should be prefixed
        ("ubuntu:22.04", "${CONTAINER_PROXY}ubuntu:22.04"),
        # Fully qualified image should remain unchanged
        ("docker.io/library/python:3.11", "docker.io/library/python:3.11"),
        # Already proxied image should remain unchanged
        (
            "${CONTAINER_PROXY}custom/image:latest",
            "${CONTAINER_PROXY}custom/image:latest",
        ),
        # Starts with variable (e.g. GitLab CI variable) should remain unchanged
        ("$CI_REGISTRY/myimage:latest", "$CI_REGISTRY/myimage:latest"),
    ],
)
# test that patch_image correctly applies or skips ${CONTAINER_PROXY} prefix.
def test_container_proxy_injection(tmp_path, image, expected):
    config_yaml = f"""
    name: test-component
    targets:
      - name: foo
        container:
          image: {image}
    """
    cici_dir = tmp_path / ".cici"
    cici_dir.mkdir()
    config_path = cici_dir / "config.yaml"
    config_path.write_text(textwrap.dedent(config_yaml))
    config_file = load(config_path)
    resolved = resolve_targets(config_file, config_path)
    assert len(resolved.targets) == 1
    actual_image = resolved.targets[0].container.image
    assert actual_image == expected


@pytest.mark.parametrize(
    "config_yaml, target_files, expected_error",
    [
        # Duplicate accross config.yaml and targets dir
        (
            """
            name: test-duplicate
            targets:
              - name: duplicate
                container:
                  image: old:version
            """,
            {
                "duplicate.yaml": """
                name: duplicate
                container:
                  image: alpine:latest
                """,
            },
            "Duplicate target names found",
        ),
        # Duplicates in config.yaml
        (
            """
            name: test-duplicate
            targets:
              - name: whatever
                container:
                  image: ubuntu:22.04
              - name: whatever
                container:
                    image: busybox
            """,
            {},
            "Duplicate target names found",
        ),
        # Duplicates in the targets dir
        (
            """
            name: test-duplicate
            targets: []
            """,
            {
                "one.yaml": """
                name: repeat
                container:
                    image: alpine:3.18
                """,
                "two.yaml": """
                name: repeat
                container:
                    image: alpine:3.19
                """,
            },
            "Duplicate target names found",
        ),
    ],
)
# test that duplicate targets raise ValueError:
def test_resolve_targets_fails_with_duplicate_names(
    tmp_path, config_yaml, target_files, expected_error
):
    cici_dir = tmp_path / ".cici"
    cici_dir.mkdir()

    config_path = cici_dir / "config.yaml"
    config_path.write_text(textwrap.dedent(config_yaml))

    targets_dir = cici_dir / "targets"

    if target_files:
        targets_dir.mkdir()
        for filename, content in target_files.items():
            (targets_dir / filename).write_text(textwrap.dedent(content))

    config_file = load(config_path)

    with pytest.raises(ValueError, match=expected_error):
        resolve_targets(config_file, config_path)
