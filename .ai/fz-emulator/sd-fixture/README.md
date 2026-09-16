# Emulator SD fixture

`tree/` is the staged virtual SD root. Files are content-addressed in `blobs/`
and hard-linked into the staged tree, so identical bytes are stored once.
`manifest.json` records the path, size, and SHA-256 of every fixture file.

The live device contributed only public files below `/ext/apps` and
`/ext/asset_packs`. The current asset-pack directories contained no files.
Public build resources came from the local `resources.tar.gz`. Update manifests,
option bytes, user data, app state, Bluetooth/pairing material, keys, dolphin
state, unique identifiers, and files with identifier-shaped content are absent.

The fixture is intentionally a staged tree instead of a filesystem image. This
keeps it portable and allows an emulator to mount it directly or generate the
filesystem format it implements without duplicating content.
