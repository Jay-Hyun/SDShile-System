#!/usr/bin/env python3
"""Download every asset of a public iCloud shared album (photos.icloud.com/shared/album/<token>).

Flow (mirrors the iCloud Photos web app):
  1. public records/resolve with the short GUID  -> zone + anonymousPublicAccess token
  2. shared records/query CPLAssetAndMasterByAssetDateWithoutHiddenOrDeleted
  3. download each CPLMaster resOriginalRes.downloadURL

Usage: fetch_icloud.py <shortGUID> <out_dir>
Writes <out_dir>/manifest.json with filename, size, dimensions, duration.
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

CONTAINER = "com.apple.photos.cloud"
HEADERS = {"Content-Type": "text/plain", "Origin": "https://photos.icloud.com"}


def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} for {url}: {e.read()[:300]!r}")


def main(token, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    res = post(
        f"https://ckdatabasews.icloud.com/database/1/{CONTAINER}/production/public/records/resolve",
        {"shortGUIDs": [{"value": token}]},
    )["results"][0]
    access = res["anonymousPublicAccess"]
    zone = {k: res["zoneID"][k] for k in ("zoneName", "ownerRecordName", "zoneType")}
    base = access["databasePartition"].replace(":443", "")
    qs = urllib.parse.urlencode({"publicAccessAuthToken": access["token"]})
    records = post(
        f"{base}/database/1/{CONTAINER}/production/shared/records/query?{qs}",
        {
            "query": {
                "recordType": "CPLAssetAndMasterByAssetDateWithoutHiddenOrDeleted",
                "filterBy": [{"fieldName": "direction", "comparator": "EQUALS",
                              "fieldValue": {"value": "ASCENDING", "type": "STRING"}}],
            },
            "resultsLimit": 200,
            "zoneID": zone,
        },
    ).get("records", [])

    assets = {}
    for r in records:
        if r["recordType"] == "CPLAsset":
            assets.setdefault(r["fields"]["masterRef"]["value"]["recordName"], r)

    manifest = []
    for m in (r for r in records if r["recordType"] == "CPLMaster"):
        f = m["fields"]
        name = base64.b64decode(f["filenameEnc"]["value"]).decode()
        orig = f["resOriginalRes"]["value"]
        asset = assets.get(m["recordName"])
        path = os.path.join(out_dir, name)
        if not (os.path.exists(path) and os.path.getsize(path) == orig["size"]):
            url = orig["downloadURL"].replace("${f}", urllib.parse.quote(name))
            print(f"downloading {name} ({orig['size'] / 1e6:.0f} MB)", flush=True)
            urllib.request.urlretrieve(url, path)
        manifest.append({
            "file": name,
            "size": orig["size"],
            "width": f["resOriginalWidth"]["value"],
            "height": f["resOriginalHeight"]["value"],
            "duration": asset["fields"]["duration"]["value"] / 1000 if asset else None,
            "assetDate": asset["fields"]["assetDate"]["value"] if asset else None,
        })
    manifest.sort(key=lambda x: x["assetDate"] or 0)
    with open(os.path.join(out_dir, "manifest.json"), "w") as fp:
        json.dump(manifest, fp, ensure_ascii=False, indent=2)
    print(f"{len(manifest)} files -> {out_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
