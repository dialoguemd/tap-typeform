#!/usr/bin/env python3

import argparse
import json
import os
import sys

import dialogue.logging
import singer
import structlog
from dialogue.logging import util
from singer import utils
from singer.catalog import Catalog, CatalogEntry, Schema
from structlog import get_logger

import tap_typeform.schemas as schemas
import tap_typeform.streams as streams
from tap_typeform.context import Context

REQUIRED_CONFIG_KEYS = []

util.setup_structlog()

LOGGER = get_logger()

env = os.environ.copy()

# def check_authorization(atx):
#    atx.client.get('/settings')


# Some taps do discovery dynamically where the catalog is read in from a
#  call to the api but with the typeform structure, we won't do that here
#  because it's always the same so we just pull it from file we never use
#  atx in here since the schema is from file but we would use it if we
#  pulled schema from the API def discover(atx):
def discover():
    catalog = Catalog([])
    for tap_stream_id in schemas.STATIC_SCHEMA_STREAM_IDS:
        # print("tap stream id=",tap_stream_id)
        schema = Schema.from_dict(schemas.load_schema(tap_stream_id))
        metadata = []
        for field_name in schema.properties.keys():
            # print("field name=",field_name)
            if field_name in schemas.PK_FIELDS[tap_stream_id]:
                inclusion = "automatic"
            else:
                inclusion = "available"
            metadata.append(
                {
                    "metadata": {"inclusion": inclusion},
                    "breadcrumb": ["properties", field_name],
                }
            )
        catalog.streams.append(
            CatalogEntry(
                stream=tap_stream_id,
                tap_stream_id=tap_stream_id,
                key_properties=schemas.PK_FIELDS[tap_stream_id],
                schema=schema,
                metadata=metadata,
            )
        )
    return catalog


# this is already defined in schemas.py though w/o dependencies.  do we keep this for the sync?
def load_schema(tap_stream_id):
    path = "schemas/{}.json".format(tap_stream_id)
    schema = utils.load_json(get_abs_path(path))
    dependencies = schema.pop("tap_schema_dependencies", [])
    refs = {}
    for sub_stream_id in dependencies:
        refs[sub_stream_id] = load_schema(sub_stream_id)
    if refs:
        singer.resolve_schema_references(schema, refs)
    return schema


def sync(atx):

    # write schemas for selected streams\
    for stream in atx.catalog.streams:
        # if stream.tap_stream_id in atx.selected_stream_ids:
        schemas.load_and_write_schema(stream.tap_stream_id)

    # since there is only one set of schemas for all forms, they will always be selected
    streams.sync_forms(atx)

    for stream_name, stream_count in atx.counts.items():
        LOGGER.info("%s: %d", stream_name, stream_count)


def load_file(filename):
    if filename is None:
        return {}

    file = {}

    try:
        with open(filename) as handle:
            file = json.load(handle)
    except Exception:
        LOGGER.fatal("Failed to decode config file. Is it valid json?")
        raise RuntimeError

    return file


@utils.handle_top_exception(LOGGER)
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--properties", help="Catalog file with fields selected")
    parser.add_argument("-c", "--config", help="Optional config file")
    parser.add_argument("-s", "--state", help="State file")
    parser.add_argument(
        "-d",
        "--discover",
        help="Build a catalog from the underlying schema",
        action="store_true",
    )

    args = parser.parse_args()
    if args.config:
        LOGGER.info("Config json found")
        config = load_file(args.config)
    elif "typeform_config" in env:
        LOGGER.info("Env var config found")
        config = json.loads(env["typeform_config"])
    else:
        LOGGER.critical("No config found, aborting run")
        return

    properties = load_file(args.properties)
    state = load_file(args.state)

    atx = Context(config, state)
    if args.discover:
        # the schema is static from file so we don't need to pass in atx for connection info.
        catalog = discover()
        json.dump(catalog.to_dict(), sys.stdout)
    else:
        atx.catalog = Catalog.from_dict(properties) if args.properties else discover()
        sync(atx)


if __name__ == "__main__":
    main()
