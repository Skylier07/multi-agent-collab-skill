#!/usr/bin/env python3
"""
Message Archiver for Multi-Agent Collaboration Protocol

Moves resolved message threads from messages.md to history.md.
Run when messages.md gets cluttered (default threshold: 10 resolved threads).

Usage:
    python archive_messages.py
    python archive_messages.py --threshold 5
    python archive_messages.py --dry-run

Exit codes:
    0 = success (or nothing to archive)
    1 = error
"""

import argparse
import re
import sys
from datetime import datetime, timezone


def parse_messages(filepath):
    """Parse messages.md into a list of message blocks."""
    with open(filepath) as f:
        content = f.read()

    # Split on the --- delimiter that precedes each message
    blocks = re.split(r'\n---\n', content)

    header = blocks[0] if blocks else ""
    messages = []

    for block in blocks[1:]:
        block = block.strip()
        if not block:
            continue

        # Extract message ID
        id_match = re.search(r'### (MSG-\d+)', block)
        msg_id = id_match.group(1) if id_match else None

        # Extract status
        status_match = re.search(r'\*\*Status:\*\*\s*(\w+)', block)
        status = status_match.group(1) if status_match else 'unknown'

        # Extract Re: field for thread tracking
        re_match = re.search(r'\*\*Re:\*\*\s*(MSG-\d+)', block)
        reply_to = re_match.group(1) if re_match else None

        messages.append({
            'id': msg_id,
            'status': status,
            'reply_to': reply_to,
            'raw': block
        })

    return header, messages


def find_resolved_threads(messages):
    """Find complete threads where all messages are resolved.

    A thread is a root message plus all messages that reference it via Re:.
    A thread is "resolved" if the root and all replies have status: resolved,
    OR if a reply with status: resolved exists (indicating the thread concluded).
    """
    # Build thread map: root_id -> [messages in thread]
    threads = {}
    for msg in messages:
        if msg['reply_to']:
            root = msg['reply_to']
            # Walk up to find the true root (in case of nested replies)
            for m in messages:
                if m['id'] == root and m['reply_to']:
                    root = m['reply_to']
            threads.setdefault(root, []).append(msg)
        else:
            threads.setdefault(msg['id'], [])

    # Also add root messages to their own threads
    for msg in messages:
        if msg['id'] in threads and msg not in threads[msg['id']]:
            threads[msg['id']].insert(0, msg)

    resolved = []
    for root_id, thread_msgs in threads.items():
        if not thread_msgs:
            continue
        # Thread is resolved if any message in it has status: resolved
        if any(m['status'] == 'resolved' for m in thread_msgs):
            resolved.append((root_id, thread_msgs))

    return resolved


def archive(messages_path='.collab/messages.md',
            history_path='.collab/history.md',
            threshold=10,
            dry_run=False):
    """Archive resolved threads from messages.md to history.md."""

    header, messages = parse_messages(messages_path)
    resolved_threads = find_resolved_threads(messages)

    if len(resolved_threads) < threshold:
        print(f"Only {len(resolved_threads)} resolved thread(s) "
              f"(threshold: {threshold}). Nothing to archive.")
        return 0

    # Collect message IDs to archive
    archive_ids = set()
    archive_blocks = []

    for root_id, thread_msgs in resolved_threads:
        for msg in thread_msgs:
            archive_ids.add(msg['id'])
            archive_blocks.append(msg['raw'])

    # Build the archive entry
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
    id_range = sorted(archive_ids)
    archive_entry = f"\n## Archived: {now}\n"
    archive_entry += f"_Threads: {id_range[0]} through {id_range[-1]}_\n\n"
    for block in archive_blocks:
        archive_entry += f"---\n{block}\n\n"

    # Build the tombstone for messages.md
    tombstone = f"_[{id_range[0]} through {id_range[-1]} archived on {now}]_"

    if dry_run:
        print(f"DRY RUN: Would archive {len(archive_ids)} messages "
              f"in {len(resolved_threads)} threads")
        print(f"IDs: {', '.join(sorted(archive_ids))}")
        return 0

    # Append to history.md
    with open(history_path, 'a') as f:
        f.write(archive_entry)

    # Rewrite messages.md without archived messages
    remaining = [m for m in messages if m['id'] not in archive_ids]
    with open(messages_path, 'w') as f:
        f.write(header)
        f.write(f"\n{tombstone}\n")
        for msg in remaining:
            f.write(f"\n---\n{msg['raw']}\n")

    print(f"Archived {len(archive_ids)} messages in {len(resolved_threads)} threads.")
    print(f"Tombstone added to messages.md, full content appended to history.md.")
    return 0


def main():
    parser = argparse.ArgumentParser(description='Archive resolved message threads')
    parser.add_argument('--threshold', type=int, default=10,
                        help='Minimum resolved threads before archiving (default: 10)')
    parser.add_argument('--messages', default='.collab/messages.md',
                        help='Path to messages.md')
    parser.add_argument('--history', default='.collab/history.md',
                        help='Path to history.md')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be archived without doing it')
    args = parser.parse_args()

    try:
        sys.exit(archive(args.messages, args.history, args.threshold, args.dry_run))
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
