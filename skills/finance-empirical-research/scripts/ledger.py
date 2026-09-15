"""Optional stdlib-only ledger tools, not a data parser or statistical engine."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

STATUSES = {'pending', 'running', 'succeeded', 'failed', 'blocked', 'not_applicable', 'stale'}


def rows(path):
    with Path(path).open(encoding='utf-8-sig') as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
                if not isinstance(row, dict):
                    raise ValueError('record must be an object')
            except (ValueError, TypeError) as error:
                raise ValueError(f'{path}:{number}: {error}') from error
            yield row


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def audit(specs_path, results_path):
    specs, results = list(rows(specs_path)), list(rows(results_path))
    def identities(records):
        return Counter(r['id'] for r in records if isinstance(r.get('id'), str) and r['id'])
    s, r = identities(specs), identities(results)
    counts = Counter(str(x.get('status')) for x in results)
    report = {
        'spec_count': len(specs), 'result_count': len(results),
        'missing_id_records': len(specs) - sum(s.values()) + len(results) - sum(r.values()),
        'duplicate_spec_ids': sorted(k for k,v in s.items() if v > 1),
        'duplicate_result_ids': sorted(k for k,v in r.items() if v > 1),
        'missing_results': sorted(s.keys()-r.keys()), 'extra_results': sorted(r.keys()-s.keys()),
        'invalid_statuses': dict((k,v) for k,v in counts.items() if k not in STATUSES),
        'status_counts': dict(counts),
        'unexplained_not_applicable': [x.get('id') for x in results if x.get('status') == 'not_applicable' and not x.get('reason')],
    }
    report['accounted'] = not any(report[k] for k in ('missing_id_records','duplicate_spec_ids','duplicate_result_ids','missing_results','extra_results','invalid_statuses','unexplained_not_applicable'))
    report['resolved_execution'] = report['accounted'] and all(x.get('status') in {'succeeded','not_applicable'} for x in results) and bool(specs)
    report['note'] = 'Checks ledger identity/status only, not semantic coverage, numerical validity, or exclusion evidence.'
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    q = subs.add_parser('query'); q.add_argument('path'); q.add_argument('--query', default='')
    q.add_argument('--fields', default=''); q.add_argument('--limit', type=int, default=20)
    q.add_argument('--offset', type=int, default=0); q.add_argument('--max-chars', type=int, default=12000)
    c = subs.add_parser('coverage'); c.add_argument('specs'); c.add_argument('results')
    h = subs.add_parser('hash'); h.add_argument('path')
    args = parser.parse_args()
    if args.command == 'hash':
        print(json.dumps({'path':args.path, 'sha256':digest(args.path)}, ensure_ascii=False)); return 0
    if args.command == 'coverage':
        report = audit(args.specs,args.results)
        print(json.dumps(report,ensure_ascii=False,indent=2)); return 0 if report['resolved_execution'] else 1
    if not 1 <= args.limit <= 200 or args.offset < 0 or args.max_chars < 200:
        parser.error('limit: 1..200, offset >= 0, max-chars >= 200')
    fields = [x.strip() for x in args.fields.split(',') if x.strip()]
    selected, matched, used = [], 0, 0
    for row in rows(args.path):
        if args.query.casefold() not in json.dumps(row,ensure_ascii=False).casefold():
            continue
        matched += 1
        if matched <= args.offset or len(selected) >= args.limit:
            continue
        value = {k:row[k] for k in fields if k in row} if fields else row
        size = len(json.dumps(value,ensure_ascii=False))
        if used + size > args.max_chars:
            continue
        selected.append(value); used += size
    print(json.dumps({'records':selected,'matched':matched,'returned':len(selected),'offset':args.offset,
                      'truncated':matched > args.offset + len(selected),
                      'hint':'Use --fields or a larger --max-chars if a record exceeds the output budget.'},ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        print(str(error),file=sys.stderr); sys.exit(2)
