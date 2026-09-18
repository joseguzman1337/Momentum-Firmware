import base64
import hashlib
import os
import shutil
import struct
import zlib

from SCons.Action import Action
from SCons.Builder import Builder
from SCons.Errors import StopError
from SCons.Node.FS import Dir, File


def _png_chunk(kind, payload):
    checksum = zlib.crc32(kind + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", checksum)


def _blank_png(width=10, height=10):
    header = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    pixels = b"".join(b"\x00" + bytes(width) for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", header)
        + _png_chunk(b"IDAT", zlib.compress(pixels))
        + _png_chunk(b"IEND", b"")
    )


def _fim_text(*, name, icon, api, uid, version_uid, path):
    if not icon:
        raise StopError(f"Flipper Lab application manifest has no icon for {path}")
    fields = (
        ("Filetype", "Flipper Application Installation Manifest"),
        ("Version", "1"),
        ("Full Name", name),
        ("Icon", base64.b64encode(icon).decode("ascii")),
        ("Version Build API", api),
        ("UID", uid),
        ("Version UID", version_uid),
        ("Path", path),
    )
    if any(not value for _, value in fields):
        raise StopError(f"Incomplete Flipper Lab application manifest for {path}")
    return "\n".join(f"{key}: {value}" for key, value in fields) + "\n"


def _read_api_version(api_definition):
    with open(api_definition, encoding="utf-8") as stream:
        for line in stream:
            fields = line.strip().split(",")
            if len(fields) >= 3 and fields[0] == "Version" and fields[2]:
                return fields[2]
    raise StopError(f"Cannot read API version from {api_definition}")


def _generate_lab_app_manifests(env, resources_root):
    manifests_dir = resources_root.Dir("apps_manifests")
    os.makedirs(manifests_dir.abspath, exist_ok=True)
    api = _read_api_version(env.File(env["SDK_DEFINITION"]).abspath)
    generated = set()

    for artifacts in env["FW_EXTAPPS"].application_map.values():
        app = artifacts.app
        for deployable, dist_path in artifacts.dist_entries:
            if not deployable or not dist_path.startswith("apps/") or not dist_path.endswith(".fap"):
                continue
            alias = os.path.splitext(os.path.basename(dist_path))[0]
            if alias in generated:
                raise StopError(f"Duplicate Flipper Lab application manifest alias: {alias}")
            generated.add(alias)
            deployed_fap = resources_root.File(dist_path).abspath
            with open(deployed_fap, "rb") as stream:
                version_uid = "nx-local-" + hashlib.sha256(stream.read()).hexdigest()
            icon = _blank_png()
            if app.fap_icon:
                with open(os.path.join(app._apppath, app.fap_icon), "rb") as stream:
                    source_icon = stream.read()
                if source_icon.startswith(b"\x89PNG\r\n\x1a\n"):
                    icon = source_icon
            manifest = _fim_text(
                name=app.name or app.appid,
                icon=icon,
                api=api,
                uid=f"nx-local-{app.appid}",
                version_uid=version_uid,
                path=f"/ext/{dist_path}",
            )
            with open(manifests_dir.File(f"{alias}.fim").abspath, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(manifest)


def __generate_resources_dist_entries(env):
    src_target_entries = []

    resources_root = env.Dir(env["RESOURCES_ROOT"])

    for app_artifacts in env["FW_EXTAPPS"].application_map.values():
        for _, dist_path in filter(
            lambda dist_entry: dist_entry[0], app_artifacts.dist_entries
        ):
            src_target_entries.append(
                (
                    app_artifacts.compact,
                    resources_root.File(dist_path),
                )
            )

    # Deploy apps' resources too
    resources_apps = env["APPBUILD"].apps.copy()
    resources_apps.extend(x.app for x in env["FW_EXTAPPS"].application_map.values())
    for app in resources_apps:
        if not app.resources:
            continue
        apps_resource_dir = app._appdir.Dir(app.resources)
        for res_file in env.GlobRecursive("*", apps_resource_dir):
            if not isinstance(res_file, File):
                continue
            src_target_entries.append(
                (
                    res_file,
                    resources_root.File(
                        res_file.get_path(apps_resource_dir),
                    ),
                )
            )

    # Deploy other stuff from _EXTRA_DIST
    for extra_dist in env["_EXTRA_DIST"]:
        if isinstance(extra_dist, Dir):
            src_target_entries.append(
                (
                    extra_dist,
                    resources_root.Dir(extra_dist.name),
                )
            )
        else:
            raise StopError(f"Unsupported extra dist type: {type(extra_dist)}")

    return src_target_entries


def _resources_dist_emitter(target, source, env):
    src_target_entries = __generate_resources_dist_entries(env)
    source = list(map(lambda entry: entry[0], src_target_entries))
    return (target, source)


def _resources_dist_action(target, source, env):
    dist_entries = __generate_resources_dist_entries(env)
    assert len(dist_entries) == len(source)
    shutil.rmtree(env.Dir(env["RESOURCES_ROOT"]).abspath, ignore_errors=True)
    for src, target in dist_entries:
        if isinstance(src, File):
            os.makedirs(os.path.dirname(target.path), exist_ok=True)
            shutil.copy(src.path, target.path)
        elif isinstance(src, Dir):
            shutil.copytree(src.path, target.path)
        else:
            raise StopError(f"Unsupported dist entry type: {type(src)}")
    _generate_lab_app_manifests(env, env.Dir(env["RESOURCES_ROOT"]))


def generate(env, **kw):
    env.SetDefault(
        ASSETS_COMPILER="${FBT_SCRIPT_DIR}/assets.py",
    )

    if not env["VERBOSE"]:
        env.SetDefault(
            RESOURCEDISTCOMSTR="\tRESDIST\t${RESOURCES_ROOT}",
            RESMANIFESTCOMSTR="\tMANIFST\t${TARGET}",
        )

    env.Append(
        BUILDERS={
            "ManifestBuilder": Builder(
                action=[
                    Action(
                        _resources_dist_action,
                        "${RESOURCEDISTCOMSTR}",
                    ),
                    Action(
                        [
                            [
                                "${PYTHON3}",
                                "${ASSETS_COMPILER}",
                                "manifest",
                                "${TARGET.dir.posix}",
                                "--timestamp=${GIT_UNIX_TIMESTAMP}",
                            ]
                        ],
                        "${RESMANIFESTCOMSTR}",
                    ),
                ],
                emitter=_resources_dist_emitter,
            ),
        }
    )


def exists(env):
    return True
