#!/usr/bin/env python3

import argparse
import json
from insta_collect.scraper import scrape_hashtag
from insta_collect.saver import save_data


def main():
    parser = argparse.ArgumentParser(description="Instagram hashtag scraper")
    parser.add_argument("--tag", required=True, help="Hashtag tanpa #")
    parser.add_argument("--limit", type=int, default=10, help="Jumlah post maksimal")
    parser.add_argument(
        "--profile",
        default="ig_profile",
        help="Folder profile Playwright (persistent login)"
    )
    args = parser.parse_args()

    print(f"[*] Target: #{args.tag} | Limit: {args.limit}")

    data = scrape_hashtag(
        hashtag=args.tag,
        limit=args.limit,
        profile_dir=args.profile
    )

    print(f"[DONE] Get {len(data)} data.")

    if data:
        filename = f"result_{args.tag}.json"
        save_data(data, filename=filename)
        print(f"[✓] Data save in {filename}")


if __name__ == "__main__":
    main()
