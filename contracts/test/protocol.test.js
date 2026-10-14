const {expect}=require('chai');
const fs=require('node:fs');
const path=require('node:path');
const {canonicalBytes,contentHash}=require('../scripts/lib/evidence_protocol');
describe('Python/Node evidence protocol vectors',function(){
  for(const vector of JSON.parse(fs.readFileSync(path.join(__dirname,'../../shared/protocol/evidence-v1-vectors.json')))) {
    it('independently matches '+vector.name,function(){
      const raw=canonicalBytes(vector.input);
      expect(raw.toString()).to.equal(vector.canonical_utf8);
      expect(contentHash(raw)).to.equal(vector.sha256);
    });
  }
  it('rejects numeric/secret/surrogate material',function(){
    for(const bad of [{amount:1},{pin:'1234'},{x:'\ud800'}]) expect(()=>canonicalBytes(bad)).to.throw();
    expect(canonicalBytes({a:'e\u0301',z:null}).toString()).to.equal('{"a":"é","z":null}');
  });
});
