
function isTag(s) {
  if( s.startsWith("Tag"))
    return true;
  return false;
}

function getTag(s) {
  var foo = s.split("=")[1].trim().split('"')
      tagMarker = foo[0].trim();
      tag = foo[1].trim();
  return {"tag": tag, "marker": tagMarker}
}

function isTagged(s, dict) {
  var mTag = s.slice(-2),
      res = {};
  res["result"] = false;
  res["tag"] = "";
  dict.forEach((tagInfo, idx) => {
    if(tagInfo["marker"] == mTag) {
      res["result"] = true;
      res["tag"] = tagInfo["tag"];
    }
  });
  return res
}


// Run
var lines = require('fs').readFileSync('input.txt', 'utf8').split('\n').filter(Boolean),
    tags = [],
    output = {}; //This is an empty object

lines.forEach((line, idx) => {
  if( isTag(line) ) {
    tags.push( getTag(line) );
  }
});

tags.forEach((tag, idx) => {
  output[tag["tag"]] = [];
});

lines.forEach((line, idx) => {
  var check = isTagged(line, tags);
  if( check["result"] === true ) {
    output[check["tag"]].push(line.slice(0, -2));
  }
});

var keys = Object.keys(output),
    stream = require('fs').createWriteStream("output.txt");

keys.sort();
stream.once('open', function(fd) {
  for( var i = 0; i < keys.length; i++) {
    var key = keys[i],
        vals = output[key];
    stream.write(key.concat(':\n'));
    vals.map(x => stream.write(x.concat('\n')));
    stream.write('\n');
  }
  stream.end()
});
