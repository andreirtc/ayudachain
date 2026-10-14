"""Consistent local backups. Quiesce business writers before operator recovery.

Checksums detect corruption; this tool makes no operational security assertion.
The signing key is not backed up. A surviving pinned chain is required.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from psycopg.conninfo import conninfo_to_dict,make_conninfo
from backend.app.config import ROOT,load_local_environment
from backend.app.database import connection
from backend.app.services.evidence import original_bytes,storage_root


def sha(raw):return hashlib.sha256(raw).hexdigest()
def pg_bin(name):
    root=Path(os.environ.get('MVP_PG_BIN',str(ROOT/'.runtime/tools/pgsql/bin')))
    path=root/(name+'.exe' if os.name=='nt' else name)
    return str(path) if path.exists() else name


def pg_env(dsn):
    info=conninfo_to_dict(dsn)
    if info.get('host') not in {'localhost','127.0.0.1','::1'}:raise ValueError('local PostgreSQL only')
    env=os.environ.copy()
    for key,name in [('host','PGHOST'),('port','PGPORT'),('user','PGUSER'),('password','PGPASSWORD'),('dbname','PGDATABASE')]:
        if key in info:env[name]=info[key]
    return env


def run_pg(name,args,dsn):
    run=subprocess.run([pg_bin(name),*args],env=pg_env(dsn),capture_output=True,timeout=60)
    if run.returncode:raise RuntimeError('PostgreSQL '+name+' failed; backup/restore not accepted')


def checkpoint(deployments,action):
    run=subprocess.run([os.environ.get('MVP_NODE','node'),str(ROOT/'contracts/scripts/recovery_checkpoint.js')],input=json.dumps({'deployments':deployments,'action':action}),capture_output=True,text=True,timeout=30,cwd=ROOT)
    value=json.loads(run.stdout)
    if not value.get('checked'):raise ValueError('Surviving pinned chain required; lost chain or unknown post-backup record')
    return value['checkpoints']


def backup(directory):
    load_local_environment();directory=Path(directory).resolve()
    if not directory.is_relative_to(ROOT/'.runtime/backups') or directory.exists():raise ValueError('New owned backup directory required')
    directory.mkdir(parents=True);files={};deployments=[]
    def write(relative,raw):
        path=directory/relative;path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as out:out.write(raw);out.flush();os.fsync(out.fileno())
        files[relative]=sha(raw)
    schema=os.environ.get('MVP_SCHEMA','public')
    with connection(purpose='owner') as db:
        db.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY')
        snapshot=db.execute('SELECT pg_export_snapshot() snapshot').fetchone()['snapshot']
        for row in db.execute('SELECT * FROM evidence_versions').fetchall():write('originals/'+row['storage_key'],original_bytes(row))
        for d in db.execute('SELECT * FROM deployments ORDER BY id').fetchall():
            source=Path(d['abi_reference'].split('#sha256=')[0]).resolve()
            if not source.is_relative_to(ROOT):raise ValueError('Manifest must be within the owned workspace')
            raw=source.read_bytes();relative='manifests/'+str(d['id'])+'.json';write(relative,raw)
            if '#sha256=' in d['abi_reference'] and d['abi_reference'].split('#sha256=')[1]!=sha(raw):raise ValueError('Pinned manifest changed')
            known=[{'public_id':'0x'+r['public_id'].hex(),'content_hash':'0x'+r['content_hash'].hex()} for r in db.execute('SELECT public_id,content_hash FROM commitments WHERE deployment_id=%s',(d['id'],)).fetchall()]
            deployments.append({'deployment_id':str(d['id']),'manifest':json.loads(raw),'backup_file':relative,'source_path':str(source),'known':known})
        checkpoints={r['deployment_id']:r for r in checkpoint(deployments,'capture')}
        for d in deployments:d['checkpoint']=checkpoints[d['deployment_id']]
        run_pg('pg_dump',['--format=custom','--no-owner','--no-privileges','--schema='+schema,'--snapshot='+snapshot,'--file='+str(directory/'database.dump')],os.environ['MVP_OWNER_DATABASE_URL'])
    files['database.dump']=sha((directory/'database.dump').read_bytes())
    secret=os.environ.get('MVP_COMMAND_DIGEST_KEY')
    if not secret or len(secret)!=64:raise ValueError('Original replay key required')
    write('private-config.json',json.dumps({'MVP_COMMAND_DIGEST_KEY':secret}).encode())
    metadata={'format':'ayudachain.local-backup.v1','schema':schema,'files':files,'deployments':deployments,'evidence_count':sum(p.startswith('originals/') for p in files)}
    raw=json.dumps(metadata,sort_keys=True,indent=2).encode();write('manifest.json',raw)
    (directory/'manifest.sha256').write_text(sha(raw),encoding='ascii')
    return {'status':'complete','directory':str(directory),'manifest_sha256':sha(raw)}


def restore(directory,database_name,*,expected_digest=None):
    load_local_environment();directory=Path(directory).resolve()
    if not directory.is_relative_to(ROOT/'.runtime/backups') or not re.fullmatch('ayudachain_mvp_restore_[a-f0-9]{8,32}',database_name):raise ValueError('Owned backup and new restore database required')
    raw=(directory/'manifest.json').read_bytes();expected_digest=expected_digest or (directory/'manifest.sha256').read_text().strip()
    if sha(raw)!=expected_digest:raise ValueError('Backup manifest checksum failed')
    metadata=json.loads(raw)
    for relative,digest in metadata['files'].items():
        path=(directory/relative).resolve()
        if not path.is_relative_to(directory) or sha(path.read_bytes())!=digest:raise ValueError('Backup component checksum failed')
    checkpoint(metadata['deployments'],'check')
    for d in metadata['deployments']:
        path=Path(d['source_path']).resolve()
        if not path.is_relative_to(ROOT):raise ValueError('Restore manifest outside workspace')
        original=(directory/d['backup_file']).read_bytes()
        if path.exists() and path.read_bytes()!=original:raise ValueError('Refusing to overwrite a different manifest')
        if not path.exists():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(original)
    source=os.environ['MVP_OWNER_DATABASE_URL'];info=conninfo_to_dict(source);pg_env(source)
    admin=make_conninfo(source,dbname='postgres');dsn=make_conninfo(source,dbname=database_name)
    with psycopg.connect(admin,autocommit=True) as db:
        if db.execute('SELECT 1 FROM pg_database WHERE datname=%s',(database_name,)).fetchone():raise ValueError('Restore database already exists; preserved')
        db.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(database_name)))
    run_pg('pg_restore',['--exit-on-error','--no-owner','--no-privileges','--dbname='+database_name,str(directory/'database.dump')],dsn)
    # pg_restore needs a target; this is supplied through PGDATABASE, not a URL with secrets.
    output=ROOT/'.runtime/restores'/database_name;output.mkdir(parents=True,exist_ok=False)
    shutil.copytree(directory/'originals',output/'originals') if (directory/'originals').exists() else (output/'originals').mkdir()
    with psycopg.connect(dsn,row_factory=dict_row) as db:
        db.execute(sql.SQL('SET search_path TO {},public').format(sql.Identifier(metadata['schema'])))
        from backend.scripts.setup_mvp import grant_roles
        grant_roles(db,metadata['schema'])
        rows=db.execute('SELECT * FROM evidence_versions').fetchall()
        if len(rows)!=metadata['evidence_count']:raise ValueError('Restored evidence catalogue differs')
        for row in rows:original_bytes(row,root=output/'originals')
    private=json.loads((directory/'private-config.json').read_bytes())
    # Do not emit replay/signing credentials. The ignored config is operator-owned.
    local_url=urlparse(source)._replace(path='/'+database_name).geturl()
    config={key:local_url for key in ['MVP_DATABASE_URL','MVP_OWNER_DATABASE_URL','MVP_INSPECTION_DATABASE_URL','MVP_WORKER_DATABASE_URL']}
    config.update(MVP_SCHEMA=metadata['schema'],MVP_EVIDENCE_ROOT=str(output/'originals'),MVP_RPC_URL=os.environ.get('MVP_RPC_URL','http://127.0.0.1:8545'),MVP_NODE=os.environ.get('MVP_NODE','node'),**private)
    (output/'restore-config.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
    return {'checked':True,'database':database_name,'evidence_count':len(rows),'configuration':str(output/'restore-config.json')}


def main():
    p=argparse.ArgumentParser();p.add_argument('operation',choices=['backup','restore']);p.add_argument('directory',type=Path);p.add_argument('--database');p.add_argument('--digest');a=p.parse_args()
    if a.operation=='backup':print(json.dumps(backup(a.directory)))
    else:print(json.dumps(restore(a.directory,a.database or '',expected_digest=a.digest)))


if __name__=='__main__':main()
