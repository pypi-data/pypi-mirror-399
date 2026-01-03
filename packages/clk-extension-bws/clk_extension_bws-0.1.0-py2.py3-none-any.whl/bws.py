#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""A simple wrapper around bws"""

__version__ = "0.1.0"

import json
from collections import defaultdict

import click
from clk.config import config
from clk.core import cache_disk
from clk.decorators import (
    argument,
    flag,
    group,
    option,
)
from clk.lib import call, check_output, json_dumps, updated_env
from clk.log import get_logger
from clk.types import DynamicChoice, ExecutableType
from keyring.compat import properties

LOGGER = get_logger(__name__)

import keyring.backend


class BWSKeyring(keyring.backend.KeyringBackend):
    @properties.classproperty
    def priority(cls) -> float:
        try:
            check_output(["bws", "--version"], internal=True)
            return 6.0
        except FileNotFoundError:
            return 0.0

    def set_password(self, _, username, password):
        raise NotImplementedError

    def get_password(self, _, secret):
        def name(secret):
            return secret["key"]

        try:
            candidates = [
                _secret["value"]
                for _secret in BWSSecretName().bws_secret_list()
                if name(_secret) == secret
            ]
        except FileNotFoundError:
            return None
        if len(candidates) > 1:
            raise NotImplementedError(
                "Do not handle the fact that several password have the same name yet"
            )
        if len(candidates) < 1:
            return None
        return candidates[0]

    def delete_password(self, servicename, username, password):
        raise NotImplementedError


class BWSProject(DynamicChoice):
    @staticmethod
    @cache_disk(expire=600)
    def bws_project_list():
        return json.loads(check_output(["bws", "project", "list"], internal=True))

    @staticmethod
    def to_name(project_id):
        return [
            project["name"]
            for project in BWSProject.bws_project_list()
            if project["id"] == project_id
        ][0]

    def choices(self):
        return [project["name"] for project in self.bws_project_list()]

    def converter(self, name):
        candidates = [
            project for project in self.bws_project_list() if project["name"] == name
        ]
        if len(candidates) > 1:
            raise NotImplementedError(
                "Several ids for the same name:"
                f" {', '.join([candidate['id'] for candidate in candidates])}"
            )
        return candidates[0]


class BWSConfig:
    pass


@group()
@option(
    "--project",
    type=BWSProject(),
    help="What project to consider, if any",
    expose_class=BWSConfig,
)
def bws():
    "Deal with bws secrets"


class BWSSecretName(DynamicChoice):
    secret_separator = "--"

    @staticmethod
    @cache_disk(expire=600)
    def bws_secret_list():
        return json.loads(check_output(["bws", "secret", "list"], internal=True))

    @staticmethod
    def format_with_project(secret):
        return (
            secret["key"]
            + BWSSecretName.secret_separator
            + BWSProject.to_name(secret["projectId"])
        )

    def choices(self):
        counter = defaultdict(lambda: 0)
        secrets = []
        result = []
        for secret in self.bws_secret_list():
            if not self.matching_project(secret):
                continue
            counter[secret["key"]] += 1
            secrets.append(secret)
        for secret in secrets:
            if not config.bws.project:
                result.append(self.format_with_project(secret))
            if counter[secret["key"]] == 1:
                result.append(secret["key"])
        return result

    @staticmethod
    def matching_project(secret, project=None):
        project = project or config.bws.project
        return not project or (project and project["id"] == secret["projectId"])

    def converter(self, name):
        candidates = [
            secret
            for secret in self.bws_secret_list()
            if self.matching_project(secret)
            and (
                (BWSSecretName.secret_separator not in name and secret["key"] == name)
                or (
                    BWSSecretName.secret_separator in name
                    and self.format_with_project(secret) == name
                )
            )
        ]
        if len(candidates) > 1:
            raise NotImplementedError(
                "Several ids for the same name:"
                f" {', '.join([candidate['id'] for candidate in candidates])}"
            )
        return candidates[0]


@bws.command()
@argument("secret", type=BWSSecretName(), help="What secret to show")
@flag("--value", help="Only the value, to ease automation")
def show(secret, value):
    "Nicely show this secret"
    projects = BWSProject.bws_project_list()
    projectName = [
        project["name"] for project in projects if project["id"] == secret["projectId"]
    ][0]

    content = {"projectName": projectName} | secret
    if value:
        print(content["value"])
    else:
        print(json_dumps(content))


def extend_with_project(secret):
    if projectId := secret.get("projectId"):
        projectName = [
            project["name"]
            for project in BWSProject.bws_project_list()
            if project["id"] == projectId
        ][0]
    return secret | {"project": projectName}


