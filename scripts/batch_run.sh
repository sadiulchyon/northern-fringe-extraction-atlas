#!/bin/bash
# usage: scripts/batch_run.sh SITE... ; runs each site, prints onset line, then @@SITE@@ + base64 panel (resized)
for s in "$@"; do bash scripts/run_site.sh $s >/tmp/${s}_run.log 2>&1; python3 scripts/onset_table.py $s | tail -1; done
for s in "$@"; do python3 -c "
from PIL import Image; im=Image.open('/tmp/${s}_panel.jpg'); im=im.resize((960,600)); im.save('/tmp/${s}_p.jpg',quality=72)"; done
for s in "$@"; do echo "@@$s@@"; base64 -w0 /tmp/${s}_p.jpg; echo; done
