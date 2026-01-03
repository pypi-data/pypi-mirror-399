# scripts/migrate_1_to_2.py

from rcdl.core.config import Config
from rcdl.core.models import Video, VideoStatus
import rcdl.core.parser as parser
from rcdl.core.db import DB

import sqlite3


def add_col_total_parts():
    db = DB()
    db.init_table()

    print("UPDATE DB")
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(videos)")
    columns = [row["name"] for row in cursor.fetchall()]

    if "total_parts" not in columns:
        cursor.execute("ALTER TABLE videos ADD COLUMN total_parts INTEGER")
        print("ADDED TOTAL PARTS")
    else:
        print("TOTAL_PARTS ALREADY IN")

    conn.commit()
    conn.close()


def update_total_parts(videos: list[Video]):
    # get unique set creator
    """
    for each videos:
    - get creator
    - read json
    - find post id 6> get post
    - get ttoal parts
    """

    for v in videos:
        json_path = Config.cache_file(
            str(Config.CACHE_DIR / f"{v.creator_id}_{v.service}")
        )
        print(json_path)

        posts = parser.filter_posts_with_videos_from_json(str(json_path))

        post = None
        for p in posts:
            if p["id"] == v.post_id:
                post = p
                break

        if post is None:
            print(
                f"Could not match {v.post_id}@{v.creator_id} with any post in {json_path}"
            )
            continue

        v.total_parts = len(parser.extract_video_urls(post))
    return videos


if __name__ == "__main__":
    # read db
    # fetch posts
    # for each post -> get total part
    # for each post id, update db

    with DB() as db:
        version = db.get_schema_version()
    if version == 2:
        print("You already are on the newer version 2")
        y = input("Continue ? (y/n)")
        if y != "y":
            quit()

    add_col_total_parts()

    with DB() as db:
        videos = db.query_all()
    print(f"Found {len(videos)} videos in DB")

    videos = update_total_parts(videos)

    # update db
    print("UPDATE DB")
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    SQL_QUERY_STR = """
    INSERT INTO videos (
    post_id, creator_id, service, domain, relative_path, url, part,
    total_parts, status, fail_count, published, title, substring,
    downloaded_at, file_size
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(service, url) DO UPDATE SET
        total_parts = excluded.total_parts
    """

    rows = []
    for video in videos:
        rows.append(
            (
                video.post_id,
                video.creator_id,
                video.service,
                video.domain,
                video.relative_path,
                video.url,
                video.part,
                video.total_parts,
                VideoStatus.NOT_DOWNLOADED.value,
                0,
                video.published,
                video.title,
                video.substring,
                None,
                None,
            )
        )

    conn.executemany(SQL_QUERY_STR, rows)
    conn.commit()

    with DB() as db:
        db.set_schema_version(2)