@bws.command()
@argument("secret", type=BWSSecretName(), help="What secret to edit")
@option("--value", help="The new value to set")
def edit(secret, value):
    "Nicely edit this secret"
    projects = BWSProject.bws_project_list()
    projectName = ""
    if projectId := secret.get("projectId"):
        projectName = [
            project["name"] for project in projects if project["id"] == projectId
        ][0]
    editable = {
        "key": secret["key"],
        "value": secret["value"],
        "note": secret["note"],
        "project": projectName,
    }
    if value:
        new_value = editable.copy()
        new_value["value"] = value
    else:
        new_value = click.edit(json_dumps(editable))
        if new_value is None or new_value.strip() == "":
            LOGGER.warning("Nothing to be done")
            return
        new_value = json.loads(new_value)
    key, value, note, projectName = (
        new_value["key"],
        new_value["value"],
        new_value["note"],
        new_value["project"],
    )
    args = ["bws", "secret", "edit", "--key", key, "--value", value, "--note", note]
    if projectName:
        projectId = [
            project["id"] for project in projects if project["name"] == projectName
        ][0]
        args += ["--project-id", projectId]
    args.append(secret["id"])
    if click.confirm(f"""I will call
{args}"""):
        call(args)
        _clean_cache()


@bws.command()
@argument("secret", type=BWSSecretName(), help="What secret to rename")
@argument("new-name", help="no comment")
def rename(secret, new_name):
    "no comment"
    args = ["bws", "secret", "edit", "--key", new_name]
    args.append(secret["id"])
    if click.confirm(f"""I will call
{args}"""):
        call(args)
        _clean_cache()


def _clean_cache():
    BWSProject().bws_project_list.drop()
    BWSSecretName().bws_secret_list.drop()


@bws.command()
def clean_cache():
    "Clean the cache to get the new secrets next time"
    _clean_cache()


@bws.command()
@argument(
    "secret",
    type=BWSSecretName(),
    help="The secret to copy",
)
@argument(
    "project",
    type=BWSProject(),
    help="Wher to copy the secret",
)
def copy_to_project(secret, project):
    """Copy the content of the secret to the given project."""
    for other_secret in BWSSecretName.bws_secret_list():
        if (
            other_secret["projectId"] == project["id"]
            and other_secret["key"] == secret["key"]
        ):
            raise click.UsageError(
                f"Secret {secret['key']} already in project {project['name']}"
            )

    call(
        [
            "bws",
            "secret",
            "create",
            "--note",
            secret["note"],
            secret["key"],
            secret["value"],
            project["id"],
        ]
    )
    # need to refresh the list to avoid being able to do it twice
    BWSSecretName.bws_secret_list.drop()
    _clean_cache()


@bws.command()
@argument("secret", type=BWSSecretName(), help="The secret to delete.")
@flag("--force", help="Don't ask for confirmation.")
def delete(secret, force):
    """Delete a secret."""
    project = [
        project
        for project in BWSProject().bws_project_list()
        if secret["projectId"] == project["id"]
    ][0]
    if force or click.confirm(
        f"Deleting {secret['key']} from project {project['id']} is irreversible, do it anyway ?"
    ):
        call(["bws", "secret", "delete", secret["id"]])
        _clean_cache()


@bws.command()
@option("--shell/--no-shell", help="Execute the command through the shell")
@argument(
    "command",
    nargs=-1,
    required=True,
    type=ExecutableType(),
    help="The command to execute",
)
@option("--secret", type=BWSSecretName(), multiple=True, help="Secret to use.")
@option("--project", type=BWSProject(), help="Use all the secrets from this project.")
def exec(command, shell, secret, project):
    """Execute a command with those secrets in the environment."""
    secrets_provider = BWSSecretName()
    secrets = {}
    if project:
        secrets.update(
            {
                secret["key"]: secret["value"]
                for secret in secrets_provider.bws_secret_list()
                if secrets_provider.matching_project(secret, project)
            }
        )
    secrets.update({s["key"]: s["value"] for s in secret})
    with updated_env(**secrets):
        call(
            command,
            shell=shell,
        )


@bws.command(handle_dry_run=True)
@argument("project", type=BWSProject(), help="In what project to create the secret.")
@argument("secret", help="The name of the secret to create.")
@argument("value", help="The value to give to the secret.")
@option("--note", help="No comment")
@flag("--update", help="Update the existing secret instead of creating one")
def create(secret, value, project, update, note):
    """Create a secret."""
    secrets_provider = BWSSecretName()
    if existing_secrets := [
        existing_secret
        for existing_secret in secrets_provider.bws_secret_list()
        if secret == existing_secret["key"]
        and project["id"] == existing_secret["projectId"]
    ]:
        if update:
            if len(existing_secrets) > 1:
                raise NotImplementedError(
                    "More than one secret with name"
                    f" {secret} in project {project['id']}"
                    ". I don't know what to do...."
                )
            existing_secret = existing_secrets[0]
            args = [
                "bws",
                "secret",
                "edit",
                "--project-id",
                project["id"],
                "--key",
                secret,
                "--value",
                value,
                existing_secret["id"],
            ]
        else:
            raise click.UsageError(
                f"Already a secret called {secret} in project {project['name']}"
            )
    else:
        args = ["bws", "secret", "create", secret, value, project["id"]]
    if note:
        args += ["--note", note]
    call(args)
    _clean_cache()


@bws.command()
def list():
    """List the secret, possibly filtered by the configured project."""
    args = ["bws", "secret", "list"]
    if config.bws.project:
        args.append(config.bws.project["id"])
    secrets_provider = BWSSecretName()
    secrets = [
        extend_with_project(secret)
        for secret in secrets_provider.bws_secret_list()
        if secrets_provider.matching_project(secret)
    ]
    print(json_dumps(secrets))
